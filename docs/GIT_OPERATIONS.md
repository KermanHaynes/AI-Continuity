# Git operation without daily Git management

Git preserves durable source evidence, reviewed changes and their verified publication. The agent should handle these mechanics within the established architecture. The user primarily chooses the work and approves its intellectual changes.

## Main and working environments

**main** is the authoritative integrated state of the private memory repository, containing approved ongoing knowledge and preserved historical artifacts according to the operating procedures. Temporary branches are useful for isolated reconstruction, review or concurrent work; they are not required for every ordinary conversation.

Checkouts/worktrees provide separate agent working environments when supported and useful. Historical branch names from another deployment are not required conventions. Confirm the intended repository, branch and remote before writing. Never push personal memory to the public software repository.

## Distinct durable transactions

Preserve original sources separately from derived knowledge/work changes. Commit reconstruction coverage, expensive evolution work and versioned artifacts often enough to survive interruption within the user’s authority. Keep prior drafts and approved finals. Distinguish a saved file, local committed checkpoint, pushed commit and independently verified remote commit.

For archive-only preservation use the archive checkpoint/receipt mode; no fictitious derived knowledge commit is needed. For integrated closeout use the existing ordered source-preservation and derived commits, matching processing checkpoint and subsequent receipt. Follow [SESSION_CLOSE](OPERATIONS/SESSION_CLOSE.md) and the exact [SETUP](SETUP.md) contracts.

## Verify remote persistence

A successful local commit does not establish remote preservation. Push within the approved scope, fetch the intended remote branch and verify actual commit ancestry. The implemented `memory.transactions.verify_remote` fetches and checks reachability. The integrated `closeout-record` and archive-only `archive-receipt` enforce their matching checkpoint/receipt conditions.

A receipt references already-created commits and the observed remote state. Commit and push the receipt separately, then fetch and verify that receipt commit too. A commit never includes its own future SHA inside its contents. A receipt created locally but not itself verified remotely is not a completed remote closeout.

## Concurrency and recovery

Fetch before publishing overlapping work. Integrate independent changes normally, inspect compatible overlaps, and preserve competing evidence if meaning conflicts. Obtain user judgment for unresolved authoritative contradictions. Never silently force-overwrite another agent’s canonical work.

Recover interrupted file publication using the existing Git-resolved journal and `recover-publication` procedure. Verify recorded starting/replacement hashes and refuse divergent concurrent edits. Multi-file updates are recoverable, with atomic per-file replacements. Source bytes and identities survive retries.

Reconstruction checkpoints resume from the exact saved coverage and artifact stage. A failed push leaves a local durable checkpoint with a remote limitation; it is not a reason to discard completed intellectual work or reread unchanged sources. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Integrate reconstruction from a temporary branch into main

1. Preserve scope, coverage, notes and each versioned evolution/draft/final artifact on the working branch with stable IDs and exact source references. Commit intermediate checkpoints without treating draft content as approved knowledge.
2. Obtain the required user review and approval of the final narrative and chosen CURRENT form. Save approval evidence and reconcile only approved knowledge/work, retaining all earlier artifacts.
3. Fetch actual main and compare overlapping canonical records, registries and artifact paths. Merge independent changes normally; resolve compatible overlaps without data loss, and obtain user judgment for semantic conflicts. Never force-overwrite another agent’s work.
4. Integrate the approved branch into main through the repository’s authorized normal merge/PR mechanism. Preserve source-preservation commits, derived commits, checkpoints and lineage. If a workflow would squash or rewrite commits referenced by a receipt or source chronology, do not use it without a reference-preserving integration plan.
5. Validate the integrated main state, required source hashes, views, links and CURRENT. Push main within the granted scope, fetch it and verify the actual relevant ancestry. Use the matching existing checkpoint/receipt mechanism; commit and remotely verify the receipt separately. A working-branch push alone is not authoritative-main completion.
6. From the fetched main state, resolve the subject and verify CURRENT, deeper artifacts and source references are retrievable as a future session will see them. Report the actual main SHA and receipt result. Only then retire a temporary branch if authorized; its earlier artifacts remain in the integrated history.

For a single-agent normal session on main, perform the same approval, separation, validation and verification without creating an unnecessary temporary branch. The agent handles these mechanics; the user reviews the intellectual changes.
