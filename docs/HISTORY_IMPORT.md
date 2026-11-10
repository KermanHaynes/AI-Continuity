# Import historical conversation evidence

Use the [archive-import prompt](../prompts/02-import-history.md). This is source preservation and normalization, not topic reconstruction or approval of interpretations.

## Intake

Obtain available genuine exports/session files from each included provider. Preserve original packages unchanged in a private intake location. Record source provider, environment, format, actual file size/hash, native identities and chronology when known, and capture limitations. Unknowns remain unknown. Scan for credentials and private disclosure risks before any remote publication; do not rewrite sensitive originals while claiming fidelity.

## Select the existing import interface

The implemented native inventory/batch path expects an intake corpus with `ORIGINALS/` and `METADATA/sources.json`. The catalog is a JSON array of entries with actual `id`, `path`, `sha256`, `bytes`, `provider`, `kind` and optional `source_format` fields. Paths resolve within the intake root and source files under ORIGINALS. Native kinds and provider shapes must match an implemented adapter; inspect the actual source metadata and adapter rather than assigning a convenient label to unsupported content.

From the software checkout, the actual commands are:

```sh
python -m memory.cli --root /absolute/path/to/private-memory archive-inventory /absolute/path/to/intake /absolute/path/to/private-inventory
python -m memory.cli --root /absolute/path/to/private-memory archive-batch sources /absolute/path/to/intake /absolute/path/to/private-inventory/sources.json
python -m memory.cli --root /absolute/path/to/private-memory archive-batch dialogue /absolute/path/to/intake /absolute/path/to/private-inventory/sources.json
```

The inventory command takes an output directory and writes `sources.json` there; each batch command takes that actual `sources.json` file. This inventory is distinct from the intake catalog at METADATA/sources.json. These commands do not imply a successful remote push. Follow source-first commits and actual remote verification. Review each batch’s returned state before proceeding.

For an available faithful export with a supported explicit normalized mapping, use the existing generic interfaces:

```sh
python -m memory.cli --root /absolute/path/to/private-memory register-export /absolute/path/to/source --provider PROVIDER --environment ENVIRONMENT --scope 'Actual accessible capture scope' --completeness unknown
python -m memory.cli --root /absolute/path/to/private-memory register-sot EXPORT_UUID /absolute/path/to/mapping.json
```

Use the actual provider/environment and returned export UUID, not invented native IDs. Mapping fields and source locators follow [SETUP.md](SETUP.md). This generic command consumes a mapping; it does not automatically parse every export. A complete declaration needs actual evidence, not an assumption based on the final visible message.

## Verify and retain

Verify source checksums, persistent conversation/message identities, exact readable content, native branches, original chronological ranges and attachment/capture status. For registered native archive records use `verify-archive-fidelity`; for generic mappings use full validation and direct source/locator checks. Reimports preserve established identities, earlier snapshots and genuine conflicts.

Preserve native evidence before derived transcripts, with distinct transaction steps. Record local-only blockers separately from remote persistence. Use archive-only checkpoints/receipts when only preservation is authorized; do not invent knowledge or a derived reconciliation commit. Read [SOT_IMPORT](OPERATIONS/SOT_IMPORT.md), [PROVIDER_ADAPTERS.md](PROVIDER_ADAPTERS.md) and [GIT_OPERATIONS.md](GIT_OPERATIONS.md).

New transcripts remain intellectually unreviewed until an actual review establishes otherwise. Once the source set is available, choose a topic, scope and depth and begin the separate exhaustive [reconstruction workflow](HISTORICAL_RECONSTRUCTION.md).
