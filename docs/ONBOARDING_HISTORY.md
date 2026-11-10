# Path B — start with existing conversations

This path uses your available historical conversations to establish durable continuity. The software is already implemented; reconstruction is an operation performed with it. Processing a large archive can require substantial time and tokens. Preserve each expensive stage so that later drafting or review interruptions do not require repeated reading.

## 1. Set up the private memory repository

Complete the repository, installation and access steps in [Path A](ONBOARDING_NEW.md). Keep the software distribution, private memory data and local archive intake separate. Use the real initializer and commands in [QUICK_START.md](QUICK_START.md).

## 2. Obtain and preserve authentic archives

Obtain available exports or session records from each provider you want included. Provider access and export features vary; establish what can actually be downloaded or read. Keep original downloaded packages unchanged. Record provider, source format, available native identities, original times, capture scope, hashes and any known gaps.

Use the [archive-import prompt](../prompts/02-import-history.md) and [HISTORY_IMPORT.md](HISTORY_IMPORT.md). Preserve native originals in the existing SOT hierarchy, normalize faithful dialogue through the supported adapter/mapping, and verify integrity and chronology. Importing evidence does not approve its intellectual interpretation or create accepted knowledge.

## 3. Define a reconstruction

Choose one complete topic or project, the providers and available archives in scope, the historical start date if known, any end boundary, and [reconstruction depth](HISTORICAL_RECONSTRUCTION.md#choose-depth-before-reading). If the start is unknown, begin with the earliest available records. Include every conversation intersecting the period, including each complete conversation that crosses a boundary and conversations whose unknown dates cannot safely exclude them.

Use the [reconstruction prompt](../prompts/03-reconstruct-topic.md). An inventory defines the complete reading set; search, titles and relevance estimates may not choose what gets read.

## 4. Read completely and preserve the evolution

The agent reads the full authentic user-assistant dialogue of every available conversation in that scope across every included provider. It records durable reading checkpoints, source/version references, full-read status, unavailable material and interruptions. During reading it saves working observations and source-grounded evolution notes.

After all available scoped dialogue is examined and material gaps are identified, save the complete evolution record before drafting an integrated narrative. A partial source review is never labeled a completed reconstruction. If a source is unavailable or incomplete, preserve the gap and agree on recovery or an explicitly revised scope; do not silently omit it or call the original scope complete.

## 5. Draft, review and finalize

From the saved complete evolution record, produce and preserve a distinct draft narrative. Review it with the [narrative-review prompt](../prompts/04-review-narrative.md). Corrections create subsequent draft versions; the original remains.

When you approve, save a separate final narrative with approval evidence, date, version and source scope. Then choose the appropriate current-knowledge form: full narrative, concise view, topical/subtopical structure, chronology, outline or hybrid. Save that separate CURRENT record and its links to the preserved evolution and narratives. See [RECONSTRUCTION_ARTIFACTS.md](RECONSTRUCTION_ARTIFACTS.md).

## 6. Expand and transition

Repeat for other complete topics. With multiple agents, the default is [one agent per complete topic](PARALLEL_RECONSTRUCTION.md), each reading its entire applicable scope. Sources remain shared and immutable; topic progress and outputs remain separate.

After reconstruction, ordinary sessions use the opening and closeout prompts and progressive retrieval. A new development is handled through normal approved knowledge maintenance. Additional material that changes the defined reconstruction scope is recorded explicitly; completed verified reading and preserved artifacts are reused rather than discarded.
