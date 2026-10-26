// Synthetic golden wire values, independently constructed from the read contract.
// No real wallet, credentials, private package imports or live network are needed.
export const hash = `0x${'1'.repeat(64)}`
const spotHash = `0x${'2'.repeat(64)}`
export const nextCursor = 'opaque+/=fixture?&page=2'
const from = 1790812800000
const to = 1790899200000
const quoteDenom = `peggy0x${'3'.repeat(40)}`
const baseDenom = 'factory/inj1fixture/btc'
const subaccountId = `0x${'a'.repeat(40)}${'0'.repeat(24)}`
const identity = {
	accountRef: 'injective:mainnet:owned-fixture:gen-1',
	instanceId: 'owned-fixture',
	walletGeneration: 'gen-1',
	environment: 'mainnet',
	nativeChainId: 'injective-1',
	evmChainId: 1776,
	evmAddress: `0x${'a'.repeat(40)}`,
	injectiveAddress: `inj1${'a'.repeat(38)}`,
	subaccountId,
}
const fresh = {
	status: 'fresh',
	completeness: 'complete',
	asOf: from,
	source: 'injective-indexer',
	sourceHeight: null,
	retryAfterMs: null,
	reason: null,
}
const stale = {
	...fresh,
	status: 'stale',
	completeness: 'partial',
	retryAfterMs: 5000,
	reason: 'upstream_unavailable',
}
const balances = {
	data: [
		{
			denom: quoteDenom,
			symbol: 'USDT',
			decimals: 6,
			bank: '100.000000',
			exchangeTotal: '100.000000',
			exchangeAvailable: '90.000000',
			held: '10.000000',
			positionMargin: null,
			spendable: null,
			total: null,
		},
		{
			denom: 'ibc/other-usdt',
			symbol: 'USDT',
			decimals: null,
			bank: null,
			exchangeTotal: null,
			exchangeAvailable: null,
			held: null,
			positionMargin: null,
			spendable: null,
			total: null,
		},
	],
	meta: { ...fresh, completeness: 'partial', reason: 'metadata_missing' },
}
const positions = {
	data: [
		{
			id: `${subaccountId}:${hash}`,
			venue: 'injective',
			scopeId: subaccountId,
			market: `injective:perp:${hash}`,
			nativeMarketId: hash,
			nativeOrderId: null,
			side: 'buy',
			quantity: '0.10000000',
			signedQuantity: '0.10000000',
			price: null,
			entryPrice: '60000.250000',
			markPrice: '60001.500000',
			positionValue: null,
			roe: null,
			pnl: null,
			settledFundingSinceOpen: null,
			margin: '1000.000000',
			liquidation: null,
			status: null,
			time: from,
			algo: false,
			marginMode: null,
			leverage: null,
			isolatedCollateral: null,
			initialMarginFraction: null,
			maintenanceMarginRate: null,
		},
	],
	meta: stale,
}
function referenceInstrument(product, marketHash) {
	return {
		id: `injective:${product}:${marketHash}`,
		venue: 'injective',
		environment: 'mainnet',
		product,
		nativeSymbol: 'BTC/USDT',
		base: 'BTC',
		quote: 'USDT',
		nativeMarketId: marketHash,
		nativeAssetId: product === 'spot' ? baseDenom : null,
		nativeTokenId: product === 'spot' ? baseDenom : null,
		executionAssetId: null,
		baseAssetId: product === 'spot' ? baseDenom : null,
		quoteAssetId: quoteDenom,
		baseTokenId: product === 'spot' ? baseDenom : null,
		quoteTokenId: quoteDenom,
		sizeDecimals: product === 'spot' ? 8 : null,
		baseDecimals: product === 'spot' ? 8 : null,
		quoteDecimals: 6,
		assetClass: 'other',
		onlyIsolated: null,
		settlementScope: {
			id: `${product}:default:${quoteDenom}`,
			product,
			settlementAsset: quoteDenom,
			settlementPool: null,
		},
		status: 'trading',
		rules: {
			priceTick: '0.01',
			priceSignificantFigures: null,
			priceMaxDecimals: null,
			sizeStep: '0.0001',
			minSize: '0.0001',
			maxSize: null,
			minNotional: '1',
			maxNotional: null,
			contractSize: '1',
			maxLeverage: null,
		},
	}
}
const perp = referenceInstrument('perp', hash)
const referenceMeta = {
	asOf: from,
	status: 'fresh',
	completeness: 'complete',
	source: 'market-data',
	retryAfterMs: null,
}
const catalog = {
	identity: { venue: 'injective', environment: 'mainnet' },
	data: [perp, referenceInstrument('spot', spotHash)],
	meta: referenceMeta,
	missing: [],
}
const instrument = {
	id: `injective:perp:${hash}`,
	venue: 'injective',
	kind: 'dex',
	product: 'perp',
	underlying: 'BTC',
	nativeSymbol: 'BTC/USDT',
	quote: 'USDT',
	exposureMultiplier: 1,
	routing: { injectiveMarketId: hash },
}
function record(kind, product, marketId, id) {
	return {
		id,
		kind,
		product,
		marketId,
		nativeType: kind === 'fill' ? 'market' : 'limit',
		side: 'buy',
		quantity: '0.10000000',
		filledQuantity: kind === 'fill' ? '0.10000000' : '0.01000000',
		price: '60000.250000',
		triggerPrice: null,
		fee: kind === 'fill' ? '0.001250' : null,
		feeDenom: kind === 'fill' ? quoteDenom : null,
		status: kind === 'fill' ? null : 'booked',
		sourceAt: from,
		orderHash: 'fixture-order-hash',
		txHash: null,
	}
}
function page(data, next = null) {
	return {
		identity,
		component: { data, meta: fresh },
		nextCursor: next,
		coverage: next ? 'partial' : 'complete',
	}
}
function candle(t, c) {
	return { t, o: 60000.25, h: 60002, l: 60000, c, v: null, closed: true }
}
export const fixtures = {
	catalog,
	exactCatalog: { ...catalog, data: [perp] },
	book: {
		instrument,
		book: {
			observedAt: from,
			sourceAt: from - 10,
			heartbeatAt: from,
			sequence: 7,
			bids: [[60000.25, 0.1]],
			asks: [[60001.5, 0.2]],
		},
		status: 'live',
		source: 'http-rest-snapshot',
	},
	trades: {
		instrument,
		trades: [
			{ id: 'fixture-trade', sourceAt: from - 20, price: 60000.25, quantity: 0.1, maker: false },
		],
		status: 'recent',
		source: 'http-rest-sample',
	},
	candles: {
		instrument,
		tf: '1h',
		source: { mode: 'native' },
		candles: [
			candle(from - 3600000, 60000.5),
			candle(from, 60000.75),
			candle(from + 3600000, 60001),
			candle(to, 60001.5),
		],
		nextCursor: from - 3600000,
		requested: { from, to },
		historyStatus: 'range-queryable',
		historyLimitFrom: from - 5 * 365 * 86400000,
		historyAvailability: 'available',
		asOf: to,
	},
	status: { identity, mode: 'read_only', executionEnabled: false, readStatus: 'available' },
	account: { identity, balances, positions, mode: 'read_only', executionEnabled: false },
	balances: { identity, balances },
	positions: { identity, component: positions, nextCursor: null, coverage: 'partial' },
	orders: page([record('order', 'spot', spotHash, 'fixture-spot-order')]),
	'order-history': page([record('order', 'perp', hash, 'fixture-perp-history')]),
	fills: page([record('fill', 'perp', hash, 'fixture-perp-fill')], nextCursor),
	unavailablePage: {
		identity,
		component: {
			data: null,
			meta: {
				...fresh,
				status: 'unavailable',
				completeness: 'partial',
				asOf: null,
				retryAfterMs: 5000,
				reason: 'not_indexed',
			},
		},
		nextCursor: null,
		coverage: 'unknown',
	},
}
