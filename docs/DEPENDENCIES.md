# Technical dependencies

Python 3.11+ and Git are required. IANA time-zone data is required for zoneinfo. zstd is optional for compressed native streams. No database or model service is required for local operations.

Direct Python dependencies: PyYAML (MIT), jsonschema (MIT). Transitive dependencies in the tested environment: attrs, jsonschema-specifications, referencing, rpds-py (all declare MIT in installed distribution metadata). Exact tested versions are in requirements-tested.txt. Packages are installed externally, not vendored. Preserve upstream notices when redistributing dependency binaries or source. Git, Python, optional zstd and GitHub Actions have their own terms; they are not relicensed by this distribution.

CI references actions/checkout@v4 and actions/setup-python@v5; these actions are fetched by GitHub, not embedded here. The project’s implementation and documentation are licensed under the included Apache License 2.0; dependency licenses and required notices remain applicable to their respective materials.
