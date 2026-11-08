// Downloads every file an index lists, the way Renplay does (Node's fetch, taking whatever encoding
// the server offers), and checks its size and sha256, and that it is served at its own address. Run before an index
// is published, so it never names a file that does not arrive whole.
//
//   node scripts/verify.mjs site/index.json
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'

const index = JSON.parse(readFileSync(process.argv[2], 'utf8'))
let bad = 0
for (const engine of index.engines) {
  for (const [name, file] of Object.entries(engine.files)) {
    const res = await fetch(file.url, { redirect: 'follow', cache: 'no-store' })
    const data = Buffer.from(await res.arrayBuffer())
    const sha = createHash('sha256').update(data).digest('hex')
    const ok = res.ok && !res.redirected && data.length === file.size && sha === file.sha256
    if (!ok) bad++
    console.log(`${ok ? 'ok  ' : 'BAD '} ${engine.version}/${name} ${res.status} ${data.length} bytes${res.redirected ? `, redirected to ${new URL(res.url).origin}` : ''}${res.headers.get('content-encoding') ? `, ${res.headers.get('content-encoding')}` : ''}`)
  }
}
if (bad) {
  console.error(`${bad} file(s) do not arrive as the index says`)
  process.exit(1)
}
