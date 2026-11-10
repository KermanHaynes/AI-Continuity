# Setup and deterministic commands

Use Python 3.11 or later, Git, PyYAML 6.x, jsonschema 4.x, and the standard-library zoneinfo module. Install system IANA time-zone data if your Python distribution does not provide it. No service or database is needed.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m memory.cli validate
python -m unittest discover -s tests -v
```

Run commands from the repository root, or place `--root /absolute/repo` before the operation. Commands emit JSON on stdout; errors emit JSON on stderr. Exit codes are 0 for success or nonblocking warnings, 1 for blocking validation findings, and 2 for invalid input or an operation failure. Audit timestamps require explicit UTC offsets. `tools/validate.py check` is a thin wrapper for `validate`; it has no independent engine.

All command mutations serialize cooperative local writers, stage only new/modified files over read-only metadata dependencies, incrementally validate affected records/relationships, and compare the starting hashes of every replacement, and publish changed files atomically per file. A Git-directory publication journal retains recovery staging on interruption. Multi-file publication is recoverable, rather than an atomic filesystem transaction. Direct review edits require `render-agenda` and `validate` before commit. Explicit caller-supplied IDs are references to existing records; new permanent identities come from UUIDv4.

The following commands are exact examples. UUID arguments below must be replaced with actual existing IDs. Input JSON paths are local files and are never interpreted as commands.

```sh
python -m memory.cli new-id
python -m memory.cli register-export /path/to/native.json --provider fictional --environment synthetic --scope 'Verified fictional full capture' --completeness complete
python -m memory.cli register-export /path/to/expanded.json --provider fictional --environment synthetic --scope 'Expanded fictional capture' --previous-export-id EXPORT_UUID
python -m memory.cli register-sot EXPORT_UUID /path/to/normalized-mapping.json
python -m memory.cli resolve-source SOT_UUID --message-id MESSAGE_UUID
python -m memory.cli create-subject 'Fictional subject' --slug fictional-subject --scope 'Explicit subject scope'
python -m memory.cli resolve-subject 'Fictional subject'
python -m memory.cli associate-source SUBJECT_UUID SOT_UUID MESSAGE_UUID --classification model_suggestion --description 'An unresolved suggestion' --occurred-at 2026-01-01
python -m memory.cli create-work 'Fictional material experiment' --type experiment
python -m memory.cli resolve-work WORK_UUID
python -m memory.cli transition-work WORK_UUID active --reason 'Established activity started' --evidence /path/to/source-refs.json --effective-at 2026-01-01T12:00:00-05:00
python -m memory.cli render-agenda
python -m memory.cli set-processing SOT_UUID topic_indexing complete
python -m memory.cli set-processing SOT_UUID work_reconciliation not_applicable --reason 'Reviewed source passages contain no material operational contribution'
python -m memory.cli raise-exception preserved_not_integrated --affected-id SOT_UUID --evidence 'Preservation checkpoint exists; review pending' --last-verified-sha FULL_SHA
python -m memory.cli review-queue
python -m memory.cli plan-repair
python -m memory.cli apply-repair --authorized
python -m memory.cli audit daily --at 2026-10-21T12:00:00-04:00
python -m memory.cli audit weekly
python -m memory.cli audit monthly
python -m memory.cli closeout-record TRANSACTION_UUID --preservation FULL_SHA --derived FULL_SHA --remote origin --branch review --affected-id WORK_UUID --limitation 'Explicit limitation, if any'
```

`register-export` optionally accepts `--native-export-id TEXT`, repeated `--previous-export-id UUID`, and `--completeness complete|partial|unknown` (default unknown). The scope is evidence supplied by a supported capture environment; the CLI cannot infer completeness. Obvious credentials or files at/over 100 MiB stop preservation without rewriting originals.

`register-sot` consumes an explicit normalized mapping, created by a supported adapter or operator. This is not a provider-native parser and must not be used to reconstruct evidence from memory. Minimal fictional example:

```json
{
  "native_conversation_id": "fictional-conversation-1",
  "title": "Fictional example",
  "original_started_at": null,
  "original_ended_at": null,
  "capture_gaps": [],
  "messages": [
    {
      "native_message_id": "fictional-message-1",
      "role": "user",
      "original_timestamp": null,
      "source_locator": "conversations[0].messages[0]",
      "content": "Exact fictional source content.",
      "attachment_ids": [],
      "limitations": []
    }
  ]
}
```

When native_conversation_id is absent/null, supply `source_conversation_locator`. A likely cross-export fingerprint match requires explicit provenance review and an existing `sot_id`; it cannot be silently merged. Reimport compares exact normalized content checksums, native IDs, role and original time. Original export bytes remain the source authority. Conflicting exports are preserved separately and an exception records the conflict.

Evidence JSON for `transition-work` is an array, for example `[ { "sot_id": "SOT_UUID", "message_ids": ["MESSAGE_UUID"] } ]`. Source associations require exact resolvable message references. Classifications are `established_user_position`, `user_proposal`, `model_suggestion`, `rejected_or_superseded`, `supporting_evidence`, `contradictory_evidence`, and `unresolved_interpretation`. Recording evidence does not change CURRENT or establish acceptance.

`render-agenda` regenerates agenda, registry, aliases, subject INDEX navigation, and topic Markdown. `plan-repair` is read-only. `apply-repair --authorized` applies only those mechanical view corrections; it cannot repair interpretations. If structural errors remain after those view corrections, validation prevents the staged changes from being written to the memory repository.

For a closeout, commit source preservation separately from derived reconciliation, push both, and record `INDEX/PROCESSING/<transaction-id>.yaml` according to `schemas/processing.schema.json`. Its verified_complete checkpoint must identify all affected records, their dispositions, the starting SHA, and the already-created preservation/derived SHAs. Commit/push the checkpoint, then run `closeout-record`. That command fetches and verifies actual remote ancestry, checks the preservation commit includes original evidence, and checks materially changed subjects/work are covered. Commit/push the receipt separately and independently verify that receipt commit. A receipt never includes its own commit SHA. A later ordinary commit does not invalidate earlier ancestry evidence.

Use `python -m memory.cli OPERATION --help` for the complete argument grammar. The commands above use fictional inputs. Run history import and archival closeout only within the user-authorized source and publication scope.

Interrupted multi-file publication can be resumed with `python -m memory.cli recover-publication`. It verifies journaled paths against their starting/published hashes, validates the affected overlay, and replays the retained replacements. Unrelated concurrent files remain untouched. Any divergent concurrent edit blocks replay for review. Further CLI mutations stop while a journal remains.

## Incremental validation and recovery behavior

Routine writes report `validation_scope: incremental` with their result. This is not a full-repository audit. The overlay links metadata dependencies, stages replacements, and never copies existing native originals. Global metadata checks retain uniqueness, reference, registry, and relationship consistency; detailed conversation/source-byte checks are limited to affected conversations, attachments and their export dependencies. Each changed existing file has a starting checksum captured before its first write. The version-2 journal records the intended path, original hash, replacement hash/location, and validation scope. Publication uses a temporary file in the destination directory and an atomic rename. Recovery refuses changed journaled paths while preserving unrelated concurrent edits. Legacy version-1 journals require explicit review rather than an unsafe automatic migration.

Use `python -m memory.cli validate` for full source checks, including checksums and first preserved Git versions. CI and weekly structural audits also retain full checks. Unrelated source corruption can therefore remain outside a routine WORK update's incremental scope; it is detected by the applicable full check and by an affected-source check. Incremental success never certifies untouched archive bytes.

Provider-independent attachments:

```sh
python -m memory.cli register-artifact SOT_UUID /path/to/source.pdf --native-artifact-id genuine-native-id --message-id MESSAGE_UUID --description 'Source attachment'
python -m memory.cli register-artifact SOT_UUID /path/to/source.pdf --artifact-id EXISTING_ARTIFACT_UUID
```

Only SOT_UUID and SOURCE_FILE are required. Repeat `--message-id` to associate additional exact messages. Optional native IDs are preserved as metadata and never interpreted as paths. Without a native or explicit existing ID, identical bytes in the same SOT resolve idempotently when unambiguous. A supplied existing/native identity with conflicting bytes preserves a separate artifact with `conflicts_with`, records a `duplicate_identity_conflict` exception, publishes validated conflict evidence, and exits 2 to report the unresolved conflict. Retrying that same conflict reuses its preserved UUID. Missing SOT/messages/files, path escapes, or a corrupt established attachment stop publication. Unknown message associations remain empty rather than invented.

Exception classifications use `[a-z0-9_]+`. Known classifications are documented by `memory.schema.KNOWN_EXCEPTION_CLASSIFICATIONS`; additional normalized identifiers need no schema change. `verified_complete` is reserved for transaction processing and is rejected as an exception classification. Permanent exception IDs, evidence, affected references, recovery instructions, and correcting commits remain required.

Daily watches use each obligation's IANA time zone. External deadlines and follow-ups alert through seven local calendar days; overdue/due follow-ups remain visible. Scheduled events alert only within seven calendar days. Past scheduled events receive a status-review finding. Unknown dates and inactive obligations never become overdue reminders.


## Source attachment inventory and linked worktrees

Every new SOT has `attachment_inventory` with `expected_logical_attachments: null`, `inventory_verification: unknown`, `inventory_evidence: []`, and canonical `registered_logical_attachment_ids: []`. Empty normalized message references do not prove an attachment-free source. Declare a reviewed source inventory explicitly:

```sh
python -m memory.cli set-attachment-inventory SOT_UUID --expected 0 --verification verified --evidence 'export EXPORT_UUID: conversations[0].attachments verified empty'
python -m memory.cli set-attachment-inventory SOT_UUID --expected 3 --verification verified --evidence 'export EXPORT_UUID: conversations[0].attachments[0:3]'
python -m memory.cli set-attachment-inventory SOT_UUID --verification unknown --evidence 'source inventory unavailable'
python -m memory.cli set-processing SOT_UUID attachment_preservation complete
```

A normalized input mapping may also supply `attachment_inventory` with the first three fields. Registered IDs are derived from canonical registered artifacts. Verified zero plus source evidence permits not_applicable with its recorded reason. One registered attachment out of several stays pending. Unknown/partial inventories cannot establish completion. Registration never auto-completes overall preservation. The explicit complete assertion is accepted only when the verified count is fully reconciled, canonical references resolve, bytes validate and no attachment conflict remains open. Evidence strings are reviewed source locators/references; the framework cannot establish their factual truth.

A new expanded export resets the inventory declaration to unknown and attachment preservation to pending while retaining registered logical IDs. Review the expanded inventory and declare it again. A conflicting artifact version points to the original canonical ID, links messages through that original ID, preserves both original and conflicting bytes and keeps an explicit exception. Versions do not increase `counts.attachments` or the logical inventory. A verified declaration smaller than the known registered count is rejected (new contradictory registration demotes verification to partial).

Git determines each checkout's metadata locations; a linked worktree's `.git` pointer is not treated as a directory. Locks and journals may legitimately live outside the checkout in the resolved Git directory. They never live in tracked repository content. Recovery uses the same checkout-specific journal; content paths and symlink targets still must remain within the working tree. Unversioned synthetic roots use separately keyed temporary metadata outside repository content.

## Standalone initialization and included data

Run the commands in this document from the distribution root. To create an empty data repository without changing the distribution:

```sh
python tools/initialize.py /absolute/path/to/new-empty-memory
python -m memory.cli --root /absolute/path/to/new-empty-memory validate
git -C /absolute/path/to/new-empty-memory init -b main
```

Initialization copies the included canonical schemas and empty context placeholders, creates empty registries and canonical directories, and regenerates navigation with the actual runtime. It refuses nonempty destinations. This is a packaging helper; record generation remains in memory.operations and memory.schema. The distribution root also includes empty starter registries for its CI validation. Follow [DEMO](DEMO.md) for executable fictional records. Do not confuse examples/starter with user records.

`python -m unittest discover -s tests -v` uses synthetic temporary repositories, including local bare remotes for transaction verification. It does not require provider credentials. Python packages are installed from requirements.txt; requirements-tested.txt records the exact versions used for release verification. No third-party Python package is vendored. `zstd` is an optional external executable required only for compressed .jsonl.zst input, not the uncompressed examples or test suite.

Review dependency licenses in [DEPENDENCIES](DEPENDENCIES.md). Project licensing and attribution are included in LICENSE, NOTICE and AUTHORS.md. For user workflows and ready-to-copy prompts, start with USER_GUIDE.md and OPERATING_RULES.md.
