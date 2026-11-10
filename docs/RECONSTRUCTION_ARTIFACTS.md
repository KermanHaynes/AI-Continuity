# Reconstruction artifacts, checkpoints and lineage

These operating conventions use the existing subject structure, ordinary versioned files and Git safeguards. Agents create and preserve these artifacts using the documented files and stage transitions.

## One durable run per topic and defined scope

Place generated reconstruction artifacts under the existing subject’s `ARTIFACTS/reconstruction/<run-id>/`. Use a permanent run identifier, stable subject identity and recorded scope. An authorized material subject may be created provisionally for the work; its working drafts do not become established CURRENT until approval. If subject creation has not yet been authorized, preserve the same run files in an explicitly designated private working folder and retain identity when attaching them later.

The run contains:

| File | Purpose and preservation rule |
| --- | --- |
| `SCOPE.json` | Topic boundaries, included providers/archives, period, depth, census version and changes. Retain prior scope versions. |
| `COVERAGE.json` | Every scoped conversation, source/transcript version and hash, messages/ranges read, full-read status, gaps and next resume point. Checkpoint after each bounded reading segment. |
| `WORKING_NOTES.md` | Source-linked observations and provisional evolution notes. Keep meaningful prior versions in commits. |
| `EVOLUTION_RECORD_v001.md` | Complete source-grounded evolution record, saved before narrative drafting. Later corrections create new versions. |
| `DRAFT_v001.md` | Distinct integrated draft derived from the saved complete record. Each revision gets a new file; do not replace the original. |
| `FINAL_v001.md` | User-approved narrative saved separately from drafts, with approval evidence/date and scope. Never silently rewrite it. |
| `LINEAGE.json` | Run identity, stage, immutable artifact paths/hashes, parent relationships, approval references, chosen current format and verified commit references. |

These are conventions for agent-managed files, not new CLI commands or fields to insert into canonical schemas. Follow the current runtime’s recognized metadata boundaries. Generated narratives are not original provider attachments; do not fabricate SOT artifact registrations for them. The subject INDEX already links to ARTIFACTS. Keep run discovery and deeper links in CURRENT/EVOLUTION outside generated marker blocks, not in an independently authoritative duplicate registry.

## Minimum checkpoint contents

SCOPE records topic/subject identity, provider/archive set, historical start and end where known, boundary handling, requested depth and a stable census identity. COVERAGE contains one entry for every scoped conversation: SOT/native identity where available; original time range or unknown; source and transcript hashes; expected readable message/branch ranges; examined ranges; full-read status; unavailable/incomplete status and reason; and next message/range to read.

Use distinct states such as `not_started`, `reading`, `read_in_full`, `unavailable` and `source_incomplete`. A source declared incomplete does not become complete just because all available text was read. Record both available-text coverage and known source gaps. Whole-scope completion requires the stated source coverage or an explicit scope revision; never silently drop blocked entries.

LINEAGE records each durable stage and its output path/hash, source scope, parent artifact/version, creator/reviewer identity when known, saved time, user approval evidence where applicable and actual Git commit/persistence status. Unknown timestamps and unobserved remote commits remain null. Neither approval nor remote verification can be asserted by setting a flag without evidence.

## Stage transitions

1. Reading: preserve census, coverage and notes continuously, with committed checkpoints where authorized.
2. Evolution saved: establish complete coverage for the declared scope and save the complete evolution record with its provenance before beginning the integrated draft.
3. Draft saved: create a new independent draft from that record. Retain it through review and after approval.
4. Final approved: save a separate final, link the approval and previous artifacts, and retain all drafts.
5. Current established: update canonical CURRENT only in the approved format, link deeper artifacts, reconcile related work and preserve original reasoning/history.

The complete evolution, draft, final narrative and CURRENT have separate purposes. Versions remain retrievable, including when the chosen current format reproduces the full narrative. A later ordinary change updates CURRENT and EVOLUTION with a new evidence trail; it does not overwrite the approved historical final.

## Safe resumption and writes

At interruption, save the exact read position and any completed artifact before ending. On resumption verify scope and source hashes, recover the next incomplete stage and reuse completed work. Never reread an unchanged completed census solely because drafting or review was interrupted. If evidence changed, identify only affected reading and retain previous versions.

Use existing safe write/recovery mechanisms for files and canonical changes, validate affected records, preserve distinct evidence/derived commits, and verify actual remote ancestry when publishing. See [GIT_OPERATIONS.md](GIT_OPERATIONS.md). The runtime manages canonical records and Git receipts. Agents maintain and check the coverage, narrative stages and approval records according to this procedure. The agent verifies the prescribed coverage, saved artifacts and approvals as it performs the workflow.
