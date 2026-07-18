## Context

The repo already ships the opsx skills/commands (`.claude/skills/openspec-*`, `.claude/commands/opsx/*`), an initialized `openspec/` root (schema `spec-driven`), and a `pre-commit` config that already uses `local` hooks (black, flake8, pylint, mypy). Contributors may drive the workflow with different AI assistants, and some commit by hand. The current `docs/contributing.md` describes a fork → branch → PR flow with no mention of OpenSpec.

The core constraint: skill prose is advisory (an assistant can ignore it or be swapped out), so a rule that must *always* hold cannot rely on the LLM alone. Conversely, a deterministic git-level hook cannot read natural-language intent to pick `feat` vs `fix` vs `doc`.

## Goals / Non-Goals

**Goals:**
- Keep every change's whole OpenSpec lifecycle on one typed branch, merged as a single PR.
- Auto-create the branch from `main` at first artifact write, with a type derived from intent.
- Guarantee OpenSpec artifacts cannot be committed on `main`, regardless of which LLM (or none) is used.
- Document the workflow for humans and non-Claude assistants.

**Non-Goals:**
- Turning `main` into a fully protected trunk — only OpenSpec paths are guarded; ordinary code commits on `main` remain allowed locally.
- Server-side branch protection or CI gating (out of scope here; the guard is a local pre-commit hook).
- Having the deterministic guard infer the branch *type* — type classification stays with the skill layer.
- Auto-switching branches from inside the git hook (risky with uncommitted work); the hook only blocks.

## Decisions

**Decision 1 — Two-layer design (intelligence vs guarantee).**
The type/name classification and the `git checkout -b` live in the opsx skill layer (Claude Code commands + agent instruction files). The hard guarantee lives in a deterministic `pre-commit` hook. Rationale: resolves the intent-vs-determinism contradiction — the LLM picks the type, git enforces the discipline. Alternative considered: a single Claude Code `settings.json` hook — rejected because it only fires in Claude Code, not for other assistants or manual commits.

**Decision 2 — Guard scope: OpenSpec paths only.**
The guard rejects a commit only when staged paths intersect `openspec/changes/**` or `openspec/specs/**` while on `main`/`master`. Rationale: matches the chosen scope — protect the opsx workflow without blocking normal `main` commits. Alternative considered: block all commits on `main` (trunk-protected) — rejected as too broad for this repo's habits. The guard validates *nothing* about the branch name pattern; naming is a skill-layer convention, keeping the guard simple and stable.

**Decision 3 — Guard implemented as a `local` pre-commit hook.**
Reuse the existing `repo: local` block in `.pre-commit-config.yaml`; ship the logic as a small script under `.github/scripts/`. Rationale: the project already documents `uv run pre-commit install`; the hook then runs for every contributor and every assistant, and is trivially testable in isolation. The script reads the current branch (`git rev-parse --abbrev-ref HEAD`) and the staged file list (`git diff --cached --name-only`), exiting non-zero with guidance on violation.

**Decision 4 — Auto-switch is skill-layer only, triggered at first artifact write.**
`explore` (read-only) never branches; `propose` (and any first artifact-writing step) performs the switch when on `main`. Rationale: explore often has no change name yet, and produces nothing to commit. Non-Claude assistants get the same instruction via the repo agent file so behavior is consistent across tools.

**Decision 5 — Type derivation.**
`feat` when the change adds/extends a capability (docs optional), `fix` when it corrects a problem, `doc` when documentation-only; extensible to `refactor`/`chore`/`ci`. The skill infers this from the change description; when ambiguous it asks the contributor.

## Risks / Trade-offs

- **Guard inactive if `pre-commit install` was skipped** → Document it prominently in `docs/contributing.md`; keep the message actionable; consider a CI job later that runs the same guard as a backstop.
- **Assistant ignores the auto-switch instruction** → The pre-commit guard is the safety net: the commit fails on `main` and the contributor is told to branch. The two layers are complementary, not redundant.
- **`.claude` skill edits could be overwritten by `openspec update`** → Keep the durable rule in the repo agent instruction file and `docs/contributing.md`; treat command-file edits as convenience that can be re-applied.
- **Legitimate need to touch `openspec/specs/` on main** (e.g. a merge) → Merges are not commits authored on `main` in the normal flow; direct authoring on `main` is exactly what we want to block. `--no-verify` remains an explicit human escape hatch.

## Migration Plan

1. Land this change on `feat/opsx-branch-workflow` (already bootstrapped manually since the rule does not exist yet).
2. Add the guard script + register the local hook; contributors re-run `uv run pre-commit install`.
3. Update opsx command files and the agent instruction file with the auto-switch rule.
4. Rewrite `docs/contributing.md`.
5. Rollback: remove the local hook entry from `.pre-commit-config.yaml` and delete the script; no runtime code is affected.

## Open Questions

- Should a CI job run the same guard as a server-side backstop, or is the local hook sufficient for now?
- Which agent instruction file is canonical for non-Claude assistants in this repo (`AGENTS.md` vs `.github/copilot-instructions.md`) — surface the rule in one or both?
