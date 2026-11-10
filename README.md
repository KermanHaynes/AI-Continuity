# AI-Continuity

## Your AI forgot everything. Again.

You've spent hours, days, or months working with AI. You've explained the project, made decisions, explored alternatives, corrected mistakes, and finally reached an understanding that works.

Then the conversation gets too long. You open a new session. Or you switch from ChatGPT to Claude, Gemini, or another model.

And suddenly, you're starting over.

The new AI doesn't know what you built, what you decided, what you rejected, or why. You're left searching old conversations, copying notes, reconstructing decisions, and explaining work you've already done.

**You shouldn't have to rebuild your history every time you want to continue your work.**

### Meet AI-Continuity

AI-Continuity is a free, open-source solution that preserves your conversations, knowledge, decisions, reasoning, and work history outside any one AI model.

It gives a new session access to the information it needs to continue your work, whether you're using the same AI or moving between different models.

Instead of relying on a model's memory of your work, AI-Continuity maintains a durable record that the AI can read.

**Your work stays with you, not with the conversation that created it.**

### What changes?

- **Start a new conversation without starting your project over.** Your established knowledge and working history remain available.
- **Switch AI models without abandoning your context.** Use the same continuity repository across supported environments.
- **Remember more than the final answer.** Preserve the decisions, alternatives, changes, and reasoning that led to it.
- **Pick up where you stopped.** Recover project status, previous work, and outstanding questions.
- **Keep the original record.** Your conversations remain available separately from summaries and later interpretations.
- **Stay in control.** You decide which conclusions and changes become authoritative knowledge.

### How does it work?

AI-Continuity keeps your working history in a repository that you control.

Your original conversations are preserved. As your work develops, current knowledge, decisions, and progress are maintained separately, with references back to the source.

When you begin another session, your AI reads the relevant information and continues from the established state. If more history is needed, it can follow the references back to the original material.

You can also import historical conversations and reconstruct how a project or subject evolved before continuing your work.

**One history. Multiple conversations. Different AI models. Continuous work.**

### Get started

Choose the path that fits your situation.

**Starting fresh?** Set up AI-Continuity and begin preserving your work from your next conversation.

**Already have months or years of AI conversations?** Import your available history, reconstruct your projects, and establish the knowledge you want future sessions to use.

Follow [new-user onboarding](docs/ONBOARDING_NEW.md), [historical onboarding](docs/ONBOARDING_HISTORY.md), or the [technical quick start](docs/QUICK_START.md). The [user guide](docs/USER_GUIDE.md) explains everyday use.

### Install and explore

You need Python 3.11 or later and Git. The runtime uses PyYAML, jsonschema and Python’s standard time-zone support; it requires no external database or paid hosted service.

```sh
git clone https://github.com/KermanHaynes/AI-Continuity.git
cd AI-Continuity
python -m venv .venv
```

Activate the environment:

```sh
# macOS / Linux
. .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Then install dependencies and inspect the command interface:

```sh
python -m pip install -r requirements.txt
python -m memory.cli --help
python -m memory.cli validate
```

Start with [user onboarding](docs/USER_GUIDE.md) or the [technical quick start](docs/QUICK_START.md), then follow the [synthetic continuity example](docs/DEMO.md) to explore source preservation, a revised decision, historical reasoning and recovery in a fresh session. The [command reference](docs/SETUP.md) documents the supported arguments and record operations.

For ongoing work, use the [operating procedures](docs/OPERATIONS/README.md). They distinguish session opening with read-only knowledge retrieval and active faithful capture, source preservation, reviewed knowledge updates and an explicitly approved closeout. Technical compatibility and operational details are in [limitations and compatibility](docs/LIMITATIONS.md).


### Daily continuity

After setup, use the [opening prompt](prompts/05-session-open.md), work normally, and use the [closeout prompt](prompts/06-session-close.md). The agent proposes knowledge changes for your approval and handles authorized validation and verified Git persistence. Read the [operating rules](docs/OPERATING_RULES.md) and [operating procedures](docs/OPERATIONS/README.md).

For a complete historical reconstruction, follow the [Cedar lifecycle example](examples/reconstruction-lifecycle/README.md), from fictional originals through preserved evolution, draft, approved final and CURRENT.

### Built to be used, improved, and shared

AI-Continuity is open source under Apache License 2.0. It is available for individuals, researchers, developers, writers, inventors, and anyone whose work with AI extends beyond a single conversation.

Contributions, integrations, improvements, and new uses are welcome.


### Work With the Creator

AI-Continuity was created and architected by **Kerman Haynes**, inventor, systems architect, author, and founder of AetherForge Labs.

I welcome opportunities to collaborate with individuals, organizations, researchers, and industry leaders interested in AI continuity, systems architecture, invention, emerging technologies, and their broader applications.

**I am available for consulting, speaking engagements, research collaborations, strategic partnerships, sponsorships, and other professional opportunities.**

My work includes [AetherForge](https://afcopilot.com), an AI-powered invention operating system designed first for neurodivergent inventors, and *Winner Loses All*, my book presenting what I believe to be the underlying architecture of a functioning civilization, with the living authorship of human judgment at its center.

**Professional inquiries: winnerlosesall@gmail.com**

AI-Continuity is freely available under Apache License 2.0. Commercial and professional engagements are separate from the right to use and contribute to the open-source software.


For keynotes, conference opportunities, AI and systems-architecture projects, and invention or innovation engagements, see [professional collaboration](COLLABORATION.md). Read the [creator story](AUTHORS.md), [project origin](ORIGIN.md), [voluntary support](SUPPORT.md) and [contribution guide](CONTRIBUTING.md).

Copyright 2026 AetherForge Labs, Inc. Original Architect and Project Founder: Kerman Haynes. See [LICENSE](LICENSE), [NOTICE](NOTICE) and [citation metadata](CITATION.cff).

**AI-Continuity: Stop reconstructing your past. Continue your work.**
