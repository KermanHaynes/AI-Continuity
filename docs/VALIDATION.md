# Validation

## Verified functionality

The executable suite covers canonical schemas and record structures; stable identities and provenance; original-source preservation; conversation/message handling; knowledge and WORK operations; integrity checks; ordered Git transactions; concurrency protection; and interruption recovery.

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
