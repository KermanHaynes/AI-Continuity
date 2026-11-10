# AI-Continuity technical specification

Original Architect and Project Founder: Kerman Haynes. Copyright 2026 AetherForge Labs, Inc.

This specification defines the current record structures, source integrity, knowledge/work behavior and transaction protections. [OPERATING_RULES.md](OPERATING_RULES.md) gives the instruction hierarchy; [USER_GUIDE.md](USER_GUIDE.md) explains everyday use. Machine-readable contract data in contracts/ supports automated consistency checks. [VALIDATION.md](VALIDATION.md) provides reproducible software checks.

Canonical schemas and the implemented command interface enforce structural behavior; approved operating procedures govern interpretation and user decisions.

---

# 1. Product contract authority

This document defines the current AI-Continuity record and operation contract.

Kerman Haynes conceived, designed and directed the architecture and its engineering. Implementation follows his architectural specifications.

Operations preserve the specified record structures, behavior, validation and procedures.

You may select ordinary internal programming details such as function decomposition, but you may not alter record semantics, remove required fields, simplify operating procedures, substitute different authority boundaries, or change the specified repository layout.

A concrete implementation/specification mismatch is reported and corrected through the contribution process.

Interpret each check within its defined record, operation and integrity scope.

Record meanings and authority boundaries follow this contract and the canonical schemas.

Resolve an actual conflicting operation requirement through the user or maintainer; preserve completed work and continue unaffected operations.

The architecture must remain portable across Claude, Codex, Grok, Muse, ChatGPT, and other model environments.

## Fundamental objective

A fresh LLM, without access to previous conversations, must be able to open the private repository, identify the intended subject or work item, recover the relevant historical reasoning and established current position, identify pending actions and outcomes, and resume without the user reconstructing prior context.

At closeout, an LLM with supported provider-native transcript access must preserve original evidence, reconcile the affected knowledge and operational records, verify Git persistence, and provide a truthful completion receipt.

The repository is not merely a conversation archive. It is simultaneously:

- An immutable evidence archive.
- An evolving knowledge system.
- A persistent operational work system.
- A provider-independent continuity mechanism.
- A verifiable history of changes and outcomes.

These five capabilities must remain separate in authority and integrated through stable references.

---

# 2. Repository Structure

A memory repository uses the following canonical structure.

    /
    ├── README.md
    ├── START_HERE.md
    ├── AGENTS.md
    ├── CONTEXT/
    │   ├── WORKING_STYLE.md
    │   ├── WRITING_STYLE.md
    │   ├── PREFERENCES.md
    │   └── RESOURCES.md
    ├── SOT/
    │   ├── EXPORTS/
    │   │   └── <export-uuid>/
    │   │       ├── original.<native-extension>
    │   │       └── export.yaml
    │   └── <provider>/<environment>/<year>/<sot-uuid>/
    │       ├── manifest.yaml
    │       ├── MESSAGES.yaml
    │       ├── transcript.md
    │       ├── TOPIC_MAP.yaml
    │       ├── TOPIC_MAP.md
    │       └── attachments/
    ├── KNOWLEDGE/
    │   └── <subject-slug>/
    │       ├── subject.yaml
    │       ├── INDEX.md
    │       ├── CURRENT.md
    │       ├── EVOLUTION.md
    │       ├── SOURCES.md
    │       └── ARTIFACTS/
    ├── WORK/
    │   ├── ITEMS/
    │   │   └── work_<uuid>.md
    │   └── AGENDA.md
    ├── INDEX/
    │   ├── REGISTRY.yaml
    │   ├── ALIASES.yaml
    │   ├── ARTIFACTS.yaml
    │   ├── EXCEPTIONS.yaml
    │   ├── PROCESSING/
    │   └── CLOSEOUTS/
    ├── TEMPLATES/
    ├── schemas/
    ├── tools/
    ├── tests/
    ├── .github/workflows/
    └── docs/
        ├── ARCHITECTURE_SPEC.md
        ├── DESIGN_DECISIONS.md
        │   # shared contract data: ../contracts/traceability.json
        ├── SETUP.md
        └── OPERATIONS/
            ├── SESSION_OPEN.md
            ├── SESSION_CLOSE.md
            ├── SOT_IMPORT.md
            ├── SUBJECT_MAINTENANCE.md
            ├── WORK_MAINTENANCE.md
            ├── RECONCILIATION.md
            ├── AUDIT.md
            └── RECOVERY.md

