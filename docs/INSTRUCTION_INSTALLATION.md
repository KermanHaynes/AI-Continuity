# Install the software and instructions in private memory

The recommended default is a **self-contained private installation**. A model connected only to your private repository can locate the same instructions and runtime regardless of which provider hosts the session. The public software repository and private memory repository remain separate; the latter contains an installed copy of the product plus your personal records.

The **operating contract** is the instructions an agent must follow when reading or changing records. The **runtime** is the Python software that performs record operations and validation. A **self-contained installation** stores both alongside your personal records so later sessions can use the same version. [Start here](../START_HERE.md) explains those records; [QUICK_START.md](QUICK_START.md) covers dependencies and the initializer. The steps below are for the authorized setup agent or a user comfortable managing files and Git.

## Exact installation set

First initialize a new empty data root with the actual command `python tools/initialize.py DESTINATION` from the release directory. Then the authorized setup agent copies these directories from that same release into the private root, preserving paths:

`memory/`, `tools/`, `schemas/`, `tests/`, `docs/`, `prompts/`, `contracts/`, `TEMPLATES/`, `examples/`, `THIRD_PARTY_NOTICES/`.

Copy these root files: `AGENTS.md`, `START_HERE.md`, `LICENSE`, `NOTICE`, `requirements.txt`, `requirements-tested.txt`. Copy `TEMPLATES/PRIVATE_README.md` as the private root’s `README.md`. The examples remain fictional reference data under examples/; never copy examples/starter into your canonical personal data directories.

Do not overwrite existing CONTEXT, SOT, KNOWLEDGE, WORK or INDEX records. Do not copy public Git history, remote configuration or .github automation by default. The initializer already supplies clean canonical schemas/context/indexes for a new repository. Installing program files does not expose private memory or activate schedules.

## Pin the installed version

Record which software was installed so a later agent can verify it has the intended version. Save `.ai-continuity/INSTALLATION.json` with the source release/tag if available, source public distribution manifest SHA-256, installation time, complete installed program/guidance relative-path hashes, authoritative branch, and actual execution/capture capability configuration. Unknown release tags remain null; the manifest hash still identifies the exact installed bundle. Do not place credentials in this record.

The agent commits and verifies this installation in the private repository within the user’s authority. It installs the declared dependencies in the environment actually used to execute commands. The runtime can then be invoked from the private repository root with `python -m memory.cli --root . OPERATION`; it no longer depends on an undisclosed original software checkout path.

## Open from a new provider or model

Give the model the private repository address and subject/request. It reads root AGENTS.md and START_HERE.md, then docs/OPERATING_RULES.md and the selected operation. It checks the installation identity/hashes, resolves the subject and reads CURRENT/associated WORK before deeper retrieval. It reads CONVERSATION_CAPTURE and the closeout/Git procedures from that same installed version.

A repository connection may be read-only. Check actual file-writing, command/Git and remote capabilities before claiming the environment can perform preservation or closeout. A read-only session can inspect the complete governing contract and identify the required additional tools or user-assisted export; it must not pretend those tools exist.

## Updates and customization

The user approves a product update. Stage the new program/guidance set, compare installed hashes, preserve previous installation metadata in Git and inspect local customizations. Replace only approved product files; preserve all personal data and preferences. Record the new manifest and hashes and validate the actual installation before publishing it. A provider does not choose a different version merely because another copy is accessible.

User preferences live in CONTEXT or an explicitly identified topic/run preference record. Record a customization separately rather than silently editing architectural invariants. If a product file was intentionally customized, record its hash and role in installation metadata and reconcile it explicitly during updates. Current user instructions, invariants and operation-specific rules take precedence as defined in OPERATING_RULES.
