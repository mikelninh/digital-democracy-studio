from __future__ import annotations

import re
from difflib import SequenceMatcher

LEGAL_FORMS = {
    "gmbh", "ag", "kg", "eg", "mbh", "se", "sce", "aps",
    "bv", "nv", "ltd", "limited", "llc", "inc", "plc", "sa", "sarl",
}

LEGAL_SEQUENCES = [
    (["g", "m", "b", "h"], "gmbh"),
    (["s", "a", "r", "l"], "sarl"),
    (["s", "c", "e"], "sce"),
    (["a", "g"], "ag"),
    (["e", "g"], "eg"),
    (["s", "e"], "se"),
    (["b", "v"], "bv"),
    (["n", "v"], "nv"),
    (["s", "a"], "sa"),
]

GROUP_WORDS = {"group", "gruppe", "unternehmensgruppe"}
ADDRESS_STOPWORDS = {
    "strasse", "str", "straße", "street", "road", "rd", "avenue", "ave",
    "germany", "deutschland", "de", "the",
}


def transliterate(value: str | None) -> str:
    return (
        (value or "")
        .lower()
        .replace("ö", "oe")
        .replace("ä", "ae")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )


def tokenise(value: str | None) -> list[str]:
    """Normalise punctuation while preserving identity-relevant structure."""
    tokens = re.findall(r"[a-z0-9]+", transliterate(value))
    out: list[str] = []
    i = 0

    while i < len(tokens):
        for sequence, replacement in LEGAL_SEQUENCES:
            if tokens[i : i + len(sequence)] == sequence:
                out.append(replacement)
                i += len(sequence)
                break
        else:
            if len(tokens[i]) == 1:
                j = i
                letters: list[str] = []
                while j < len(tokens) and len(tokens[j]) == 1:
                    letters.append(tokens[j])
                    j += 1
                if len(letters) >= 2:
                    out.append("".join(letters))
                    i = j
                    continue
            out.append(tokens[i])
            i += 1

    return out


def legal_form(name: str | None) -> str | None:
    forms = [token for token in tokenise(name) if token in LEGAL_FORMS]
    if "gmbh" in forms and "kg" in forms:
        return "gmbh_co_kg"
    return forms[0] if forms else None


def group_marker(name: str | None) -> str | None:
    return "group" if any(token in GROUP_WORDS for token in tokenise(name)) else None


def base_tokens(name: str | None) -> list[str]:
    result: list[str] = []
    for token in tokenise(name):
        if token in LEGAL_FORMS or token == "co":
            continue
        if token in GROUP_WORDS:
            result.append("group")
        else:
            result.append(token)
    return result


def base_name(name: str | None) -> str:
    return " ".join(base_tokens(name))


def address_tokens(value: str | None) -> set[str]:
    return {
        token
        for token in tokenise(value)
        if token not in ADDRESS_STOPWORDS and not token.isdigit() and len(token) > 1
    }


def address_relation(a: str | None, b: str | None) -> str:
    if not a or not b:
        return "unknown"

    a_tokens = address_tokens(a)
    b_tokens = address_tokens(b)
    if not a_tokens or not b_tokens:
        return "unknown"

    if (
        a_tokens == b_tokens
        or a_tokens.issubset(b_tokens)
        or b_tokens.issubset(a_tokens)
    ):
        return "compatible"

    overlap = a_tokens & b_tokens
    if len(overlap) >= 2 or (
        len(overlap) == 1 and min(len(a_tokens), len(b_tokens)) <= 2
    ):
        return "compatible"

    return "conflict"


def evidence_contract(a: dict, b: dict) -> dict:
    return {
        "stable_id_a": a.get("stable_id"),
        "stable_id_b": b.get("stable_id"),
        "base_a": base_name(a.get("name")),
        "base_b": base_name(b.get("name")),
        "legal_form_a": legal_form(a.get("name")),
        "legal_form_b": legal_form(b.get("name")),
        "group_a": group_marker(a.get("name")),
        "group_b": group_marker(b.get("name")),
        "address_relation": address_relation(a.get("address"), b.get("address")),
    }


def predict(a: dict, b: dict) -> tuple[str, str, dict]:
    """
    Return (decision, reason, evidence).

    decision is one of:
      - merge: enough evidence for an automatic SAME_AS proposal
      - separate: enough evidence to keep identities distinct
      - review: plausible/ambiguous identity that should not be auto-decided

    The explicit review state is intentional: consequential identity resolution
    should optimise for precision and calibrated coverage, not forced guesses.
    """
    evidence = evidence_contract(a, b)

    stable_a = evidence["stable_id_a"]
    stable_b = evidence["stable_id_b"]
    if stable_a and stable_b:
        if stable_a == stable_b:
            return "merge", "matching stable identifiers", evidence
        return "separate", "conflicting stable identifiers", evidence

    if bool(evidence["group_a"]) != bool(evidence["group_b"]):
        a_without_group = evidence["base_a"].replace(" group", "").strip()
        b_without_group = evidence["base_b"].replace(" group", "").strip()
        if a_without_group == b_without_group:
            return (
                "separate",
                "group identity and operating/legal identity are distinct without stronger evidence",
                evidence,
            )

    form_a = evidence["legal_form_a"]
    form_b = evidence["legal_form_b"]
    if (
        form_a
        and form_b
        and form_a != form_b
        and evidence["base_a"] == evidence["base_b"]
    ):
        return (
            "review",
            "same base name but conflicting legal forms require registry/temporal evidence",
            evidence,
        )

    name_a = evidence["base_a"]
    name_b = evidence["base_b"]
    address = evidence["address_relation"]

    if name_a == name_b:
        if address == "conflict":
            return "separate", "canonical name match but addresses conflict", evidence
        if address == "compatible":
            return "merge", "canonical name + compatible address", evidence
        if len(name_a.replace(" ", "")) >= 10:
            return "review", "canonical name match but address evidence is missing", evidence
        return (
            "review",
            "short canonical name match without independent identity evidence",
            evidence,
        )

    tokens_a = set(name_a.split())
    tokens_b = set(name_b.split())
    union = tokens_a | tokens_b
    token_similarity = len(tokens_a & tokens_b) / len(union) if union else 0.0
    char_similarity = SequenceMatcher(
        None, name_a.replace(" ", ""), name_b.replace(" ", "")
    ).ratio()

    if address == "compatible" and (
        token_similarity >= 0.85 or char_similarity >= 0.94
    ):
        return (
            "merge",
            f"name similarity + compatible address "
            f"(token={token_similarity:.2f}, char={char_similarity:.2f})",
            evidence,
        )

    if address == "conflict" and (
        token_similarity >= 0.85 or char_similarity >= 0.94
    ):
        return (
            "separate",
            f"similar names but conflicting addresses "
            f"(token={token_similarity:.2f}, char={char_similarity:.2f})",
            evidence,
        )

    if token_similarity >= 0.70 or char_similarity >= 0.90:
        return (
            "review",
            f"plausible identity match lacks enough corroboration "
            f"(token={token_similarity:.2f}, char={char_similarity:.2f})",
            evidence,
        )

    return (
        "separate",
        f"insufficient identity similarity "
        f"(token={token_similarity:.2f}, char={char_similarity:.2f})",
        evidence,
    )
