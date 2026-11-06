# Creative direction — ArchLang marketing spectacle

**Audience room:** developer / Hacker News / agent builders (ArchLang open-source).  
**Not** the ArchCanvas consumer funnel — do not sell “floor plans as code” to homeowners; that claim lives here, in the substrate room.

## Thesis (the hook)

The shareable wonder is **not** a pretty building render.  
It is: **a few lines of `.arch` growing into a precise, lintable drawing that no one would draft by hand** — then elevating that compile moment into visual spectacle.

ArchLang’s brand promise is already a triple reading in the mark (letter · house · floor plan). Spectacle content should make that promise *felt*:

1. **Source is visible** — monospaced `.arch` fragments are on-screen characters, not captions.
2. **Geometry is authored** — walls, rooms, loops, `theme from "#8052ff"` — not freeform sci-fi meshes that the language couldn’t specify.
3. **Compile is the magic trick** — tokens → walls → sheet. Determinism, not hallucination.
4. **Brand system holds** — Void `#0f1115`, Plum `#8052ff`, Sheet `#f5f2ea`, Ink `#111111`. Tagline: **Designs that compile.**

## What “奇观 / 吸睛” means for this product

| Do | Don’t |
|---|---|
| Parametric loops that spawn cities of courtyards | Generic cyberpunk towers with no plan logic |
| Hex / arc / polygon plans that only code can keep honest | Claiming “AI architect” (banned title) |
| Code typography extruding into walls | Fake permit / construction docs |
| A-frame mark as monument (letter=house=plan) | Retired spark mark; alternate logos |
| Short loops that invite “wait, that’s a floor plan?” | Long cinematic trailers with no code |

## Viral formats (v1 production set)

1. **Code-to-form hero** — source panel → extruded plan on a drafting sheet in the void.
2. **Recursive courtyard** — `for i in 1..DEPTH` as nested 3D rings (impossible to mouse, trivial to loop).
3. **A-frame monument** — the brand mark built as architecture.
4. **Assemble motion (5–8s)** — walls scale up from zero as tokens fall in; camera push.

## Social crops

- 16:9 hero (docs / X landscape / LinkedIn)
- 1:1 (X / LinkedIn / posts)
- 9:16 (stories / short video covers)

## Voice alignment (from growth `voice.md` / messaging library)

- Developer one-liner is allowed here: *deterministic DSL · compile to SVG/DXF/PDF · diffable source*.
- Prefer founder-specific angles in captions later (“I wrote a courtyard city as a loop”).
- Physical + code beats pure AI glamour renders when posting; these Blender pieces are **spectacle layer** on top of real `.arch` source kept in `source/archlang/`.

## Pipeline story

```
.source/archlang/*.arch   →  (future) archlang compile → SVG/PNG sheet
                          ↘
source/blender/*.py       →  blender --background --python  → output/images|videos
                          →  ffmpeg (encode / crop / loop)
```

Today Blender **interprets the intent** of the spectacle programs. When the box can run `@chanmeng666/archlang` reliably on these files, wire compiled SVGs into the sheet plane as image textures.
