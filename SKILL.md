---
name: specdev
description: Repo-agnostic engineering lifecycle skill with four modes. SPEC — build features spec-first: Socratic brainstorm, researched spec, clarify, plan, dependency-ordered tasks, gated implementation. AUDIT — adversarially verified review across ten dimensions (architecture, duplication, clean code, correctness, product guarantees, cost & metering, security, performance, docs truthfulness, product maturity vs industry standards). UNTANGLE — method-diverse agent council (LLM Council pattern) to question and unpick spaghetti code. CLEANUP — rewrite accreted docs/code into one cohesive entity. The bar is the REAL APP end to end, never unit-test coverage; the repo's invariants are discovered into a constitution, never hardcoded. Use for "spec out/plan/build a feature" ("/specdev spec dark-mode"), scan/audit/health-check ("/specdev audit cost"), refactoring tangled code ("/specdev untangle src/foo"), or a clean write of an accreted artifact ("/specdev cleanup README.md"). Audit/untangle report-only and spec implements only with "--fix"; cleanup writes by default.
version: 3.0.0
user-invocable: true
argument-hint: "[spec <feature> | audit [dimension] | untangle <target> | cleanup [target]] [--fix]"
license: MIT
---

# specdev

A repo-agnostic skill for the full engineering lifecycle: building new features spec-first, and keeping what's already built honest — with itself, with its docs, and with its users. It hardcodes nothing about any particular project: every project-specific rule it enforces is *discovered* from the target repo (docs, code, git history) before any judgment is made. Four modes share one discovery phase, one constitution, and one set of principles:

| Mode | Question it answers | Output |
|---|---|---|
| `spec <feature>` | We want to build something new — what exactly, and how will we know it's right? | Researched spec → plan → tasks; gated implementation with `--fix` |
| `audit [dimension]` *(default)* | Is the repo right, and is the product complete? | Scorecard + verified findings, P0→P2 |
| `untangle <target>` | This code is spaghetti — how should it actually be structured? | A council-deliberated disentanglement verdict |
| `cleanup [target]` | This artifact is patch-upon-patch — what is its clean form? | The artifact rewritten as one cohesive entity |

The modes feed each other: audit's product-maturity gaps are spec mode's inputs; spec mode's specs are what the next audit grades shipped features against; audit's tangle signals name untangle's targets. Methodology lineage, so future edits know what to preserve: the audit dimensions and council pattern (Karpathy's LLM Council via council-review/design-council), the spec workflow (GitHub spec-kit), brainstorm-first, per-task verification, and two-stage review (obra/superpowers).

## Operating principles (all modes)

- **The bar is the real app, end to end.** The quality bar everywhere is "does the actual product work" — a live run of the core flow behaving correctly. Unit tests are a free background signal if the repo has them (a red suite is still information), but never the bar, never a grading criterion, and never something to spend time writing during a run. This deliberately overrides methodologies that center TDD.
- **Discovered, not hardcoded.** Which modules matter, which invariants hold, what the product promises, how the app runs — all of it comes from Phase 0 discovery, none of it from this file.
- **Evidence over claims.** Every finding survives adversarial verification (a genuine attempt to refute it against current code) before it is reported; findings without file:line proof are dropped silently. Every "done" is demonstrated against the running app, never asserted.
- **Ambiguity is resolved, never guessed through.** Before expensive work — a spec, a council, a rewrite — enumerate the open questions. What the code and docs can answer, answer from them; what they can't goes to the owner as an explicit question. An assumption silently baked into work product is a defect.
- **Not everything applies everywhere.** A repo with no paid APIs has no metering to audit; a library has no routes to auth-gate. Grade inapplicable checks `N/A` with one line saying why — never invent findings to fill a section.
- **Never push.** If pushing (or merging) auto-deploys, the owner decides that. Committing locally is always fine; check `git status` first and flag uncommitted work rather than building on top of it.
- **Spending needs consent.** The skill is read-only and free by default. Paid probes — running the repo's paid benchmark/eval scripts, WebSearch to re-verify vendor pricing, anything touching production state — need explicit user OK first. Free read-only queries against the repo's own telemetry are allowed without asking.
- **Proportionality.** Fan-out and council deliberation cost many times a single analysis. Use a lone verifier for routine findings; convene a council only when the stakes earn it (see "Council deliberation").