The repository must not require an external database, web application, paid hosting service, or proprietary runtime.

Use Python 3.11+, PyYAML, jsonschema, the standard-library `zoneinfo` module, Git, GitHub Actions, Markdown, and YAML.

Consolidate duplicate templates and redundant indexes. Preserve a single authoritative definition for each record type.

Use `.gitkeep` only where necessary to preserve otherwise empty directories.

## Documentation authority

`docs/ARCHITECTURE_SPEC.md` defines the complete architectural contract; the overview provides navigation.

`docs/DESIGN_DECISIONS.md` must record the governing architectural choices and their rationale.

The machine-readable contracts/ data binds required behavior to implementation and check references.

`AGENTS.md` and `START_HERE.md` are concise navigation and operating entry points, not competing architectural specifications.

The operating procedures must implement the authoritative architecture without silently changing it.

---

# 3. Sources of Truth and Authority Hierarchy

There are four separate forms of authority.

**Original source authority:** Native provider exports and original attachments represent what was actually recorded.

**Interpretive authority:** KNOWLEDGE represents reviewed understanding derived from evidence. It must distinguish user-established positions from model suggestions.

**Operational authority:** WORK records represent established activities, statuses, commitments, dates, dependencies, external interactions, and outcomes.

**Historical transaction authority:** Git commits and durable transaction receipts represent changes actually preserved in the repository.

A derived record cannot overwrite, replace, or retrospectively rewrite original evidence.

A model-generated suggestion cannot become a user decision merely because it appears in a transcript.

A completed technical operation cannot be treated as an externally realized outcome.

An index or agenda cannot become a competing authority against its underlying record.

If two sources disagree, preserve both and identify the conflict. Do not silently resolve it.

Unknown information must remain unknown.

---

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

# 7. Knowledge Subject Contract

Every knowledge subject consists of one permanent identity and five required components:

- `subject.yaml`
- `INDEX.md`
- `CURRENT.md`
- `EVOLUTION.md`
- `SOURCES.md`
- `ARTIFACTS/`

## subject.yaml

Require:

- `record_type: knowledge_subject`
- Schema version
- Immutable subject UUID
- Canonical name
- Aliases
- Classifications
- Subject scope
- Explicit boundaries/exclusions
- Status
- Related subject IDs
- Source references
- Created timestamp
- Updated timestamp
- Last evidence-reviewed timestamp
- Integration state

Approved subject states are `provisional`, `active`, `dormant`, and `archived`.

Aliases and classifications may be empty, but the record must contain the fields.

## Subject lookup

Resolution order:

1. Exact UUID
2. Exact canonical name
3. Exact registered alias
4. Normalized canonical name or alias

Normalize with Unicode normalization, case folding, and whitespace normalization.

Do not silently merge similar subjects.

An ambiguous lookup produces an explicit ambiguity finding.

A subject rename retains the UUID and existing source chain.

## INDEX.md

Contains the subject's identity, scope, exclusions, aliases, classifications, short navigational summary, and links to its required files.

## CURRENT.md

Require these sections:

- Established Current Position
- Accepted Decisions
- Current Constraints
- Unresolved Questions
- Relevant Active Work
- Resume From Here
- Last Supporting Evidence

The document describes the most recent **established** position, not merely the latest imported statement.

An unresolved suggestion cannot supersede an accepted decision.

Unknowns must be explicit.

## EVOLUTION.md

Retain chronological entries describing:

- Original observation or position
- Later developments
- Alternatives considered
- Rejected approaches and reasons
- Decisions
- Revisions
- Contradictory evidence
- Supersession relationships
- Remaining uncertainty
- Supporting SOT/message references

Historical ordering follows the original occurrence date when known, not Git import order.

Unknown dates retain their uncertainty.

Older conversations imported later must be placed in the correct historical context.

## SOURCES.md

Maintain exact source references, chronological contribution, and evidence classification.

At minimum distinguish:

- Established user position
- User proposal or developing idea
- Model suggestion
- Rejected or superseded position
- Supporting evidence
- Contradictory evidence
- Unresolved interpretation

