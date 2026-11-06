# Creative direction v3 — ArchLang’s own drawings and 3D

**Audience:** developers / Hacker News / agent builders.  
**Trigger:** the v1/v2 spectacle package treated ArchLang as a texture on invented purple Blender geometry, hid the 2D drawings, and set 3D type that could not be read. This rewrite starts from what the compiler and `@chanmeng666/archlang-3d` actually emit.

## What was found (ran on the box, `@chanmeng666/archlang@1.55.0` + `@chanmeng666/archlang-3d@0.3.0`)

### Core — floor plans as code
ArchLang is plan-first. It compiles `.arch` to **SVG, DXF, TXT, JSON, PDF, PNG**. It does **not** draw elevations or sections (the docs say so plainly: “Heights are data and draw nothing”). What it *does* draw, at full resolution, is a dimensioned sheet: walls, openings, furniture symbols, north arrow, scale bar, title block, room labels and areas.

Commands actually exercised:

| Command | What we used it for |
|---|---|
| `archlang compile` / `preview` | High-res PNG sheets (`-w 2000`) |
| `theme rendered` (and presentation / dark / blueprint) | Studio sheet in the rendered palette |
| `compile --view iso` / `--view axon` | Native isometric / 30-60 plan-oblique pictures of the *same* building. Deprecated for 2.0, still works in 1.55 — extruded walls, floor plates, openings cut, no furniture, no roof, no title block |
| `preview --review` | Review sheet: warnings ringed and numbered, access graph, legend |
| `lint` / `suggest` | `W_BEDROOM_NO_WINDOW` + a ready-to-paste `window` statement |
| `describe` | Room counts, net/gross areas, reachability — the facts under the stills and inside the replay |
| `repair` | Pushed a colliding bed clear of a partition (not the hero story) |
| `--overlay circulation` | Compiled; not used in the final heroes |

Other native capabilities confirmed but not hero-ed: `fix`, `finish`, `impact --set`, `reroll`, multi-storey `--level` (hillside villa L1/L2 and a stacked iso), MCP (`@chanmeng666/archlang-mcp` / `https://mcp.archlang.uk/mcp`).

### Downstream 3D — this *is* the built-in 3D modelling
`@chanmeng666/archlang-3d@0.3.0` (`archlang3d`) is published. It reads the same `.arch` through `resolvePlan`, checks the mesh against the plan, and writes:

- **`archlang3d build plan.arch -o plan.glb`** — a Khronos-checked GLB (nodes named `wall:…`, `door:…`, furniture, extras.archlang). Built successfully for studio, courtyard-house, hillside-villa, furnished-flat, garden-loft, parametric, two-storey.
- **`archlang3d view plan.arch --replay --video`** — an offline HTML file plus an MP4: the plan draws itself, then the walls rise. Dark theme, 1280×720, 24 fps. Furniture is in the model; doors default closed; stairs / outdoor / fences are omitted in this milestone (stated in `assumptions[]`).
- `check`, `doctor`, `schema scene3d`, `--doors closed|plan`, `--storey n|all`, `--theme light|dark`.

A Blender import of the studio GLB was tested *only* for lighting/camera. The official replay’s cutaway (plan → risen walls, interior furniture visible) is a clearer picture of the same model than an exterior-with-roof beauty render, so the shipped 3D stills and videos are the replay frames themselves — no invented mesh.

### What ArchLang is not (so we do not fake it)
No sections, no elevations, no IFC yet, no free camera inside `compile --view`. Iso/axon is “a picture, never a measured drawing.” 3D defaults (slab 200 mm, flat roof, closed doors) are labelled assumptions, not design decisions.

## Concept

Every hero frame is something ArchLang produced, composed with **flat 2D typography** (PIL / ffmpeg overlays — never 3D text).

1. **Code → plan → 3D, same building** (`studio.arch`, the canonical example).  
   Left: a readable excerpt of the source. Centre: `archlang compile` / `theme rendered` at full resolution. Right: last frame of `archlang3d view --replay` of that same file. Caption from `describe()`: 4 rooms · 42 m² · every room reachable.

2. **Courtyard house — the hole is the point** (`examples/courtyard-house.arch`).  
   A large compiled sheet (room labels, areas, dimensions, furniture kept large enough to read on a phone) beside the replay 3D of the same plan, where the courtyard reads as a void in the mass, not a room. Quote, as 2D type: *the courtyard is not a room — it is the hole the building wraps around.*

3. **Lint / fix** (`preview --review` then a clean compile).  
   Bedroom ringed on the native review sheet, `W_BEDROOM_NO_WINDOW` set in monospaced type, and the same plan after `window at (7000,1500) width 1200` — lint clean. The diagnostic is the product.

**Videos**

1. Studio replay (7 s, 1280×720, 24 fps) — plan draws, walls rise — scored with Andrew Ev’s *Vastness* and a Mixkit whoosh. 2D title overlay only.
2. Courtyard-house replay (8 s) — same treatment.
3. Parametric row (6.75 s) — `let COUNT = 2…5` as 2D type next to the real compiled sheets of `parametric.arch`. Kenney ticks + *Vastness*.

## Rules this draft refuses

- No invented purple solids, A-frame monuments, or helix towers that the language did not compile.
- No 3D-extruded lettering. Code and captions are rasterised type.
- 2D drawings are compiled at ~2000 px and cropped to the *building*, not shrunk to a texture on a 3D slab.
- 9:16 uses stacked contain-fit with ≥64 px side margins so nothing important clips.
- Audio is the real files already in `source/audio/` (see `source/audio/CREDITS.md`). No generated music.

## Brand

Void `#0f1115`, Plum `#8052ff`, Sheet `#f5f2ea`. Inter + JetBrains Mono. Tagline **Designs that compile.**

## Honest remaining weaknesses

- Replay stills and videos are 1280×720 (the viewer’s native export). They are slightly softer than the 2000 px plan PNGs when shown large.
- `compile --view iso` is a clean line drawing but has no furniture (by contract). The heroes feature `archlang3d` replay 3D instead; iso/axon PNGs remain in `output/v3/intermediates/iso|axon/` if needed.
- The Blender GLB test (`output/v3/intermediates/glb_renders/studio.png`) shows the closed exterior and a solid ground plane — useful as proof the GLB is real, not as a hero.
- On the 1:1 code→plan→3D still, the source excerpt is cropped before every room statement; the drawing still names all four rooms.
- Some courtyard dimension numerals are small at phone size; room names, areas and the courtyard itself stay readable.
- `archlang-3d` 0.3.0 omits stairs, outdoor ground and fences. That is the package’s stated M1 scope, not something we filled in by hand.
