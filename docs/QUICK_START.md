# Technical quick start

For guided setup without a command-line background, start with [USER_GUIDE.md](USER_GUIDE.md). The agent can perform these steps for you in an environment you authorize.

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

## Create an empty personal-memory data root

Run from the software distribution directory; replace the example destination with a new local path:

```sh
python tools/initialize.py /absolute/path/to/new-empty-memory
python -m memory.cli --root /absolute/path/to/new-empty-memory validate
git -C /absolute/path/to/new-empty-memory init -b main
```

The actual initializer uses a positional destination, not `--root`. It creates canonical empty registries, context and schemas and refuses nonempty destinations. It does not create a remote repository or grant an agent access. The agent connects the data root to your approved private remote and verifies persistence as part of onboarding. Keep software checkout and personal-memory data root distinct. Complete the recommended self-contained private installation in [INSTRUCTION_INSTALLATION.md](INSTRUCTION_INSTALLATION.md). It copies the specified program/guidance files into the data repository and pins their hashes, so later sessions do not depend on the original checkout.

## Run the existing fictional demonstration

```sh
python examples/demo.py /absolute/path/to/new-empty-demo
python -m memory.cli --root examples/starter resolve-subject 'Fictional lantern controller'
python -m memory.cli --root examples/starter validate
```

The executable example follows the lantern controller’s decision history. Read [DEMO.md](DEMO.md) for actual behavior, synthetic expected findings and source-integrity checks. The demo creates new local fictional Git history and never pushes to GitHub.

## Begin operating

Choose [starting without history](ONBOARDING_NEW.md) or [starting with archives](ONBOARDING_HISTORY.md). Confirm a [faithful capture method](CONVERSATION_CAPTURE.md) before the first working session. Use the [ready-to-copy prompts](../prompts/README.md) and [operating rules](OPERATING_RULES.md). Exact CLI contracts remain in [SETUP.md](SETUP.md).
