# Intelligence Assessment V-001

**Subject:** Northstar Components GmbH — ownership, asset, payment-route and screening review  
**Case type:** Synthetic training exercise  
**Assessment date:** 1 September 2026  
**Handling:** Public portfolio fixture; no real-world allegations  
**Confidence:** Moderate-high on documented corporate and asset relationships; moderate on current director status; unresolved on part of beneficial ownership

## Executive summary

The supplied record supports the assessment that **Meridian Ventures Ltd owns 70% of Northstar Components GmbH**, while **Alder Ventures GmbH owns 30%**. Meridian is in turn recorded as 60% owned by Asterion Capital FZE and 40% by Helix Nominees Ltd. On that basis, Asterion has a documented **42% indirect economic interest** in Northstar and Helix has a documented **28% indirect interest**. The natural person, if any, behind Helix's stake is not established by the supplied material.

The synthetic asset trace attributes the **Leipzig Distribution Centre** to Northstar as legal owner, while separately recording a lender's security interest and a related company's operation at the site. A second asset, **CNC Production Line 7**, is used by Northstar under a lease but is recorded as legally owned by Arcadia Leasing GmbH. The distinction is material: possession, use, financing and group association are not ownership.

The supplied screening fixture does **not** establish a sanctions match for Northstar director candidate Marek Vostrik. A near-name candidate, Marek Vostryk, is a poor identity match because the recorded date of birth and nationality conflict and no stable identifier overlaps. The candidate should remain `RELATED_TO` only as a screening lead, not `SAME_AS`.

Two matters justify targeted enhanced due diligence. First, the beneficial owner behind Helix Nominees Ltd's stake remains unresolved. Second, a later payment instruction directs funds for an Eastbridge Logistics contract to Oriole Settlement Services FZE, which is not the contractual counterparty or original beneficiary in the supplied agreement. This is a **transaction anomaly**, not evidence of fraud by itself.

The record also contains a contradiction about Marek Vostrik's current director status: the official filing fixture and an archived company leadership page do not describe the same current state. The official record should receive greater evidential weight, but a fresh registry history is required before stating his current status definitively.

**Recommended decision:** proceed only after verifying the unresolved beneficial ownership, authenticating the payment-change instruction through a known counterparty channel, establishing beneficiary-account ownership, refreshing current director information, and rerunning sanctions screening against authoritative live datasets relevant to the engagement.

## Key findings

### 1. Ownership and control

The German corporate filing fixture records Meridian Ventures Ltd as the 70% shareholder of Northstar and Alder Ventures GmbH as the 30% shareholder. The UK filing fixture records Asterion Capital FZE as holding 60% of Meridian and Helix Nominees Ltd as holding 40%.

The arithmetic supports a 42% indirect economic interest for Asterion (`70% × 60%`) and a 28% indirect economic interest for Helix (`70% × 40%`). These percentages describe the supplied ownership chain; they do **not** by themselves prove practical control, voting arrangements outside the supplied documents, or ultimate natural-person ownership.

**Assessment:** supported.  
**Main gap:** beneficial ownership behind Helix Nominees Ltd.

### 2. Asset attribution

The synthetic property-record fixture records Northstar as legal owner of the Leipzig Distribution Centre and separately records a security interest in favour of Borealis Bank AG. An operating-permit fixture places Northstar Operations GmbH at the site. The asset map therefore contains three different relationships to the same property: **owner**, **secured creditor**, and **operator**.

The synthetic equipment lease identifies Arcadia Leasing GmbH as legal owner of CNC Production Line 7 and Northstar as lessee. Northstar's contractual use of the equipment should not be counted as owned assets.

**Assessment:** two material asset interests traced, with legal ownership distinguished from security, operation and lease/use.  
**Analytical rule:** do not inflate a subject's asset base by treating possession, occupation, financing or group association as ownership.

### 3. Sanctions-screening identity

