# Faithful conversation capture

**Capture** means keeping the actual messages and available attachments from your conversation, with information about where they came from. It lets you check a later interpretation against the original exchange. **SOT** means Source of Truth: that preserved evidence, distinct from reviewed knowledge. A continuity session needs authentic conversational evidence. Select and activate the capture method at opening, maintain it during the session when applicable, and verify it before declaring source preservation complete. Summaries, remembered reconstructions and interpretive paraphrases are not SOT transcripts.

## Choose a method based on actual access

**Native provider record:** retain the genuine original export/session record unchanged. Use the supported native adapter to derive readable dialogue with native identity, timestamps, source spans and branches where present.

**Faithful session export:** preserve an available complete Markdown, JSON or equivalent export of the authentic exchange. Record its actual exporter, format, scope and transformation limits. Do not call it provider-native unless it is. A generic mapping can preserve its faithful text and explicit source locators; it cannot manufacture native identity or prove missing content was captured.

**Running transcript:** when the environment can reliably access and write the actual messages, maintain an external file as the conversation progresses. Preserve exact message text, order, speakers, available dates/times, attachment/output references, capture metadata and explicit gaps. Do not invent timestamps or reconstruct earlier messages from memory. A model-authored transcript is not self-verifying: compare it with accessible message records or user-provided exports, and record the verified scope. If exact text is inaccessible, mark the gap and obtain faithful user-assisted capture before claiming full preservation.

Some environments require the user to download or supply a transcript. Ask for that source at closeout when necessary, then preserve and inspect it. Do not simulate a completed capture by writing a summary file.

## Capability check at opening

Identify the actual environment—ordinary ChatGPT, ChatGPT Work, Codex, Claude, Grok or another tool—and check the capabilities available in that particular session. Can the agent read exact current messages? Obtain an original export or session download? Write a persistent external file? Read referenced attachments? Access the intended repository and perform approved Git operations?

Do not assume that similarly named products or different accounts expose the same tools. No universal live-export feature is asserted here. Implemented native adapter formats are described in [PROVIDER_ADAPTERS.md](PROVIDER_ADAPTERS.md); that is distinct from access to a running provider account.

Agree on the method, output location, session identity where available, capture start/cutoff and limitations. For running-file capture, actually create/open the file and begin recording accessible messages now; follow [RUNNING_CAPTURE.md](RUNNING_CAPTURE.md). If no reliable method is available, arrange a user-assisted faithful record and clearly identify the missing step. The initial method must be established from the first conversation of a new memory repository.

## Preserve content and provenance

Keep the original file and register its actual source bytes and checksum. Preserve complete authentic user-assistant communications without significance filtering; a long assistant contribution may matter even without explicit acknowledgment. Original native records may also contain execution or hidden material. Conversation-only transcripts follow the implemented typed boundary rules; native originals remain unchanged.

Record original timestamps when available, otherwise null. Retain branches rather than inventing a single exchange. Preserve references to original attachments and generated artifacts, while distinguishing a known reference from bytes actually recovered and verified. Conflicting source snapshots remain separate evidence.

At closeout, compare the preserved record with the actual accessible scope. Use native fidelity checks for native-import records and canonical validation plus source/locator checks for generic mappings. Do not apply a native-span verifier to an unsupported generic mapping and treat the result as capture proof. Missing material stays explicit until recovered.
