// Execute every authored shell example through the real CLI against strict loopback fixtures.
// Binary: PURR_TEST_BINARY=/path/to/purr node tests/skills/injective-command-contract.mjs
// Source: node tests/skills/injective-command-contract.mjs /path/to/cli-entry.ts /path/to/bun
import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { mkdtemp, readFile, rm } from 'node:fs/promises'
import { createServer } from 'node:http'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { fixtures, hash, nextCursor } from './injective-fixtures.mjs'

const [entry, bun] = process.argv.slice(2)
const binary = process.env.PURR_TEST_BINARY
assert.ok(
	binary || (entry && bun),
	'Set PURR_TEST_BINARY or pass a CLI source entry and Bun executable',
)
const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const catalogPath = '/v1/market-data/reference/terminal/instruments'
const accountPath = '/v1/instances/owned-fixture/injective'
const exactQuery = {
	venue: 'injective',
	environment: 'mainnet',
	product: 'perp',
	ids: `injective:perp:${hash}`,
}
const catalogRead = { path: catalogPath, query: exactQuery, data: fixtures.exactCatalog }
const marketArgs = ['--market-id', hash, '--market-type', 'perp']
const historyArgs = [
	'--start-at',
	'2026-10-01T00:00:00Z',
	'--end-at',
	'2026-10-02T00:00:00Z',
	'--limit',
	'50',
]
const historyQuery = { product: 'perp', limit: '50', from: '1790812800000', to: '1790899200000' }
const cases = [
	{ args: ['--help'], help: true, requests: [] },
	{
		args: ['markets', '--market-type', 'all'],
		data: fixtures.catalog,
		requests: [
			{
				path: catalogPath,
				query: { venue: 'injective', environment: 'mainnet' },
				data: fixtures.catalog,
			},
		],
	},
	{ args: ['market', ...marketArgs], data: fixtures.exactCatalog, requests: [catalogRead] },
	{
		args: ['order-book-depth', ...marketArgs, '--limit', '20'],
		data: fixtures.book,
		requests: [
			catalogRead,
			{
				path: '/v1/market-data/orderbook',
				query: { underlying: 'BTC', instrumentId: `injective:perp:${hash}`, levels: '20' },
				data: fixtures.book,
			},
		],
	},
	{
		args: ['recent-trades', ...marketArgs, '--limit', '50'],
		data: fixtures.trades,
		requests: [
			catalogRead,
			{
				path: '/v1/market-data/trades',
				query: { underlying: 'BTC', instrumentId: `injective:perp:${hash}`, limit: '50' },
				data: fixtures.trades,
			},
		],
	},
	{
		args: [
			'candles',
			...marketArgs,
			'--resolution',
			'1h',
			'--start-at',
			'2026-10-01T00:00:00Z',
			'--end-at',
			'2026-10-02T00:00:00Z',
		],
		data: { ...fixtures.candles, candles: fixtures.candles.candles.slice(1, 3) },
		requests: [
			catalogRead,
			{
				path: '/v1/market-data/candles',
				query: {
					underlying: 'BTC',
					instrumentId: `injective:perp:${hash}`,
					tf: '1h',
					to: '1790899200000',
					limit: '24',
				},
				data: fixtures.candles,
			},
		],
	},
	...['status', 'account', 'balances'].map((command) => ({
		args: [command],
		data: fixtures[command],
		requests: [{ path: `${accountPath}/${command}`, query: {}, data: fixtures[command] }],
	})),
	{
		args: ['positions', '--market-type', 'perp', '--limit', '50'],
		data: fixtures.positions,
		requests: [
			{
				path: `${accountPath}/positions`,
				query: { product: 'perp', limit: '50' },
				data: fixtures.positions,
			},
		],
	},
	{
		args: ['orders', '--market-type', 'spot', '--limit', '50'],
		data: fixtures.orders,
		requests: [
			{
				path: `${accountPath}/orders`,
				query: { product: 'spot', limit: '50' },
				data: fixtures.orders,
			},
		],
	},
	...['order-history', 'fills'].map((command) => ({
		args: [command, '--market-type', 'perp', '--limit', '50'],
		data: fixtures[command],
		requests: [
			{
				path: `${accountPath}/${command}`,
				query: { product: 'perp', limit: '50' },
				data: fixtures[command],
			},
		],
	})),
	{
		args: ['fills', '--market-type', 'perp', ...historyArgs],
		data: fixtures.fills,
		requests: [{ path: `${accountPath}/fills`, query: historyQuery, data: fixtures.fills }],
	},
	{
		args: ['fills', '--market-type', 'perp', ...historyArgs, '--cursor', nextCursor],
		data: fixtures.unavailablePage,
		requests: [
			{
				path: `${accountPath}/fills`,
				query: { ...historyQuery, cursor: nextCursor },
				data: fixtures.unavailablePage,
			},
		],
	},
]

let active
let totalRequests = 0
const server = createServer((request, response) => {
	totalRequests++
	try {
		assert.ok(active, 'HTTP outside an active command')
		const expected = active.requests[active.received++]
		assert.ok(expected, `Unexpected HTTP: ${request.method} ${request.url}`)
		assert.equal(request.method, 'GET', 'Read examples must use GET')
		assert.equal(
			request.headers.authorization,
			'Bearer fixture-token',
			'Platform API authentication',
		)
		const url = new URL(request.url, 'http://fixture')
		assert.equal(url.pathname, expected.path, 'Exact backend route')
		assert.deepEqual(
			[...url.searchParams].sort(),
			Object.entries(expected.query).sort(),
			'Exact query, including duplicates and cursor encoding',
		)
		response.writeHead(expected.status ?? 200, {
			'Content-Type': 'application/json',
			...expected.headers,
		})
		response.end(JSON.stringify(expected.body ?? { ok: true, data: expected.data }))
	} catch (error) {
		if (active) active.failure ??= error
		response.writeHead(500, { 'Content-Type': 'application/json' })
		response.end(JSON.stringify({ ok: false, error: { code: 'UNEXPECTED_FIXTURE_REQUEST' } }))
	}
})
const home = await mkdtemp(join(tmpdir(), 'injective-skill-contract-'))
await new Promise((done) => server.listen(0, '127.0.0.1', done))

