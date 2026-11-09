# Renplay engines: notes for agents

This repository packages the official Ren'Py web engine, one pack per Ren'Py version, for
[Renplay](https://github.com/renplay-org/renplay) (a self-hosted web app that plays Ren'Py games
in the browser). Packs are GitHub releases named `renpy-<version>`, and their files are published at
`https://engines.renplay.org/<version>/` with the index at `https://engines.renplay.org/index.json`.
Renplay downloads a pack from there the first time a game needs that version and checks every file
against the index. The releases are the archive the site is made from.

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

- `versions.txt`: versions to publish, one per line. CI builds those without a release. A line
  `8.6.0 prerelease` marks a public pre-release: `index.json` gets `"prerelease": true` on its entry,
  and Renplay uses it only for games made with a newer Ren'Py than every stable engine.
- `prerelease-sums/<version>.txt`: sha256 sums of a pre-release's SDK and web files. renpy.org
  publishes no `checksums.txt` for a pre-release, so `build-pack.sh` checks against these.
- `scripts/build-pack.sh`: builds one pack (Linux; needs curl, bzip2, unzip, python3).
- `scripts/site.py`: writes the site: each release's files, checked against its `manifest.json`,
  in `site/<version>/`, and `index.json` listing them there.
- `scripts/verify.mjs`: downloads every file an index names, as Renplay does, and checks it.
- `.github/workflows/build.yml`: builds packs on pull requests. On `main` it releases new versions,
  publishes their files to engines.renplay.org (Cloudflare), checks they download whole, and only
  then publishes the index that names them.

## Rules

- Only Ren'Py 8.x. Games made with Ren'Py 7 run on the newest 8.x engine (Renplay picks it for
  them), so 7.x packs are not needed; Ren'Py 7's own web support (renpyweb) is a different engine
  and loader that Renplay does not drive.
- A released pack never changes. To fix one, publish a new Ren'Py version (or ask the maintainer).
- Adding a pre-release: mark it in `versions.txt`, and pin its sums in `prerelease-sums/` (download
  the two files, run `sha256sum`). When renpy.org publishes the final release, its files differ from
  the pre-release's, so ask the maintainer how to publish it.
- Adding a version: add it to `versions.txt` in a pull request; CI must build it. After merging,
  check the release and `index.json`, then try a game on that engine in Renplay
  (`RENPLAY_ENGINE=<version>` or a recipe's `engine`).

Agents prepare pull requests; a maintainer merges.
