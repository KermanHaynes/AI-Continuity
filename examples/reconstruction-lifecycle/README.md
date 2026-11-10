# Complete fictional reconstruction

This example uses actual illustrative files, not an automated reconstruction command. Every conversation and approval is newly authored fiction. No personal transcript, customer record or real founder approval is represented.

Read the three complete original conversations through [source references](SOURCE_REFERENCES.json). The first crosses the start boundary. The second is titled Bicycle repair notes and contains an important Cedar proposal in an otherwise unrelated paragraph. [COVERAGE](memory/KNOWLEDGE/cedar/ARTIFACTS/reconstruction/8a23eb37-2808-4e0c-96b5-3ba77be2e049/COVERAGE.json) includes every message of all three; titles and search did not exclude any conversation. The fourth source is the later fictional review/approval, outside the original historical window.

## Follow the full lineage

1. [Scope](memory/KNOWLEDGE/cedar/ARTIFACTS/reconstruction/8a23eb37-2808-4e0c-96b5-3ba77be2e049/SCOPE.json) and [coverage](memory/KNOWLEDGE/cedar/ARTIFACTS/reconstruction/8a23eb37-2808-4e0c-96b5-3ba77be2e049/COVERAGE.json).
2. [Complete evolution record](memory/KNOWLEDGE/cedar/ARTIFACTS/reconstruction/8a23eb37-2808-4e0c-96b5-3ba77be2e049/EVOLUTION_RECORD_v001.md), saved before drafting.
3. [Original draft](memory/KNOWLEDGE/cedar/ARTIFACTS/reconstruction/8a23eb37-2808-4e0c-96b5-3ba77be2e049/DRAFT_v001.md), including a preserved overstatement.
4. [Approved final](memory/KNOWLEDGE/cedar/ARTIFACTS/reconstruction/8a23eb37-2808-4e0c-96b5-3ba77be2e049/FINAL_v001.md), correcting rejection versus deferment and linking the fictional user approval.
5. [Concise canonical CURRENT](memory/KNOWLEDGE/cedar/CURRENT.md), separate from the final, with access to full historical WHY.
6. [Lineage](memory/KNOWLEDGE/cedar/ARTIFACTS/reconstruction/8a23eb37-2808-4e0c-96b5-3ba77be2e049/LINEAGE.json), artifact hashes, parents and source/approval identities.

The chosen CURRENT is intentionally short. It preserves access to why timer-only was accepted, why sensor-only was rejected, how fallback was deferred and later adopted, and which possibility remains deferred. Every earlier artifact remains retrievable.

## Inspect with the existing runtime

From the software distribution root:

```sh
python -m memory.cli --root examples/reconstruction-lifecycle/memory validate
python -m memory.cli --root examples/reconstruction-lifecycle/memory resolve-subject 'Cedar courtyard irrigation'
```

Read the returned CURRENT/history/source paths under this example’s memory root. Perform reconstruction reading, narrative construction and approval through the operating guides. Publish the approved records using the actual branch/main and receipt process in [Git operation](../../docs/GIT_OPERATIONS.md).

## Processing and review state

All four authored source files are preserved and normalized; exact messages, identities, timestamps and bytes have been checked against their original fixture JSON. The known fixture scope and zero-attachment inventory are verified. Topic maps cover the Cedar material and the unrelated errands/bicycle material. Cedar knowledge reconciliation is complete, and the Cedar subject is active with the approved concise CURRENT. No WORK record is requested for this knowledge-only example; work reconciliation is not applicable to that approved scope.

The source review metadata records exact approved message IDs and the authored fictional approval. The bicycle-only message and the assistant procedural confirmation in the later review conversation remain outside that approval scope, so those two source records retain `in_review` with explicit pending message IDs. This does not change the completed Cedar narrative/current approval. Reading coverage and topic-specific intellectual approval are separate records.

SCOPE, COVERAGE and LINEAGE preserve the reconstruction progress and artifact versions. This distributed dataset starts no Git publication transaction. Create the canonical Git processing checkpoint and receipt when performing the actual approved transaction in your private repository, using real commit identities and remote verification.
