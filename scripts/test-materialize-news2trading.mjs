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
			join('scripts', 'news_client.py'),
			join('scripts', 'publish.py'),
		].sort())
		const skill = readFileSync(join(output, 'SKILL.md'), 'utf8')
		assert.match(skill, /^---\nname: news2trading\n/m)
		assert.doesNotMatch(skill, /runtime-variants/)
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
	})
}

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