The screening fixture returns a near-name candidate for Marek Vostrik. The names are similar, but the candidate has a different date of birth and nationality and no stable identifier overlap.

The appropriate analytical treatment is therefore a **rejected identity merge**, not a positive sanctions finding. Fuzzy matching can generate a research lead; it cannot establish identity on its own.

**Assessment:** no confirmed match in the supplied synthetic fixture.  
**Required real-world step:** rerun against authoritative, current sanctions data at decision time and document the matching fields used.

### 4. Payment-route anomaly

The supplied contract identifies Eastbridge Logistics Sp. z o.o. as the supplier and original payment counterparty. A later instruction requests payment to Oriole Settlement Services FZE. The supplied record does not independently establish who authorised the change, why the additional entity is involved, or who owns the destination account.

Possible explanations range from legitimate settlement arrangements to error or misconduct. The evidence currently distinguishes only the **fact of the discrepancy** from hypotheses about its cause.

**Assessment:** material due-diligence flag; cause unresolved.  
**Next action:** verify the instruction through a pre-existing contact route, obtain documentary rationale, and verify account ownership before payment.

### 5. Director-status contradiction

An official corporate filing fixture and an archived company leadership page conflict on whether Marek Vostrik remained a managing director at the relevant time. A corporate website may be stale; a filing may also have an effective date or later update that matters.

**Assessment:** current status unresolved.  
**Next action:** retrieve the latest authoritative filing history and effective dates.

### 6. Negative evidence

The supplied court-record fixture contains no adverse finding against Northstar. This is recorded as a bounded no-hit, not as a statement that the company has never been involved in litigation or regulatory action.

**Assessment:** no adverse finding in this specific supplied search fixture; broader absence not established.

## Source evaluation

The assessment gives greatest weight to authoritative corporate and property filings for legal identity, ownership and registered interests. Supplied contracts are strong evidence of what the documents say but still require provenance and authenticity checks in a real engagement. Company self-reporting is useful for leads and contradiction discovery but receives less weight for current legal status. Screening output is treated as candidate generation until identity is resolved.

Source authority, relevance and freshness are scored separately. This prevents a common failure mode in which an authoritative but stale record is treated as automatically dispositive.

## Alternative explanations considered

The payment-route change could reflect a legitimate settlement agent, factoring arrangement, treasury function or group payment service. The current record does not distinguish among these possibilities. Likewise, the nominee shareholder may be routine legal administration rather than concealment. These alternatives reduce the strength of any adverse inference and define the documents that should be sought next.

The asset records also demonstrate a separate attribution risk: an entity may use a property or piece of equipment without owning it, while a lender may hold a registered security interest without being the owner. Those relationships should remain separate even when a simplified network graph would be visually tempting to collapse.

## Priority collection plan

1. Obtain current beneficial-ownership/PSC information for Helix Nominees Ltd or client-authorised KYC evidence sufficient to identify the relevant natural person(s).
2. Authenticate the payment-change request via a known Eastbridge contact and verify the beneficiary account and relationship to Oriole Settlement Services FZE.
3. Obtain current Northstar corporate filing history to resolve Marek Vostrik's director status and effective dates.
4. Refresh EU, UK, UN and any other engagement-relevant sanctions screening using authoritative current sources and preserve the screening inputs, timestamp and match rationale.
5. If asset value or recoverability is decision-relevant, refresh the authoritative property/security records and establish current encumbrances and transfer history rather than relying on the synthetic snapshot.

## Analytical caveats

This is a **synthetic portfolio case** designed to demonstrate method, not a live due-diligence or asset-recovery result. Names, identifiers, records, assets and risk signals are fixtures. The exercise intentionally includes ambiguity, contradiction and a false-positive screening candidate. No conclusion here should be applied to any real person, company or property with a similar name.

The core standard is simple: **preserve what the evidence proves, preserve what it does not prove, and make the next research decision explicit.**
