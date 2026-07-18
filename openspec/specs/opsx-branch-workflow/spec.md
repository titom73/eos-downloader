# opsx-branch-workflow Specification

## Purpose
TBD - created by archiving change opsx-branch-workflow. Update Purpose after archive.
## Requirements
### Requirement: Typed branch naming convention

Every OpenSpec change SHALL live on a dedicated git branch named `<type>/<change-name>`, where `<change-name>` is the change's kebab-case identifier and `<type>` is derived from the contributor's intent.

The `<type>` value MUST be one of:
- `feat` — the change adds or extends a capability (optionally including its documentation).
- `fix` — the change corrects a defect or problem.
- `doc` — the change updates documentation only.

The taxonomy MAY be extended with additional conventional types (`refactor`, `chore`, `ci`) as needed. `main`, `master`, and release branches are reserved and MUST NOT be used to host a change's working artifacts.

#### Scenario: Feature change with documentation

- **WHEN** a contributor starts a change that adds a new capability and updates its docs
- **THEN** the branch is named `feat/<change-name>`

#### Scenario: Documentation-only change

- **WHEN** a contributor starts a change that only updates documentation
- **THEN** the branch is named `doc/<change-name>`

#### Scenario: Fix change

- **WHEN** a contributor starts a change that corrects a problem
- **THEN** the branch is named `fix/<change-name>`

### Requirement: Whole lifecycle stays on one branch

The full OpenSpec lifecycle of a change — exploration outputs, `proposal.md`, `design.md`, delta specs, `tasks.md`, the implementation, and the archive commit that updates main specs — SHALL be committed on the change's own branch, independent of `main` and of other change branches. The change SHALL be integrated into `main` as a single Pull Request.

#### Scenario: Archive happens on the change branch

- **WHEN** a change is archived after implementation is complete
- **THEN** the move into `openspec/changes/archive/` and the updates to `openspec/specs/` are committed on the change's branch, not on `main`

#### Scenario: No cross-branch dependency

- **WHEN** a change branch is created
- **THEN** it does not depend on any branch other than its base (`main`), and can be reviewed and merged as one unit

### Requirement: Auto-switch from main at first artifact write

When an OpenSpec artifact is about to be written for the first time while the current branch is `main` (or `master`), the opsx skill layer SHALL classify the contributor's intent into a `<type>`, derive a kebab-case `<change-name>`, and create and switch to `<type>/<change-name>` before writing the artifact. Exploration, which produces no committed artifact, does not trigger the switch.

#### Scenario: First artifact triggers branch creation

- **WHEN** the opsx workflow is about to create the first change artifact and the current branch is `main`
- **THEN** it runs `git checkout -b <type>/<change-name>` and writes the artifact on the new branch

#### Scenario: Already on a change branch

- **WHEN** the opsx workflow creates an artifact and the current branch is already a `<type>/<change-name>` branch
- **THEN** it does not create a new branch and continues on the current branch

#### Scenario: Explore does not branch

- **WHEN** the contributor only explores and no artifact is committed
- **THEN** no branch is created

### Requirement: Deterministic pre-commit guard for OpenSpec artifacts

The repository SHALL provide a deterministic guard, registered as a local `pre-commit` hook, that runs independently of any AI assistant. The guard SHALL reject a commit when staged files include paths under `openspec/changes/**` or `openspec/specs/**` and the current branch is `main` or `master`. The guard SHALL NOT block commits that touch only other paths, and SHALL NOT block OpenSpec commits on non-reserved branches.

When it rejects a commit, the guard SHALL print an actionable message explaining that OpenSpec changes must live on a `<type>/<change-name>` branch and how to create one.

#### Scenario: OpenSpec artifact staged on main is rejected

- **WHEN** a commit is attempted on `main` with a staged file under `openspec/changes/` or `openspec/specs/`
- **THEN** the guard fails the commit and prints guidance to create a `<type>/<change-name>` branch

#### Scenario: OpenSpec artifact on a change branch is allowed

- **WHEN** a commit is attempted on a `feat/…`, `fix/…`, or `doc/…` branch with staged OpenSpec files
- **THEN** the guard allows the commit

#### Scenario: Non-OpenSpec commit on main is allowed

- **WHEN** a commit on `main` stages only files outside `openspec/changes/` and `openspec/specs/`
- **THEN** the guard allows the commit

### Requirement: Contribution documentation reflects the workflow

`docs/contributing.md` SHALL document the OpenSpec-based contribution workflow, including the typed-branch convention, the one-change-per-branch rule, the auto-switch behavior, and the pre-commit guard (including that `uv run pre-commit install` activates it). The same branch discipline SHALL be surfaced to non-Claude AI assistants through the repository's agent instruction file(s).

#### Scenario: Contributor reads the workflow

- **WHEN** a contributor opens `docs/contributing.md`
- **THEN** they find the typed-branch convention, the lifecycle-on-one-branch rule, and how the guard enforces it

#### Scenario: Non-Claude assistant is informed

- **WHEN** a contributor uses a non-Claude AI assistant configured from the repo's agent instruction file
- **THEN** that file states the typed-branch rule and the guard's existence

