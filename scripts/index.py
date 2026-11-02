"""Writes the engines index from the published GitHub releases."""
import json, os, subprocess, sys, urllib.request

repo = os.environ["GITHUB_REPOSITORY"]
out = sys.argv[1]
releases = json.loads(subprocess.check_output(["gh", "api", f"repos/{repo}/releases", "--paginate"]))
engines = []
for rel in releases:
    tag = rel["tag_name"]
    if not tag.startswith("renpy-") or rel.get("draft"):
        continue
    assets = {a["name"]: a["browser_download_url"] for a in rel["assets"]}
    if "manifest.json" not in assets:
        continue
    with urllib.request.urlopen(assets["manifest.json"]) as r:
        manifest = json.load(r)
    files = {name: dict(meta, url=assets[name]) for name, meta in manifest["files"].items() if name in assets}
    engines.append({"version": manifest["version"], "renpy": manifest["renpy"], "python": manifest["python"], "files": files})


def key(e):
    return tuple(int(p) for p in e["version"].split("."))


engines.sort(key=key, reverse=True)
os.makedirs(out, exist_ok=True)
json.dump({"schema": 1, "engines": engines}, open(os.path.join(out, "index.json"), "w"), indent=1)
open(os.path.join(out, ".nojekyll"), "w").close()
print("indexed", [e["version"] for e in engines])
