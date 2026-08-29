#!/usr/bin/env node

function requiredEnv(name) {
	const value = process.env[name]?.trim()
	if (!value) throw new Error(`Missing required environment variable: ${name}`)
	return value
}

function trustedWakeContext() {
	const runtimeKind = requiredEnv('PURRFECT_NEWS_RUNTIME_KIND')
	const runtimeRunId = requiredEnv('PURRFECT_NEWS_RUNTIME_RUN_ID')
	const activationEpoch = Number(requiredEnv('PURRFECT_NEWS_ACTIVATION_EPOCH'))
	if (!Number.isSafeInteger(activationEpoch) || activationEpoch < 0) {
		throw new Error('PURRFECT_NEWS_ACTIVATION_EPOCH must be a non-negative integer')
	}
	return {
		wakeAttemptId: requiredEnv('PURRFECT_NEWS_WAKE_ATTEMPT_ID'),
		claimantId: `${runtimeKind}:${runtimeRunId}`,
		activationEpoch,
	}
}

async function requestJson(pathname, init) {
	const baseUrl = requiredEnv('WALLET_API_URL')
	const token = requiredEnv('WALLET_API_TOKEN')
	const response = await fetch(new URL(pathname, `${baseUrl.replace(/\/$/, '')}/`), {
		...init,
		headers: {
			accept: 'application/json',
			authorization: `Bearer ${token}`,
			'content-type': 'application/json',
			...init?.headers,
		},
		signal: AbortSignal.timeout(15_000),
	})
	const text = await response.text()
	let body
	try {
		body = text ? JSON.parse(text) : null
	} catch {
		body = text
	}
	if (!response.ok) {
		const code =
			typeof body === 'object' &&
			body !== null &&
			typeof body.code === 'string' &&
			/^[a-z0-9_]{1,64}$/i.test(body.code)
				? `: ${body.code}`
				: ''
		throw new Error(`News API request failed (${response.status})${code}`)
	}
	return body
}

function optionValue(name, { required = true } = {}) {
	const index = process.argv.indexOf(name)
	const value = index >= 0 ? process.argv[index + 1]?.trim() : undefined
	if (required && !value) throw new Error(`Missing required option: ${name}`)
	return value
}

async function main() {
	const command = process.argv[2]
	const instanceId = encodeURIComponent(requiredEnv('INSTANCE_ID'))
	let result
	if (command === 'pull') {
		const batchId = encodeURIComponent(requiredEnv('PURRFECT_NEWS_BATCH_ID'))
		result = await requestJson(`/v1/instances/${instanceId}/news/batches/${batchId}/pull`, {
			method: 'POST',
			body: JSON.stringify(trustedWakeContext()),
		})
	} else if (command === 'read') {
		const itemId = encodeURIComponent(optionValue('--item-id'))
		const versionId = optionValue('--version-id', { required: false })
		const query = versionId ? `?${new URLSearchParams({ versionId })}` : ''
		result = await requestJson(`/v1/instances/${instanceId}/news/items/${itemId}${query}`, { method: 'GET' })
	} else if (command === 'ack') {
		const batchId = encodeURIComponent(requiredEnv('PURRFECT_NEWS_BATCH_ID'))
		result = await requestJson(`/v1/instances/${instanceId}/news/batches/${batchId}/ack`, {
			method: 'POST',
			body: JSON.stringify({
				...trustedWakeContext(),
				claimToken: optionValue('--claim-token'),
				thinkingWorkId: optionValue('--thinking-work-id'),
			}),
		})
	} else {
		throw new Error(
			'Usage: news-client.mjs pull | read --item-id <id> [--version-id <id>] | ack --claim-token <token> --thinking-work-id <id>',
		)
	}
	process.stdout.write(`${JSON.stringify(result)}\n`)
}

main().catch((error) => {
	process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
	process.exitCode = 1
})
