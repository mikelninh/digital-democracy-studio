# Application proof — Junior Intelligence Analyst

## Why I built this

Venatic’s work sits exactly where I want to grow: public-record research, ownership networks, sanctions and financial-crime questions, asset tracing, source criticism and clear reporting — supported by software that helps analysts structure fragmented information.

Instead of only saying I am interested in that work, I built a small evidence-first investigation system around it.

## The case

**Meridian Atlas Trading — Ownership, Sanctions & Asset Attribution**

A synthetic 28-source investigation across Germany, the UK, UAE, Cyprus and Serbia asks:

> Who ultimately owns or controls the company? Is the apparent sanctions connection real? Which assets can actually be attributed? What material risks are supported? What should be investigated next?

The pack deliberately contains traps:

- economic ownership differs from voting rights;
- a nominee shareholder hides an unresolved natural-person principal;
- a near-name sanctions candidate has conflicting DOB, nationality and passport;
- a payment beneficiary changes but has a plausible receivables-assignment explanation;
- the company operates a warehouse it does not legally own;
- the lender has security but is not the property owner;
- an archived director page conflicts with the current register until chronology is checked;
- duplicated media creates apparent corroboration without independent evidence.

## Measured result

SafeTrace receives only the initial 18-source pack and does not read the hidden gold answer.

**Blind first pass: 95/100 · zero critical failures**

It correctly:

- calculates 36.4% indirect economic / 30.8% indirect voting interest for the material natural person;
- leaves the nominee principal unresolved;
- rejects the sanctions homonym using stable identifiers;
- separates property owner, operator/lessee and lender security;
- keeps the director conflict visible;
- avoids unsupported fraud or sanctions-evasion claims.

The system then gets a realistic constraint: **it may acquire only five of ten optional sources.**

A value-of-information ranker selects the five records most likely to change or strengthen the assessment and rejects duplicate media noise.

**After targeted collection: 100/100 · zero critical failures.**

## What I wanted to prove

This is not a claim that software replaces an investigator. The opposite: consequential judgments remain reviewable and evidence-bounded.

The proof is meant to demonstrate five things about how I would work as a junior analyst:

1. I structure an ambiguous question before researching.
2. I care about entity identity, provenance and source quality.
3. I distinguish a lead from a conclusion.
4. I make uncertainty and alternative explanations visible.
5. I think about the next best research action, not just how many sources I can collect.

## How I built it

I used an agent-heavy product-development workflow: I defined the outcome, architecture, evidence boundaries, failure conditions and acceptance tests; agents accelerated implementation and review; I verified the working product through CI, adversarial test cases and real browser interaction.

The result is meant to be judged as a working investigation increment, not by how many lines of code were written.

## Where I would take it next inside a real analyst team

- adapt the schema to actual analyst workflows and source subscriptions;
- learn the firm’s research standards before automating more;
- measure analyst time saved and error reduction on controlled cases;
- add temporal network analysis and source-independence views where useful;
- keep final consequential conclusions human-owned.