## Knowledge acceptance rules

A model may identify candidate subjects and proposed interpretations.

It may not silently promote a candidate into an established user-approved position.

A subject marked integrated must contain the required structure and navigable evidence.

Structural validation must not pretend to establish interpretive truth.

Do not create a subject for every passing mention.

---

# 8. Canonical WORK Contract

Use exactly one authoritative operational record per material pursuit:

`WORK/ITEMS/work_<uuid>.md`

Use YAML front matter for structured metadata and Markdown for historical operational narrative.

Set the work-record schema version to 3.

Do not continue creating separate YAML-only canonical work items.

## Required front-matter fields

- `record_type: work_item`
- `schema_version: 3`
- `work_item_id`
- `title`
- `aliases`
- `type`
- `status`
- `status_history`
- `subject_ids`
- `source_refs`
- `relationships`
- `external_parties`
- `actions`
- `dates`
- `events`
- `outcomes`
- `last_external_verification`
- `resumption`
- `created_at`
- `updated_at`

A new work item must be created only for a material pursuit, commitment, experiment, application, external engagement, or activity that needs continuity.

Trivial isolated tasks do not require permanent work records.

## Lifecycle

The lifecycle states are:

- `planned`
- `active`
- `waiting`
- `blocked`
- `paused`
- `completed`
- `awaiting_outcome`
- `closed`

Preserve status-transition history.

Each transition includes previous state, new state, effective time if known, reason if known, and evidence.

`completed` means the defined activity was performed.

`awaiting_outcome` means an external result is still pending.

`closed` means the activity reached a recorded endpoint, including an explicit ending without the hoped-for result.

Outcomes are independent of lifecycle statuses.

An awaiting-outcome item may retain earlier partial outcomes.

Reopening must retain the prior history.

## Relationships

Require:

- `parent`: UUID or null
- `children`: array of UUIDs
- `depends_on`: array of UUIDs
- `related_to`: array of UUIDs
- `follows_from`: array of UUIDs

All references must resolve.

Parent/child and related-to links must be reciprocal.

Dependency and follows-from links are directional.

For hierarchy cycle validation, use only child-to-parent edges.

For dependency cycles, use only depends-on edges.

For succession cycles, use only follows-from edges.

Do not combine reciprocal relationship directions into a cycle-detection graph.

Do not reject legitimate reciprocal parent/child pairs.

Do not duplicate a work item because it belongs to several knowledge subjects.

## Actions

Each recorded action includes:

- Action UUID
- Description
- Classification as established or proposed
- Evidence references
- State: outstanding, completed, cancelled, or superseded
- Relevant date record IDs, if any

Only established actions enter the authoritative operational agenda.

Do not invent a next action.

## Dates

Each date record includes:

- Date UUID
- Kind: `external_deadline`, `internal_target`, or `follow_up`
- Date or datetime, or null
- Precision
- IANA time zone when applicable
- State: active, satisfied, superseded, or cancelled
- Supporting evidence
- External verification information where applicable

Date-only commitments must not be converted into imaginary UTC midnight deadlines.

## Events

Each event has a stable UUID, description, date/datetime, applicable time zone, source evidence, and state.

Event states: `scheduled`, `occurred`, `cancelled`, `unknown`.

Historical events remain in the activity record but do not indefinitely trigger upcoming-event alerts.

## Outcomes

Each outcome contains a stable UUID, description, partial/final classification, occurrence date if known, and supporting evidence.

## Resumption

Require:

- Current operational position
- Last meaningful development
- Established next action IDs, possibly empty
- Unresolved questions
- Pending external matters
- Relevant source references
- Last review timestamp

Unknowns must not be filled with model-generated assumptions.

## Markdown sections

Require:

- Objective
- Current Position
- Activity and Status History
- External Interactions
- Outcomes
- Constraints and Dependencies
- Resume From Here

These sections preserve the substance needed to resume a complicated activity, not merely status metadata.

The validator checks their existence and structural completeness. A model or human reviews their meaning.

---

# 9. Agenda Contract

`WORK/AGENDA.md` is a deterministic view of canonical work records.

It is not independently edited as an authority.

Include all relevant records in:

