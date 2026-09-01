# Interview proof map

Use the project as evidence, not as a monologue. Answer the question first, then point to the smallest relevant proof.

## Why Venatic?

**Answer shape:** The combination of investigative tradecraft and software is the reason. I want to learn rigorous corporate-intelligence work, and I am especially interested in environments where technology helps analysts structure fragmented evidence without replacing judgment.

**Proof:** one-link case → source evidence + research-budget stage.

## Why intelligence / OSINT from an AI background?

**Answer shape:** The part of AI work I enjoyed most was not generating text; it was deciding what evidence a system can rely on, resolving messy entities, handling contradictions and proving why an answer should be trusted. Corporate intelligence makes those questions the core job.

**Proof:** SafeTrace ownership graph, entity-resolution benchmark and Claim Ledger.

## How do you know when a source is trustworthy?

**Answer shape:** I separate authority, freshness, independence and relevance. An official filing can still be stale; five articles can still come from one original allegation. I try to identify the underlying evidence origin before treating repetition as corroboration.

**Proof:** source-independence view; S27 duplicate media rejected from the evidence budget.

## Tell me about a false positive you avoided.

**Answer shape:** The synthetic case has Mihailo Petrović and a sanctioned Mikhail Petrovich. The names are close, but DOB, nationality and passport conflict. I deliberately made that a critical-fail condition: fuzzy similarity is enough to investigate, not enough to identify.

**Proof:** sanctions hypothesis → REJECTED.

## What do you do when information conflicts?

**Answer shape:** Preserve both records, reason about time/source quality, and define the next evidence that could resolve the conflict. In the case, an archived leadership page names Markus Stein while the current register names Anna Keller. The answer is not to pick one silently; the filing history resolves the chronology.

**Proof:** research budget ranks S28 first.

## How do you work under time pressure?

**Answer shape:** I try to optimize decision value rather than research volume. I define what question would materially change the assessment, rank candidate sources by authority, novelty and expected information gain, and stop when further collection has low marginal value.

**Proof:** five-source budget: S28, S25, S22, S19, S24; duplicate mirror rejected.

## How do you communicate uncertainty to a client?

**Answer shape:** Separate established facts, analytical judgments and unresolved gaps. State what the evidence proves, what it does not prove and what would change the conclusion. Avoid turning a risk indicator into an allegation.

**Proof:** Cedar nominee principal remains UNRESOLVED; payment change is not promoted to fraud or sanctions evasion.

## What did the software get wrong while you built this?

Strong answer because it proves real verification:

- German financial-number parsing once turned €25,000 into €2,500,000.
- address punctuation once produced a false contradiction.
- the first browser version had a JavaScript runtime collision that stopped the graph rendering.
- relationship labels initially intercepted edge clicks.
- the blind benchmark initially scored 85/100 because the evidence contract wrongly required optional corroboration for roles already established by initial sources.

**Lesson:** passing code/tests is not the same as a correct product. I changed the product, contracts and browser gates rather than explaining the failures away.

## Did AI/agents build this for you?

**Answer shape:** Agents accelerated implementation, testing and review. The important work I owned was deciding the analyst outcome, evidence boundaries, architecture, failure conditions and acceptance criteria, then verifying the resulting workflow. When agents produced something technically valid but analytically or visually weak, I changed the specification and iterated.

Do not claim “I wrote every line”. The stronger story is that you can direct fast implementation without outsourcing judgment.

## What would you change after joining a real team?

**Answer shape:** A lot. This proof encodes my current assumptions. I would first learn the team’s research standards, source subscriptions, client formats, legal/confidentiality constraints and review process. Then I would measure where tooling actually reduces repetitive work or catches errors before changing the workflow.

That answer prevents the project from sounding like “I already know your job better than you do.”
