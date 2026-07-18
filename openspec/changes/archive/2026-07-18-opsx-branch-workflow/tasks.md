## 1. Deterministic guard (guarantee layer)

- [x] 1.1 Create `.github/scripts/opsx-branch-guard` that reads the current branch (`git rev-parse --abbrev-ref HEAD`) and staged files (`git diff --cached --name-only`)
- [x] 1.2 Fail with exit code 1 when staged paths intersect `openspec/changes/` or `openspec/specs/` AND branch is `main`/`master`; otherwise exit 0
- [x] 1.3 Print an actionable message on failure (explain the one-change-per-branch rule and show `git checkout -b <type>/<change-name>`)
- [x] 1.4 Register the guard as a `repo: local` hook in `.pre-commit-config.yaml` (`pass_filenames: false`, `always_run: true`, appropriate stages)
- [x] 1.5 Verify manually: staging an `openspec/changes/**` file on `main` is rejected; the same on a `feat/…` branch is allowed; a non-OpenSpec commit on `main` is allowed

## 2. Auto-switch (intelligence layer)

- [x] 2.1 Add the auto-switch instruction to `.claude/commands/opsx/propose.md` (and any first artifact-writing entry point): when on `main`/`master`, classify intent → `<type>`, derive kebab-case `<change-name>`, run `git checkout -b <type>/<change-name>` before the first artifact write
- [x] 2.2 Confirm `.claude/commands/opsx/explore.md` explicitly does NOT branch (read-only)
- [x] 2.3 Document the type taxonomy (`feat`/`fix`/`doc`, extensible) and the "ask when ambiguous" rule in the command instruction
- [x] 2.4 Surface the same branch discipline in the repo agent instruction file for non-Claude assistants (decide `AGENTS.md` and/or `.github/copilot-instructions.md`) — chose canonical root `AGENTS.md` + pointers in `.github/copilot-instructions.md` and `CLAUDE.md`

## 3. Contribution documentation

- [x] 3.1 Rewrite `docs/contributing.md` to describe the OpenSpec-based flow (explore → propose → apply → archive on one branch)
- [x] 3.2 Document the typed-branch convention and the one-change-per-branch / single-PR rule
- [x] 3.3 Document the pre-commit guard and that `uv run pre-commit install` activates it
- [x] 3.4 Reconcile the existing fork-based section with the new workflow (contributors on forks still branch locally)

## 4. Validation

- [x] 4.1 Run `openspec validate opsx-branch-workflow --strict` and fix any issues
- [x] 4.2 Run `uv run pre-commit run --all-files` to confirm the new hook passes on a clean tree (ran `opsx-branch-guard` via pre-commit → Passed; config parses)
- [x] 4.3 Confirm no `eos_downloader/` runtime code changed (workflow/docs/tooling only)
