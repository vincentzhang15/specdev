# specdev

A generic, repo-agnostic **repo-audit** skill for Claude Code. It runs a comprehensive, adversarially verified audit of any repository across ten dimensions (architecture, duplication, clean code, correctness, product guarantees, cost/metering, security, performance, docs truthfulness, and spec-vs-implementation product maturity).

Nothing project-specific is hardcoded: the skill's first phase *discovers* the target repo's own invariants, toolchain, verification bar, and backlog convention from its docs and code, then grades the repo against those.

## Install

Copy (or symlink) this folder as a skill:

```sh
# globally, for all projects
ln -s "$(pwd)" ~/.claude/skills/repo-audit

# or per project
cp -R . /path/to/project/.claude/skills/repo-audit
```

## Use

```
/repo-audit                        # full ten-dimension audit, report-only
/repo-audit cost                   # one dimension
/repo-audit untangle src/engine    # council deliberation on a tangled area → disentanglement verdict
/repo-audit --fix                  # audit, then apply P0/P1 fixes in verified incremental commits
```

The `untangle` mode convenes a method-diverse agent council (adapted from Karpathy's LLM Council pattern): five advisors reasoning by different methods (inversion, first-principles decomposition, analogy, naive questioning, dependency graphing), anonymized peer review, a step-back judge that classifies disagreements as value tensions vs error catches, and a synthesized verdict that preserves the strongest dissent. Councils deliberate; code only changes with `--fix`, seams-first, one behavior-preserving commit at a time.

See `SKILL.md` for the full process and dimension checklists.
