"""Writes the engine site that Cloudflare serves at engines.renplay.org.

    GITHUB_REPOSITORY=renplay-org/engines python3 scripts/site.py site

Each release's files are downloaded through the GitHub API, checked against the release's
manifest.json, and placed in site/<version>/. index.json lists them there, so Renplay downloads
its engines from engines.renplay.org: the releases on GitHub stay the archive they come from, and
a GitHub outage can delay publishing a version but never an install.
"""
import hashlib, json, os, subprocess, sys

repo = os.environ["GITHUB_REPOSITORY"]
out = sys.argv[1]
base = os.environ.get("ENGINES_URL", "https://engines.renplay.org").rstrip("/")


def gh(*args):
    return subprocess.check_output(["gh", *args])


releases = [r for page in json.loads(gh("api", f"repos/{repo}/releases", "--paginate", "--slurp")) for r in page]
engines = []
for rel in releases:
    tag = rel["tag_name"]
    if not tag.startswith("renpy-") or rel.get("draft") or not any(a["name"] == "manifest.json" for a in rel["assets"]):
        continue
    folder = os.path.join(out, tag.removeprefix("renpy-"))
    gh("release", "download", tag, "--repo", repo, "--dir", folder, "--clobber")
    manifest = json.load(open(os.path.join(folder, "manifest.json")))
    if manifest["version"] != tag.removeprefix("renpy-"):
        raise SystemExit(f"{tag} holds the manifest of {manifest['version']}")
    files = {}
    for name, meta in manifest["files"].items():
        data = open(os.path.join(folder, name), "rb").read()
        if len(data) != meta["size"] or hashlib.sha256(data).hexdigest() != meta["sha256"]:
            raise SystemExit(f"{tag}/{name} does not match its manifest")
        files[name] = dict(meta, url=f"{base}/{manifest['version']}/{name}")
    engines.append({"version": manifest["version"], "renpy": manifest["renpy"], "python": manifest["python"], "files": files})


def key(e):
    return tuple(int(p) for p in e["version"].split("."))


engines.sort(key=key, reverse=True)
os.makedirs(out, exist_ok=True)
json.dump({"schema": 1, "engines": engines}, open(os.path.join(out, "index.json"), "w"), indent=1)
# Cloudflare reads these. A version's files never change, so browsers and Renplay may keep them.
headers = "/*\n  Access-Control-Allow-Origin: *\n  X-Content-Type-Options: nosniff\n/index.json\n  Cache-Control: public, max-age=300\n"
for e in engines:
    headers += f"/{e['version']}/*\n  Cache-Control: public, max-age=31536000, immutable\n"
open(os.path.join(out, "_headers"), "w").write(headers)
# Files are served at exactly their paths (wrangler.jsonc), so the address itself goes to Renplay.
open(os.path.join(out, "_redirects"), "w").write("/ https://renplay.org 302\n")
open(os.path.join(out, "index.html"), "w").write(
    '<!doctype html>\n<meta charset="utf-8">\n<title>Renplay engines</title>\n<meta name="robots" content="noindex">\n'
    '<meta http-equiv="refresh" content="0; url=https://renplay.org">\n'
    '<p>This is where Renplay finds its Ren\u2019Py web engines (<a href="index.json">index.json</a>). '
    'Renplay itself is at <a href="https://renplay.org">renplay.org</a>.</p>\n'
)
print("published", [e["version"] for e in engines])
