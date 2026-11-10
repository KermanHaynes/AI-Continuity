> Operation authority: [OPERATING_RULES.md](../OPERATING_RULES.md) governs the selected task. Historical reconstruction reads every scoped conversation exhaustively and preserves the full artifact lineage; ordinary ongoing sessions use progressive retrieval. Faithful source capture, approval of intellectual changes and actual Git verification remain required.

# Work Maintenance

Executable guidance: Use `create-work` only for a material pursuit explicitly authorized by the user. `transition-work` appends lifecycle history and retains the narrative. Explicitly review/edit actions, dates, events, outcomes, external interactions, relationships and resumption in the Markdown front matter/narrative as a coherent batch. Reciprocal relationships must be changed together. Run `render-agenda`, then `validate`; review diff before commit. Completion does not imply an external outcome. Empty established next_action_ids is valid.

Commands emit JSON and exit 0 on success, 1 on blocking validation findings, or 2 on invalid input/operation failure. Full CLI arguments: [SETUP](../SETUP.md).

The following record and operation requirements apply.

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
