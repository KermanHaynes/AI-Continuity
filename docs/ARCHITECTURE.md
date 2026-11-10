# Architecture overview

AI-Continuity is an implemented, functioning, model-independent memory continuity architecture. Kerman Haynes conceived, designed and directed its architecture and engineering.

## A connected record of the work

Original conversation evidence lives in SOT. Reviewed understanding lives in KNOWLEDGE. Operational activity lives in WORK. Git history and durable receipts record what was preserved and verified. Stable UUID identities and exact source references connect these layers through names, paths, revisions and model changes.

A knowledge subject has a canonical identity, CURRENT, EVOLUTION, SOURCES and navigational records. CURRENT identifies the established position and what to resume. EVOLUTION retains observations, alternatives, decisions, rejected approaches, changes and their reasoning. SOURCES connects those developments to original messages and artifacts.

A work item combines structured metadata and a historical narrative: status, actions, dates, dependencies, external interactions, outcomes and resumption context. The agenda is generated from those records. A performed activity and an external outcome are recorded separately.

## Preservation and change

Native exports and attachments retain their original bytes and checksums. Expanded exports extend the evidence chain without replacing earlier originals. Permanent identities and native identity mappings support stable reimport and conflict handling.

Source association records classified evidence. Reviewed updates establish current knowledge, retain the development that led to it, and identify unresolved questions. A model suggestion remains distinguishable from a user decision.

Writes use changed-file staging, affected-record validation and precondition hashes. Atomic per-file replacement and a retained publication journal support recovery across an interrupted multi-file update. Git transactions separately preserve evidence, derived reconciliation and verified receipts. Concurrency checks protect overlapping work.

## Retrieval across sessions and models

A session resolves the relevant subject or work item, reads its current position and resumption context, expands into relevant history, and follows exact evidence when needed. This progressive retrieval lets a supported model recover the work without loading the whole archive or relying on another session’s active context.

## Detailed reference

The [architectural contract](ARCHITECTURE_SPEC.md) retains record structures, lifecycle semantics, validation, recovery and traceability requirements. [OPERATING_MODEL.md](OPERATING_MODEL.md) distinguishes archive preservation from integrated closeout. [SETUP.md](SETUP.md) gives exact commands, and [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) records implementation choices and rationale.
