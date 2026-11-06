# ArchLang v5 videos

Bright sheet `#f5f2ea`, ink `#111`, brand plum `#8052ff`.
Motion compositor: `pipeline/v5/engine.py` + `scenes.py` (cubic / spring easing, Ken Burns, kinetic type, syntax-highlighted typing, code→room connectors) rather than hard-cut PIL stills.

## 01-explainer-1080.mp4 — 91.0s — 1920×1080 @ 24fps — −15.7 LUFS

Narrative per chapter: problem → promise → show → proof.
Each chapter opens with a numbered title card / lower-third and a one-line “why it matters” caption. A plum progress bar and `NN / 12` indicator run throughout.

| # | Start | Dur | Id | Title | Why it matters |
|---|------:|----:|----|-------|----------------|
| 01 | 0.0 | 7.0 | hook | A language for floor plans | one file becomes a precise sheet and a 3D model |
| 02 | 7.0 | 9.5 | write | Write the building as text | rooms, walls and openings are source you can diff |
| 03 | 16.5 | 7.0 | compile | The compiler draws the sheet | the same source always produces the same drawing |
| 04 | 23.5 | 7.0 | themes | Restyle, don’t redraw | inks and fills change; measurements never do |
| 05 | 30.5 | 7.0 | describe | Facts, not a guess | areas and reachability come back as data an agent can read |
| 06 | 37.5 | 7.0 | lint | Catch the missing window | every warning has a code, and often a ready fix |
| 07 | 44.5 | 6.0 | fix | Suggest, apply, compile again | the review ring disappears when the source is corrected |
| 08 | 50.5 | 8.0 | param | Change one number | a loop writes the row; you don’t copy rooms by hand |
| 09 | 58.5 | 12.0 | rise | The plan draws itself | walls rise from the same source, in daylight |
| 10 | 70.5 | 7.0 | export | One source, five formats | SVG, DXF, PDF, PNG and a checked GLB fan out from one file |
| 11 | 77.5 | 7.0 | mcp | The compiler is the agent interface | an agent writes ArchLang, calls tools, and reads the facts |
| 12 | 84.5 | 6.5 | end | Designs that compile. | archlang.uk · playground.archlang.uk · @chanmeng666/archlang |

Total 91.0s.

## Cutdowns

- `02-wow-cutdown-1080.mp4` — hook 6 + compile 7 + rise 10 + end 4 = 27.0s (1920×1080) — −15.7 LUFS
- `03-agent-cutdown-1080.mp4` — describe 6.5 + lint 6.5 + fix 5.5 + mcp 6.5 + end 3.5 = 28.5s (1920×1080) — −16.8 LUFS
- `04-vertical-9x16.mp4` — hook 6 + compile 7 + rise 8 + end 4 = 25.0s (1080×1920) — −15.6 LUFS

## Audio

Valley Sunset by Alejandro Magaña (Mixkit 127) bed, Kenney CC0 clicks/ticks/plucks/confirmation plus Mixkit whooshes on chapter hits, room highlights, counter ticks, wipe and export fan. `loudnorm=I=-16:TP=-1.5:LRA=11`. See `source/audio/CREDITS.md`.