`planned`, `active`, `waiting`, `blocked`, `paused`, and `awaiting_outcome`.

For each, display:

- Work ID
- Title
- Status
- Established next action, or undetermined
- External deadlines
- Internal targets, separately labeled
- Follow-up dates
- Scheduled events
- Pending external matters
- Relevant time zones
- Link to the canonical work record

Sort dated items chronologically, using the appropriate local date/time semantics.

Place undated items in a separate section.

Do not exclude an item merely because its date is unknown.

Exclude resolved, cancelled, superseded, and occurred obligations from upcoming-event listings, while retaining their historical records.

Any authoritative work-record change must regenerate or verify the agenda.

A mismatched agenda must fail structural validation.

---

# 10. Global Context

`CONTEXT/` contains durable, broadly applicable preferences, working methods, writing style, and resources.

Do not populate these files with invented personal facts.

Only durable user-established information belongs here.

Do not promote a single situational preference into a global instruction without evidence.

`RESOURCES.md` distinguishes:

- A resource known to exist
- A resource connected to the present environment
- A resource accessible and verified
- A resource unavailable or requiring authorization

Never infer access to a provider transcript from access to GitHub.

---

# 11. Session Opening Operating Contract

The session-opening procedure is:

1. Resolve the intended private repository and authoritative branch.
2. Verify remote state and record the starting SHA.
3. Read `START_HERE.md` and `AGENTS.md`.
4. Read the relevant operation guidance.
5. Establish actual provider-native capture capability.
6. Resolve the requested subject or work item by ID/name/alias.
7. Retrieve current knowledge and operational resumption records.
8. Retrieve associated unfinished work and the agenda.
9. Retrieve historical evolution necessary to understand the present position.
10. Inspect original source passages when deeper evidence is required.
11. Surface relevant unresolved exceptions and incomplete integrations.
12. Distinguish stored status from externally reverified status.
13. Report readiness, inspected evidence, unknowns, and any limitations.

Use three levels of progressive retrieval:

**Level 1:** Current knowledge and active work.

**Level 2:** Relevant history, reasoning, and dependencies.

**Level 3:** Exact original messages and artifacts.

Do not load the complete repository unnecessarily.

Opening leaves canonical knowledge and WORK unchanged. Establish the selected faithful capture file and append accessible session messages as described in the capture procedure.

Do not create exception records or modify authoritative content merely because a problem was found during orientation.

Report ambiguities rather than guessing.

---

# 12. Session Closeout Operating Contract

Closeout requires an explicit user instruction.

The closeout sequence is:

## A. Preflight

Identify provider, environment, session identity, cutoff, native export accessibility, attachments, completeness, and current Git state.

If source capture is unavailable, do not claim complete archival.

## B. Preservation

Preserve actual source bytes.

Create or reuse permanent identities.

Generate validated normalized records.

Commit source preservation separately.

## C. Reconciliation

Identify every materially affected subject and work record.

For each affected record, classify the operation as:

- Changed
- Verified unchanged
- Not applicable
- Incomplete

Preserve historical reasoning, accepted decisions, revisions, outcomes, obligations, and unresolved issues.

Regenerate indexes and agenda.

Validate.

Commit derived changes separately.

## D. Concurrency

Compare the original starting SHA to the latest remote state.

If there are concurrent changes:

- Integrate unrelated changes.
- Reconcile compatible overlapping changes without losing either.
- Preserve competing evidence when meaning conflicts.
- Escalate unresolved authoritative contradictions for user judgment.

Never silently apply last-writer-wins.

## E. Remote verification

Push the authorized transaction.

Verify actual remote commit ancestry.

Confirm the preservation and derived commits are remotely reachable.

Record the observed branch, SHA, time, and verification mechanism.

## F. Receipt

Create a subsequent receipt/attestation record referencing the already-created commits.

Commit and verify that receipt separately.

Return actual full commit SHAs and GitHub links, validation results, affected IDs, and limitations.

Do not place a commit's own SHA inside its own contents.

A historical closeout remains valid after subsequent ordinary commits advance the repository.

Do not equate caller-supplied verification flags with actual remote verification.

---

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

# 14. Validation Contract

The same deterministic validation engine serves local checks and GitHub CI.

It must verify:

