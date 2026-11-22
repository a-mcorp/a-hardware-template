# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
Template
## [{project-version}] - {YYYY-MM-DD}

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
-->

## [1.0.0] - 2026-11-22

### Added
- Project setup
  - Hardware `.gitignore` (OpenSCAD, KiCad, slicer and Python artefacts), with `docs/datasheets/` for local copies of the makers' drawings.
  - `LICENSE` (MIT No Attribution, MIT-0), like the other templates: a project created from the template chooses its own licence.
- CAD
  - `cad/README.md` with the four roles of the CAD - parts, layout, printable parts, assembly and checks - for any tool and any number of files.
- Circuits
  - `circuits/`, empty (`circuits/.gitkeep`), for the wiring in the form that fits the project, Markdown or KiCad.
- Bill of materials
  - `bom/bom.csv` with parts, codes, suppliers, quantities, prices and their `origin` (ordered, planned, printed, at hand, cancelled), with `small` and `optional` columns.
  - `bom/dimensions.csv` with the dimensions per part and their validation against the makers' drawings, linked, not stored.
  - `bom/rates.csv` with the base currency, EUR; each project adds the currencies it pays in, with their current rates.
  - `bom/bom.py` (standard library only) writing `bom/BOM.md`: Parts, Small Parts, Total (in EUR and every currency paid in), Dimensions and Dimensions Validation, with a Legend table the table headers link to.
- Documentation
  - `README.md` with Metadata, Features (one table with the features and two example screenshots), Setup (Dependencies and Usage side by side, Installation, Repository structure) and a commented-out Troubleshooting section; links point to the 'a-mcorp' organisation.
  - `DESIGN.md` for the architecture, the decisions, what was considered and set aside, the limitations, the open questions and the prototype history.
  - `docs/` (`docs/.gitkeep`) and `exports/` (`exports/.gitkeep`).
  - `CHANGELOG.md` and its template `.github/CHANGELOG_TEMPLATE/CHANGELOG.md`, based on Keep a Changelog.
  - `TO-DO.md`.
- GitHub repository templates
  - Default pull request template `.github/pull_request_template.md` and `.github/PULL_REQUEST_TEMPLATE/Default.md`, with a hardware testing prompt and a checkbox for changes written with the help of an assistant.
  - `.github/CODEOWNERS`, its template `.github/CODEOWNERS_TEMPLATE/CODEOWNERS` and the GitHub sample `.github/CODEOWNERS_TEMPLATE/CODEOWNERS_SCHEMA`.
- Template conventions
  - Kebab-case placeholder names (`{project-*}`, `{author-*}`, `{part-N-*}`, `{printer-*}`) across all template files, as in 'A-Python-Template' and 'A-TypeScript-Template'.
  - File headers in source code and configuration with the file's name, its source repository under 'a-mcorp', its licence as an SPDX identifier and the year.
  - Compatibility with 'a-skills'.
