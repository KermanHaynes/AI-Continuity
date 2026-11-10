# Using AI-Continuity

AI-Continuity lets you continue meaningful work across AI sessions and models while preserving the evidence, reasoning and decisions behind the current position. Your personal memory belongs in a private repository. The public repository supplies the software, documentation and fictional examples.

## Choose your starting point

**No historical conversations:** follow [ONBOARDING_NEW.md](ONBOARDING_NEW.md). Establish a private memory repository and a faithful capture method before the first conversation.

**Existing conversations:** follow [ONBOARDING_HISTORY.md](ONBOARDING_HISTORY.md). Preserve the archives, then reconstruct selected topics through complete reading and durable stages.

An authorized agent can handle installation, files, Git and validation. You decide the subject, preferred detail and which intellectual changes to approve. You should not need to operate the CLI or manage branches during ordinary use.

## Normal daily use

1. Copy the [opening prompt](../prompts/05-session-open.md), identifying your private repository, topic and working request.
2. The agent reads current governing instructions, retrieves current knowledge and associated work, and activates the selected faithful capture process, including opening and maintaining the running file when that method is used.
3. Work normally. The capture method preserves authentic dialogue as it occurs or through an available faithful export.
4. Copy the [closeout prompt](../prompts/06-session-close.md).
5. Review the proposed knowledge, decision, evolution and operational changes. Accept, correct, reject or defer individual items.
6. The agent preserves evidence, applies approved changes, validates, commits, pushes and verifies the remote result, including the durable receipt.
7. A later session or supported model uses the same repository to recover context.

If evidence or remote access is unavailable, the agent preserves completed independent work and identifies the exact unfinished step. It does not ask you to recreate a transcript from memory or claim a completed transaction without evidence.

## Two reading modes

Ordinary ongoing sessions use efficient progressive retrieval: current position and work first, history next when relevant, exact original evidence when needed. [Historical reconstruction](HISTORICAL_RECONSTRUCTION.md) instead reads every available complete conversation in the defined scope across the selected providers. Output depth never reduces that coverage.

## Make it fit your work

You choose the shape of current knowledge, reconstruction depth and operating preferences. [CUSTOMIZATION.md](CUSTOMIZATION.md) explains how to record those choices while preserving source fidelity, approval boundaries, lineage and Git integrity. For a direct change to an existing position, use [knowledge maintenance](KNOWLEDGE_MAINTENANCE.md), not a new whole-history reconstruction.

The setup and any historical reconstruction establish durable memory. Routine use then becomes opening, working, reviewing a closeout and continuing later.
