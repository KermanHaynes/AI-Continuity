# Machine-readable product contracts

`identities.json` locks the stable identity and source hash of each current architecture or maintenance unit. IDs are never reused for different requirements. `requirements.json` is generated from those authoritative documents. `bindings.json` associates units with implementation, schema, procedure and check references. `traceability.json` and `review-obligations.json` are generated data.

Run `python tools/build_requirements_matrix.py` after a source or binding change. The generator rejects unknown, duplicate, missing or mismatched identities. A changed requirement retains its identity only when its meaning remains the same; maintainers update the corresponding source hash explicitly.

Binding statuses describe an individual reference check or an actual user operation. `partial` with `human_review_required` means the current source interpretation needs its user's decision. `deferred_provider_specific` identifies an operation requiring actual account or tool access. A missing binding is a maintainer consistency error. These data are not ordinary session acceptance gates.

User operations follow [OPERATING_RULES.md](../docs/OPERATING_RULES.md). Contributor changes follow [MAINTENANCE.md](../docs/MAINTENANCE.md).
