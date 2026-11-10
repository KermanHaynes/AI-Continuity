# Executable fictional continuity demonstration

Run from the extracted distribution root after installing requirements:

```sh
python examples/demo.py /absolute/path/to/new-empty-demo
```

The destination must be empty. The script initializes canonical empty registries, creates a local Git repository, and invokes the actual CLI for every record operation. It authors two explicitly fictional original conversations, preserves each original before derived changes, records competing proposals, a decision, rejection, subsequent revision, and unresolved interpretation. Explicit reviewed edits establish CURRENT; source association alone never promotes knowledge. It creates associated operational work and starts it on the fictional user's instruction.

Each CLI invocation starts a separate Python process. The final processes recover current knowledge, historical reasoning, exact original message anchors, and work resumption. They validate all records and verify unchanged source hashes. Expected result: JSON with `result: PASS`, generated UUIDv4 subject/work IDs, a report path, and `external_model_executed: false`. UUIDs, timestamps, Git SHAs, and absolute paths vary. The destination's DEMO_RESULT.json records actual commands and outputs. Git history in this demonstration is newly generated fictional history.

The included `examples/starter/` records are an already generated fictional dataset. Inspect it with:

```sh
python -m memory.cli --root examples/starter validate
python -m memory.cli --root examples/starter resolve-subject 'Fictional lantern controller'
python -m memory.cli --root examples/starter resolve-work 'Document fictional fallback procedure'
```

Expected validation exits 0 with no ERROR findings and eight `incomplete_processing` WARNING findings (four per conversation: native completeness, topic indexing, knowledge reconciliation and work reconciliation remain pending). The findings identify the processing operations performed and those left pending by this command sequence. The empty distribution baseline validates as `[]`. Subject resolution includes the sensor with timer fallback position, associated active work, and paths to EVOLUTION.md and SOURCES.md. Read those paths relative to examples/starter, then pass their exact SOT/message UUIDs to:

```sh
python -m memory.cli --root examples/starter resolve-source SOT_UUID --message-id MESSAGE_UUID
```

Resolution returns a manifest and a transcript path with a message anchor. Read that anchored passage and use manifest.source_files to inspect preserved original bytes. The original JSON messages carry matching messages[n] locators. Earlier timer-only reasoning remains in classified contributions, EVOLUTION.md, SOURCES.md, and original evidence.

To evaluate an external model, give that model read access to this distribution and the generated data root, then ask it to follow SESSION_OPEN.md and recover the lantern's current policy, rejected alternative, revision rationale, exact sources, and pending work. Record which files and message anchors it actually inspected. Use the model environment’s actual repository, capture and execution tools for that live exercise. No API key, model SDK, or live provider capture is bundled.

Local synthetic Git transaction/remote ancestry and failure handling are exercised by the preserved test suite using temporary repositories. The demo command performs local fixture operations; use the Git closeout procedure for a remote continuity transaction.
