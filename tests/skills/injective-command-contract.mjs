// Execute authored examples through the actual CLI against a loopback fixture API.
// Usage: node tests/skills/injective-command-contract.mjs /path/to/cli-entry.ts /path/to/bun
import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { readFile } from 'node:fs/promises'
import { createServer } from 'node:http'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const [entry, bun] = process.argv.slice(2)
assert.ok(entry && bun, 'Pass an actual purr CLI source entry and Bun executable')
const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const hash = `0x${'1'.repeat(64)}`
const calls = []
const server = createServer((request, response) => {
	calls.push({ method: request.method, url: request.url })
	const url = new URL(request.url, 'http://fixture')
	let data = { identity: null, component: { data: [], meta: { status: 'fresh' } }, nextCursor: null }
	if (url.pathname.endsWith('/instruments')) {
		const product = url.searchParams.get('product') ?? 'perp'
		data = {
			identity: { venue: 'injective', environment: 'mainnet' },
			data: [{ id: `injective:${product}:${hash}`, nativeMarketId: hash, venue: 'injective', environment: 'mainnet', product, base: 'BTC' }],
			meta: { status: 'fresh' }, missing: [],
		}
	} else if (url.pathname.endsWith('/status') || url.pathname.endsWith('/account')) {
		data = { mode: 'read_only', executionEnabled: false, identity: null }
	} else if (url.pathname.endsWith('/candles')) {
		data = { candles: [], historyAvailability: 'partial' }
	}
	response.writeHead(200, { 'Content-Type': 'application/json' })
	response.end(JSON.stringify({ ok: true, data }))
})
await new Promise((done) => server.listen(0, '127.0.0.1', done))
try {
	const api = `http://127.0.0.1:${server.address().port}`
	const env = { ...process.env, WALLET_API_URL: api, WALLET_API_TOKEN: 'fixture', INSTANCE_ID: 'owned-fixture', NO_PROXY: '*', no_proxy: '*' }
	for (const key of ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy', 'FX_PLATFORM_QUOTE_TOKEN', 'FX_PLATFORM_UNISWAP_QUOTE_URL', 'FX_PLATFORM_DFLOW_QUOTE_URL']) delete env[key]
	let checked = 0
	for (const file of ['SKILL.md', 'references/market-data.md', 'references/account.md', 'references/errors.md']) {
		const content = await readFile(resolve(root, 'injective', file), 'utf8')
		for (const block of content.matchAll(/```sh\n([\s\S]*?)```/g)) {
			for (const line of block[1].trim().split('\n')) {
				assert.ok(line.startsWith('purr injective '), `Unsupported example: ${line}`)
				const tokens = line.match(/"[^"]*"|'[^']*'|\S+/g).slice(1).map((token) => token.replace(/^(["'])(.*)\1$/, '$2').replaceAll('$MARKET_HASH', hash).replaceAll('$NEXT_CURSOR', 'fixture-cursor'))
				const result = await new Promise((done, reject) => {
					const child = spawn(bun, [resolve(entry), ...tokens], { cwd: dirname(resolve(entry)), env, stdio: ['ignore', 'pipe', 'pipe'] })
					let stderr = ''
					child.stderr.on('data', (chunk) => { stderr += chunk })
					child.stdout.resume()
					child.on('error', reject)
					child.on('close', (code) => done({ code, stderr }))
				})
				assert.equal(result.code, 0, `${file}: ${line}: ${result.stderr}`)
				checked++
			}
		}
	}
	assert.ok(checked >= 12 && calls.length > 0, 'Examples must exercise actual read commands')
	assert.ok(calls.every((call) => call.method === 'GET'), 'Authored examples must only send GET')
	console.log(`Validated ${checked} authored examples through the actual CLI; ${calls.length} loopback GETs, no writes.`)
} finally {
	await new Promise((done) => server.close(done))
}
