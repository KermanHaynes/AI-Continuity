# Activate a running transcript

A running transcript is a faithful message record, separate from interpretation and the closeout proposal. Use it only when the environment can actually access the message contents and maintain a persistent file.

## Opening activation

When this method is selected, the agent creates or opens the agreed private capture file, for example `CAPTURE/<session-id>/transcript.json`, using [the template](../TEMPLATES/RUNNING_TRANSCRIPT.json). This temporary capture path is an intake record, not a new canonical SOT hierarchy. Record the actual session identity, provider/environment and available opening metadata; unknown timestamps stay null.

Append accessible messages in order as the exchange progresses. Each message has `ordinal`, `speaker`, `content`, `timestamp` (or null), native ID when available, source locator/identity where available, and `attachments`/`generated_outputs` references with availability status. Preserve exact text, paragraphs, code and visible markup rather than paraphrasing. Record any missing earlier message or inaccessible output in gaps. An illustrative initialized record is in [the synthetic example](../examples/running-capture/transcript.json).

A message append occurs when its actual complete content is available; do not invent a future assistant message or assume access to hidden interface content. Preserve unknown metadata as null. Track the last verified ordinal and comparison method. Follow normal file safety and checkpointing so a session interruption does not discard captured messages.

## Closing verification and SOT preservation

Retrieve the file chosen at opening and compare its captured ordered messages with the accessible session scope. Record the cutoff, actual coverage and unresolved gaps. Obtain a user export or another faithful record for inaccessible messages before claiming complete preservation. A self-reported message count alone does not prove fidelity.

Preserve the resulting actual file unchanged through the existing register-export/source mapping or appropriate supported adapter path. The preserved export’s source metadata identifies it as a running transcript, not a provider-native export. Generate only mappings supported by its real text and locators; retain source identities and hashes. Running-file contents are not accepted knowledge until the separate closeout review approves changes.

## If the method is unavailable

If the agent cannot access exact text or update the persistent file, switch to an actually supported faithful export or user-assisted record and identify the required user action. Never simulate activation by writing a summary and never claim automatic interface capture without tools that can do it.
