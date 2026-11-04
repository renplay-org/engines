# Renplay engines: notes for agents

This repository packages the official Ren'Py web engine, one pack per Ren'Py version, for
[Renplay](https://github.com/renplay-org/renplay) (a self-hosted web app that plays Ren'Py games
in the browser). Packs are GitHub releases named `renpy-<version>`; the index is published at
`https://engines.renplay.org/index.json`. Renplay downloads a pack the first time a game
needs that version and checks every file against the index.

## What a pack is

Built by `scripts/build-pack.sh <version> <out-dir>` from renpy.org's SDK and web support (verified
against renpy.org's sha256 sums). It keeps what every web game of that version shares:

| File | Purpose |
|---|---|
| `renpy.wasm.gz`, `renpy.data.gz` | The engine, served precompressed |
| `renpy.js`, `renpy-pre.js` | The engine loader |
| `index.html`, `web-presplash.jpg` | Page template (Renplay injects its runtime) and default splash |
| `renpy.zip` | The Ren'Py Python package and `main.py`, placed at the root of every game's `game.zip` |
| `manifest.json` | Version, Python major, sizes and sha256s |
| `LICENSE.txt` | Ren'Py's license |

Nothing from Ren'Py is modified. Renplay assembles each game's web build itself from these files
and the game's PC download, so it never runs the Ren'Py SDK.

## Files

- `versions.txt`: versions to publish, one per line. CI builds those without a release.
- `scripts/build-pack.sh`: builds one pack (Linux; needs curl, bzip2, unzip, python3).
- `scripts/index.py`: writes `index.json` from the releases.
- `.github/workflows/build.yml`: builds packs on pull requests; on `main` it releases new versions
  and publishes the index to engines.renplay.org (Cloudflare).

## Rules

- Only Ren'Py 8.x. Games made with Ren'Py 7 run on the newest 8.x engine (Renplay picks it for
  them), so 7.x packs are not needed; Ren'Py 7's own web support (renpyweb) is a different engine
  and loader that Renplay does not drive.
- A released pack never changes. To fix one, publish a new Ren'Py version (or ask the maintainer).
- Adding a version: add it to `versions.txt` in a pull request; CI must build it. After merging,
  check the release and `index.json`, then try a game on that engine in Renplay
  (`RENPLAY_ENGINE=<version>` or a recipe's `engine`).

Agents prepare pull requests; a maintainer merges.
