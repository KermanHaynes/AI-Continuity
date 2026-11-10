> Operation authority: [OPERATING_RULES.md](../OPERATING_RULES.md) governs the selected task. Historical reconstruction reads every scoped conversation exhaustively and preserves the full artifact lineage; ordinary ongoing sessions use progressive retrieval. Faithful source capture, approval of intellectual changes and actual Git verification remain required.

# Audit

Audit schedules operate when configured and authorized. Audits are finding-only; they do not approve interpretations or establish external outcomes.

---

The detailed operating requirements below apply to the stated operation.

## Procedure

Executable guidance: Use `python -m memory.cli audit daily|weekly|monthly`. Supply `--at ISO_OFFSET_DATETIME` for reproducible temporal evaluation. Weekly validation reports missing local workflow evidence as a limitation; tools/ci_audit.py additionally inspects recent GitHub Actions executions using read-only actions permission. Audits compare full file checksums and Git status before and after in CI. No canonical edits, repairs, semantic exception resolutions, or invented reminders are authorized by an audit. Use `plan-repair` for a finding-only mechanical plan; apply only on explicit authorization.

Commands emit JSON and exit 0 on success, 1 on blocking validation findings, or 2 on invalid input/operation failure. Full CLI arguments: [SETUP](../SETUP.md).

The following record and operation requirements apply.

# 14. Validation Contract

Build one deterministic validation engine used identically by local checks and GitHub CI.

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

Configure any external recurring watchdog separately with actual user authorization.

---

## Calendar horizons

Evaluate each obligation in its applicable IANA time zone. External deadlines and follow-ups use seven local calendar days, with due/overdue records retained. Scheduled events beyond seven days do not appear as upcoming; past scheduled events receive a status-review finding. Unknown dates and inactive obligations never generate invented overdue alerts. Apply these calendar semantics to the actual recorded obligations.
