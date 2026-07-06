---
name: repo-audit
description: Run a comprehensive, verified audit of any repository across ten dimensions — architecture & layering, duplication, clean code, correctness & robustness, product guarantees, cost efficiency & metering, security, performance, docs truthfulness + live verifiability, and product feature maturity (spec-vs-implementation against researched industry standards). Includes an "untangle" mode that convenes a method-diverse agent council (LLM Council pattern) to question and unpick spaghetti code. The bar is the REAL APP working end to end, never unit-test coverage. Every confirmed finding is also filed to the repo's backlog. Use when the user asks to scan, audit, health-check, or deep-review a repo (or one dimension, e.g. "/repo-audit cost", "/repo-audit product"), or to untangle/refactor a tangled area ("/repo-audit untangle src/foo"). Report-only by default; applies fixes only with an explicit "--fix".
version: 1.1.0
user-invocable: true
argument-hint: "[architecture|duplication|clean-code|correctness|guarantees|cost|security|performance|docs-live|product | untangle <target>] [--fix]"
license: Apache 2.0
---

# Repo audit

A full-repo scan that produces a **scorecard + verified findings**, graded against the repo's **own** invariants — not generic lint rules. This skill hardcodes nothing about any particular project: every project-specific rule it enforces is *discovered* from the repo itself (docs, code, git history) at the start of the run. Every finding must survive adversarial verification before it is reported. The deliverable is a report the owner can act on: grades per dimension, findings ranked P0→P2, and the three highest-leverage fixes.

**Arguments:** an optional dimension filter (`architecture`, `duplication`, `clean-code`, `correctness`, `guarantees`, `cost`, `security`, `performance`, `docs-live`, `product`), or `untangle <target>`, and/or `--fix`. No filter = all ten (note: `product` involves web research and is the slowest — on a full run, ask whether to include it). `untangle <file|module|area>` = skip the scorecard and convene a council deliberation (see "Council deliberation" below) on that tangled area, producing a disentanglement verdict — report-only unless `--fix`. `--fix` = after reporting, apply P0/P1 fixes committed incrementally, each verified against the LIVE app (see fix gates below).

**Quality bar: the real app, end to end.** The bar everywhere in this audit is "does the actual product work" — a live run of the app's core flow behaving correctly. Unit tests are a free background signal if the repo has them (a red suite is still information), but never the bar, never a grading criterion, and never something to spend time writing or extending during an audit.

**Not every dimension applies to every repo.** A repo with no paid external APIs has no metering to audit; a library has no routes to auth-gate. Grade inapplicable dimensions `N/A` with one line saying why — never invent findings to fill a section.

## Process

### Phase 0 — discovery & baseline (always, cheap)

This phase is what makes the audit repo-specific. Do it before any scanning:

