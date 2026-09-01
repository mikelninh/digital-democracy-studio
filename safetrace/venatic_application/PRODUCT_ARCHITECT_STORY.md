# How I built this proof

## The operating model

I treated this application proof as a product-architecture problem, not as a coding exercise.

The loop was:

1. **Define the analyst outcome.** Not “build an ownership graph”, but: help an analyst decide who owns or controls a target, what is supported, what remains unknown, and what evidence should be collected next.
2. **Set system constraints before implementation.** Economic ownership is separate from voting and other control. Name similarity is not identity. Possession or operation is not asset ownership. Negative search results are bounded. Missing evidence must stay missing.
3. **Specify failure conditions and acceptance tests.** Every consequential claim needs evidence. Ambiguous identity must halt propagation. A sanctions homonym must be rejected when stable identifiers conflict. Nominee ownership must remain unresolved until a natural person is evidenced.
4. **Use agents for implementation, testing and review.** Separate implementation, regression, browser-QA and review passes attacked the specification from different directions.
5. **Review the working product, not just the diff.** I opened the generated interface, clicked the graph, inspected evidence, found runtime and interaction bugs, and kept the build red until the analyst workflow actually worked.
6. **Measure the result.** A hidden-gold benchmark tests a 28-source, five-jurisdiction synthetic investigation. SafeTrace scores 95/100 on the initial 18-source pack with zero critical failures, then reaches 100/100 by selecting five high-information sources from ten optional records.

## Why this matters

Implementation speed was not the limiting factor. Judgment was.

The hard decisions were:

- What should the analyst see first?
- Which conclusions are safe to automate and which require human review?
- What exactly counts as corroboration?
- When should the graph refuse to draw an edge?
- How do we distinguish ownership, voting rights, board rights, operation and security interests?
- How do we measure analytical quality without rewarding confident overclaiming?
- Which five additional sources are worth acquiring when time is limited?

Those decisions became the architecture, tests and user experience.

## What I would bring to Venatic

I am applying for a junior analyst role, so this is not an attempt to present myself as a senior architect or investigator. It is proof of the way I work.

I like ambiguous problems. I turn them into explicit questions, evidence rules and testable workflows. I use software and agents aggressively where they create leverage, while keeping human judgment around consequential conclusions. When a test or real browser interaction exposes a weakness, I change the system rather than defend the demo.

That is the operating model behind SafeTrace:

**Human judgment sets the problem and constraints. Agents accelerate implementation and review. Evidence decides what survives.**
