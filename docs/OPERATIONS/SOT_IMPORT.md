> Operation authority: [OPERATING_RULES.md](../OPERATING_RULES.md) governs the selected task. Historical reconstruction reads every scoped conversation exhaustively and preserves the full artifact lineage; ordinary ongoing sessions use progressive retrieval. Faithful source capture, approval of intellectual changes and actual Git verification remain required.

# Source-of-truth import

The archival commands are `archive-inventory`, `archive-batch sources`, and `archive-batch dialogue`; inspect `python -m memory.cli --help` for arguments. Complete and verify the inventory, preserve native sources, commit source evidence, then generate and commit faithful transcripts. The restart ledger is Git-resolved metadata, never a tracked conversation database. Publication receipts are separate and require an actual fetched remote ancestry check.

Archive-only import uses SOT/EXPORTS/<UUID>/original.<native-format> once per unique original hash and SOT/<provider>/<environment>/<original-year>/<UUID> for one logical conversation. Unknown chronology stays unknown; do not use download time as original chronology. Preserve snapshots and provenance. Reconcile genuine native identities, retain branches and actual visible-text conflicts, and ignore thinking/tool-only differences when comparing dialogue. Preserve source bytes before derived transcripts in distinct evidence commits. No empty topic maps, attachment retrieval, subject creation, WORK updates, or agenda regeneration are required. Topic, knowledge and work states remain pending. A local-only original must carry its exact publication blocker; it is not remotely preserved.

Conversation-format transcripts retain exact UTF-8 body bytes with stable msg-UUID anchors. MESSAGES.yaml records byte ranges and source field spans; tools and reasoning remain in native originals. All new imports have explicit unreviewed metadata and all message IDs pending. Never infer significance or adoption during extraction.

---

The detailed operating requirements below apply to the stated operation.

## Procedure

Executable guidance: `register-export` preserves raw bytes and a checksum. `register-sot EXPORT_UUID mapping.json` consumes an explicit normalized mapping; it is not a native provider parser. Preserve exact content, roles, native IDs and locators supplied by a supported adapter. Use authentic user-authorized evidence for memory operations and fictional data for examples/checks. Native-ID absence requires a source_conversation_locator; cross-export ambiguous matches require explicit reviewed sot_id. Run `validate` and separately commit preservation before interpretation. Never resolve an identity collision by replacing old source bytes.

Commands emit JSON and exit 0 on success, 1 on blocking validation findings, or 2 on invalid input/operation failure. Full CLI arguments: [SETUP](../SETUP.md).

The following record and operation requirements apply.

# 4. Permanent Identities

Use UUIDv4 for permanent repository identities.

Required identity types:

- Export ID
- SOT conversation ID
- Normalized message ID
- Topic ID
- Artifact ID
- Knowledge subject ID
- Work item ID
- Action ID
- Date/commitment ID
- Event ID
- Outcome ID
- Exception ID
- Closeout/transaction ID

IDs must be independent of paths, names, topic classifications, timestamps, and model providers.

An identity is minted once and subsequently reused.

## Native identity mapping

Preserve provider-native export, conversation, message, and artifact identifiers when available.

Use a composite source identity based on provider, environment, and genuine native conversation identifier.

If a native identifier is absent, record the absence. Use original source provenance and a deterministic fingerprint to detect likely duplicates.

Never collapse two conversations merely because they are stored in the same export.

Never silently merge ambiguous identities.

## Renaming

Subject and work-item names may change without changing UUIDs.

Retain historical names as aliases unless a name is explicitly disassociated.

## Reimporting

Reimporting identical evidence must not create duplicate SOT or message records.

Additional messages from a later export must extend the existing conversation identity, retain existing message IDs, and preserve the earlier export as historical evidence.

Conflicting export content must be preserved separately and registered as an unresolved conflict.

Do not silently overwrite the earlier source.

---

# 5. Native Evidence Preservation

`SOT/EXPORTS/<export-id>/original.<ext>` preserves the actual provider-generated source bytes.

When an export contains multiple conversations, preserve the original export once.

Individual conversation manifests reference the shared export record.

When an export represents one conversation, the same reference model applies. Do not create unnecessary duplicate native files.

Every preserved source file must have a SHA-256 checksum.

The validator must verify that registered source files exist and that their content matches their recorded checksum.

Native source files are immutable after preservation.

An expanded or corrected export is a new evidence version with its own export ID, linked to the existing conversation identity where appropriate.

The earlier original remains preserved.

## Capture completeness

Distinguish:

- `complete`: all messages and relevant attachments known to be present under the verified capture scope.
- `partial`: known omissions or inaccessible sections.
- `unknown`: no adequate evidence to establish completeness.

Do not infer completeness from the apparent last message or a model's context window.

Never reconstruct a complete native transcript from remembered or summarized conversation content.

When source capture is unavailable, report the limitation and leave the operation incomplete.

## Source security

Before publishing, detect obvious credential and secret exposure.

Do not publish secrets into the private repository, workflow logs, generated indexes, or audit summaries.

If an authentic original contains sensitive credential material, stop the affected preservation step for authorized review. Do not silently rewrite the original while claiming byte-for-byte preservation.

Do not expose historical personal content in public workflow artifacts or external services.

Respect GitHub repository size and file-size restrictions. If a source exceeds supported limits, preserve it outside any destructive transformation, record the blocker, and request authorization for a storage solution. Do not silently substitute an unapproved external source-of-truth system.

---

# 6. SOT Conversation Contract

For each conversation, implement the required files:

