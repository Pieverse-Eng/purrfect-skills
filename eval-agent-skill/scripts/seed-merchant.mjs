// Template: seed deterministic in-pod state for the merchant skill eval.
// Copy this into the pod's skill workspace dir and run:
//   cd /root/.openclaw/workspace/skills/purrfect-merchant-skill
//   node seed-merchant.mjs
//
// Adapt the W (wallets) / loyalPayments / orders sections per skill — the
// pattern is: deterministic IDs, mixed states (active/expired/cancelled),
// at least one failure case (failed_settlements), enough variety that a
// curated corpus has plausible right answers (e.g. multiple customers so
// "list customers" returns >0; reward rules above + below thresholds).

import Db from 'better-sqlite3'

const db = new Db('data/merchant.db')

// Wallets — realistic-looking EVM addresses, picked so the tail digits
// hint at the customer's role (helpful when reading eval output).
const W = {
	loyal: '0xAa1234567890aBcDeF1234567890ABCDEF000001', // 8 visits, regular
	spender: '0xBB987654321098765432109876543210FEDCBA02', // 3 visits, big spender
	newbie: '0xCC0011223344556677889900aabbccddeeff0303', // 1 visit
	ghost: '0xDD0099887766554433221100ffeeddccbbaa0404', // shows up only in failed settle
}

const txn = db.transaction(() => {
	// Wipe existing customer/payment/order/coupon state for deterministic seed.
	// Products + reward rules are added separately via the skill's CLI so this
	// script doesn't have to know their schemas.
	db.exec(`
		DELETE FROM coupons; DELETE FROM coupon_awards;
		DELETE FROM order_items; DELETE FROM orders;
		DELETE FROM event_inbox; DELETE FROM processed_payment_events;
		DELETE FROM failed_settlements; DELETE FROM payments; DELETE FROM customers;
	`)

	const insertCustomer = db.prepare(
		`INSERT INTO customers (wallet_address, total_payments, total_spent_base_units, first_seen, last_seen) VALUES (?, ?, ?, ?, ?)`,
	)
	const insertPayment = db.prepare(
		`INSERT INTO payments (customer_wallet, amount_base_units, credential_id, challenge_id, settled_at, description) VALUES (?, ?, ?, ?, ?, ?)`,
	)
	const insertOrder = db.prepare(
		`INSERT INTO orders (code, amount_base_units, description, status, payment_id, credential_id, challenge_id, created_at, expires_at, paid_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
	)
	const insertCoupon = db.prepare(
		`INSERT INTO coupons (customer_wallet, rule_id, value_base_units, type, status, created_at) VALUES (?, ?, ?, ?, ?, ?)`,
	)
	const insertFailed = db.prepare(
		`INSERT INTO failed_settlements (challenge_id, customer_wallet, amount_base_units, credential_id, idempotency_key, error_message) VALUES (?, ?, ?, ?, ?, ?)`,
	)

	// Helper: timestamp string offset by hours from now (negative = in past)
	const ts = (hoursAgo) => {
		const d = new Date(Date.now() - hoursAgo * 3600 * 1000)
		return d.toISOString().replace('T', ' ').replace('Z', '').slice(0, 19)
	}

	// Customer: loyal — 8 payments over past 2 weeks, total ~28 USDT
	insertCustomer.run(W.loyal, 8, '28000000000000000000', ts(24 * 14), ts(2))
	const loyalPayments = [
		[3500000000000000000n, '经典珍珠奶茶', 24 * 14],
		[5000000000000000000n, '抹茶拿铁', 24 * 12],
		[3500000000000000000n, '经典珍珠奶茶', 24 * 10],
		[4500000000000000000n, '芋头波霸', 24 * 7],
		[2500000000000000000n, '柠檬绿茶', 24 * 4],
		[3500000000000000000n, '经典珍珠奶茶', 24 * 3],
		[2500000000000000000n, '柠檬绿茶', 24 * 2],
		[3000000000000000000n, '经典珍珠奶茶 (with coupon)', 2],
	]
	for (let i = 0; i < loyalPayments.length; i++) {
		const [amt, desc, hoursAgo] = loyalPayments[i]
		insertPayment.run(W.loyal, amt.toString(), `cred_loyal_${i}`, `chal_loyal_${i}`, ts(hoursAgo), desc)
	}

	// Customer: spender — 3 big purchases, total 30 USDT
	insertCustomer.run(W.spender, 3, '30000000000000000000', ts(24 * 5), ts(8))
	insertPayment.run(W.spender, '10000000000000000000', 'cred_spender_0', 'chal_spender_0', ts(24 * 5), '抹茶拿铁 + 芋头波霸 (combo)')
	insertPayment.run(W.spender, '10000000000000000000', 'cred_spender_1', 'chal_spender_1', ts(24 * 3), 'company event order')
	insertPayment.run(W.spender, '10000000000000000000', 'cred_spender_2', 'chal_spender_2', ts(8), '团购 4 杯')

	// Customer: newbie — 1 payment, today
	insertCustomer.run(W.newbie, 1, '3500000000000000000', ts(1), ts(1))
	insertPayment.run(W.newbie, '3500000000000000000', 'cred_newbie_0', 'chal_newbie_0', ts(1), '经典珍珠奶茶')

	// Orders — mix of statuses
	insertOrder.run('ORD7K2A', '7500000000000000000', '抹茶拿铁 + 芋头波霸 take-out', 'pending', null, null, null, ts(0.5), ts(-0.5), null)
	insertOrder.run('ORD9M3B', '4500000000000000000', '芋头波霸', 'pending', null, null, null, ts(0.9), ts(-0.05), null)
	const lastSpenderPayment = db.prepare(`SELECT id FROM payments WHERE customer_wallet=? ORDER BY id DESC LIMIT 1`).get(W.spender)
	insertOrder.run('ORD3F9C', '10000000000000000000', '团购 4 杯', 'paid', lastSpenderPayment.id, 'cred_spender_2', 'chal_spender_2', ts(9), ts(8.5), ts(8))
	insertOrder.run('ORD2X8D', '3500000000000000000', '经典珍珠奶茶 (取消了)', 'cancelled', null, null, null, ts(28), ts(27), null)
	insertOrder.run('ORDXP1E', '5000000000000000000', '抹茶拿铁 (没付钱)', 'expired', null, null, null, ts(48), ts(47), null)

	// Active coupon for loyal customer (rule 1: payment_count threshold met)
	insertCoupon.run(W.loyal, 1, '1000000000000000000', 'fixed_discount', 'active', ts(48))

	// Failed settlement — reconcile_list test depends on this
	insertFailed.run('chal_ghost_failed', W.ghost, '5000000000000000000', 'cred_ghost_failed', 'idem_ghost_failed', 'CP timeout 504')
})

txn()

// Print summary so the runner can confirm seed succeeded
console.log('=== seeded ===')
console.log('customers:', db.prepare('SELECT COUNT(*) as n FROM customers').get().n)
console.log('payments :', db.prepare('SELECT COUNT(*) as n FROM payments').get().n)
console.log('orders   :', db.prepare(`SELECT status, COUNT(*) as n FROM orders GROUP BY status`).all())
console.log('coupons  :', db.prepare(`SELECT status, COUNT(*) as n FROM coupons GROUP BY status`).all())
console.log('failed_settle:', db.prepare('SELECT COUNT(*) as n FROM failed_settlements').get().n)
console.log("today total:", db.prepare(`SELECT SUM(CAST(amount_base_units AS INTEGER))/1000000000000000000 as today_usdt FROM payments WHERE settled_at >= datetime('now', 'start of day', 'utc')`).get())
