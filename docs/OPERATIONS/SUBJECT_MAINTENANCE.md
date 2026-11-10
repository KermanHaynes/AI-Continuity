> Operation authority: [OPERATING_RULES.md](../OPERATING_RULES.md) governs the selected task. Historical reconstruction reads every scoped conversation exhaustively and preserves the full artifact lineage; ordinary ongoing sessions use progressive retrieval. Faithful source capture, approval of intellectual changes and actual Git verification remain required.

# Subject Maintenance

Executable guidance: Use `create-subject`, `resolve-subject`, and `associate-source` from SETUP.md. Directly review/edit CURRENT.md, EVOLUTION.md and classified contributions without promoting unresolved suggestions. Rename canonical_name in subject.yaml while retaining old names in aliases unless explicitly disassociated; retain subject_id. Run `render-agenda` to regenerate registry, aliases and navigation after review edits, then `validate`. Source association regenerates a marked chronological contribution timeline and SOURCES.md; retain human/model-reviewed historical discussion outside the generated marker. Do not directly edit generated blocks.

Commands emit JSON and exit 0 on success, 1 on blocking validation findings, or 2 on invalid input/operation failure. Full CLI arguments: [SETUP](../SETUP.md).

The following record and operation requirements apply.

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
