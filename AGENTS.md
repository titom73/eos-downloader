# AGENTS.md

Guidance for AI coding assistants (Codex, Cursor, Copilot, Claude, …) working in
this repository. For the full human contribution guide, see
[`docs/contributing.md`](docs/contributing.md).

## OpenSpec branch discipline (required)

This project plans changes with [OpenSpec](https://github.com/Fission-AI/OpenSpec)
(the `openspec` CLI, `opsx:*` workflow). Two rules are non-negotiable:

1. **One change = one typed branch.** Every OpenSpec change lives on its own
   branch named `<type>/<change-name>`, and the *entire* lifecycle
   (`explore → propose → apply → archive`) is committed on that branch, then
   merged into `main` as a single Pull Request. Do not commit a change's
   artifacts or implementation directly to `main`.

2. **Auto-switch from `main` at the first artifact write.** When you are about to
   create the first OpenSpec artifact (proposal, design, spec, tasks) and the
   current branch is `main`/`master`, first classify the intent and create the
   branch:

   ```bash
   git checkout -b <type>/<change-name>
   ```

   | `<type>`   | When to use                                          |
   |------------|------------------------------------------------------|
   | `feat`     | Add or extend a capability (documentation optional)  |
   | `fix`      | Correct a defect or problem                          |
   | `doc`      | Documentation only                                   |
   | `refactor` / `chore` / `ci` | Other conventional types             |

   `<change-name>` is the change's kebab-case identifier. If the type is
   ambiguous, ask the contributor before branching. Pure exploration (no
   committable artifact) does not create a branch.

## Deterministic guard

A local `pre-commit` hook (`.github/scripts/opsx-branch-guard`) enforces rule 1
independently of any assistant: it **rejects any commit that stages files under
`openspec/changes/**` or `openspec/specs/**` while on `main`/`master`**. It
blocks nothing else on `main`. Activate it once with:

```bash
uv run pre-commit install
```

If a commit is rejected, create the correct `<type>/<change-name>` branch and
commit again. `git commit --no-verify` is an explicit, deliberate escape hatch.

## Other conventions

- Package/venv management via **uv** (`uv sync --all-extras`, `uv run …`).
- Quality gates: `make check` (lint + type + test). See `docs/contributing.md`.
- Never write application code from `/opsx:explore` — explore is for thinking;
  implementation happens during `/opsx:apply` on the change branch.
