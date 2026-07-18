## Why

Today the OpenSpec workflow (`explore → propose → apply → archive`) can run directly on `main`, mixing planning artifacts, implementation, and archived specs into whatever branch the contributor happens to be on. This makes a single change hard to review as one unit and risks polluting `main`. Contributors also use different AI assistants (Claude Code, Codex, Cursor, …), so any rule enforced only through skill prose is silently skippable. We need a workflow where each change lives fully in its own typed branch, with a guarantee that does not depend on which LLM is driving.

## What Changes

- Establish the rule: **one OpenSpec change = one branch** named `<type>/<change-name>`, holding the entire lifecycle (proposal, design, specs, tasks, implementation, and the archive commit), merged into `main` as a single Pull Request.
- Define the branch **type** taxonomy, derived from the contributor's intent: `feat` (add capability, optionally with docs), `fix` (correct a problem), `doc` (documentation only), extensible to `refactor`, `chore`, `ci`.
- **Auto-switch (convenience layer, LLM-driven):** when an OpenSpec artifact is first written while on `main`, the opsx skill classifies the intent, derives a kebab-case change name, and runs `git checkout -b <type>/<change-name>` before writing.
- **Guard (guarantee layer, deterministic):** a local `pre-commit` hook refuses any commit that stages files under `openspec/changes/**` or `openspec/specs/**` while on `main`/`master`, printing guidance on how to create the correct branch. It blocks nothing else on `main`.
- Update `docs/contributing.md` to document the OpenSpec-based contribution flow and the branch discipline.
- Surface the same rule to non-Claude assistants via the repo's agent instruction file(s).

## Capabilities

### New Capabilities
- `opsx-branch-workflow`: Branch discipline for OpenSpec changes — typed-branch naming convention, LLM-driven auto-switch from `main` at first artifact write, and a deterministic pre-commit guard that prevents OpenSpec artifacts from being committed on `main`.

### Modified Capabilities
<!-- No existing spec capabilities change their requirements. -->

## Impact

- **New:** `.github/scripts/opsx-branch-guard` (deterministic guard script).
- **Modified:** `.pre-commit-config.yaml` (register the local guard hook), `.claude/commands/opsx/explore.md` and `.claude/commands/opsx/propose.md` (auto-switch instruction), agent instruction file(s) for non-Claude LLMs, `docs/contributing.md` (workflow rewrite).
- **Developer workflow:** contributors must run `uv run pre-commit install` (already documented) for the guard to be active locally; the guard also protects CI-side hygiene.
- **No application/runtime code** (`eos_downloader/`) is affected.
