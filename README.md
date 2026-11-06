# ArchLang Spectacle

<p align="center">
  <img src="https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/02-courtyard-plan-3d-16x9.png" alt="ArchLang courtyard house: a compiled dimensioned plan beside a daylight 3D cutaway from the same .arch file" width="100%">
</p>

<p align="center">
  <em>One <code>.arch</code> file becomes a precise sheet and a daylight 3D model.</em><br>
  Tagline: <strong>Designs that compile.</strong>
</p>

Marketing films and stills for **[ArchLang](https://github.com/ChanMeng666/archlang)** — an open-source language and compiler for floor plans. You (or an agent) write `.arch` source; ArchLang compiles it to SVG, DXF, PDF, and PNG, lints it, describes it as data, and extrudes it with [`archlang3d`](https://www.npmjs.com/package/@chanmeng666/archlang-3d).

This repository is the **production pipeline** behind the v1.0.0 release: bright, product-faithful motion graphics that walk through writing, compiling, restyling, describing, linting, fixing, varying, rising into 3D, exporting, and calling the compiler from an agent.

- Docs: [archlang.uk](https://archlang.uk)
- Playground: [playground.archlang.uk](https://playground.archlang.uk)
- Language repo: [ChanMeng666/archlang](https://github.com/ChanMeng666/archlang)
- npm: [`@chanmeng666/archlang`](https://www.npmjs.com/package/@chanmeng666/archlang) · [`@chanmeng666/archlang-3d`](https://www.npmjs.com/package/@chanmeng666/archlang-3d)

Rendered videos and stills are attached to the [v1.0.0 GitHub Release](https://github.com/ChanMeng666/archlang-spectacle/releases/tag/v1.0.0) rather than stored in git, so the repository stays small.

## Gallery

Every frame is something ArchLang itself produced: a compiled plan, a lint review sheet, or an official `archlang3d` light-theme replay — composed on Sheet `#f5f2ea` with Ink `#111111` and brand plum `#8052ff`.

### Studio — code, plan, and 3D

| 16:9 | 1:1 | 9:16 |
| :---: | :---: | :---: |
| [![Studio 16:9](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/01-code-plan-3d-16x9.png)](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/01-code-plan-3d-16x9.png) | [![Studio 1:1](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/01-code-plan-3d-1x1.png)](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/01-code-plan-3d-1x1.png) | [![Studio 9:16](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/01-code-plan-3d-9x16.png)](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/01-code-plan-3d-9x16.png) |

### Courtyard house — the same source as a sheet and a model

| 16:9 | 1:1 | 9:16 |
| :---: | :---: | :---: |
| [![Courtyard 16:9](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/02-courtyard-plan-3d-16x9.png)](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/02-courtyard-plan-3d-16x9.png) | [![Courtyard 1:1](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/02-courtyard-plan-3d-1x1.png)](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/02-courtyard-plan-3d-1x1.png) | [![Courtyard 9:16](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/02-courtyard-plan-3d-9x16.png)](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/02-courtyard-plan-3d-9x16.png) |

### Lint catches a missing window — then the fix compiles clean

| 16:9 | 1:1 | 9:16 |
| :---: | :---: | :---: |
| [![Lint 16:9](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/03-lint-fix-16x9.png)](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/03-lint-fix-16x9.png) | [![Lint 1:1](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/03-lint-fix-1x1.png)](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/03-lint-fix-1x1.png) | [![Lint 9:16](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/03-lint-fix-9x16.png)](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/03-lint-fix-9x16.png) |

## Videos

Shipped at 24 fps with a stereo score at about −16 LUFS. Full chapter list: [`docs/chapters-v5.md`](docs/chapters-v5.md).

| File | Length | Format | What it shows |
|---|---|---|---|
| [explainer-1080p.mp4](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/explainer-1080p.mp4) | 91s | 1920×1080 | The full walkthrough: hook → write `.arch` → compile → themes → describe → lint → fix → parametric `COUNT` → walls rising → export → MCP → end card |
| [wow-cutdown-1080p.mp4](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/wow-cutdown-1080p.mp4) | 27s | 1920×1080 | Hook, compile-with-connectors, 3D rise, end card |
| [agent-cutdown-1080p.mp4](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/agent-cutdown-1080p.mp4) | 28.5s | 1920×1080 | Describe, lint, fix, agent prompt → tool calls → drawing |
| [vertical-9x16.mp4](https://github.com/ChanMeng666/archlang-spectacle/releases/download/v1.0.0/vertical-9x16.mp4) | 25s | 1080×1920 | Vertical cutdown of hook, compile, 3D rise, and end card |

## Pipeline

```
source/archlang/*.arch
        │
        ├─► npx @chanmeng666/archlang compile / preview / describe / lint
        │         crisp 2D sheets, review rings, export SVG·DXF·PDF·PNG
        │
        ├─► npx @chanmeng666/archlang-3d view --replay --theme light
        │         official daylight replay (plan draws itself, walls rise)
        │
        └─► pipeline/v5  (Python compositor: easing, Ken Burns, typing,
                          code→room connectors, wipe, slider, export fan)
                  │
                  └─► ffmpeg  →  1080p24 H.264 + AAC, loudnorm ≈ −16 LUFS
```

Earlier experiments live alongside that path:

- `source/blender/` and `./generate.sh` — Blender 4.2 EEVEE spectacle scripts (code-to-form, courtyard grow).
- `pipeline/v3` and `pipeline/v4` — prior bright-compositor revisions.
- `docs/creative-direction.md` and `docs/creative-direction-v3.md` — the brief: every hero frame is ArchLang’s own output, not invented geometry.

## How to regenerate

### Requirements

| Tool | Version | Notes |
|---|---|---|
| Python | 3.11+ | `Pillow` and `NumPy`. Inter and JetBrains Mono improve typography; the compositor looks for those variable fonts on disk. |
| Node.js / npx | 20+ | `npx -y @chanmeng666/archlang@1.55.0` and `npx -y @chanmeng666/archlang-3d@0.3.0` |
| ffmpeg | 6+ | Encode, mix, and `loudnorm` |
| Blender | **4.2** | Only for `source/blender/` and `./generate.sh`. The shipped v5 films do not require Blender. |

### Shipped v5 films

The compositor reads compiled intermediates (themed studio and courtyard sheets, a lint review PNG, parametric `COUNT` 2–5 plans, export thumbnails, and a light `archlang3d` replay) from `output/v3` and `output/v4`, then writes `output/v5`.

```bash
# 1. Compile official examples (high-res PNG sheets)
npx -y @chanmeng666/archlang@1.55.0 compile source/archlang/official-studio.arch -w 2000
npx -y @chanmeng666/archlang@1.55.0 compile source/archlang/official-courtyard-house.arch -w 2000

# 2. Capture a light-theme 3D replay
npx -y @chanmeng666/archlang-3d@0.3.0 view source/archlang/official-courtyard-house.arch \
  --replay --theme light --size 1920x1080 --fps 24

# 3. Compose motion frames, then encode and score
python3 pipeline/v5/render.py
python3 pipeline/v5/assemble.py
```

Outputs land in `output/v5/videos/` and `output/v5/stills/`.

### Earlier Blender spectacle

```bash
./generate.sh          # or: make all
# stills only:          make stills
# v2 improved stills:   make v2
```

## Layout

```
archlang-spectacle/
  README.md                 # this file
  LICENSE                   # MIT (code)
  Makefile / generate.sh    # Blender spectacle entry points
  docs/                     # creative direction and v5 chapter list
  pipeline/v5/              # shipped motion compositor + encoder
  pipeline/v4/ pipeline/v3/ # earlier revisions
  source/archlang/          # .arch programs used in the films
  source/audio/             # Mixkit + Kenney beds and SFX (see CREDITS)
  source/blender/           # optional Blender generators
  source/textures/          # small compiled-sheet rasters
  _research/brand/          # official ArchLang marks (recolor only)
```

`output/` is gitignored. Download finished films from the release.

## Audio credits

Every scored video uses **real** royalty-free recordings — no AI-generated music and no commercial library tracks.

| Asset | Author | License | Role |
|---|---|---|---|
| Valley Sunset | Alejandro Magaña, [Mixkit 127](https://mixkit.co/free-stock-music/discover/valley-sunset/) | [Mixkit License](https://mixkit.co/license/#musicFree) | v4 / v5 music bed |
| Vastness | Andrew Ev, [Mixkit 184](https://mixkit.co/free-stock-music/discover/vastness/) | Mixkit License | Earlier scored cuts; kept on disk |
| Interface Sounds | [Kenney](https://kenney.nl/assets/interface-sounds) | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | Clicks, ticks, plucks, confirmation |
| Whoosh SFX | Mixkit | [Mixkit License](https://mixkit.co/license/#sfxFree) | Chapter transitions |

Full titles, CDN origins, and per-version usage: [`source/audio/CREDITS.md`](source/audio/CREDITS.md).

Suggested line for posts:

> Music: “Valley Sunset” by Alejandro Magaña via Mixkit.  
> SFX: Kenney Interface Sounds (CC0) + Mixkit Whoosh SFX.

## License

- **Code** (pipeline scripts, Blender generators, Makefiles, and this documentation structure) is licensed under the [MIT License](LICENSE). Copyright © 2026 Chan Meng ([ChanMeng666](https://github.com/ChanMeng666)).
- **ArchLang language examples** follow the license of [ChanMeng666/archlang](https://github.com/ChanMeng666/archlang) (MIT).
- **Brand marks** in `_research/brand/` are the official ArchLang identity — recolor only; do not redraw the geometry.
- **Audio** is not covered by this repository’s MIT grant. Use it under the Mixkit License or CC0 as listed in [`source/audio/CREDITS.md`](source/audio/CREDITS.md). Do not redistribute the Mixkit beds as a standalone music product.
- **Rendered stills and videos** in the GitHub Release depict compiler output from ArchLang and `archlang3d`. Credit ArchLang if you reuse them.

## Related

- [ArchLang](https://github.com/ChanMeng666/archlang) — the language and compiler
- [archlang.uk](https://archlang.uk) — documentation
- [playground.archlang.uk](https://playground.archlang.uk) — in-browser playground
