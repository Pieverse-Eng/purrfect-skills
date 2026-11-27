#!/usr/bin/env node
// Read-only decimal arithmetic. No network, credentials, profiles or order submission.
import { realpathSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const SCALE = 10n ** 18n
const ceil = (a, b) => (a + b - 1n) / b
const maximum = (...values) => values.reduce((a, b) => (a > b ? a : b))
const minimum = (a, b) => (a < b ? a : b)
const decimal = (value) => {
	const whole = value / SCALE
	const fraction = (value % SCALE).toString().padStart(18, '0').replace(/0+$/, '')
	return fraction ? `${whole}.${fraction}` : `${whole}`
}
const parse = (input, name, positive = false) => {
	const value = input[name]
	if (typeof value !== 'string' || !/^\d{1,40}(?:\.\d{1,18})?$/.test(value)) {
		throw new Error(`${name} must be a bounded unsigned decimal string`)
	}
	const [whole, fraction = ''] = value.split('.')
	const result = BigInt(whole) * SCALE + BigInt(fraction.padEnd(18, '0'))
	if (positive && result === 0n) throw new Error(`${name} must be positive`)
	return result
}

export function orderSize(input) {
	if (!input || typeof input !== 'object' || Array.isArray(input)) {
		throw new Error('Expected a JSON object of verified native decimal inputs')
	}
	const fields = new Set([
		'price', 'quantityStep', 'minimumNotional', 'minimumQuantity', 'maximumQuantity',
		'leverage', 'tradingFeeRate', 'routingFeeRate', 'slippageBps', 'availableMargin', 'quantity',
	])
	if (Object.keys(input).some((key) => !fields.has(key))) throw new Error('Unknown sizing field')
	const price = parse(input, 'price', true)
	const step = parse(input, 'quantityStep', true)
	const minNotional = parse(input, 'minimumNotional')
	const minQuantity = parse(input, 'minimumQuantity')
	const maxQuantity = input.maximumQuantity === undefined ? null : parse(input, 'maximumQuantity', true)
	const missing = ['leverage', 'tradingFeeRate', 'routingFeeRate', 'slippageBps']
		.filter((key) => input[key] === undefined)
	const leverage = input.leverage === undefined ? null : parse(input, 'leverage', true)
	const fees = ['tradingFeeRate', 'routingFeeRate'].map((key) => {
		if (input[key] === undefined) return null
		const value = parse(input, key)
		if (value > SCALE) throw new Error(`${key} exceeds one`)
		return value
	})
	const slippage = input.slippageBps === undefined ? null : parse(input, 'slippageBps')
	if (slippage !== null && slippage >= 10_000n * SCALE) throw new Error('slippageBps must be below 10000')
	const reservePrice = slippage === null ? null : ceil(price * (10_000n * SCALE + slippage), 10_000n * SCALE)
	const economics = (quantity) => {
		const notional = quantity * price
		const protectedNotional = reservePrice === null ? null : quantity * reservePrice
		const margin = leverage === null || protectedNotional === null ? null : ceil(protectedNotional, leverage)
		const tradingFee = fees[0] === null || protectedNotional === null ? null : ceil(protectedNotional * fees[0], SCALE * SCALE)
		const routingFee = fees[1] === null || protectedNotional === null ? null : ceil(protectedNotional * fees[1], SCALE * SCALE)
		const reservation = margin === null || tradingFee === null || routingFee === null ? null : margin + tradingFee + routingFee
		return {
			quantity: decimal(quantity), notional: decimal(ceil(notional, SCALE)),
			margin: margin === null ? null : decimal(margin),
			tradingFee: tradingFee === null ? null : decimal(tradingFee),
			routingFee: routingFee === null ? null : decimal(routingFee),
			reservation: reservation === null ? null : decimal(reservation),
		}
	}
	// Minimum size rounds UP. A budget cap rounds DOWN in the search below.
	const minLots = maximum(1n, ceil(minQuantity, step), ceil(minNotional * SCALE, price * step))
	const legalMinimum = minLots * step
	if (maxQuantity !== null && maxQuantity / step < minLots) {
		throw new Error('No quantity meets the native minimum and maximum constraints')
	}
	const available = input.availableMargin === undefined ? null : parse(input, 'availableMargin')
	let capacity = null
	if (available !== null && missing.length === 0) {
		let low = 0n
		let high = (available * leverage) / (reservePrice * step)
		if (maxQuantity !== null) high = minimum(high, maxQuantity / step)
		while (low < high) {
			const middle = (low + high + 1n) / 2n
			const cost = parse(economics(middle * step), 'reservation')
			if (cost <= available) low = middle
			else high = middle - 1n
		}
		capacity = low < minLots
			? { ...economics(0n), reason: 'MINIMUM_ORDER_UNAFFORDABLE' }
			: { ...economics(low * step), reason: null }
	}
	let requested = null
	if (input.quantity !== undefined) {
		const quantity = parse(input, 'quantity')
		const reasons = []
		if (quantity === 0n || quantity % step !== 0n) reasons.push('INVALID_QUANTITY_STEP')
		if (quantity < minQuantity) reasons.push('BELOW_MINIMUM_QUANTITY')
		if (quantity * price < minNotional * SCALE) reasons.push('BELOW_MINIMUM_NOTIONAL')
		if (maxQuantity !== null && quantity > maxQuantity) reasons.push('ABOVE_MAXIMUM_QUANTITY')
		const values = economics(quantity)
		if (available !== null && values.reservation !== null && parse(values, 'reservation') > available) reasons.push('INSUFFICIENT_MARGIN_AND_FEES')
		requested = { ...values, valid: reasons.length === 0, reasons }
	}
	return {
		authority: 'arithmetic_only',
		price: decimal(price),
		reservationPrice: reservePrice === null ? null : decimal(reservePrice),
		quantityStep: decimal(step),
		minimumNotional: decimal(minNotional),
		minimum: economics(legalMinimum), maximum: capacity, requested, missing,
		limitations: 'Estimates at the supplied price and slippage envelope. Native account risk, leverage tiers, liquidity and current venue admission must still be verified. No order was prepared or submitted.',
	}
}

function isCliEntry() {
	if (!process.argv[1]) return false
	try {
		return realpathSync(fileURLToPath(import.meta.url)) === realpathSync(process.argv[1])
	} catch {
		return false
	}
}

if (isCliEntry()) {
	try {
		let raw = ''
		const args = process.argv.slice(2)
		if (args.length === 2 && args[0] === '--input-json') raw = args[1]
		else if (args.length === 0) {
			for await (const chunk of process.stdin) {
				raw += chunk
				if (raw.length > 16_384) throw new Error('Sizing input exceeds 16384 characters')
			}
		}
		else throw new Error('Use --input-json with one nonsecret JSON argument, or provide JSON on stdin')
		if (raw.length > 16_384) throw new Error('Sizing input exceeds 16384 characters')
		process.stdout.write(`${JSON.stringify(orderSize(JSON.parse(raw)))}\n`)
	} catch (error) {
		process.stderr.write(`${JSON.stringify({ error: error.message })}\n`)
		process.exitCode = 2
	}
}
