# CAD
The enclosure and any other printed or machined parts. Any CAD tool and any number of files fit here; what matters is that the design keeps four roles apart:

| Role | Holds |
|---|---|
| **Parts** | every bought part as a simple model, with its dimensions in mm, each marked `measured`, `drawing` or `MEASURE` (still an estimate) - see `bom/dimensions.csv` |
| **Layout** | the single source of truth for positions, the stack and the clearances; every other file reads from it |
| **Printable parts** | the parts to export, with one switch choosing which one (e.g. `part = "back"`) |
| **Assembly and checks** | all parts in place, with fit checks that report the clearances (e.g. in the console) |

A measured value then changes in one place, and the whole design follows. Small projects may keep the roles as sections of one file; larger ones split them, e.g. `parts.scad`, `layout.scad`, `enclosure.scad` and `assembly.scad` in OpenSCAD.

Export the printable parts into `exports/`.
