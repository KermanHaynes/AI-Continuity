# Validation

## Verified functionality

The executable suite covers canonical schemas and record structures; stable identities and provenance; original-source preservation; conversation/message handling; knowledge and WORK operations; integrity checks; ordered Git transactions; concurrency protection; and interruption recovery.

## Capabilities, use and evidence

AI-Continuity implements source preservation, reviewed knowledge and work records, archive interfaces, retrieval, validation and verified Git closeout. Model independence means these records and instructions can be used by supported environments without depending on one provider’s conversational memory; each environment still needs actual access and compatible tools.

| Capability | Publicly reproducible evidence | Requirements for an actual operation |
| --- | --- | --- |
| Historical reconstruction | Adapter tests check supported source formats. The Cedar example exposes source-to-evolution-to-draft-to-approved-final-to-current lineage for inspection. | Obtain authentic available archives; preserve originals; read every available complete conversation in the declared scope; retain stages and obtain user review. A parser test alone does not establish a completed reconstruction. |
| Continuing across sessions or models | Lantern exercises preservation, revision, reasoning and work recovery through fresh CLI processes. It reports that no external model was executed. | Give the selected model access to the installed repository and instructions, verify capture/execution capabilities, retrieve the reviewed position and work, and follow approved closeout. Fresh-process recovery alone does not establish live cross-model performance. |

**Reported private operational use:** Kerman Haynes reports using AI-Continuity in a private knowledge repository for genuine cross-model continuity and historical reconstruction. That operating history is founder-reported; private records are not included in this distribution and were not independently inspected for this documentation update. It is distinct from the reproducible public examples and tests.

The public checks establish the behavior and source scope they actually exercise. They do not establish results for arbitrary users, providers, models, archive sizes or extended operating conditions. Live access and capture requirements remain in [interface and operation requirements](LIMITATIONS.md) and [provider interfaces](PROVIDER_ADAPTERS.md).

## Interpreting validation evidence

The distribution includes 187 executable tests. Run the commands below against the exact tree and environment being evaluated; record the command, environment, exit status, test count, failures, skips and elapsed time with that run. A successful historical run does not verify later file changes or another installation. Demonstration success applies to the fictional data and checks actually exercised, not to live provider access or a user’s memory.

An earlier distribution was observed to pass 187 tests on Python 3.13.2/macOS in 34.363 seconds, with successful Lantern, empty-root and reconstruction checks. This is historical engineering evidence, not a current-release certification or a performance guarantee. Fresh verification evidence belongs with the specific reviewed archive and its checksum; reproduce the checks when evaluating a different tree.

## Demonstrations

The lantern demonstration preserves original fictional conversations, records accepted and rejected approaches, applies a revision, retains the earlier WHY, creates related WORK and recovers state through fresh CLI processes. It checks canonical structure and original bytes.

The [Cedar reconstruction example](../examples/reconstruction-lifecycle/README.md) contains the complete source-to-evolution-to-draft-to-approved-final-to-CURRENT lineage. Its manifest states identify the completed source and Cedar knowledge operations, separate topic-specific review scopes, and the operations not performed in that static example.

These commands run local software and fictional data. Connect the repository and the required capture/execution tools when operating from a model environment.

## Check an installation

```sh
python -m unittest discover -s tests -v
python -m memory.cli validate
python tools/initialize.py /absolute/path/to/new-empty-memory
python examples/demo.py /absolute/path/to/new-empty-demo
python -m memory.cli --root examples/starter validate
python -m memory.cli --root examples/reconstruction-lifecycle/memory validate
```

Use new empty destinations for initialization and the executable demo. Inspect reported processing findings for the particular record or example being checked.

## Operational scope

Full validation checks registered records, references, source hashes and transaction conditions. Routine writes validate affected records and dependencies. The user-review procedure establishes accepted meaning; capture completeness records the actual available source scope. Git completion uses fetched remote ancestry and the separately committed receipt.
