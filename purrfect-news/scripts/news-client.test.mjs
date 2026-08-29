import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { once } from 'node:events'
import { createServer } from 'node:http'
import path from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

const scriptPath = path.join(path.dirname(fileURLToPath(import.meta.url)), 'news-client.mjs')

async function startServer(handler) {
	const server = createServer(handler)
	server.listen(0, '127.0.0.1')
	await once(server, 'listening')
	const address = server.address()
	return {
		baseUrl: `http://127.0.0.1:${address.port}`,
		close: () => new Promise((resolve, reject) => server.close((error) => (error ? reject(error) : resolve()))),
	}
}

async function runClient(args, env) {
	const child = spawn(process.execPath, [scriptPath, ...args], {
		env: { ...process.env, ...env },
		stdio: ['ignore', 'pipe', 'pipe'],
	})
	let stdout = ''
	let stderr = ''
	child.stdout.setEncoding('utf8').on('data', (chunk) => (stdout += chunk))
	child.stderr.setEncoding('utf8').on('data', (chunk) => (stderr += chunk))
	const [exitCode] = await once(child, 'exit')
	return { exitCode, stdout, stderr }
}

test('pull claims the trusted wake context through the Instance-authenticated API', async () => {
	let received
	const server = await startServer(async (request, response) => {
		let body = ''
		for await (const chunk of request) body += chunk
		received = {
			method: request.method,
			url: request.url,
			authorization: request.headers.authorization,
			body: JSON.parse(body),
		}
		response.writeHead(200, { 'content-type': 'application/json' })
		response.end(JSON.stringify({ status: 'claimed', cards: [{ itemId: 'news-1' }] }))
	})

	try {
		const result = await runClient(['pull'], {
			WALLET_API_URL: server.baseUrl,
			WALLET_API_TOKEN: 'instance-secret',
			INSTANCE_ID: 'instance/one',
			PURRFECT_NEWS_RUNTIME_KIND: 'openclaw',
			PURRFECT_NEWS_RUNTIME_RUN_ID: 'run-123',
			PURRFECT_NEWS_BATCH_ID: 'batch one',
			PURRFECT_NEWS_WAKE_ATTEMPT_ID: 'wake-456',
			PURRFECT_NEWS_ACTIVATION_EPOCH: '7',
		})

		assert.equal(result.exitCode, 0, result.stderr)
		assert.deepEqual(JSON.parse(result.stdout), {
			status: 'claimed',
			cards: [{ itemId: 'news-1' }],
		})
		assert.deepEqual(received, {
			method: 'POST',
			url: '/v1/instances/instance%2Fone/news/batches/batch%20one/pull',
			authorization: 'Bearer instance-secret',
			body: {
				wakeAttemptId: 'wake-456',
				claimantId: 'openclaw:run-123',
				activationEpoch: 7,
			},
		})
	} finally {
		await server.close()
	}
})

test('read fetches one immutable item version without requiring wake context', async () => {
	let received
	const server = await startServer((request, response) => {
		received = {
			method: request.method,
			url: request.url,
			authorization: request.headers.authorization,
		}
		response.writeHead(200, { 'content-type': 'application/json' })
		response.end(JSON.stringify({ itemId: 'item/1', versionId: 'version 2', content: 'article' }))
	})

	try {
		const result = await runClient(['read', '--item-id', 'item/1', '--version-id', 'version 2'], {
			WALLET_API_URL: server.baseUrl,
			WALLET_API_TOKEN: 'instance-secret',
			INSTANCE_ID: 'instance/one',
		})

		assert.equal(result.exitCode, 0, result.stderr)
		assert.deepEqual(JSON.parse(result.stdout), {
			itemId: 'item/1',
			versionId: 'version 2',
			content: 'article',
		})
		assert.deepEqual(received, {
			method: 'GET',
			url: '/v1/instances/instance%2Fone/news/items/item%2F1?versionId=version+2',
			authorization: 'Bearer instance-secret',
		})
	} finally {
		await server.close()
	}
})

test('ack binds durable Thinking work to the same trusted claimant', async () => {
	let received
	const server = await startServer(async (request, response) => {
		let body = ''
		for await (const chunk of request) body += chunk
		received = {
			method: request.method,
			url: request.url,
			body: JSON.parse(body),
		}
		response.writeHead(200, { 'content-type': 'application/json' })
		response.end(JSON.stringify({ status: 'acknowledged', thinkingWorkId: 'thinking-9' }))
	})

	try {
		const result = await runClient(
			['ack', '--claim-token', 'claim-secret', '--thinking-work-id', 'thinking-9'],
			{
				WALLET_API_URL: server.baseUrl,
				WALLET_API_TOKEN: 'instance-secret',
				INSTANCE_ID: 'instance-1',
				PURRFECT_NEWS_RUNTIME_KIND: 'hermes',
				PURRFECT_NEWS_RUNTIME_RUN_ID: 'run-789',
				PURRFECT_NEWS_BATCH_ID: 'batch-1',
				PURRFECT_NEWS_WAKE_ATTEMPT_ID: 'wake-2',
				PURRFECT_NEWS_ACTIVATION_EPOCH: '11',
			},
		)

		assert.equal(result.exitCode, 0, result.stderr)
		assert.deepEqual(JSON.parse(result.stdout), {
			status: 'acknowledged',
			thinkingWorkId: 'thinking-9',
		})
		assert.deepEqual(received, {
			method: 'POST',
			url: '/v1/instances/instance-1/news/batches/batch-1/ack',
			body: {
				wakeAttemptId: 'wake-2',
				claimantId: 'hermes:run-789',
				activationEpoch: 11,
				claimToken: 'claim-secret',
				thinkingWorkId: 'thinking-9',
			},
		})
	} finally {
		await server.close()
	}
})

test('API failures do not print Instance or claim credentials', async () => {
	const server = await startServer(async (request, response) => {
		let body = ''
		for await (const chunk of request) body += chunk
		response.writeHead(409, { 'content-type': 'application/json' })
		response.end(
			JSON.stringify({
				code: 'claim_token_mismatch',
				message: `rejected ${request.headers.authorization} ${JSON.parse(body).claimToken}`,
			}),
		)
	})

	try {
		const result = await runClient(
			['ack', '--claim-token', 'claim-secret', '--thinking-work-id', 'thinking-9'],
			{
				WALLET_API_URL: server.baseUrl,
				WALLET_API_TOKEN: 'instance-secret',
				INSTANCE_ID: 'instance-1',
				PURRFECT_NEWS_RUNTIME_KIND: 'hermes',
				PURRFECT_NEWS_RUNTIME_RUN_ID: 'run-789',
				PURRFECT_NEWS_BATCH_ID: 'batch-1',
				PURRFECT_NEWS_WAKE_ATTEMPT_ID: 'wake-2',
				PURRFECT_NEWS_ACTIVATION_EPOCH: '11',
			},
		)

		assert.equal(result.exitCode, 1)
		assert.match(result.stderr, /News API request failed \(409\)/)
		assert.doesNotMatch(result.stderr, /instance-secret|claim-secret/)
		assert.equal(result.stdout, '')
	} finally {
		await server.close()
	}
})
