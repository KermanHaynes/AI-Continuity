# Technical quick start

For guided setup without a command-line background, start with [USER_GUIDE.md](USER_GUIDE.md). The agent can perform these steps for you in an environment you authorize.

For the three kinds of information you will keep and how a session works, read [Start here](../START_HERE.md). This page is the command-line route: install, try fictional data, then create personal memory if you want to continue.

## Install the software

Use Python 3.11 or later and Git. From a local checkout of the public software distribution:

```sh
python -m venv .venv
```

Activate `.venv` using `. .venv/bin/activate` on macOS/Linux or `.venv\Scripts\Activate.ps1` in Windows PowerShell.

```sh
python -m pip install -r requirements.txt
python -m memory.cli --help
python -m memory.cli validate
```

## Run the existing fictional demonstration

Run these commands from the software checkout. Choose a new empty demo destination, separate from any personal records. The first command builds a fictional history; the other two inspect the included starter fixture.

```sh
python examples/demo.py /absolute/path/to/new-empty-demo
python -m memory.cli --root examples/starter resolve-subject 'Fictional lantern controller'
python -m memory.cli --root examples/starter validate
```

The executable example follows the lantern controller’s decision history. Read [DEMO.md](DEMO.md) for actual behavior, synthetic expected findings and source-integrity checks. The demo creates new local fictional Git history and never pushes to GitHub.

## Create an empty personal-memory data root

The **data root** is the top-level folder for your personal memory. The **software checkout** is the public code you downloaded. Create personal memory in a separate folder; later copy the required software/instructions into it using the installation guide below.

Run from the software distribution directory; replace the example destination with a new local path:

```sh
python tools/initialize.py /absolute/path/to/new-empty-memory
python -m memory.cli --root /absolute/path/to/new-empty-memory validate
git -C /absolute/path/to/new-empty-memory init -b main
```

The initializer takes the destination directly after its filename, not through `--root`. It creates empty record indexes (registries), context and rules defining valid records (schemas), and refuses nonempty destinations. An empty initialized root should validate to `[]` with exit 0. The Git command starts local version history; it does not upload anything. Initialization does not create a remote repository or grant an agent access. The agent connects the data root to your approved private remote and verifies persistence as part of onboarding.

Complete the recommended self-contained private installation in [INSTRUCTION_INSTALLATION.md](INSTRUCTION_INSTALLATION.md). It copies the specified program/guidance files into the data repository and pins their hashes, so later sessions do not depend on the original checkout.

## Begin operating

Choose [starting without history](ONBOARDING_NEW.md) or [starting with archives](ONBOARDING_HISTORY.md). Confirm a [faithful capture method](CONVERSATION_CAPTURE.md) before the first working session. Use the [ready-to-copy prompts](../prompts/README.md) and [operating rules](OPERATING_RULES.md). Exact CLI contracts remain in [SETUP.md](SETUP.md).
