import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { existsSync, mkdtempSync, rmSync, symlinkSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import test from 'node:test'

const helper = new URL('../../hyperliquid/scripts/order-size.mjs', import.meta.url)
const observed = {
	price: '2315.1',
	quantityStep: '0.0001',
	minimumNotional: '10',
	minimumQuantity: '0',
	leverage: '5',
	tradingFeeRate: '0.00045',
	routingFeeRate: '0.0005',
	slippageBps: '0',
}
const calculate = (input) => {
	assert.ok(existsSync(helper), 'A deterministic read-only sizing helper must be shipped')
	const result = spawnSync(process.execPath, [helper.pathname], {
		input: JSON.stringify(input), encoding: 'utf8', timeout: 5_000,
	})
	assert.equal(result.status, 0, result.stderr)
	return JSON.parse(result.stdout)
}

test('minimum quantity rounds upward to a legal native lot', () => {
	const result = calculate(observed)
	assert.equal(result.minimum.quantity, '0.0044')
	assert.equal(result.minimum.notional, '10.18644')
	assert.equal(result.maximum, null, 'No maximum capacity without authoritative collateral')
})

test('direct nonsecret JSON input needs no shell pipe or credential environment', () => {
	const result = spawnSync(process.execPath, [helper.pathname, '--input-json', JSON.stringify(observed)], {
		encoding: 'utf8', timeout: 5_000,
	})
	assert.equal(result.status, 0, result.stderr)
	assert.equal(JSON.parse(result.stdout).minimum.quantity, '0.0044')
})

test('a symlinked CLI entry point returns one JSON result', () => {
	const directory = mkdtempSync(join(tmpdir(), 'hyperliquid-order-size-'))
	try {
		const linked = join(directory, 'order-size.mjs')
		symlinkSync(fileURLToPath(helper), linked)
		const result = spawnSync(process.execPath, [linked, '--input-json', JSON.stringify(observed)], {
			encoding: 'utf8', timeout: 5_000,
		})
		assert.equal(result.status, 0, result.stderr)
		assert.equal(result.stdout.trim().split('\n').length, 1)
		assert.equal(JSON.parse(result.stdout).minimum.quantity, '0.0044')
		assert.equal(result.stderr, '')
	} finally {
		rmSync(directory, { recursive: true, force: true })
	}
})

test('importing the helper does not run its CLI', () => {
	const result = spawnSync(process.execPath, [
		'--input-type=module', '--eval', `await import(${JSON.stringify(helper.href)})`,
		'--', 'unrelated-eval-argument',
	], { encoding: 'utf8', timeout: 5_000 })
	assert.equal(result.status, 0, result.stderr)
	assert.equal(result.stdout, '')
	assert.equal(result.stderr, '')
})

test('a requested quantity below the native minimum is rejected after quantization', () => {
	const result = calculate({ ...observed, quantity: '0.0043' })
	assert.equal(result.requested.valid, false)
	assert.ok(result.requested.reasons.includes('BELOW_MINIMUM_NOTIONAL'))
})

test('a collateral budget must cover both margin and all supplied fees', () => {
	const result = calculate({ ...observed, availableMargin: '2.04' })
	assert.equal(result.maximum.quantity, '0')
	assert.equal(result.maximum.reason, 'MINIMUM_ORDER_UNAFFORDABLE')
})

test('budget quantity is floored and validated with fee-inclusive reservation', () => {
	const result = calculate({ ...observed, availableMargin: '10.71' })
	assert.equal(result.maximum.quantity, '0.023')
	assert.ok(Number(result.maximum.reservation) <= 10.71)
	assert.ok(Number(result.maximum.notional) >= 10)
})

test('unknown fees or slippage cannot yield a spend-capacity claim', () => {
	for (const field of ['tradingFeeRate', 'routingFeeRate', 'slippageBps']) {
		const input = { ...observed, availableMargin: '10.71' }
		delete input[field]
		const result = calculate(input)
		assert.equal(result.maximum, null)
		assert.ok(result.missing.includes(field))
	}
})

test('conflicting native minimum and maximum constraints cannot produce a legal size', () => {
	const result = spawnSync(process.execPath, [helper.pathname], {
		input: JSON.stringify({
			price: '100', quantityStep: '1', minimumNotional: '100',
			minimumQuantity: '1', maximumQuantity: '0.5',
		}), encoding: 'utf8', timeout: 5_000,
	})
	assert.equal(result.status, 2)
	assert.match(JSON.parse(result.stderr).error, /No quantity meets the native minimum and maximum/)
})
