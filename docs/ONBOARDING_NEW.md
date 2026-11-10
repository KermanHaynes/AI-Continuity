# Path A — start with no historical conversations

Use the [initialization prompt](../prompts/01-initialize.md) to have an authorized agent guide setup. You remain responsible for granting access and approving changes; the agent handles the mechanics available in your environment.

## 1. Establish the private memory repository

Create a private repository under an account or organization you control. Confirm it is private before adding personal material. If your agent can create it through an authorized connection, ask it to do so; otherwise create it using the hosting service and give the agent the repository address. Do not fork your personal data into the public software repository.

Give the agent the intended local data-root path, authoritative branch (normally main), and approved private remote. Use the [technical quick start](QUICK_START.md): install the software in its own checkout, run the existing `tools/initialize.py` on a new empty data root, validate it and establish main and the remote. If the service created an initial README commit, integrate that ordinary history rather than force-replacing it. The agent records the actual starting state and verifies the initialized content at the remote.

## 2. Give a supported environment the access it needs

Connect or open the private memory repository in the chosen AI environment using the access methods actually available there. Read access is sufficient for orientation; approved closeout also needs file changes, local Git and permission to publish to your private remote. Verify access by reading the repository’s instructions and a harmless record, not by assuming a connection grants every capability.

Install the exact program/guidance set in [INSTRUCTION_INSTALLATION.md](INSTRUCTION_INSTALLATION.md) into the private repository. Root AGENTS.md and START_HERE.md are mandatory entry files, and `.ai-continuity/INSTALLATION.json` pins the installed paths/hashes and execution configuration. This is the default installation, not an optional suggestion. A later model connected only to the private repository can read the same contract and run the installed runtime when it has the necessary execution tools. Do not copy fictional example records into canonical personal knowledge.

## 3. Confirm capture before you begin

Follow [CONVERSATION_CAPTURE.md](CONVERSATION_CAPTURE.md). Establish whether a native provider record, faithful session export or verifiable running transcript is available. Record the method, accessible scope, attachment handling and any gap. Do this for the first session, not after a body of uncaptured work accumulates.

A running transcript must contain the actual messages in order and their available provenance; a model-maintained file is checked for fidelity and never silently treated as provider-native evidence. If the environment cannot capture a faithful record, arrange a user-assisted export/copy before proceeding with a preservation claim. Summaries are not Source of Truth.

## 4. Begin and review your first subject

Use the [opening prompt](../prompts/05-session-open.md). In a blank repository, the agent identifies the topic and reports that no established knowledge exists yet rather than inventing a position. Work normally while preserving authentic dialogue.

At closeout, the agent examines the full session and proposes meaningful developments, decisions, alternatives, unresolved questions and related work. You approve the content before it becomes established knowledge. A subject is created only for a material continuing topic. It retains CURRENT, EVOLUTION and SOURCES linked to original message identities; rejected or deferred branches and their reasoning remain available.

## 5. Verify and resume

Use the [closing prompt](../prompts/06-session-close.md). The agent preserves authentic source material, applies only approved changes, validates, performs separate source/derived transactions and verifies remote ancestry and the committed receipt. You receive a short confirmation of what was preserved and updated, and any precise unfinished step.

In a later conversation, identify the same repository and topic in the opening prompt. The agent retrieves the accumulated current position and operational context, expanding into history and source evidence as necessary. You do not repeat setup or reconstruct the first conversation from a summary.