`manifest.yaml`, `MESSAGES.yaml`, `transcript.md`, `TOPIC_MAP.yaml`, `TOPIC_MAP.md`, and the `attachments/` directory.

## manifest.yaml

Require these fields:

- `record_type: sot_conversation`
- `schema_version`
- `sot_id`
- `provider`
- `environment`
- `native_conversation_id`
- `title`
- `export_ids`
- `source_files`, with registered paths and SHA-256 hashes
- `transcript_file`
- `message_index_file`
- `topic_map_file`
- `topic_map_markdown_file`
- `timestamps`
- `counts`
- `states`
- `integrated_subject_ids`
- `integrated_work_item_ids`
- `capture_gaps`
- `last_processed_at`

The timestamps structure must distinguish original conversation time from import time.

Unknown original timestamps remain null.

The counts structure must retain total messages, role-specific totals, user turns, attachment count, and topic count.

An undetermined topic count is null, not zero.

## Processing states

Use `pending`, `in_progress`, `complete`, `blocked`, and `not_applicable` for individual processing operations.

Preserve separate states for:

- Original source preservation
- Native completeness verification
- Normalization
- Attachment preservation
- Topic indexing
- Knowledge reconciliation
- Work reconciliation

An import can be fully preserved while knowledge reconciliation remains pending.

A conversation with no durable knowledge or work contribution may be marked `not_applicable` for that integration, with an evidence-backed reason.

Do not create fictitious knowledge or work records to satisfy an integration count.

## MESSAGES.yaml

Maintain the authoritative normalized message index.

For each message, record:

- Immutable normalized message UUID
- Provider-native message ID, if available
- Ordinal position
- Role
- Original timestamp or null
- Source export reference
- Exact source locator when available
- Transcript heading/anchor
- Referenced attachment IDs
- Completeness or transformation limitations

The message index is derived metadata, not a substitute for the original message content.

## transcript.md

Use a single deterministic GitHub-compatible anchor convention.

Each message receives a heading of the form:

`### msg-<message-uuid>`

The normalized content follows the heading, with role, original timestamp, and provenance information.

Use Markdown links targeting `#msg-<message-uuid>`.

Do not rewrite original quoted content as an interpretation.

Preserve distinctions among user messages, assistant messages, tool messages, and other provider-native message roles.

Where source formatting cannot be faithfully represented in Markdown, reference the original material and disclose the limitation.

## TOPIC_MAP.yaml

Each topic record contains:

- Stable topic UUID
- Label
- Provisional flag
- One or more message references or message ranges
- Associated subject IDs
- Decisions stated
- Revisions
- Open questions
- Experiments and results
- Relevant artifacts

Topics may overlap.

One topic may appear in several noncontiguous portions of the conversation.

Do not require one exclusive topic per conversation.

A source passage may contribute to several subjects without duplicating the original SOT.

`TOPIC_MAP.md` is a readable navigational view of the structured map.

## SOT validation

When normalization is marked complete, verify:

- Message IDs are unique within and across the relevant namespace.
- Every message anchor is unique.
- Message index entries resolve to transcript anchors.
- Message counts match indexed messages.
- Role totals reconcile with total messages.
- User-turn counts are deterministically checked where the normalized mapping permits.
- Topic references resolve to existing messages.
- Completed topic-indexing counts reconcile.
- Artifact references resolve and checksums match.
- Source export references exist.
- Every complete-processing assertion has the necessary supporting structure.

Do not scan the contents of arbitrary original JSON or YAML as repository metadata.

Only explicitly recognized metadata paths are parsed as schemas.

---

## Provider-independent attachment registration

Use `python -m memory.cli register-artifact SOT_UUID SOURCE_FILE`, optionally with `--native-artifact-id`, repeated `--message-id`, `--description`, and an explicit existing `--artifact-id`. The command preserves original bytes under the SOT's `attachments/<artifact-uuid>/original.<ext>`, registers hashes and genuine native IDs, validates supplied references, and reports incremental validation scope. Identical evidence is idempotent. Conflicting evidence is preserved separately with a conflict link and exception; exit 2 reports the unresolved conflict after safe preservation. Missing files/references, path escapes and corrupted established evidence stop the operation. See SETUP.md for arguments and output details. No provider-specific parser is implied.

A genuine Claude export package may contain both web conversations and Design conversations. Preserve that package once, with export environment `web_and_design`, and reference it from the original `web` and `design` conversation destinations. This source-package scope does not change either conversation's native environment. It does not admit local sessions or another provider. Metadata-only packages remain source evidence without fabricated dialogue.

Attachment-only USER communications retain their native identities, order, role and source locators, with an empty text body. A zero-length field span identifies a native non-text communication, not recovered attachment bytes. Attachment contents remain authoritative in the native record; retrieval and inventory reconciliation remain pending. Thinking-only or execution-only model events do not become dialogue turns.

Catalog mappings are discovery hints. Native session identity fields take precedence over a conflicting application-metadata association. Apply a metadata title, date range or supporting-source association only when its identity resolves to the native session. Preserve rejected metadata separately and record the mismatch. Record identity corrections separately without modifying the original catalog or source bytes.

An export's `publication.status` records its intake eligibility checkpoint. Actual remote persistence is established separately by the archive receipt and fetched Git ancestry; the intake declaration does not substitute for that verification.

Application-wrapper `createdAt` and `lastActivityAt` values are not evidence of the CLI session's original chronological range merely because the wrapper currently points to that CLI ID. Preserve those values in the original metadata. Use the original native message timestamps for the available CLI conversation range; exact native-session metadata can supply a session boundary only when it identifies that same native session directly.
