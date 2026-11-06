# Audio credits — archlang-spectacle

All audio below is a **real downloaded recording** from a royalty-free / CC0 library.
Nothing here is AI-generated music, and no copyrighted commercial tracks were used.

Mixkit attribution is appreciated but **not required** under the Mixkit License.
Kenney Interface Sounds are **CC0** (public domain); credit is appreciated but not required.
We credit everyone anyway.

---

## Music

### Vastness
| | |
|---|---|
| **Title** | Vastness |
| **Author** | Andrew Ev |
| **Source** | Mixkit — https://mixkit.co/free-stock-music/discover/vastness/ |
| **File used** | `music/vastness-andrew-ev-mixkit-184.mp3` (CDN asset id `184`) |
| **CDN origin** | `https://assets.mixkit.co/music/184/184.mp3` |
| **License** | [Mixkit License](https://mixkit.co/license/#musicFree) — free for commercial & non-commercial use in videos; attribution appreciated, not required. Not for redistribution as a standalone music product / CD / game soundtrack pack / radio broadcast (see license). |
| **Use in project** | Background bed for `04-code-assemble-scored.mp4` (slice ~20–26s) and loop cut `04-code-assemble-loop5s-scored.mp4` (slice ~45–50s). Loudnorm ≈ −15 LUFS. |

### Valley Sunset (alternate bed, kept on disk)
| | |
|---|---|
| **Title** | Valley Sunset |
| **Author** | Alejandro Magaña (A. M.) |
| **Source** | Mixkit — https://mixkit.co/free-stock-music/discover/valley-sunset/ |
| **File used** | `music/valley-sunset-alejandro-magana-mixkit-127.mp3` (CDN asset id `127`) |
| **CDN origin** | `https://assets.mixkit.co/music/127/127.mp3` |
| **License** | Mixkit License (same as above) |
| **Use in project** | Alternate / unused in v1 scored mux (available for future cuts). |

---

## Sound effects — Kenney Interface Sounds (CC0)

| | |
|---|---|
| **Pack** | Interface Sounds |
| **Author** | Kenney (www.kenney.nl) |
| **Source page** | https://kenney.nl/assets/interface-sounds |
| **Mirror used** | https://cc0-sounds.exi.software/collection/kenney_interfacesounds/ |
| **License** | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain dedication |
| **Files used** | `sfx/kenney/click_001.ogg`, `click_002.ogg`, `click_003.ogg`, `tick_001.ogg`, `tick_002.ogg`, `tick_004.ogg`, `confirmation_002.ogg`, `pluck_001.ogg`, `pluck_002.ogg`, `open_002.ogg`, `open_003.ogg`, `switch_001.ogg` |
| **Role** | Code/token ticks & clicks during assemble; open/pluck/confirmation as the “compile settle” sting |

---

## Sound effects — Mixkit Whoosh (Mixkit License)

Downloaded as the public preview MP3s Mixkit serves for free SFX (real recordings, not synthesized here).

| File in repo | Mixkit id | Title (from Mixkit Whoosh category listing) | Page |
|---|---|---|---|
| `sfx/mixkit/cinematic-whoosh-fast-transition-1489.mp3` | 1489 | Cinematic whoosh fast transition | https://mixkit.co/free-sound-effects/whoosh/ |
| `sfx/mixkit/arrow-whoosh-1492.mp3` | 1492 | Arrow whoosh | same |
| `sfx/mixkit/fast-whoosh-transition-1714.mp3` | 1714 | Fast whoosh transition | same |
| `sfx/mixkit/cinematic-whoosh-stutter-2350.mp3` | 2350 | Cinematic whoosh stutter | same |
| `sfx/mixkit/ghostly-whoosh-passing-1485.mp3` | 1485 | Ghostly whoosh passing | same |

| | |
|---|---|
| **CDN pattern** | `https://assets.mixkit.co/active_storage/sfx/{id}/{id}-preview.mp3` |
| **License** | [Mixkit License](https://mixkit.co/license/#sfxFree) — free SFX for use in videos; attribution appreciated, not required |
| **Role in v1 mix** | Arrow whoosh + cinematic whoosh under wall extrusion / camera move (main 6s). Loop cut uses arrow whoosh only. Extra whooshes kept for future edits. |

---

## Suggested attribution line (optional, for posts)

> Music: “Vastness” by Andrew Ev via Mixkit.  
> SFX: Kenney Interface Sounds (CC0) + Mixkit Whoosh SFX.


---

## Use in courtyard-grow motion (`05-courtyard-grow-scored.mp4`)

Same real sources as the assemble score — no new downloads:

- Music bed: Mixkit **Vastness** by Andrew Ev (slice ~30s onward)
- SFX: Kenney Interface Sounds ticks/clicks/pluck/confirmation/open (CC0)
- Whooshes: Mixkit Arrow whoosh (#1492) on each DEPTH ring birth; Cinematic whoosh fast transition (#1489) mid-grow

See `pipeline/score_courtyard_grow.sh`.


## Final package (24fps)
Same real Mixkit Vastness + Kenney Interface Sounds + Mixkit Whoosh stack via `pipeline/score_final.sh`. No new downloads.

---

## Use in v4 bright explainer (`output/v4/videos/`)

No new audio was downloaded. The v4 package reuses the real Mixkit and Kenney recordings already on disk.

| Asset | Role in v4 |
|---|---|
| **Valley Sunset** — Alejandro Magaña, Mixkit 127 | Main bed for `01-explainer-1080.mp4` (slice from ~0:03, faded in/out across 86.5s). Also sliced as the bed for `02-wow-cutdown-1080.mp4`, `03-agent-cutdown-1080.mp4`, and `04-vertical-9x16.mp4`. Chosen over Vastness because it is warmer and reads better against the light Sheet palette. |
| **Vastness** — Andrew Ev, Mixkit 184 | On disk, unused in v4 mixes. |
| Kenney `click_002.ogg` | Typing chapter (six clicks while `.arch` is written) |
| Kenney `tick_002.ogg` | describe / lint / parametric beats; agent cutdown chapter marks |
| Kenney `confirmation_002.ogg` | fix chapter sting; end-card sting on every video |
| Kenney `open_002.ogg` | compile-settle sting |
| Kenney `pluck_002.ogg` | themes chapter accent |
| Mixkit cinematic whoosh fast transition (#1489) | Hook open and 3D-rise chapter |
| Mixkit arrow whoosh (#1492) | compile and export chapter transitions |
| Mixkit ghostly whoosh passing (#1485) | themes and MCP chapter transitions |

Suggested attribution line for v4 posts:

> Music: “Valley Sunset” by Alejandro Magaña via Mixkit.  
> SFX: Kenney Interface Sounds (CC0) + Mixkit Whoosh SFX.

---

## Use in v5 bright explainer (`output/v5/videos/`)

No new audio was downloaded. The v5 package reuses the same Mixkit and Kenney recordings.

| Asset | Role in v5 |
|---|---|
| **Valley Sunset** — Alejandro Magaña, Mixkit 127 | Bed for `01-explainer-1080.mp4` (from ~0:03 across 91s) and the wow, agent, and vertical cutdowns. |
| **Vastness** — Andrew Ev, Mixkit 184 | On disk, unused in v5 mixes. |
| Kenney `click_002.ogg` | Typing chapter and MCP tool-call ticks |
| Kenney `tick_002.ogg` | describe / lint / parametric counter ticks |
| Kenney `confirmation_002.ogg` | Fix-wipe settle and end-card sting |
| Kenney `open_002.ogg` | Compile settle and export fan |
| Kenney `pluck_002.ogg` | Room-highlight and themes accents |
| Mixkit cinematic whoosh fast transition (#1489) | Hook open and 3D-rise chapter |
| Mixkit arrow whoosh (#1492) | Compile and export transitions |
| Mixkit ghostly whoosh passing (#1485) | Themes and MCP transitions |

Suggested attribution line for v5 posts:

> Music: “Valley Sunset” by Alejandro Magaña via Mixkit.  
> SFX: Kenney Interface Sounds (CC0) + Mixkit Whoosh SFX.

Target loudness ≈ −16 LUFS integrated (`loudnorm=I=-16:TP=-1.5:LRA=11`).