## Phase 0 — discovery & baseline (precedes every mode)

This phase is what makes the run repo-specific:

1. **Read the map.** `README.md`, `CLAUDE.md`/`AGENTS.md`, `CONTRIBUTING.md`, any `docs/` or architecture files. These are the map; the work checks the territory against them.
2. **Detect the toolchain.** From `package.json` scripts, `Makefile`, `Cargo.toml`, `pyproject.toml`, CI config, etc.: the typecheck, lint, and test commands, and how the app runs locally. Run the cheap ones now: typecheck must be clean; run the test suite as a free signal only. Note HEAD.
3. **Identify the verification bar.** How would you demonstrate the real product working end to end, right now? (Boot the dev server and exercise the core flow; run the CLI on real input; run the repo's own bench/smoke scripts.) Write this down — it is the acceptance criterion for all code changes and the standard for dimension 9.
4. **Identify deploy risk.** Does pushing auto-deploy? If yes, the never-push principle is absolute for this repo.
5. **Build the constitution.** Extract the repo's own rules from its docs, comments, and structure: intended dependency order, single-authority rules ("X is the only writer of Y"), fail-direction promises ("never show unverified data"), sanctioned exceptions, cost/metering rules, policy conventions (e.g. zero-TODO policies). Persist at `specs/constitution.md` — if one exists from a previous run, load and refresh it instead of rediscovering. The constitution is what every mode works against: audit grades by it, spec plans within it, untangle and cleanup must preserve it.
6. **Locate the backlog.** Find the repo's backlog convention (`TODO.md`, `BACKLOG.md`, a tracker named in docs). If none exists, findings live in the report only — offer to create one, don't assume.

## Fix gates (any mode that changes code)

Write work happens in an **isolated git worktree on a branch**, cut from a verified baseline: typecheck clean and the live smoke passing *before* the first change (stop and ask if the main tree is dirty — never build on uncommitted work). Apply changes in incremental commits; the gate between commits is **typecheck clean + an e2e smoke against the locally running app** using the Phase 0 verification bar — boot it, exercise one real core flow, confirm success and sane output. Run the test suite too (it's free) but the working live app is the acceptance criterion. If a step's smoke fails, revert that step — don't debug forward on top of a broken change.

Before the work is called done, review it **twice, in order**: first **spec compliance** — does it do exactly what the spec, finding, or verdict called for, nothing more and nothing less (agents' classic failure is beautiful code that quietly reinterprets the requirement); then **code quality** — against the constitution and the standards of dimensions 1–3. Merge back only after both pass. Never push.

---

# Mode: spec

Building a new feature spec-first, so that "what" and "why" are settled — and testable — before any "how" is chosen. Artifacts live at `specs/<feature>/` (`spec.md`, `plan.md`, `tasks.md`), in the same tree audit's dimension 10 maintains, so shipped features are automatically graded against their specs on the next audit. Inputs are the user's ask, or gaps filed by a previous audit.

1. **Brainstorm.** Interrogate the ask itself before accepting it — Socratic, one question at a time: what problem is this actually solving, for whom, what happens if it doesn't exist, what are two cheaper shapes of the same value? Explore alternatives with the owner; don't spec the first framing.
2. **Specify** (`spec.md`). What and why only — user stories and concrete capabilities phrased testably ("user can restrict who sees their activity", "the action is reachable in ≤2 taps"), tagged `[core]` / `[expected]` / `[differentiator]` exactly as dimension 10 does. **No technology choices here.** For consumer-facing features, research what best-in-class apps in the category do (WebSearch) and date the findings in a research-notes section, same method as dimension 10.
3. **Clarify.** Sweep the spec for ambiguity — coverage-based, not vibes: for every capability, is scope, edge behavior, and failure behavior pinned? Resolve what the repo can answer; put the rest to the owner as explicit questions. Guessing here is how implementations drift.
4. **Plan** (`plan.md`). Now the how: architecture and tech choices, written *within the constitution* — respect single-authority rules, fail directions, metering completeness, and the discovered dependency order. A plan that needs a constitution exception must say so explicitly and get the owner's sign-off, not slip it in.
5. **Tasks** (`tasks.md`). Decompose the plan into small, dependency-ordered tasks; mark independent ones parallel-safe `[P]`. **Every task carries its own verification procedure** — how you'll know it worked, exercised against the live app, not one smoke test at the finish line.
6. **Implement** (only with `--fix` or an explicit go-ahead). Execute the tasks in order under the fix gates: worktree, per-task verification, incremental commits, then the two-stage review (spec compliance, then quality) before merging.

Without `--fix`, spec mode still writes its artifacts — specs are documents, and authoring them is the mode's purpose; only code changes wait for the gate.

---

# Mode: audit

A full-repo scan producing a **scorecard + verified findings**, graded against the repo's own constitution — not generic lint rules. The deliverable is a report the owner can act on: grades per dimension, findings ranked P0→P2, and the three highest-leverage fixes.

An optional dimension filter (`architecture`, `duplication`, `clean-code`, `correctness`, `guarantees`, `cost`, `security`, `performance`, `docs-live`, `product`) scopes the run. No filter = all ten; note `product` involves web research and is the slowest — on a full run, ask whether to include it.

**Scan.** For a full audit, fan out parallel read-only agents (one per 2–3 dimensions, each given the relevant checklist below plus the constitution verbatim). Agents run with independent contexts — none sees another's findings while scanning; independence blocks anchoring. For a single dimension, scan inline. Agents return findings as `{file, line, claim, evidence, severity, confidence}` — raw data, not prose.

**Verify.** Re-check every finding against current code yourself (or via a verifier agent prompted to REFUTE it). A finding with no file:line proof, or whose "dead code" has a caller anywhere in the repo (source, tests, scripts, static assets), or whose "stale claim" turns out true, is dropped silently. Only CONFIRMED findings reach the report. When a P0's validity — or the right fix for it — stays genuinely contested after refutation, escalate to a council deliberation instead of picking a side on one line of reasoning.

**Report + backlog.** Scorecard table (dimension → grade A–F → one-line justification), findings grouped by severity, then "top 3 highest-leverage fixes". Every confirmed finding is ALSO appended to the repo's backlog file (matching section, one actionable line, dedupe against existing entries first, never delete existing ones) — the report is for reading now, the backlog is durable. Severity: **P0** = loses money, breaks a product guarantee, or corrupts data; **P1** = drift that will cause a P0 or misleads an operator; **P2** = polish. With `--fix`, apply P0/P1 under the fix gates.

## The ten dimensions

Each checklist is the *generic* shape of its dimension; the specifics come from the constitution. Where a checklist says "discovered", substitute the repo's own rule.

### 1. Architecture & layering
- The intended dependency order (discovered) must actually hold: verify by grepping imports, not by trusting comments. Cycles where docs claim a DAG are P1.
- Barrel/index files that convention says are pure re-exports must stay pure; logic creeping into them is a finding.
- Entry points (route handlers, CLI mains, controllers) stay thin: parse → auth → delegate → record. Business logic creeping into them is a finding.
- **Single-authority invariants** (discovered): for each concept the repo declares has exactly ONE writer or ONE sanctioned call path (money mutations, user-visible copy for a given notice, the sole client wrapper for an external API), grep for a second implementation anywhere. A second writer is P1.
- Swappable seams stay swappable: where the code declares a pluggable interface (backend flags, strategy functions), verify all declared implementations still satisfy the shared signature.
- **Tangle signals** (spaghetti detection): cyclic import clusters; modules with both high fan-in AND high fan-out; shotgun surgery in the history (`git log` shows the same file sets repeatedly changed together); functions mixing abstraction levels (I/O + business rules + presentation in one body); control flow threaded through shared mutable state or mode flags. Report the worst offenders as findings and name them candidates for `untangle` mode — detection is this dimension's job; the disentanglement plan is the council's.

### 2. Duplication
- Grep for re-implementations of the repo's own utility concepts — derive the list from its actual utils/helpers modules (distance math, time/date parsing, formatting, normalization, scoring…). One implementation per concept, imported everywhere.
- Sanctioned mirrors (client/server constant tables, generated-vs-source pairs) are allowed duplication but must MATCH. Diverged mirrors are P1.
- Near-identical templates/prompts/config blocks across files: flag pairs that drifted apart where the difference is accidental rather than purposeful.
- Loose duplication in one-off scripts/benchmarks is P2 at most.

### 3. Clean code
- Dead exports: for every exported symbol in source, grep callers across the whole repo (source, tests, scripts, static assets). Zero callers = P2 finding (test-only callers = "test-only, consider inlining").
- **Stale comments are bugs** in repos that lean on rationale comments: any comment stating a checkable fact — a version, a cost figure, a file location, a default value, a model/tool name as current — must match the code *today*. Check especially around recent renames, moves, and dependency swaps in git history.
- God-file watch: modules drifting far past the repo's own norm (compare to the size distribution of its peers) are candidates for the next split.
- Config/env surface: every declared variable read somewhere; every read variable declared/documented.
- TODO/FIXME/commented-out code: grade against the repo's own policy (discovered) — some repos allow inline TODOs, some route everything to a backlog file.

### 4. Correctness & robustness
- **Fail-direction audit** — enumerate the safety-relevant checks (from the constitution) and build a table: for each, does it fail OPEN or CLOSED, and is that the direction the product promise requires? Verification/safety gates should fail closed; availability-only conveniences may fail open. A safety check that fails open is P0/P1 by impact.
- Comparisons must be like-for-like: never compare an estimate against a real measurement to make a decision the user pays for (the classic bug class: a $0 placeholder "beating" a real price).
- Atomicity & idempotency: money/credit/quota mutations are single-statement guarded updates or transactions; external payment/webhook events are deduplicated; signatures verified before any state change.
- Compensation paths: every charged or destructive action that then fails must roll back/refund — trace each failure branch.
- Background-write races: anything deferred (`waitUntil`, queues, async jobs) that writes a row/file the foreground can also write — check the interleavings.
- Every externally reachable entry point: auth gate present where required, input validated, rate-limited where abusable.

### 5. Product guarantees (the reason users trust the product)
- Enumerate the product's core promises from its docs, marketing copy, and UI text (discovered — e.g. "results are real venues", "prices are never invented", "your data is private", "output compiles"). Each promise needs an enforcement site in code, not just prompt/docs wording.
- Data honesty: where real data is missing, the UI must say so (hedge or "unavailable") — never fabricate. Every path that sets a user-visible figure routes through its single authority (dimension 1).
- Constraint enforcement: for each user-settable constraint/filter, there must be BOTH a hard enforcement site in code (never left to a model or to luck) AND a way to exercise it end to end. An unenforced constraint or an unexercisable enforcement is P1.
- Versioned caches: if any cached computation's inputs (prompts, algorithms, schemas) changed since its cache key version last bumped, stale results are being served — check git log of the input vs the key constant. P1.
- Optional (ask first): run the repo's own eval/bench harness and report the delta vs its recorded baseline.

### 6. Cost efficiency & metering
(N/A for repos with no metered external services.)
- **Metering completeness:** every call site that spends money (paid API fetches, LLM calls, per-unit billed services) must either (a) execute inside the repo's metering wrapper / tally into its cost-recording path, or (b) carry a comment declaring why it's exempt. Grep all external call sites and trace each. A new unmetered spend path is P0.
- Known sanctioned blind spots (discovered): report as context, not findings; recommend billing-export reconciliation if volume has grown.
- Fan-out caps hold: any loop over items that fetches/spends per iteration must be bounded by a discovered budget constant — flag unbounded ones.
- Cache discipline: every cached external call has a versioned key + TTL matched to the data's volatility; negative caching where "not found" is stable; keys coarsened (geography snapped, inputs normalized) so similar requests share entries.
- Unit-price tables in code vs current published vendor pricing (optional WebSearch, ask first) — stale unit prices silently corrupt any margin/cost math built on them.
- Telemetry pull (when free and read-only): recent per-kind averages/p95s from the repo's own cost records; flag regressions vs documented baselines, and any kind whose expected counters are systematically zero (the signature of a metering gap).

### 7. Security
- Secrets: local secret files gitignored; no key ever logged or echoed into client responses; server-side keys never reach the client bundle or page.
- Injection: 100% parameterized queries (grep for string interpolation into SQL/shell/eval); no user input concatenated into commands.
- Webhooks/callbacks: signatures verified (timing-safe compare) before state changes; receipts/tokens verified server-side, never trusted from the client.
- Proxies & fetch-on-behalf endpoints: inputs validated against strict patterns (no open proxy / SSRF).
- Auth: mutating routes behind session/bearer; signup/login/reset rate-limited; session tokens hashed at rest; lookups resistant to enumeration (exact-match, uniform errors/timing).

### 8. Performance & latency
- Response path: nothing slow runs before first byte/response except deliberate documented exceptions (discovered) — verify the exception list is still complete and still exclusive.
- Fan-outs parallelized, not serial; per-item expensive loops bounded.
- Round trips per request reasonable (KV/cache lookups, DB queries); no N+1 queries in list endpoints — batched paths must stay batched.

### 9. Docs truthfulness & live verifiability
- Every factual claim in the repo's docs (README, pricing/architecture docs, CLAUDE.md) spot-checked hard against code: names, versions, costs, flows, flags, file paths. Drift usually lands here first — treat any stale factual claim as P1.
- **Cross-artifact consistency** (the specs are artifacts too): `specs/` and the constitution vs the code, and both vs the backlog — a spec marking shipped what the code lacks, a backlog entry for a gap that's been resolved, a constitution rule nothing enforces anymore. Each is P1 drift.
- **Every guarantee from dimensions 4–6 must be demonstrable against the RUNNING app**: it maps to an existing bench/smoke scenario or a one-off live probe you could run right now. A guarantee that can only be argued from code reading — never exercised end to end — is a P1 verifiability gap. (Unit-test coverage is explicitly NOT the criterion.)
- The repo's own e2e harnesses (benches, smoke scripts, seed users) still run end to end: paths valid, data files present, credentials path unbroken. A rotted harness is P1 because it is the app's safety net.
- Migrations/schema history: numbering sane going forward; applied migrations never renumbered.
- Docs and memory files pointing at deleted files.

### 10. Product feature maturity — spec vs implementation
The other dimensions ask "is the code right?"; this one asks **"is the product complete?"** — whether each user-facing feature is a thin MVP or genuinely competitive with what users expect from the best apps in its category. Method:

1. **Enumerate feature areas** from the live surface, not from assumptions: routes/entry points + the UI's sections + README. Re-derive the list each run — new features join automatically.
2. **Build or refresh the spec** for each area at `specs/<area>.md` (features built by spec mode already have one at `specs/<feature>/spec.md` — grade against it). A spec is the checklist of capabilities an *industry-standard* implementation has. Derive it by **researching the current best-in-class apps for that feature category online** (WebSearch — e.g. "best <category> apps <year> features", teardown articles, changelogs). Never hardcode competitor names into this skill or the specs' criteria structure — name them inside a spec's research-notes section as evidence, dated, so specs stay refreshable as the market moves. Each spec line is a concrete capability phrased testably ("user can restrict who sees their activity", "items support notes/photos", "the action is reachable in ≤2 taps"), tagged `[core]` (users assume it exists), `[expected]` (common in leaders), or `[differentiator]`.
3. **Gap-compare** implementation against the spec, capability by capability, citing the code/UI that satisfies each or marking it missing. Judge from what actually ships, not from intentions.
4. **Grade maturity per area**: `MVP` (core gaps) / `functional` (core ✓, expected gaps) / `competitive` (expected ✓) / `best-in-class` (differentiators present). A `[core]` gap in a shipped, user-visible feature is P1.
5. **Also audit integration, not just presence**: features that exist but don't feed each other are gaps too (canonical example: user data that never influences recommendations). Ask of every data asset "what else should this power?".
6. File every gap to the backlog — gaps worth building become `spec` mode's inputs — and keep `specs/` committed: the next run diffs against it instead of starting over, and re-research only when a spec is >6 months old or the user asks.

## Report template

```
# Repo audit — <date> @ <short-sha>
Baseline: typecheck <clean/errors> · live smoke <pass/fail/not-run> · <dimensions run>
(product dimension adds: | Feature area | Maturity | Top gaps | table + specs/ updates)

| Dimension | Grade | One-liner |
|---|---|---|
...

## P0 (act now)         — finding · file:line · evidence · suggested fix
## P1 (drift, will bite) — ...
## P2 (polish)           — ...

## Top 3 highest-leverage fixes
## Sanctioned exceptions observed (no action)
```

Grades: A = invariant holds everywhere checked; B = holds with P2 nits; C = a P1 exists; D/F = P0s; N/A = dimension doesn't apply (say why). Be stingy — an unearned A makes the next audit worthless.

---

# Council deliberation

Some judgments are too consequential for one line of reasoning: how to unpick a load-bearing tangle, whether a contested P0 is real, which of several plausible fix designs to ship. For those, this skill uses a **council** — adapted from the LLM Council pattern (Karpathy; the council-review and design-council skills): several advisors reasoning in parallel from *genuinely different methods*, anonymized peer review, a step-back judge, and one synthesized verdict with dissent preserved.

**When to convene.** A council costs 10–20× a single analysis — convene one only when the stakes earn it: `untangle` mode on a load-bearing module, a contested P0 whose fix has multiple plausible designs, or an architecture-changing decision during `--fix`. For routine findings, a single adversarial verifier remains the default. Councils deliberate; they never edit code.

**Mechanics:**

1. **Brief once, share with all.** Write a shared brief before spawning anyone: the evidence (file:line, a dependency sketch, who calls what, and — critically — the observable behaviors that must NOT change), the constitution, constraints, and the repo's verification bar. Enumerate the open ambiguities while writing it: what the code and docs can't answer goes to the owner *before* the council convenes — advisors debate the design, not guesses about intent. Every advisor gets the same brief; none sees another's reasoning while forming its position — parallel independence blocks groupthink and anchoring.
2. **Method-diverse advisors.** Diversity of reasoning *method*, not just persona — same-model advisors given only different hats converge on identical logic. The default bench, each with a mandated stance so structural tension forces coverage:
   - **Contrarian** — inversion: assume the proposal shipped and broke production; trace backward to what broke. MUST find failure modes.
   - **First-principles** — decomposition: enumerate the code's actual responsibilities as atomic claims; challenge whether each belongs here at all. MUST question the existing structure, not accept it as given.
   - **Expansionist** — analogy: how do adjacent domains and well-factored codebases structure this concern? MUST find at least one alternative shape.
   - **Outsider** — naive questioning: flag every part of the design that can only be justified by insider knowledge or historical accident. MUST ask the "dumb" questions.
   - **Executor** — dependency graphing: what order of change is actually shippable; what blocks what; where the seams already are. MUST produce a step sequence, not an end-state.
   Swap in domain seats (security, performance, data-migration) when the subject touches those areas.
3. **Anonymized peer review.** Strip the role labels, relabel positions A–E, and have each advisor critique the other four. Anonymity removes deference to the "senior-sounding" role; critique targets reasoning, not status.
4. **Step-back judge.** One agent audits the *debate itself*, not the code: what did ALL advisors miss? And classify every disagreement — a **value tension** (a real tradeoff; surface it to the owner) or an **error catch** (someone is factually wrong; resolve it, never average over it).
5. **Synthesis with dissent preserved.** One clear, unhedged recommendation — the synthesizer may side with a minority when its reasoning is strongest (no tyranny of the majority). The verdict must state: **convergence zones** (what independent advisors agreed on unprompted — the high-confidence signal), the chosen plan, **"what you lose"** (the strongest dissent, kept intact, not smoothed over), and **concrete verification steps** against the live app for each stage.

---

# Mode: untangle

Questioning and unpicking spaghetti code. The target is a file, module, or area named by the user — or the worst tangle-signal offenders surfaced by an audit.

1. **Map the tangle.** Gather the evidence the council brief needs: the tangle signals present (dimension 1), a dependency sketch, callers and their expectations, and the observable behaviors that must not change.
2. **Convene the council** with the tangle map as the brief.
3. **Deliver the verdict** (report-only by default): convergence zones; the seam-by-seam disentanglement plan in the Executor's shippable order, independent seams marked parallel-safe `[P]` and **each seam carrying its own verification step** against the live app; "what you lose"; and the open value tensions for the owner.
4. **With `--fix`, execute — behavior-preserving and seams-first, never a big-bang rewrite.** First characterize current behavior against the live app, *including its bugs* — changing behavior is a separate decision for the owner. Then extract one seam per commit in the planned order, each under the fix gates (worktree, per-seam verification, two-stage review before merge).

---

# Mode: cleanup

Repos accrete. An artifact that has been patched repeatedly — a doc, a module, a config, a skill file — eventually records its *edit history* instead of its *logic*: the new section bolted on wherever the last patch landed, the same concept under three names from three eras, references that only exist because content was inserted later, shims kept past their need. Each patch was locally reasonable; the whole no longer reads as if one author wrote it in one sitting. Cleanup erases the scars without losing the substance.

**Target:** a path (one doc, one module, one directory), or nothing — in which case sweep the repo for the worst-accreted artifacts, list them, and confirm scope before rewriting.

**Accretion scars to look for:**
- Structure that mirrors edit order, not logic: appendix-itis (everything new appended at the end), sections that interrupt each other, argument lists where the newest option dangles last.
- Redundancy between vintages: two passages (or two functions) saying the same thing, written at different times, drifted slightly apart.
- Terminology drift: one concept, several names, each marking an era.
- Scar-tissue indirection: wrappers around wrappers, re-exports and shims whose only reason is where the code *used* to live.
- Register mismatch: paragraphs (or code idioms) in noticeably different voice or style between old and new parts.
- Comments narrating the patch ("new approach", "now also handles X") rather than the code.

**Method — rewrite, don't re-patch:**

1. **Inventory.** Extract the artifact's actual content as atomic units — every fact, rule, requirement, behavior. For code: the observable behavior and its callers' expectations, not the current shape. Ambiguities in what a unit means are surfaced to the owner, never guessed through.
2. **Design the structure it would have if written today, in one sitting** — ordered by logic, one name per concept, one home per idea.
3. **Clean write.** Rewrite the artifact whole. Incremental edits are exactly the process that produced the scars; do not use them here.
4. **Reconcile.** Diff the inventory against the rewrite: every unit is either present or *deliberately dropped and listed in the commit message*. Nothing silently lost, nothing silently invented. Code targets must additionally pass the fix gates.
5. **One commit per artifact**, message stating what was consolidated and any deliberate drops.

Cleanup **writes by default** — a cleanup that only describes itself is a report, and audit already produces those. It stays safe the same way everything here does: clean tree to start, incremental commits, code gated on the live smoke, and never a push.
