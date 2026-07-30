## Context

The repository is functionally stable and already passes `flake8`, `pylint`, and `mypy`, but the implementation is unevenly distributed across a few large modules. The main hotspots are the CLI download commands, download orchestration, shared helper/reporting code, and configuration mapping. The current unit-test suite passes yet reports 94% coverage for `eos_downloader`, which is below the expected 95% threshold.

This change is intentionally internal-first: it improves maintainability without changing the public CLI surface or the programmatic entry points already used by downstream callers.

## Goals / Non-Goals

**Goals:**
- Raise measured unit-test coverage for `eos_downloader` to at least 95%.
- Reduce the number of responsibilities carried by the largest modules.
- Isolate shared EOS/CVP orchestration logic so future changes do not require mirrored edits across several command paths.
- Keep command-line behavior, supported flags, and public library usage backward compatible.
- Make the uncovered and high-risk branches easier to reason about and test independently.

**Non-Goals:**
- No feature expansion beyond what is necessary to support the refactor.
- No intentional CLI flag renaming or public API redesign.
- No migration to a different CLI framework or test framework.
- No broad rewrite of stable modules that are already cohesive and well covered.

## Decisions

### Decision: Refactor by extracting focused helpers, not by rewriting whole modules

The implementation should break large orchestration files into smaller functions or modules with explicit boundaries, while preserving the current call graph at the public entry points.

Rationale:
- This lowers regression risk compared with a rewrite.
- Existing tests can be retained and supplemented instead of replaced.
- The current code already has good behavioral coverage in several areas; extracting focused units lets that coverage be reused.

Alternatives considered:
- Full rewrite of the CLI/download stack: rejected because it is too risky for a maintainability-driven change.
- Keeping the current structure and only adding tests: rejected because it would raise coverage without addressing the maintainability hotspot.

### Decision: Treat the 95% threshold as a required quality gate for unit tests

The change should add targeted unit tests for uncovered branches and weakly covered code paths until the repository reaches at least 95% coverage for `eos_downloader` under the unit-test suite.

Rationale:
- The repository already uses coverage in local and CI quality workflows.
- The current gap is small, so enforcing the threshold is practical.
- Targeting uncovered branches produces more value than adding redundant happy-path tests.

Alternatives considered:
- Lowering the target to current reality: rejected because the explicit goal is to improve the baseline.
- Relying on integration tests to close the gap: rejected because the requirement is specifically about unit-test coverage.

### Decision: Preserve public behavior with regression tests around command surfaces

Before and during the refactor, tests should pin the existing behavior of `ardl` commands, shared download flows, and the library façades that remain public.

Rationale:
- Internal cleanup is only valuable if external behavior stays stable.
- The current code contains duplicated branches and broad exception handling; regression tests make safe extraction possible.

Alternatives considered:
- Allowing minor behavior drift during refactor: rejected because the proposal explicitly excludes breaking changes.

### Decision: Split helper/reporting internals by concern

Shared helper code should be organized around concerns such as progress reporting, signal handling, file transfer orchestration, and security helpers instead of continuing to expand one large `helpers/__init__.py` module.

Rationale:
- The current `__init__.py` is acting as a package API and an implementation bucket at the same time.
- Concern-based modules improve readability and enable more focused tests.

Alternatives considered:
- Keeping the implementation in `__init__.py` and only documenting it better: rejected because it leaves the structural problem intact.

## Risks / Trade-offs

- [Refactor churn across multiple modules] → Mitigation: keep public entry points stable and move behavior behind extracted helpers incrementally.
- [Coverage increases without meaningful quality gain] → Mitigation: prioritize currently uncovered error paths and branching logic, not duplicate happy-path assertions.
- [Module moves complicate imports and tests] → Mitigation: preserve package-level exports where needed and update imports in small, reviewable steps.
- [Shared EOS/CVP extraction accidentally changes edge-case behavior] → Mitigation: add command-level regression tests before or alongside the extractions.

## Migration Plan

1. Add or extend regression tests around the currently weakly covered CLI/config/helper branches.
2. Extract focused helpers from the largest hotspots while preserving current public entry points.
3. Re-run unit coverage and close the remaining uncovered branches until the total is at least 95%.
4. Run the standard quality gate (`make check`) before merge.

Rollback strategy:
- Because no public behavior change is intended, rollback is a standard revert of the refactor branch if regressions are discovered.

## Open Questions

- Should the 95% threshold be enforced directly in the test command/configuration during this change, or remain a documented and review-enforced target for now?
- Should `helpers/__init__.py` continue re-exporting moved helper symbols for compatibility, or can internal imports be updated everywhere in one pass?
