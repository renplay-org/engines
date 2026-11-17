# Renplay engines

**The official Ren’Py web engines that [Renplay](https://github.com/renplay-org/renplay) plays games with, packaged one per Ren’Py version.**

Renplay is a self-hosted player for Ren’Py games in the browser, with saves on your own server. It builds each
game for the web from its normal PC download, and runs the game on the Ren’Py web engine. This repository
packages that engine. A Renplay installation downloads the pack a game needs the first time it needs it, checks
every file, and keeps it, so nothing has to be set up by hand.

You do not need anything from here to use Renplay. Read on if you are curious, or want to add a version.

## Where the packs are

- Each pack is a GitHub release named `renpy-<version>`.
- Its files are served from `https://engines.renplay.org/<version>/`.
- The index Renplay reads is [`https://engines.renplay.org/index.json`](https://engines.renplay.org/index.json).
  It lists every file with its size and sha256.
- [engines.renplay.org](https://engines.renplay.org) shows the versions in a page for people.
- The docs explain
  [how Renplay picks an engine](https://docs.renplay.org/engines/).

## What a pack holds

A pack holds what every Ren’Py web game built with that version shares: the WebAssembly engine, its loader, the
page template, and the Ren’Py Python package that sits next to the game files in `game.zip`. Ren’Py’s own license
is in each pack as `LICENSE.txt`.

Packs are built in CI from the official SDK and web support on renpy.org, and checked against renpy.org’s
published sha256 sums. Nothing in them is modified. CI also downloads every file the index names, as Renplay
does, before the index is published.

Only Ren’Py 8 is packaged. The 8.x engine runs games made with earlier 8.x releases and most games made with
Ren’Py 7, which Renplay builds with it. Ren’Py 7’s own web support is a different engine that Renplay does
not need. HTML games need no engine pack, since they are web pages already.

## Adding a version

Add it to `versions.txt` and open a pull request. CI builds the pack to check it. After the pull request is
merged, the version is released and indexed. To build a pack on your own machine, run
`scripts/build-pack.sh <version> <out-dir>`. It needs Linux with `curl`, `bzip2`, `unzip` and `python3`, or a
Linux container with those installed.

A public pre-release is marked in `versions.txt` (`8.6.0 prerelease`). It is listed in the index under
`"prereleases"`, apart from `"engines"`, which older Renplay versions read, and Renplay uses it only for games
that need a newer Ren’Py than any stable engine. renpy.org publishes no sums for a pre-release, so they are
pinned in `prerelease-sums/`.

A released pack never changes. To fix one, publish a new Ren’Py version.

## More

- [Renplay](https://github.com/renplay-org/renplay), the app, and its [docs](https://docs.renplay.org)
- [The catalog](https://github.com/renplay-org/catalog), the tested games
- Working on this repository with an AI agent: see [AGENTS.md](AGENTS.md)

Ren’Py is © Tom Rothamel and contributors, under its own license. Renplay is not affiliated with it.
