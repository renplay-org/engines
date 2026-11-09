#!/usr/bin/env bash
# Builds a renplay engine pack for one Ren'Py version.
#
#   scripts/build-pack.sh <version> <out-dir>
#
# Downloads the official Linux SDK and web support from renpy.org, checks
# them against renpy.org's published sha256 sums (for a pre-release, which has
# none, against prerelease-sums/<version>.txt), builds the bundled sample
# game for the web and keeps only the parts every web game shares:
#
#   renpy.wasm.gz renpy.data.gz   engine (renplay serves these precompressed)
#   renpy.js renpy-pre.js         engine loader
#   index.html web-presplash.jpg  page template and default splash
#   renpy.zip                     the Ren'Py Python package + main.py, as they
#                                 appear at the root of every web game.zip
#   manifest.json                 version, Python major, sizes and sha256s
#   LICENSE.txt                   Ren'Py's license
set -euo pipefail

VERSION="${1:?version}"
OUT="${2:?out dir}"
BASE="https://www.renpy.org/dl/${VERSION}"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

sha_of() { grep -E "^[0-9a-f]{64} $1\$" "$WORK/checksums.txt" | cut -d' ' -f1; }

echo "== Ren'Py ${VERSION}"
# Releases publish checksums.txt. A pre-release does not, so its sums are pinned in this repository.
if ! curl -fsSL "${BASE}/checksums.txt" -o "$WORK/checksums.txt"; then
  PINNED="$HERE/../prerelease-sums/${VERSION}.txt"
  [ -f "$PINNED" ] || { echo "no checksums.txt on renpy.org and no $PINNED" >&2; exit 1; }
  echo "no checksums.txt on renpy.org, using the pinned sums"
  cp "$PINNED" "$WORK/checksums.txt"
fi
SDK="renpy-${VERSION}-sdk.tar.bz2"
WEB="renpy-${VERSION}-web.zip"
for f in "$SDK" "$WEB"; do
  want="$(sha_of "$f")"
  [ -n "$want" ] || { echo "no sha256 for $f" >&2; exit 1; }
  curl -fsSL "${BASE}/${f}" -o "$WORK/$f"
  echo "$want  $WORK/$f" | sha256sum -c -
done

tar -xjf "$WORK/$SDK" -C "$WORK"
SDKDIR="$WORK/renpy-${VERSION}-sdk"
unzip -q "$WORK/$WEB" -d "$SDKDIR"
[ -f "$SDKDIR/web/renpy.wasm" ] || { echo "web support missing" >&2; exit 1; }

# Build the sample game; only the shared parts are kept.
cp -r "$SDKDIR/the_question" "$WORK/sample"
printf '%s\n' '- image game/gui/**' '+ image game/**' > "$WORK/sample/progressive_download.txt"
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy HOME="$WORK/home"
mkdir -p "$HOME"
"$SDKDIR/renpy.sh" "$SDKDIR/launcher" web_build "$WORK/sample" --destination "$WORK/build" > "$WORK/build.log" 2>&1 || {
  tail -40 "$WORK/build.log" >&2
  exit 1
}

rm -rf "$OUT"
mkdir -p "$OUT"
for f in renpy.js renpy-pre.js index.html web-presplash.jpg; do cp "$WORK/build/$f" "$OUT/$f"; done
gzip -9 -n -c "$WORK/build/renpy.wasm" > "$OUT/renpy.wasm.gz"
gzip -9 -n -c "$WORK/build/renpy.data" > "$OUT/renpy.data.gz"
cp "$SDKDIR/LICENSE.txt" "$OUT/LICENSE.txt" 2>/dev/null || true

# Everything at the root of game.zip except the sample game itself.
python3 - "$WORK/build/game.zip" "$OUT/renpy.zip" <<'PY'
import sys, zipfile
src, dst = sys.argv[1], sys.argv[2]
keep = 0
with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zo:
    for info in zi.infolist():
        n = info.filename
        if n.startswith("renpy/") or n == "main.py":
            if n.endswith("/"):
                continue
            zo.writestr(info, zi.read(info))
            keep += 1
if keep < 100:
    sys.exit("renpy package missing from game.zip (%d files)" % keep)
print("renpy.zip: %d files" % keep)
PY

FULL="$(sed -n "s/^version = '\(.*\)'/\1/p" "$SDKDIR/renpy/vc_version.py" | head -1)"
PY_MAJOR=3
case "$VERSION" in 7.*|6.*) PY_MAJOR=2 ;; esac
python3 - "$OUT" "$VERSION" "$FULL" "$PY_MAJOR" <<'PY'
import hashlib, json, os, sys
out, version, full, py = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
files = {}
for name in sorted(os.listdir(out)):
    data = open(os.path.join(out, name), "rb").read()
    files[name] = {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
json.dump({"schema": 1, "version": version, "renpy": full or version, "python": py, "files": files},
          open(os.path.join(out, "manifest.json"), "w"), indent=1)
PY
ls -la "$OUT"
