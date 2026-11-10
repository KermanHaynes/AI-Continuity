> Operation authority: [OPERATING_RULES.md](../OPERATING_RULES.md) governs the selected task. Historical reconstruction reads every scoped conversation exhaustively and preserves the full artifact lineage; ordinary ongoing sessions use progressive retrieval. Faithful source capture, approval of intellectual changes and actual Git verification remain required.

# Recovery

Resume archive work from verified per-source checkpoints and persistent UUID identities. Verify immutable original hashes and existing message mappings before extension. Preserve conflicting originals. Keep journals in Git-resolved metadata, outside tracked content; repository content paths remain contained. A failed push is not remote preservation. A source blocked by size, credentials or interpretation stays local with its precise blocker while independent eligible records continue. Never force-overwrite concurrent work or fabricate a successful receipt.

---

The detailed operating requirements below apply to the stated operation.

## Procedure

Executable guidance: Inspect INDEX/PROCESSING, INDEX/EXCEPTIONS and the last verified SHA. Retry register-export/register-sot only after verifying original checksums; exact reimports reuse IDs. For interrupted CLI publication inspect .git/memory-publish-journal.json and its retained stage; use `python -m memory.cli recover-publication` for validated mechanical replay. Compare each journaled replacement's before/after hashes to its current canonical file before resuming; never overwrite a concurrent edit. Keep originals, reconcile remaining derived views, validate, and record the recovery checkpoint. Use normal new commits; never destructively rewrite history. Missing native capture and remote push failures remain incomplete.

Commands emit JSON and exit 0 on success, 1 on blocking validation findings, or 2 on invalid input/operation failure. Full CLI arguments: [SETUP](../SETUP.md).

The following record and operation requirements apply.

# 13. Exception and Recovery Contract

Maintain persistent exception records with:

- Stable exception UUID
- Classification
- Detection timestamp
- Affected record IDs
- Evidence
- Last verified SHA
- Current status
- Recovery requirements
- Correcting commit references

Support these interruption conditions:

- Native capture unavailable
- Captured but not normalized
- Preserved but not integrated
- Derived reconciliation incomplete
- Validation failed
- Remote push failed
- Concurrent semantic conflict
- Verified complete

Never discard valid original evidence.

Never overwrite conflicting SOT bytes.

Resume from the last verified checkpoint.

Reattempting a failed operation must not generate duplicate identities or duplicate authoritative records.

Do not use destructive Git history rewriting as ordinary recovery.

Audits cannot autonomously resolve semantic exceptions.

---

## Changed-file publication and problem classifications

Version-2 publication journals record only intended replacements, starting hashes, replacement hashes/locations and incremental validation scope. Recovery revalidates affected dependencies and refuses divergence on changed paths; unrelated concurrent files remain untouched. Legacy journals stop for explicit recovery review. Routine overlays never copy existing SOT originals. Explicit full validation and weekly structural audits continue to verify all registered source checksums and first Git versions.

Exception classifications are extensible normalized lowercase identifiers (`[a-z0-9_]+`). Defined conditions are listed in `memory.schema.KNOWN_EXCEPTION_CLASSIFICATIONS`. `verified_complete` remains exclusively a processing state. Additional valid problem identifiers require no schema edit and retain the same permanent-ID, evidence, recovery and correcting-commit fields.
