#!/usr/bin/env node

import { copyFileSync, existsSync, mkdirSync, readdirSync, statSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const source = join(repo, 'news2trading')
const args = parseArgs(process.argv.slice(2))
const runtimeFiles = {
	openclaw: {
		skill: join(source, 'SKILL.md'),
		publish: join(source, 'scripts', 'publish.py'),
	},
	hermes: {
		skill: join(source, 'runtime-variants', 'hermes', 'SKILL.md'),
		publish: join(source, 'runtime-variants', 'hermes', 'scripts', 'publish.py'),
	},
}

if (!runtimeFiles[args.runtime]) fail('runtime must be openclaw or hermes')
const output = resolve(args.output)
if (existsSync(output) && readdirSync(output).length > 0) {
	fail('output directory must be absent or empty')
}

const manifest = [
	[runtimeFiles[args.runtime].skill, 'SKILL.md'],
	[join(source, 'references', 'news-impact-analysis.md'), join('references', 'news-impact-analysis.md')],
	[join(source, 'references', 'profile-api.md'), join('references', 'profile-api.md')],
	[join(source, 'references', 'profile-intent.md'), join('references', 'profile-intent.md')],
	[join(source, 'scripts', 'news_client.py'), join('scripts', 'news_client.py')],
	[join(source, 'scripts', 'profile.py'), join('scripts', 'profile.py')],
	[runtimeFiles[args.runtime].publish, join('scripts', 'publish.py')],
]

for (const [input] of manifest) {
	if (!existsSync(input) || !statSync(input).isFile()) fail(`required source is missing: ${input}`)
}
mkdirSync(output, { recursive: true })
for (const [input, relative] of manifest) {
	const destination = join(output, relative)
	mkdirSync(dirname(destination), { recursive: true })
	copyFileSync(input, destination)
}
process.stdout.write(`${output}\n`)

function parseArgs(argv) {
	const result = {}
	for (let index = 0; index < argv.length; index += 2) {
		const flag = argv[index]
		const value = argv[index + 1]
		if (!value || (flag !== '--runtime' && flag !== '--output')) fail('usage: --runtime RUNTIME --output DIRECTORY')
		if (result[flag.slice(2)]) fail(`duplicate argument: ${flag}`)
		result[flag.slice(2)] = value
	}
	if (!result.runtime || !result.output) fail('usage: --runtime RUNTIME --output DIRECTORY')
	return result
}

function fail(message) {
	process.stderr.write(`materialize-news2trading: ${message}\n`)
	process.exit(1)
}
