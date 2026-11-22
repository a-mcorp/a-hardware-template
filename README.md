<sup>This project has been generated using ['A-Hardware-Template' (AHT)](https://github.com/a-mcorp/a-hardware-template).</sup>

# {project-name}

## Metadata
<!-- - Author: {author-name}/{author-alias}. -->
- Name: '{project-name}'.
- Purpose: {project-summary}.
- Format: {project-format}.
  <!-- printed enclosure, electronics, mixed -->
- License:
  - This project's license: [MIT No Attribution](LICENSE) <!-- the template's own licence: in a project created from it, replace `LICENSE` and this line with the project's licence, e.g. CERN-OHL-S-2.0 for a hardware design -->
  <!-- - Part-1: [{part-1-name}]({part-1-datasheet}) -->
  <!-- - Library-1: [{library-1-name}]({library-1-license}) -->

## Features
<table>
<tr>
<th colspan="2">Features</th>
</tr>
<tr>
<td colspan="2">

- {feature-1}
- {feature-2}

</td>
</tr>
<tr>
<th>{example-1-title}</th>
<th>{example-2-title}</th>
</tr>
<tr>
<td align="center"><img src="docs/{example-1-image}" alt="{example-1-title}" width="480"></td>
<td align="center"><img src="docs/{example-2-image}" alt="{example-2-title}" width="370"></td>
</tr>
</table>

## Setup
<table>
<tr>
<th>Dependencies</th>
<th>Usage</th>
</tr>
<tr>
<td valign="top">

  - CAD: [__{cad-tool}__]({cad-tool-url}) __{cad-tool-version}__
    <!-- [__OpenSCAD__](https://openscad.org/) -->
  - Circuits (optional): [__KiCad__](https://www.kicad.org/) __{kicad-version}__
  - Slicer: [__{slicer-name}__]({slicer-url})
    <!-- [__PrusaSlicer__](https://github.com/prusa3d/PrusaSlicer) -->
    <!-- [__OrcaSlicer__](https://github.com/SoftFever/OrcaSlicer) -->
  - BoM: [__Python__](https://www.python.org/) 3.10+ (standard library only)

</td>
<td valign="top">

  - BoM
    - parts in `bom/bom.csv`, dimensions in `bom/dimensions.csv` (columns described in `bom/bom.py`), currencies in `bom/rates.csv`
    - `python3 bom/bom.py` writes `bom/BOM.md`
  - CAD
    - sources in `cad/`, organised as described in [cad/README.md](cad/README.md); exports in `exports/`
  - Circuits
    - wiring, pin assignments and the power budget in `circuits/`
  - Design
    - decisions, limitations, open questions and the prototype history in `DESIGN.md`
  - Printing
    - {printer-name}, {filament}, {layer-height} mm layers, {walls} walls

</td>
</tr>
</table>

### Installation
{...}

### Repository structure
```
.
├── .github
│   ├── CHANGELOG_TEMPLATE         # Template for CHANGELOG.md
│   ├── CODEOWNERS_TEMPLATE        # Template for CODEOWNERS
│   ├── PULL_REQUEST_TEMPLATE      # Additional pull request templates
│   ├── CODEOWNERS                 # Code owners
│   └── pull_request_template.md   # Default pull request template
├── bom
│   ├── bom.csv                    # Parts, codes, suppliers, quantities, prices and origin
│   ├── bom.py                     # Totals and BOM.md from bom.csv and dimensions.csv (standard library only)
│   ├── BOM.md                     # Generated bill of materials - do not edit by hand
│   ├── dimensions.csv             # Dimensions per part and their validation, with links to the drawings
│   └── rates.csv                  # Exchange rates to the reporting currency
├── cad                            # CAD sources, in the four roles of cad/README.md (any tool, any number of files)
├── circuits                       # Wiring, pin assignments and power budget (Markdown or KiCad)
├── docs                           # Photos and own drawings; datasheets/ is local only (git-ignored)
├── exports                        # STL / 3MF exports for printing
├── CHANGELOG.md                   # Project changelog
├── LICENSE                        # Project license
├── DESIGN.md                      # Architecture, decisions, limitations and prototype history
├── README.md                      # Project documentation
└── TO-DO.md                       # Parked work
```

<!--
## Troubleshooting
-->