try {
	const api = `http://127.0.0.1:${server.address().port}`
	const env = {
		...process.env,
		HOME: home,
		WALLET_API_URL: api,
		WALLET_API_TOKEN: 'fixture-token',
		INSTANCE_ID: 'owned-fixture',
		NO_PROXY: '*',
		no_proxy: '*',
	}
	for (const key of [
		'HTTP_PROXY',
		'HTTPS_PROXY',
		'ALL_PROXY',
		'http_proxy',
		'https_proxy',
		'all_proxy',
		'FX_PLATFORM_QUOTE_TOKEN',
		'FX_PLATFORM_UNISWAP_QUOTE_URL',
		'FX_PLATFORM_DFLOW_QUOTE_URL',
	])
		delete env[key]
	async function run(testCase, label) {
		active = { ...testCase, received: 0 }
		const result = await new Promise((done, reject) => {
			const child = spawn(
				binary ? resolve(binary) : bun,
				binary ? ['injective', ...testCase.args] : [resolve(entry), 'injective', ...testCase.args],
				{
					cwd: binary ? root : dirname(resolve(entry)),
					env,
					stdio: ['ignore', 'pipe', 'pipe'],
					timeout: 10_000,
				},
			)
			let stdout = ''
			let stderr = ''
			child.stdout.on('data', (chunk) => {
				stdout += chunk
			})
			child.stderr.on('data', (chunk) => {
				stderr += chunk
			})
			child.on('error', reject)
			child.on('close', (code, signal) =>
				done({ code, signal, stdout: stdout.trim(), stderr: stderr.trim() }),
			)
		})
		if (active.failure)
			throw new Error(`${label}: ${active.failure.message}`, { cause: active.failure })
		assert.equal(active.received, testCase.requests.length, `${label}: expected HTTP requests`)
		assert.equal(result.signal, null, `${label}: CLI exceeded its deadline`)
		assert.equal(result.code, testCase.error ? 1 : 0, `${label}: ${result.stderr}`)
		if (testCase.error) {
			assert.equal(result.stdout, '', `${label}: errors must not print success JSON`)
			for (const pattern of testCase.error) assert.match(result.stderr, pattern, label)
		} else {
			assert.equal(result.stderr, '', `${label}: unexpected stderr`)
			if (testCase.help) {
				assert.match(result.stdout, /^Usage: purr injective/)
				assert.match(result.stdout, /Read-only Injective mainnet/)
			} else {
				assert.deepEqual(
					JSON.parse(result.stdout),
					testCase.data,
					`${label}: output must preserve amounts, identity, freshness and coverage`,
				)
			}
		}
		active = undefined
	}
	const remaining = new Map(cases.map((testCase) => [JSON.stringify(testCase.args), testCase]))
	let checked = 0
	for (const file of [
		'SKILL.md',
		'references/market-data.md',
		'references/account.md',
		'references/errors.md',
	]) {
		const content = await readFile(resolve(root, 'injective', file), 'utf8')
		for (const block of content.matchAll(/```sh\n([\s\S]*?)```/g)) {
			for (const line of block[1].trim().split('\n')) {
				assert.ok(line.startsWith('purr injective '), `Unsupported example: ${line}`)
				const args = line
					.match(/"[^"]*"|'[^']*'|\S+/g)
					.slice(2)
					.map((token) =>
						token
							.replace(/^(["'])(.*)\1$/, '$2')
							.replaceAll('$MARKET_HASH', hash)
							.replaceAll('$NEXT_CURSOR', nextCursor),
					)
				const key = JSON.stringify(args)
				const testCase = remaining.get(key)
				assert.ok(testCase, `Add an explicit request/output fixture for ${file}: ${line}`)
				await run(testCase, `${file}: ${line}`)
				remaining.delete(key)
				checked++
			}
		}
	}
	assert.equal(remaining.size, 0, 'All fixtures must correspond to authored examples')
	await run(
		{
			args: ['status'],
			requests: [
				{
					path: `${accountPath}/status`,
					query: {},
					status: 429,
					headers: { 'Retry-After': '3' },
					body: {
						ok: false,
						error: { code: 'INJECTIVE_RATE_LIMITED', reason: 'rate_limited', retryAfterMs: 1250 },
					},
				},
			],
			error: [
				/error \[INJECTIVE_RATE_LIMITED\]/,
				/"reason": "rate_limited"/,
				/"retryAfterMs": 1250/,
				/"retryAfter": "3"/,
			],
		},
		'Rate-limit response stays an error with retry metadata and no retry',
	)
	await run(
		{ args: ['cancel'], requests: [], error: [/error \[INJECTIVE_READ_ONLY\]/] },
		'Execution stays unavailable without HTTP',
	)
	console.log(
		`Validated all ${checked} authored examples plus 2 error boundaries through the actual CLI; ${totalRequests} authenticated loopback GETs, no writes.`,
	)
} finally {
	server.closeAllConnections()
	await new Promise((done) => server.close(done))
	await rm(home, { recursive: true, force: true })
}
