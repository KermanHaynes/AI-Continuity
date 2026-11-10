# Software maintenance

This document is a companion to [the architectural specification](ARCHITECTURE_SPEC.md). Numbered sections share the specification’s contract section namespace: maintenance sections 18 and 21 supplement architectural sections 18 and 21. Stable requirement identities span both documents; checklist item numbers are presentation order, not requirement identities.

These procedures govern changes to the working software. Ordinary memory operations follow [OPERATING_RULES.md](OPERATING_RULES.md).

# 17. Integrity scenarios and required behavior

Examples and automated checks use explicitly fictional source material.

Integrity handling distinguishes valid scenarios from deliberately invalid states.

## A. Native archive preservation

Two conversations share one original export.

Both register successfully with distinct SOT IDs.

The original export is preserved once.

Reimporting the same conversation is idempotent.

An expanded export preserves the earlier version.

A conflicting export is flagged, not overwritten.

## B. Source fidelity

Verify hashes, message counts, role totals, message IDs, anchor uniqueness, topic references, and registered attachments.

Introduce incorrect values individually and require validation failures.

## C. Multitopic conversation

One SOT contains three subjects in overlapping and noncontiguous message ranges.

All three subjects reference the same original SOT.

No duplicate original archive is created.

## D. Evolving knowledge

Three conversations establish an original position, reject an alternative, and later introduce unresolved evidence.

The established current position remains correct.

The complete historical reasoning is retained.

The unresolved evidence is not silently promoted into a new decision.

## E. Subject identities

Create two distinct subjects with similar names.

Register aliases.

Verify unambiguous lookup, rename stability, and detection of colliding aliases.

Do not silently merge identities.

## F. Work continuity

Create an activity with multiple status transitions, external interactions, deadlines, intermediate outcomes, and pending external results.

Verify the historical operational narrative and resumption metadata.

Completion without an external outcome must remain valid.

## G. Work relationships

A valid reciprocal parent/child pair must pass.

A valid three-level hierarchy must pass.

A missing reciprocal reference must fail.

A genuine hierarchy cycle must fail.

A genuine dependency cycle must fail.

A succession cycle must fail.

A valid dependency between related hierarchical records must not be rejected merely because of the hierarchy.

## H. Temporal behavior

Test dates before and after local midnight, daylight-saving transitions, date-only commitments, unknown dates, cancelled events, and completed obligations.

Ensure the agenda and daily audit behave correctly.

## I. Session opening

Using only synthetic repository contents, resolve a subject by alias, retrieve its current state, associated work, source chain, and resumption context.

Recovered state comes from repository records rather than an earlier process’s memory.

## J. Closeout transaction

Use a temporary local bare Git remote.

Create separate preservation and derived commits.

Push and verify them.

Create and push a later receipt commit.

Advance the repository afterward.

Verify the earlier closeout remains valid.

Reject forged or missing evidence.

## K. Recovery

Interrupt a synthetic import or closeout after source preservation.

Resume from the last verified checkpoint.

Confirm the source is not duplicated and the resulting indexes reconcile.

## L. Concurrency

Create two independent branches from the same base SHA.

Test unrelated compatible updates and conflicting updates to the same canonical record.

Prove no last-writer-wins data loss.

## M. Read-only audits

Compare the repository worktree and tracked-file checksums before and after each audit.

No canonical tracked file may be changed.

## N. Defect sensitivity

For every mandatory validator invariant, include at least one fixture in which violating that invariant produces the expected finding.

Record checks cover populated records and invalid states as well as empty registries.

---

# 18. Contract binding maintenance

Each row must contain:

- Requirement ID

- Exact requirement

- Authoritative record or schema

- Implementation path/function

- Governing procedure

- Positive test

- Negative test where applicable

- Actual result

- Completion status

- Evidence or limitation

Maintain an explicit binding for every active requirement when changing the software.

The repository's design documentation must be reconciled to this specification.

# 19. Software maintenance sequence

Maintenance follows these dependencies:

1. Preserve the intended repository state and inspect current changes.
2. Read the current architectural specification.
3. Keep schemas and templates aligned.
4. Preserve canonical reader/writer behavior.
5. Preserve permanent identity and SOT registration behavior.
6. Maintain knowledge identity and source-chain validation.
7. Preserve canonical Markdown WORK records.
8. Maintain lifecycle and relationship rules.
9. Preserve agenda and time-zone semantics.
10. Keep session instructions aligned with the actual interface.
11. Preserve source and reconciliation transaction separation.
12. Preserve concurrency and recovery controls.
13. Preserve receipt and remote-verification requirements.
14. Maintain configured finding-only audit behavior.
15. Maintain synthetic integration and invalid-state coverage.
16. Keep operating documentation consistent with the implementation.
17. Keep machine-readable contract references consistent.
18. Run the complete applicable verification suite.
19. Verify configured CI within the approved operation.
20. Publish only the approved change through the normal repository workflow.

Preserve compatible runtime behavior when modifying the software.

Remove obsolete code, schemas, templates, and documentation that contradict the authoritative architecture.

Do not retain a compatibility mechanism that silently permits invalid legacy records.

---


# 21. Change verification

1. Preserve the authoritative architectural specification in the repository.

2. Every mandatory requirement is traced.

3. Canonical record structures match the specification.

4. Schemas and generators agree.

5. Operating procedures are executable and internally consistent.

6. All required synthetic positive and negative tests pass.

7. Configured CI results are reported for the operation actually run.

8. Verification examples do not modify a user’s personal memory.

9. Only authorized changes enter the authoritative branch.
