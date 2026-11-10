"""Writes the engine site that Cloudflare serves at engines.renplay.org.

    GITHUB_REPOSITORY=renplay-org/engines python3 scripts/site.py site

Each release's files are downloaded through the GitHub API, checked against the release's
manifest.json, and placed in site/<version>/. index.json lists them there (pre-releases apart, under "prereleases"), so Renplay downloads
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


def prereleases():
    """Versions that versions.txt marks as pre-releases, such as "8.6.0 prerelease"."""
    found = set()
    for line in open(os.path.join(os.path.dirname(__file__), "..", "versions.txt")):
        words = line.split("#")[0].split()
        if len(words) > 1 and words[1] == "prerelease":
            found.add(words[0])
    return found


def key(e):
    return tuple(int(p) for p in e["version"].split("."))


engines.sort(key=key, reverse=True)
# Pre-releases are listed apart: Renplay 4.6.3 and older read only "engines" and build a game without a
# recipe on the newest engine there, which must never be a pre-release. Newer Renplay reads both lists.
pre = prereleases()
stable = [e for e in engines if e["version"] not in pre]
early = [dict(e, prerelease=True) for e in engines if e["version"] in pre]
os.makedirs(out, exist_ok=True)
json.dump({"schema": 1, "engines": stable, "prereleases": early}, open(os.path.join(out, "index.json"), "w"), indent=1)
# Cloudflare reads these. A version's files never change, so browsers and Renplay may keep them.
headers = "/*\n  Access-Control-Allow-Origin: *\n  X-Content-Type-Options: nosniff\n  X-Robots-Tag: noindex\n/index.json\n  Cache-Control: public, max-age=300\n"
for e in engines:
    headers += f"/{e['version']}/*\n  Cache-Control: public, max-age=31536000, immutable\n"
open(os.path.join(out, "_headers"), "w").write(headers)
# Files are served at exactly their paths (wrangler.jsonc), so the address itself is rewritten to a small
# page that says what this host is. Search engines are kept away (robots.txt, X-Robots-Tag).
open(os.path.join(out, "_redirects"), "w").write("/ /index.html 200\n")
open(os.path.join(out, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
items = "".join(f'<li>Ren\u2019Py {e["version"]}{" (pre-release)" if e["version"] in pre else ""}</li>' for e in engines)
open(os.path.join(out, "index.html"), "w").write(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Renplay engines</title>
<meta name="description" content="The Ren\u2019Py web engines Renplay plays games with.">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#0a0a0f">
<link rel="icon" href="https://renplay.org/logo.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="https://renplay.org/logo.png">
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; background: #0a0a0f; color: #e8e6ef; font: 16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 34rem; padding: 32px 24px; }}
  .brand {{ display: flex; align-items: center; gap: 12px; color: inherit; text-decoration: none; font-weight: 700; font-size: 20px; }}
  .brand img {{ width: 40px; height: 40px; }}
  h1 {{ font-size: 28px; line-height: 1.25; margin: 28px 0 12px; }}
  p {{ color: #b6b2c4; margin: 0 0 16px; }}
  ol {{ color: #b6b2c4; margin: 0 0 8px; padding-left: 20px; }}
  ul {{ list-style: none; padding: 0; margin: 24px 0 0; display: grid; gap: 10px; }}
  a {{ color: #ff7ab8; }}
  ul a {{ display: block; padding: 14px 16px; border: 1px solid rgb(255 255 255 / .1); border-radius: 14px; background: rgb(255 255 255 / .03); text-decoration: none; color: #e8e6ef; }}
  ul a span {{ display: block; color: #8f8aa3; font-size: 14px; }}
  ul a:hover, ul a:focus-visible {{ border-color: #ff7ab8; }}
</style>
</head>
<body>
<main>
  <a class="brand" href="https://renplay.org"><img src="https://renplay.org/logo.svg" alt="" width="40" height="40">Renplay</a>
  <h1>The engines Renplay plays games with</h1>
  <p>Renplay builds each game for the web with an official Ren\u2019Py web engine, repackaged here. An installation downloads the engine a game needs, once.</p>
  <ol>{items}</ol>
  <ul>
    <li><a href="https://docs.renplay.org/engines/">How Renplay picks an engine<span>docs.renplay.org</span></a></li>
    <li><a href="https://github.com/renplay-org/engines">The repository<span>How the engines are packaged and checked</span></a></li>
    <li><a href="/index.json">The index<span>What Renplay reads, as JSON</span></a></li>
  </ul>
</main>
</body>
</html>
""")
print("published", [e["version"] for e in engines])
