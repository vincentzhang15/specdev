# specdev

A repo-agnostic engineering-lifecycle skill for Claude Code: build new features spec-first, and keep what's already built honest. Nothing project-specific is hardcoded — every run starts by discovering the target repo's own invariants (its *constitution*), toolchain, verification bar, and backlog convention from its docs and code, then works against those. The quality bar everywhere is the real app running end to end — never unit-test coverage.

Four modes:

- **`/specdev spec <feature>`** — spec-driven development (adapted from GitHub spec-kit + obra/superpowers): Socratic brainstorm of the ask itself → testable spec with industry research (what/why, no tech) → coverage-based clarify → plan written within the repo's constitution → dependency-ordered tasks with parallel-safe markers and per-task verification → with `--fix`, gated implementation in an isolated worktree with two-stage review (spec compliance, then code quality).
- **`/specdev`** (or `/specdev audit [dimension]`) — a comprehensive, adversarially verified audit across ten dimensions: architecture & layering, duplication, clean code, correctness & robustness, product guarantees, cost efficiency & metering, security, performance, docs truthfulness + live verifiability, and product feature maturity (spec-vs-implementation, researched against current industry standards). Report-only; `--fix` applies P0/P1 fixes under the same gates.
- **`/specdev untangle <target>`** — questions and unpicks spaghetti code by convening a council (adapted from Karpathy's LLM Council pattern): five advisors reasoning by genuinely different methods — inversion, first-principles decomposition, analogy, naive questioning, dependency graphing — then anonymized peer review, a step-back judge that separates value tensions from error catches, and a synthesized verdict that preserves the strongest dissent. With `--fix`, execution is seams-first: one behavior-preserving commit per seam, never a big-bang rewrite.
- **`/specdev cleanup [target]`** — rewrites accreted artifacts (docs, modules, configs) into one cohesive entity. It inventories the artifact's content as atomic units, designs the structure it would have if written today in one sitting, does a clean whole rewrite, then reconciles the inventory against the result so nothing is silently lost or invented. Writes by default; code targets pass the same gates.

The modes close a loop: audit's product-maturity gaps feed `spec`; `spec`'s artifacts are what the next audit grades shipped features against; audit's tangle signals name `untangle`'s targets; and `cleanup` keeps every artifact — including the specs — cohesive.

## Install

Copy (or symlink) this folder as a skill:

```sh
# globally, for all projects
ln -s "$(pwd)" ~/.claude/skills/specdev

# or per project
cp -R . /path/to/project/.claude/skills/specdev
```

See `SKILL.md` for the full process, dimension checklists, spec workflow, and council mechanics.
