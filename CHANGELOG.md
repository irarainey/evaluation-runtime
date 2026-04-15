# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-04-15

### Changed

- Migrated package management from Poetry to uv
- Converted `pyproject.toml` from Poetry format to PEP 621
- Updated `Dockerfile` to use uv instead of Poetry
- Replaced `poetry.lock` with `uv.lock`

### Removed

- Removed `black` dev dependency

### Security

- Resolved all Dependabot security alerts across 23 vulnerable packages
- Updated direct dependencies: `python-multipart`, `marshmallow`
- Updated transitive dependencies: `nltk`, `h11`, `azure-core`, `urllib3`, `tornado`, `nbconvert`, `cryptography`, `starlette`, `jinja2`, `requests`, `pyjwt`, `pygments`
- Removed vulnerable packages no longer in dependency tree: `waitress`, `pillow`, `protobuf`, `flask`, `flask-cors`, `werkzeug`, `filelock`, `pyasn1`

## [0.1.0] - Initial Release

### Added

- FastAPI-based runtime for executing Python scripts and Jupyter notebooks
- Integration with Azure OpenAI endpoints for inference
- Evaluation of output using configurable evaluators (`f1`, `bleu`, `gleu`, `meteor`, `rouge`)
- Dynamic Docker image building with necessary dependencies
- Deployment support for Azure Kubernetes Service (AKS)
- Azure Identity authentication for local and container environments
- Multipart form data API for uploading scripts and extraction files
- Sample notebook and extraction file in `resources/samples`
