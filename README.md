# Field Index — UAP Archive Investigation Prototype

A dependency-free static reference prototype for a public-record narrative investigation game, built independently from the approved task materials and source files in `UAP档案调查游戏体验设计-20260924`.

## Open locally

From this directory, start any local HTTP server:

```bash
python3 -m http.server 8765
```

Open <http://127.0.0.1:8765/prototype/>. The screenshot gallery is at <http://127.0.0.1:8765/prototype_screenshots/>. Opening `index.html` directly with `file://` is not supported because media and browser storage behavior should be exercised through HTTP.

## Structure

- `prototype/index.html` — semantic application shell and dialogs
- `prototype/data.js` — case, source-record, method, and PR159 data
- `prototype/app.js` — navigation, comparisons, notebook, persistence, import/export, Aguadilla lab, and release workflow
- `prototype/styles.css` — responsive desktop/mobile visual system
- `prototype/assets/` — small selected set of local source media and derivatives
- `prototype_screenshots/` — 30 generated viewport PNGs and responsive gallery
- `tests/smoke.py` — desktop/mobile Playwright behavior and network validation
- `tests/screenshots.py` — sequential UI-driven screenshot generation and Pillow validation

No package manager, build step, web font, analytics, CDN, or runtime network request is used.

## Design rationale

The interface treats each case as a source register and the player’s desk as a durable working set. “View,” “pin,” “compare,” and “conclude” remain visible instead of being converted into a score. Early cases foreground straightforward source distinctions; later cases center chronology, sensor motion, retained radar, and version lineage. The conclusion form requires support, conflict, weakness, missing information, and a revision trigger. It accepts multiple positions and contains no hidden expected answer.

The full Aguadilla flow makes the player inspect provenance and competing analyses, select the three latest TJBQ rows before the 27 April 01:22 UTC event, compare their calculated offsets, convert knots to mph, and identify that the bundled extract ends before the event. It therefore has no post-event observation, does not bracket the event, and cannot directly reproduce AARO’s exact 4.4 m/s. Platform-motion and separation/transmedium checks state what each method changes without silently selecting a verdict.

The PR159 flow preserves a user-created Tremonton conclusion, exposes exact manifest metadata, synchronizes two playable local representations, records a player-authored relationship reason, explains the mechanical consequence of each relationship type, and reopens Tremonton. Choosing “same underlying film, different version” attaches provenance but does not increase independent corroboration.

## Source scope and factual caveats

Content was checked against `environment/source_manifest.csv`, the task instructions/answer points, TJBQ weather CSV, AARO’s 20 March 2025 Puerto Rico resolution, the Condon Tremonton case page, and selected competing Aguadilla analyses. Important represented facts include:

- PR159: `release_06`, record `DOW-UAP-PR159`, title as published, incident date `7/2/52`, Tremonton, 79,823,577-byte MP4, 70.083333 seconds, 1920×1080, DVIDS ID 1023402, and manifest SHA-256.
- Tremonton Condon record: 2 July 1952; daylight handheld 16 fps film; about 1,200 frames/75 seconds; film considered consistent with birds but not conclusive by film alone.
- Aguadilla AARO record: 26 April 2013 locally (27 April UTC); assessed 8 mph and 656 ft; two nearby objects; motion-parallax and over-land reconstruction; moderate-confidence sky-lantern attribution.
- TJBQ supplied observations: 26 April 21:50 UTC 060°/11 kt, 22:50 UTC 060°/10 kt gusting 14, and 23:50 UTC 060°/9 kt. They are 3h32m, 2h32m, and 1h32m before the 27 April 01:22 UTC event. The extract ends with the last row, so there is no post-event observation; it neither brackets the event nor directly reproduces AARO’s exact 4.4 m/s.
- Competing Aguadilla analyses differ on line-of-sight geometry, required drift speed, separation, occlusion, and apparent water interaction. The prototype presents these as disputed analytical claims, not adjudicated facts.

The prototype uses authored summaries rather than republishing rights-unclear reports, articles, or large compilations. Included media are: the manifest PR159 file; a later Tremonton representation; a 24-second, 960×540 excerpt derived from the DVIDS/AARO public-domain-labelled reconstruction; two low-resolution McMinnville case plates; and compact Socorro/Rendlesham reference images. Public access does not itself establish reuse rights. This is a local research/design prototype, and item-level rights should be reviewed before distribution.

## Tests

Installed Python Playwright and Pillow are required only for automation:

```bash
python3 tests/smoke.py
python3 tests/screenshots.py
```

Both scripts start their own local server by default. Use `--no-server --port 8765` to target an already running server. `smoke.py` exercises all eight cases plus complete Aguadilla and PR159 flows at 1440×900 and 390×844, verifies persistence, catches console/page errors, rejects external requests and non-aborted failed requests, and checks horizontal overflow. `screenshots.py` drives the actual UI, deliberately scrolls each decisive region into view, creates 15 paired viewport captures (30 PNGs), then checks exact dimensions, sticky navigation placement, hidden skip-link state, and pixel variance for nonblank output.
