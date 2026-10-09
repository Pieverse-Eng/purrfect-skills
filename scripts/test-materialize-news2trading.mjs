import assert from 'node:assert/strict'
import { execFileSync, spawnSync } from 'node:child_process'
import { mkdtempSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const script = join(repo, 'scripts', 'materialize-news2trading.mjs')

function filesBelow(root, prefix = '') {
	return readdirSync(join(root, prefix), { withFileTypes: true }).flatMap((entry) => {
		const relative = join(prefix, entry.name)
		return entry.isDirectory() ? filesBelow(root, relative) : [relative]
	})
}

for (const runtime of ['openclaw', 'hermes']) {
	test(`materializes a complete ${runtime} news2trading package`, () => {
		const parent = mkdtempSync(join(tmpdir(), `news2trading-${runtime}-`))
		const output = join(parent, 'news2trading')
		execFileSync(process.execPath, [script, '--runtime', runtime, '--output', output], {
			cwd: repo,
			stdio: 'pipe',
		})

		assert.deepEqual(filesBelow(output).sort(), [
			'SKILL.md',
			join('references', 'news-impact-analysis.md'),
			join('references', 'profile-api.md'),
			join('references', 'profile-intent.md'),
			join('scripts', 'news_client.py'),
			join('scripts', 'profile.py'),
			join('scripts', 'publish.py'),
		].sort())
		const skill = readFileSync(join(output, 'SKILL.md'), 'utf8')
		assert.match(skill, /^---\nname: news2trading\n/m)
		assert.doesNotMatch(skill, /runtime-variants/)
		assert.match(skill, /Read-only\s+market-data tools are allowed/)
		assert.match(skill, /Do not invoke trading tools or account-changing operations/)
		assert.match(skill, /When the user explicitly asks, deepen market, background and scenario analysis/)
		const analysis = readFileSync(join(output, 'references', 'news-impact-analysis.md'), 'utf8')
		assert.match(analysis, /Observed market prices and historical levels are evidence/)
		assert.match(analysis, /observation\s+time and comparison window/)
		assert.doesNotMatch(`${skill}\n${analysis}`, /without market\/trading tools|invokes market\/trading tools/)
		// Check active-mode rules in their own sections: background NO_REPLY rules
		// must not accidentally satisfy (or override) this ordinary-chat contract.
		const activeSkill = skill.match(/^## Active holdings-news analysis\n([\s\S]*?)^## /m)?.[1]?.replace(/\s+/g, ' ')
		const activeAnalysis = analysis.match(/^## Active holdings-news report\n([\s\S]*?)^## /m)?.[1]?.replace(/\s+/g, ' ')
		assert.ok(activeSkill, 'The runtime artifact must retain active holdings-news mode')
		assert.ok(activeAnalysis, 'The shared reference must retain active holdings-news mode')
		assert.match(activeSkill, /explicit user request/)
		assert.match(activeSkill, /Opening or refreshing a page.*never consent/)
		assert.match(activeSkill, /Cover every supplied asset/)
		assert.match(activeSkill, /missing news, omitted evidence, unsupported identities and failed\/stale\/uncollected sources explicit/)
		assert.match(activeSkill, /Return a normal readable assistant report/)
		assert.match(activeSkill, /Never return only `NO_REPLY` for this active request/)
		assert.match(activeSkill, /Do not use `profile\.py` or `publish\.py`, create a subscription\/Topic/)
		assert.match(activeSkill, /perform extra searches, push Telegram\/LINE, or prepare\/execute trades/)
		assert.match(activeAnalysis, /Use only supplied PANews\/CoinDesk\/Cointelegraph materials/)
		assert.match(activeAnalysis, /For each asset, explain the event/)
		assert.match(activeAnalysis, /changing long\/short exposure must not reverse the assessment/)
		assert.match(activeAnalysis, /Disclose failed\/stale\/uncollected sources and evidence omitted/)
		assert.match(activeAnalysis, /No-data requests still receive an explicit answer, never only `NO_REPLY`/)
		assert.match(activeAnalysis, /Do not invoke the Profile or batch publisher, create a Topic\/subscription/)
		assert.match(activeAnalysis, /search extra sources, send Telegram\/LINE, prepare an order, or execute trades/)
		assert.match(activeAnalysis, /`NO_REPLY` rules below apply to background delivery batches/)
		if (runtime === 'hermes') {
			// Hermes skill_utils.extract_skill_description displays at most 60 characters.
			const description = skill.match(/^description: (.+)$/m)?.[1]
			assert.ok(description)
			const visible = description.length > 60 ? `${description.slice(0, 57)}...` : description
			assert.match(visible, /Pawpilot/i)
			assert.match(visible, /news/i)
			assert.match(visible, /settings|preferences|frequency/i)
			assert.match(visible, /batch/i)
		}
		for (const reference of skill.matchAll(/\]\((references\/[^)]+)\)/g)) {
			assert.doesNotThrow(() => readFileSync(join(output, reference[1])))
		}
		const help = spawnSync('python3', [join(output, 'scripts', 'publish.py'), '--help'], {
			encoding: 'utf8',
		})
		assert.equal(help.status, 0, help.stderr)
		assert.match(help.stdout, /--batch-id/)
		assert.match(help.stdout, /--text-file/)
		assert.doesNotMatch(help.stdout, /--runtime|--recipient|--base-url|--token/)
		const profileHelp = spawnSync('python3', [join(output, 'scripts', 'profile.py'), '--help'], {
			encoding: 'utf8',
		})
		assert.equal(profileHelp.status, 0, profileHelp.stderr)
		assert.match(profileHelp.stdout, /get,.*create,.*update,.*pause,.*resume/)
		const invalidIdentity = spawnSync('python3', [join(output, 'scripts', 'profile.py'), 'get'], {
			encoding: 'utf8', env: { ...process.env, WALLET_API_TOKEN: '' },
		})
		assert.notEqual(invalidIdentity.status, 0)
		assert.equal(JSON.parse(invalidIdentity.stdout).code, 'invalid_hosted_identity')
	})
}

test('Profile API JSON examples use routable event identifiers in requests and responses', () => {
	const reference = readFileSync(join(repo, 'news2trading', 'references', 'profile-api.md'), 'utf8')
	// These are the public V1 Collector event identifiers, not presentation labels.
	const events = new Set([
		'listing_delisting', 'funding_investment', 'partnership_launch',
		'exploit_security', 'regulation_legal', 'etf_flow', 'token_unlock_burn',
		'buyback', 'liquidation', 'macro_data',
	])
	let checked = 0
	for (const [, json] of reference.matchAll(/```json\n([\s\S]*?)\n```/g)) {
		const body = JSON.parse(json)
		const profile = body.data ?? body
		for (const term of [...(profile.includeTerms ?? []), ...(profile.excludeTerms ?? [])]) {
			if (term.type !== 'event_type') continue
			const value = term.value ?? term.normalizedValue
			assert.ok(events.has(value), `Unroutable event identifier in API example: ${value}`)
			checked += 1
		}
	}
	assert.ok(checked >= 2, 'Exercise canonical routing terms in onboarding changes')
})

test('refuses to materialize over a non-empty directory', () => {
	const parent = mkdtempSync(join(tmpdir(), 'news2trading-nonempty-'))
	const output = join(parent, 'news2trading')
	mkdirSync(output)
	writeFileSync(join(output, 'keep.txt'), 'keep')
	const result = spawnSync(
		process.execPath,
		[script, '--runtime', 'openclaw', '--output', output],
		{ cwd: repo, encoding: 'utf8' },
	)
	assert.notEqual(result.status, 0)
	assert.equal(readFileSync(join(output, 'keep.txt'), 'utf8'), 'keep')
})