1. **Read the map.** `README.md`, `CLAUDE.md`/`AGENTS.md`, `CONTRIBUTING.md`, any `docs/` or architecture files. These are the map; the audit checks the territory against them.
2. **Detect the toolchain.** From `package.json` scripts, `Makefile`, `Cargo.toml`, `pyproject.toml`, CI config, etc.: the typecheck command, lint command, test command, and how the app runs locally. Run the cheap ones now: typecheck must be clean; run the test suite as a free signal only (a failure is worth reporting; coverage is NOT graded). `git status` (flag uncommitted work), note HEAD.
3. **Identify the verification bar.** How would you demonstrate the real product working end to end, right now? (Boot the dev server and exercise the core flow; run the CLI on real input; run the repo's own bench/smoke scripts if it has them.) Write this down — it is the acceptance criterion for any `--fix` work and the standard for dimension 9.
4. **Identify deploy risk.** Does pushing (or merging) auto-deploy? If yes, **never push** during this audit — the owner decides that. Committing locally is fine.
5. **Build the invariants profile.** Extract the repo's own rules from its docs, comments, and code structure: intended module/dependency order, single-authority rules ("X is the only writer of Y"), fail-direction promises ("never show unverified data"), sanctioned exceptions, cost/metering rules, naming and policy conventions (e.g. zero-TODO policies). If the repo keeps a persisted profile (e.g. `specs/invariants.md` from a previous run), load and refresh it instead of starting over; if not, persist what you derive there so the next run diffs instead of rediscovering. These discovered invariants — not this skill's text — are the checklist the dimensions below are graded against.
6. **Locate the backlog.** Find the repo's backlog convention (`TODO.md`, `BACKLOG.md`, issue tracker noted in docs). If none exists, findings live in the report only — offer to create one, don't assume.

### Phase 1 — dimension scans

For a full audit, fan out parallel read-only agents (one per 2–3 dimensions, each given the relevant checklist below **plus the discovered invariants profile** verbatim). Agents run with independent contexts — none sees another's findings while scanning (independence blocks anchoring). For a single dimension, scan inline. Agents return findings as `{file, line, claim, evidence, severity, confidence}` — raw data, not prose.

### Phase 2 — adversarial verification

Re-check every finding against current code yourself (or via a verifier agent prompted to REFUTE it). A finding with no file:line proof, or whose "dead code" has a caller anywhere in the repo (source, tests, scripts, static assets), or whose "stale claim" turns out true, is dropped silently. Only CONFIRMED findings reach the report. When a P0's validity — or the right fix for it — stays genuinely contested after refutation, escalate to a council deliberation (below) instead of picking a side on one line of reasoning.

### Phase 3 — report + backlog

Scorecard table (dimension → grade A–F → one-line justification), findings grouped by severity, then "top 3 highest-leverage fixes". **Every confirmed finding and opportunity is ALSO appended to the repo's backlog file** (matching section, one actionable line, dedupe against existing entries first, never delete existing ones) — the report is for reading now, the backlog is durable.

Severity: **P0** = loses money, breaks a product guarantee, or corrupts data; **P1** = drift that will cause a P0 or misleads an operator; **P2** = polish.

If `--fix`: apply P0/P1 in incremental commits; the gate between commits is typecheck clean + an **e2e smoke against the locally running app** using the verification bar identified in Phase 0 (boot it, exercise one real core flow, confirm success and sane output). Run the test suite too (it's free) but a working live app is the acceptance criterion. **Never push** if pushing deploys — the owner decides that.

**Cost controls.** The audit itself is read-only and free by default. Anything that spends real money or touches production needs explicit user OK first: running paid benchmark/eval scripts, `WebSearch` to re-verify current vendor pricing, writes of any kind to production systems. Read-only queries against the repo's own telemetry/analytics are allowed without asking when they're free.

---

## The ten dimensions

Each checklist below is the *generic* shape of the dimension. The specifics — which modules, which invariants, which guarantees — come from the Phase 0 profile. Where a checklist says "discovered", that is the cue to substitute the repo's own rule.

### 1. Architecture & layering
- The intended dependency order (discovered from docs or evident structure) must actually hold: verify by grepping imports, not by trusting comments. Cycles where docs claim a DAG are P1.
- Barrel/index files that docs or convention say are pure re-exports must stay pure; logic creeping into them is a finding.
- Entry points (route handlers, CLI mains, controllers) stay thin: parse → auth → delegate → record. Business logic creeping into them is a finding.
- **Single-authority invariants** (discovered): for each concept the repo declares has exactly ONE writer or ONE sanctioned call path (money mutations, user-visible copy for a given notice, the sole client wrapper for an external API), grep for a second implementation anywhere. A second writer is P1.
- Swappable seams stay swappable: where the code declares a pluggable interface (backend flags, strategy functions), verify all declared implementations still satisfy the shared signature.
- **Tangle signals** (spaghetti detection): cyclic import clusters; modules with both high fan-in AND high fan-out; shotgun surgery in the history (`git log` shows the same file sets repeatedly changed together — a change here always drags changes there); functions mixing abstraction levels (I/O + business rules + presentation in one body); control flow threaded through shared mutable state or mode flags. Report the worst offenders as findings, and name them candidates for `untangle` mode — detection is this dimension's job; the disentanglement *plan* is the council's.

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
- **Fail-direction audit** — enumerate the safety-relevant checks (discovered from the guarantees profile) and build a table: for each, does it fail OPEN or CLOSED, and is that the direction the product promise requires? Verification/safety gates should fail closed; availability-only conveniences may fail open. A safety check that fails open is P0/P1 by impact.
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
- **Every guarantee from dimensions 4–6 must be demonstrable against the RUNNING app**: it maps to an existing bench/smoke scenario or a one-off live probe you could run right now. A guarantee that can only be argued from code reading — never exercised end to end — is a P1 verifiability gap. (Unit-test coverage is explicitly NOT the criterion.)
- The repo's own e2e harnesses (benches, smoke scripts, seed users) still run end to end: paths valid, data files present, credentials path unbroken. A rotted harness is P1 because it is the app's safety net.
- Migrations/schema history: numbering sane going forward; applied migrations never renumbered.
- Docs and memory files pointing at deleted files.

### 10. Product feature maturity — spec vs implementation
The other dimensions ask "is the code right?"; this one asks **"is the product complete?"** — whether each user-facing feature is a thin MVP or genuinely competitive with what users expect from the best apps in its category. Method:

1. **Enumerate feature areas** from the live surface, not from assumptions: routes/entry points + the UI's sections + README. Re-derive the list each run — new features join automatically.
2. **Build or refresh the spec** for each area at `specs/<area>.md`. A spec is the checklist of capabilities an *industry-standard* implementation has. Derive it by **researching the current best-in-class apps for that feature category online** (WebSearch — e.g. "best <category> apps <year> features", teardown articles, changelogs). Never hardcode competitor names into this skill or the specs' criteria structure — name them inside a spec's research-notes section as evidence, dated, so specs stay refreshable as the market moves. Each spec line is a concrete capability phrased testably ("user can restrict who sees their activity", "items support notes/photos", "the action is reachable in ≤2 taps"), tagged `[core]` (users assume it exists), `[expected]` (common in leaders), or `[differentiator]`.
3. **Gap-compare** implementation against the spec, capability by capability, citing the code/UI that satisfies each or marking it missing. Judge from what actually ships, not from intentions.
4. **Grade maturity per area**: `MVP` (core gaps) / `functional` (core ✓, expected gaps) / `competitive` (expected ✓) / `best-in-class` (differentiators present). A `[core]` gap in a shipped, user-visible feature is P1.
5. **Also audit integration, not just presence**: features that exist but don't feed each other are gaps too (canonical example: user data that never influences recommendations). Ask of every data asset "what else should this power?".
6. File every gap to the backlog, and keep `specs/` committed — the next run diffs against it instead of starting over, and re-research only when a spec is >6 months old or the user asks.

---

## Council deliberation — questioning and untangling tangled code

Detection tells you a module is spaghetti; deciding how to unpick it is a design judgment where any single line of reasoning reliably misses things. For those calls this skill uses a **council** — adapted from the LLM Council pattern (Karpathy; the council-review and design-council skills): several advisors reasoning in parallel from *genuinely different methods*, anonymized peer review, a step-back judge, and one synthesized verdict with dissent preserved.

**When to convene (proportionality).** A council costs 10–20× a single analysis — convene one only when the stakes earn it: `untangle` mode on a load-bearing module, a contested P0 whose fix has multiple plausible designs, or an architecture-changing decision during `--fix`. For routine findings, Phase 2's single adversarial verifier remains the default. Councils deliberate; they never edit code.

**Mechanics:**

1. **Brief once, share with all.** Write a shared brief before spawning anyone: the tangle map (file:line evidence from the tangle signals, a dependency sketch, who calls what, and — critically — the observable behaviors that must NOT change), the discovered invariants profile, constraints, and the repo's verification bar. Every advisor gets the same brief; none sees another's reasoning while forming its position (parallel independence blocks groupthink and anchoring).
2. **Method-diverse advisors.** Diversity of reasoning *method*, not just persona — same-model advisors given only different hats converge on identical logic. The default bench, each with a mandated stance so structural tension forces coverage:
   - **Contrarian** — inversion: assume the proposed untangling shipped and broke production; trace backward to what broke. MUST find failure modes.
   - **First-principles** — decomposition: enumerate the module's actual responsibilities as atomic claims; challenge whether each belongs here at all. MUST question the existing structure, not accept it as given.
   - **Expansionist** — analogy: how do adjacent domains and well-factored codebases structure this concern? MUST find at least one alternative shape.
   - **Outsider** — naive questioning: flag every part of the design that can only be justified by insider knowledge or historical accident. MUST ask the "dumb" questions.
   - **Executor** — dependency graphing: what extraction order is actually shippable; what blocks what; where the seams already are. MUST produce a step sequence, not an end-state.
   Swap in domain seats (security, performance, data-migration) when the tangle touches those areas.
3. **Anonymized peer review.** Strip the role labels, relabel positions A–E, and have each advisor critique the other four. Anonymity removes deference to the "senior-sounding" role; critique targets reasoning, not status.
4. **Step-back judge.** One agent audits the *debate itself*, not the code: what did ALL advisors miss? And classify every disagreement — a **value tension** (a real tradeoff; surface it to the owner) or an **error catch** (someone is factually wrong; resolve it, never average over it).
5. **Synthesis with dissent preserved.** One clear, unhedged recommendation — the synthesizer may side with a minority when its reasoning is strongest (no tyranny of the majority). The verdict must state: **convergence zones** (what independent advisors agreed on unprompted — the high-confidence signal), the chosen seam-by-seam plan, **"what you lose"** (the strongest dissent, kept intact, not smoothed over), and **concrete verification steps** against the live app for each stage of the plan.

**Untangling execution (only with `--fix` or an explicit ask).** Behavior-preserving and seams-first, never a big-bang rewrite: first characterize current behavior against the live app (record what the tangled code actually does today, including its bugs — changing behavior is a separate decision for the owner); then extract one seam per commit in the Executor's order; gate every commit on the Phase 3 fix gates (typecheck + live e2e smoke). If a step's smoke fails, revert that step — don't debug forward on top of a broken extraction.

---

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
