# SafeTrace Case 004 — Gesetzes-Fairness-Monitor

This module tests political distribution claims against enacted law and attributable policy ownership.

## First question

**Does the Merz government make policy for wealthy interests while cutting support for poorer families?**

The monitor does not publish a single ideological fairness score. It separates:

- direct cash and tax effects;
- access, obligations and sanctions;
- public-revenue effects;
- reach and targeting by need;
- expected but uncertain investment or employment effects;
- policy origin and correct political attribution;
- documented lobbying positions without inferring unlawful influence.

## Initial result

The broad allegation is **partly supported**:

- substantial business tax relief was enacted by the Merz coalition;
- the July 2026 basic-security reform increased conditions and possible financial consequences for recipients;
- nominal basic-security rates were not cut in 2026, although a nominal freeze can reduce real purchasing power;
- the 2026 child-benefit increase was enacted in December 2024 and must not be presented as a new Merz-government measure.

## Run

```bash
python -m safetrace.law_fairness.build_public_status
python -m unittest discover -s safetrace/law_fairness/tests -v
```

## Publication boundary

Connections and sequence are not proof of corruption. Expected macroeconomic effects are not presented as measured outcomes. Lobby-register records show advocacy, not purchase of a political decision.