- Record schemas
- Permanent ID uniqueness
- Native source hashes
- Valid source references
- Transcript anchors
- Message counts and role totals
- Topic-map references
- Subject identity and aliases
- Subject structural completeness
- Work lifecycle
- Work status history
- Work relationships
- Hierarchy, dependency, and succession cycles
- Outcome and action evidence references
- Dates and time zones
- Agenda consistency
- Registry coherence
- Processing-state completeness
- Exception references
- Closeout processing status
- Git receipt structural integrity
- Known incomplete operations

Support these modes:

- `check`: read-only validation
- `plan-repair`: report proposed mechanical corrections without writing
- `apply-repair`: authorized deterministic correction only

Do not implement semantic repair as an autonomous validator action.

Differentiate:

- Blocking errors
- Nonblocking warnings
- Informational findings

A validator must not pass merely because it skipped mandatory checks.

Do not parse arbitrary provider-native source content as repository metadata.

---

# 15. Auditing and Watchdogs

Maintain GitHub Free-compatible, read-only GitHub Actions.

## Daily operational

Identify:

- External deadlines approaching within seven calendar days
- Overdue established external deadlines
- Due or overdue follow-ups
- Scheduled upcoming events
- Scheduled events whose dates passed without an updated state
- Relevant operational exceptions

Use IANA time zones and correct date-only semantics.

Never invent reminders.

## Weekly structural

Perform whole-repository integrity validation and identify unresolved recovery exceptions and missing audit executions.

## Monthly fidelity preparation

Generate a review queue for:

- Recently changed knowledge
- Pending historical integrations
- Open exceptions
- Older source sampling
- Prior interpretation concerns

This is review preparation, not a claim that semantic fidelity was independently audited.

## Audit behavior

Scheduled checks are finding-only.

They must not modify canonical SOT, KNOWLEDGE, WORK, or authoritative indexes.

Use minimum necessary GitHub permissions.

Do not write native transcript content into logs.

Preserve actual workflow SHA, run ID, execution time, scope, findings, and limitations.

External recurring watchdogs require separate authorized configuration.

---

# 16. Deterministic Command Interface

Provide a documented command-line interface with these operations:

- `validate`
- `new-id`
- `register-export`
- `register-sot`
- `resolve-source`
- `create-subject`
- `resolve-subject`
- `associate-source`
- `create-work`
- `transition-work`
- `render-agenda`
- `set-processing`
- `raise-exception`
- `review-queue`
- `closeout-record`
- `plan-repair`
- `apply-repair`

Use `python -m memory.cli` as the primary entry point.

Keep `tools/validate.py` only as a compatibility wrapper if useful.

All write operations must validate their input before modification and be safe for ordinary Git review.

The command layer performs deterministic record handling.

It does not independently interpret a conversation into accepted decisions, invent commitments, or settle source contradictions.

Exact CLI arguments, outputs and exit codes are in `docs/SETUP.md` and the operating procedures.

---

# 18. Contract identities and consistency

Machine-readable contract data is maintained in contracts/.

Every mandatory architectural and operational behavior has a stable requirement identity.

The requirements matrix must derive from this specification, not from the current code.

Preserve the full architectural contract and its requirement meanings.

---

# 20. Environment-specific operation boundaries

The following require actual environment/account access independently of local record handling:

- Live Claude capture access beyond the included supported native parser.
- Live Codex capture access beyond the included supported native parser.
- Live Grok capture access beyond the included supported native parser.
- Muse-native capture and format compatibility in the user’s actual environment.
- Access to proprietary native session stores in the chosen environment.
- User review of the meaning of actual conversational evidence.
- Repository/tool access in each environment used for a live cross-provider handoff.
- Explicit configuration and verification of an external recurring watchdog.

These operations use the permissions, interfaces and evidence actually available to the user.

A local format check does not grant live account access or authorize an external operation.

Native and generic import paths preserve the same source, identity and approval invariants.

---

# 21. Authorized operation reporting

Report the actual unfinished record or operation and the action needed to complete it.

Record observed operation results accurately.

Merge and publication follow the user’s explicit approval and repository controls.

Stop at the completed authorized scope and report the observed result.

**Preserve the working architecture, canonical records and user-approved operation boundaries.**
