================================================================
JK3DA Texel Kit — Blender Add-on
================================================================

Version: 1.0.0
Author: JK3DA
Website: https://jk3da.com

License: GPL-3.0
Commercial Support License available separately.

AI-assisted development using Claude (Anthropic)
and GitHub Copilot.

================================================================
OVERVIEW
================================================================

JK3DA Texel Kit is a Texel Density toolkit for Blender 4.0+.

It helps artists measure, set, normalize, and visually inspect
Texel Density across 3D assets — a standard workflow used in
game art, environment design, and film production pipelines.

Texel Density (TD) defines how many texture pixels are mapped
onto a specific real-world surface size.

Maintaining consistent Texel Density ensures textures appear
uniformly sharp across all assets in a scene.

Designed for:
  - Game artists
  - Environment artists
  - Hard-surface workflows
  - Asset production pipelines
  - Film & cinematic workflows

================================================================
FEATURES
================================================================

Texel Density Scanning
----------------------
- Measure Texel Density for:
    - single objects
    - multiple selected objects
    - entire scenes

- Fast TD analysis directly inside Blender

Set Density
-----------
- Automatically scale UVs to a target Texel Density
- Consistent TD across multiple assets

Preset Grid
------------
One-click preset values:

  - 20.48 px/cm
  - 10.24 px/cm
  - 5.12 px/cm
  - 2.56 px/cm
  - 1.28 px/cm
  - 0.64 px/cm

Quick Scaling
-------------
- x0.5 → halve current TD
- x2   → double current TD

Units
-----
Switch between:
  - px/cm
  - px/m
  - px/in
  - px/ft

Checker Preview
----------------
- Assign checker materials automatically
- Detect UV stretching visually
- Supports custom checker textures
  (e.g. CustomUVChecker)

Normalize UVs
-------------
- Snap UVs back into the 0-1 range
- Useful for fixing drifting UV islands

Scale Warning
--------------
- Detect unapplied object scale
- Alerts user when Ctrl+A Apply Scale is recommended

Scene TD Report
----------------
- Scan all mesh objects in the scene
- Sort objects by Texel Density
- Click entries to instantly select objects

UV Editor Integration
----------------------
Full interface support inside:
  - 3D Viewport
  - UV Editor

================================================================
INSTALLATION
================================================================

1. Open Blender
2. Go to:
     Edit → Preferences → Add-ons
3. Click:
     Install...
4. Select:
     jk3da_texelkit.zip
5. Enable:
     "JK3DA Texel Kit"
6. Open the N-Panel:
     JK3DA Texel Kit tab

================================================================
REQUIREMENTS
================================================================

- Blender 4.0 or newer

================================================================
LICENSE
================================================================

JK3DA Texel Kit is licensed under the GNU General Public
License v3.0 (GPL-3.0).

This means you are free to:
  - use the software commercially
  - modify the source code
  - redistribute the software
  - create derivative works

A separate optional Commercial Support License is available
for studios and companies requiring formal procurement or
production documentation.

See:
  LICENSE_Commercial.txt

Full GPL license:
https://www.gnu.org/licenses/gpl-3.0.html

================================================================
CREDITS
================================================================

Developed by JK3DA
https://jk3da.com

AI-assisted development using:
  - Claude (Anthropic)
  - GitHub Copilot

All design direction, implementation decisions,
testing, and validation were performed by JK3DA.