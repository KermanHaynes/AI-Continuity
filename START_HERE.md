# Start here

AI-Continuity keeps a record of your work that a later AI session can read: what you discussed, what you decided, why it changed and what to do next. Your personal records belong in a private repository you control. The public software distribution supplies the software, instructions and fictional examples.

Kerman Haynes is the Original Architect and Project Founder. AetherForge Labs, Inc. maintains the project under Apache License 2.0.

## Understand the three kinds of record

A **repository** is a folder whose changes Git records over time; a **remote** is its hosted copy. AI-Continuity keeps three kinds of information separate inside your personal repository:

| Kind | What it means | Name you will see in files and instructions |
| --- | --- | --- |
| Original evidence | The actual conversations and available attachments, preserved unchanged with references to where they came from. A summary cannot replace them. | **SOT**, short for Source of Truth |
| Reviewed knowledge | Your established position on a continuing topic, together with how it developed and the messages supporting it. A model suggestion remains a suggestion unless you approve it. | **KNOWLEDGE**; a topic is called a **subject** |
| Work to resume | Tasks, status, next actions, unresolved questions and matters awaiting an external response. | **WORK** |

Within a subject, **CURRENT** holds the reviewed position to use now, **EVOLUTION** retains earlier positions, alternatives and reasoning, and **SOURCES** points back to the original messages. **Provenance** means those origins and references; **lineage** means the retained chain of revisions. Earlier evidence and history remain available when a position changes.

## Choose your first step

- **Try it with fictional data first:** follow the [technical quick start](docs/QUICK_START.md). Install the dependencies and run the demonstration before choosing a personal-memory destination. This needs no provider account or personal conversations.
- **Start preserving new conversations:** follow [setup without historical conversations](docs/ONBOARDING_NEW.md). It guides you through private storage, agent access, message capture and your first session.
- **Bring existing conversations:** follow [setup with archives](docs/ONBOARDING_HISTORY.md). Preserve the originals first; then choose the topic and source scope to reconstruct and review.
- **Already installed in your private repository:** use [open, work, close and resume](docs/USER_GUIDE.md#normal-daily-use). You do not repeat setup for each conversation or model.

You can ask an authorized AI agent to perform setup and Git commands if its environment provides those tools. You choose the repository and approve access and substantive knowledge changes. A repository connection alone does not provide message capture or permission to write and publish files.

## What happens in a working session?

1. **Open:** give the agent your private repository, topic and request using the [opening prompt](prompts/05-session-open.md). It checks the installed instructions, reads your current position and associated work, and establishes how this conversation will be recorded.
2. **Work:** discuss the topic normally. **Faithful capture** means keeping the actual messages in order, with their available source information and explicit gaps, through a supported export or a checked running transcript. It is not a summary written later. See [capture methods and access checks](docs/CONVERSATION_CAPTURE.md).
3. **Close and review:** use the [closing prompt](prompts/06-session-close.md). **Closeout** is the process of preserving the conversation, reviewing proposed knowledge/work changes and verifying their storage. Accept, correct, reject or defer individual proposals; silence does not establish a decision.
4. **Verify:** the agent applies only authorized changes and checks the records. It saves original evidence separately from records derived from it, publishes the required Git commits to your approved private remote, verifies that they arrived and separately commits/publishes a **receipt** recording the verified result, then verifies that receipt commit too. A local save alone does not complete closeout. Missing capture, access or verification is reported as an unfinished step.
5. **Resume:** in a later session, provide the same repository and topic. The agent reads current knowledge and work first, then follows relevant history and original messages as needed. This is **progressive retrieval**; it avoids rereading your entire archive for ordinary work.

Reconstructing an old topic is different: the agent reads every available complete conversation in the agreed source scope and preserves each stage before moving from evolution to draft, approved final and current knowledge. See [historical onboarding](docs/ONBOARDING_HISTORY.md); progressive retrieval does not reduce that reading requirement.

## When you need the detailed instructions

The [user guide](docs/USER_GUIDE.md) explains the daily routine. The [self-contained installation](docs/INSTRUCTION_INSTALLATION.md) puts the software and instructions in your private repository, so a new model can find them. The [prompt index](prompts/README.md) helps you choose the next operation.

Before an actual memory operation, the agent must read [AGENTS.md](AGENTS.md), [OPERATING_RULES.md](docs/OPERATING_RULES.md) and the selected [operating procedure](docs/OPERATIONS/README.md) from that installed version, verify its installation identity/hashes and activate the agreed capture method. These are the **operating contract**: the instructions governing how records may be read and changed. The architectural contract, canonical schemas (the required record structures) and transaction safeguards remain binding. Exact command arguments are in [SETUP.md](docs/SETUP.md).
