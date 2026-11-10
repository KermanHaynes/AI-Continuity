# Using AI-Continuity

AI-Continuity lets you continue meaningful work across AI sessions and models while preserving the evidence, reasoning and decisions behind the current position. Your personal memory belongs in a private repository. The public repository supplies the software, documentation and fictional examples.

If this is your first visit, [Start here](../START_HERE.md) explains the record names and the full setup-to-resumption path. A **subject** is a continuing topic; **CURRENT** is its reviewed position, **EVOLUTION** its retained history and **SOURCES** its original-message references. **WORK** holds tasks and the information needed to resume them.

## Choose your starting point

**No historical conversations:** follow [ONBOARDING_NEW.md](ONBOARDING_NEW.md). Establish a private memory repository and a faithful capture method before the first conversation.

**Existing conversations:** follow [ONBOARDING_HISTORY.md](ONBOARDING_HISTORY.md). Preserve the archives, then reconstruct selected topics through complete reading and durable stages.

An authorized agent can handle installation, files, Git and validation. You decide the subject, preferred detail and which intellectual changes to approve. You should not need to operate the CLI or manage branches during ordinary use.

## Normal daily use

1. Copy the [opening prompt](../prompts/05-session-open.md), identifying your private repository, topic and working request.
2. The agent checks the installed instructions, reads the topic’s current reviewed position and associated work, and confirms how the actual messages will be recorded. If using a running transcript, it opens and maintains that file now. This is faithful capture; a later summary does not replace the conversation.
3. Work normally. The capture method preserves authentic dialogue as it occurs or through an available faithful export.
4. Copy the [closeout prompt](../prompts/06-session-close.md).
5. Review the proposed changes to your established position, its reasoning/history and associated tasks. Accept, correct, reject or defer individual items. The agent distinguishes your decisions from its suggestions and retains rejected or superseded alternatives and their reasons.
6. The agent preserves the original evidence, applies only approved changes and validates the records. It commits evidence separately from derived changes, pushes to your approved private remote and verifies the remote history. It then separately commits/pushes and verifies the receipt: the record of what was actually completed. [Git operations](GIT_OPERATIONS.md) defines the exact sequence.
7. In a later session or supported model, use the opening prompt with the same private repository and topic. The agent reads CURRENT and associated WORK first and reports the current position, next actions and unresolved matters. It follows EVOLUTION and SOURCES when more context is needed; setup is not repeated.

If evidence or remote access is unavailable, the agent preserves completed independent work and identifies the exact unfinished step. It does not ask you to recreate a transcript from memory or claim a completed transaction without evidence.

## Two reading modes

Ordinary ongoing sessions use efficient progressive retrieval: current position and work first, history next when relevant, exact original evidence when needed. [Historical reconstruction](HISTORICAL_RECONSTRUCTION.md) instead reads every available complete conversation in the defined scope across the selected providers. Output depth never reduces that coverage.

## Make it fit your work

You choose the shape of current knowledge, reconstruction depth and operating preferences. [CUSTOMIZATION.md](CUSTOMIZATION.md) explains how to record those choices while preserving source fidelity, approval boundaries, lineage and Git integrity. For a direct change to an existing position, use [knowledge maintenance](KNOWLEDGE_MAINTENANCE.md), not a new whole-history reconstruction.

The setup and any historical reconstruction establish durable memory. Routine use then becomes opening, working, reviewing a closeout and continuing later.
