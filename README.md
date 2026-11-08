# Renplay engines

Ren'Py web engines packaged for [Renplay](https://github.com/renplay-org/renplay). One pack per
Ren'Py version, kept as a GitHub release (`renpy-<version>`) and served from
`https://engines.renplay.org/<version>/`, listed in `https://engines.renplay.org/index.json`.

A pack holds what every Ren'Py web game built with that version shares: the WebAssembly engine,
its loader, the page template and the Ren'Py Python package that sits next to the game files in
`game.zip`. Renplay downloads a pack the first time a game needs that version, checks every
file against the index, and builds games itself from their PC downloads, without running the
Ren'Py SDK.

Packs are built in CI from the official SDK and web support on renpy.org, verified against
renpy.org's published sha256 sums. Nothing in them is modified. Ren'Py is MIT-licensed; see
`LICENSE.txt` in each pack.

Only Ren'Py 8 is packaged. The 8.x engine runs games made with earlier 8.x releases and most games
made with Ren'Py 7, which Renplay builds with it. Ren'Py 7's own web support (`index.wasm`,
separate Python data packages) is a different engine that Renplay does not need. HTML games need no
engine pack: they are web pages already.

## Adding a version

Add it to `versions.txt` and open a pull request. CI builds the pack to check it; after merging,
it is released and indexed. Build locally with `scripts/build-pack.sh <version> <out-dir>`
(Linux, or `docker run --rm -v "$PWD":/w -w /w debian:bookworm-slim` with `curl bzip2 unzip
python3` installed).

Working on this repository with an AI agent: see [AGENTS.md](AGENTS.md).
