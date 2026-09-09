# Capture news interests without changing their meaning

Use this reference for Pawpilot news onboarding or changes to news interests.
Follow [profile-api.md](profile-api.md) for the executable read/change/verify
workflow. The same intent contract applies to OpenClaw and Hermes.

## Recognize the subscription request

For a bare “开启 Pawpilot”, ask a focused question in the user's language, for
example: “你想开启持续新闻关注吗？可以告诉我关注的币种或主题，以及多久检查一次；
不确定的话，我可以先给你一个通用 Crypto 方案。” Do not ask them to find a
technical skill name or product link. If they already explicitly requested
ongoing news updates, proceed with only the missing preferences; do not ask
them to opt in again or restart onboarding for an existing Profile.

For “Pawpilot 是什么？”, explain ongoing news monitoring and the separate
research/trade-preparation workflow without writing a Profile. For a one-off
request such as “分析一下这条新闻” or “BTC 现在什么价格？”, follow the existing
market-research instructions instead of subscribing the user.

Read the current Profile before applying agreed changes. “暂停新闻推送” pauses
only news matching/delivery; it does not disable market research or delete
history. Resume only on an explicit news-resume request. Subscription consent
does not authorize trading or enable the platform's market-research flag. If
research is unavailable, explain that limitation rather than claiming that a
Profile write enabled it.

Describe cadence as how often to check a matched batch, not a promise of a
Trading Idea every interval: irrelevant or unsupported batches may stay silent.

## Guide, then preserve

Ask only for missing information that changes the subscription: assets or
ecosystems, kinds of events, exclusions, and preferred cadence. Do not require
the user to know tickers or event-type names. Do not infer positions, leverage,
trade direction, or risk tolerance from a news preference.

If the user does not know what to follow, offer an editable Crypto-only draft:
“News about Bitcoin, Ethereum and Solana, protocol security, exchange listing
changes, and regulation directly affecting crypto.” Explain that this is a
broad starting point, not an investment recommendation. Ask whether to enable
it; asking for suggestions alone is not opt-in. Use 360 minutes only for a new
subscription without a user-selected cadence. Do not replace an existing
Profile with this draft.

Persist two text fields when saving an agreed interest:

- `interestOriginal`: the complete agreed interest in the input language, not
  the requested reply language. On creation or a full restatement, retain the
  user's interest wording/language. On an incremental edit (“also SOL”), amend
  the existing complete interest in its existing language. An explicit request
  to convert the stored Profile to another language overrides that default.
  For an assistant-proposed draft, use the wording the user agreed to.
- `interestEn`: a faithful, complete English rendering of the same intent, not
  a keyword list or summary. If already English, both may be identical.

For English interests with “reply in Chinese”, keep both interest fields in
English and set only `preferredLanguage` to `zh-CN`. A cadence-only or reply-
language-only update contains only that changed field: the script preserves
both interest texts exactly.

Support the user's language, including simplified/traditional Chinese,
Japanese, Korean, Russian and Spanish. Preserve negation, AND/OR groups,
“only”, primary versus incidental mention, and planned versus completed
events. Keep names, amounts and time ranges unchanged. Do not add a causal or
bullish/bearish interpretation. If ambiguity changes the meaning, clarify
before saving. Each field is limited to 4,000 characters; do not silently
truncate or drop constraints to fit.

Example: “比特币 ETF 资金流，或以太坊安全事件；不要空投” means
“Bitcoin ETF flows OR Ethereum security incidents; exclude airdrops.” It does
not mean “all Bitcoin news AND all Ethereum news” or “buy BTC and ETH”.

Show a brief read-back of the intended subscription in the user's language.
Keep `preferredLanguage` as the user's reply language; English retrieval text
does not authorize changing it to English.

In an ongoing subscription conversation, “改成中文通知” or “偏好语言改成 Chinese”
is a Profile language update, even if memory already says Chinese. Use the
verified script workflow. If the user specifies chat-only replies, leave the
Profile unchanged; clarify when the scope is genuinely ambiguous.

## Retain compatible legacy fields without promising exact filtering

The API still needs its legacy preference fields. Use supported asset/event
terms that reflect the agreed interest, but do not invent event types or erase
the full text merely because the legacy fields cannot express it. Preserve
unrelated fields from GET.

Use the exact event identifiers in [profile-api.md](profile-api.md), including
underscores. In the example above, `etf_flow` and `exploit_security` are supported;
the asset/event combinations and airdrop exclusion are not fully expressible
by V1 selectors. A save confirmation must distinguish the complete intent stored
from the routing constraints actually supported, rather than promising exact
filtering just because the text was accepted.

Check the V1 scoring contract in [profile-api.md](profile-api.md) against the
draft's selectors and minimum score. Event-only selectors with the default score
50 cannot yield candidates; explain and obtain agreement on a viable draft.
Do not silently add broad asset selectors or lower an existing threshold.

Saved text is not proof that semantic matching is enabled for this Instance.
Do not claim an unsupported selector “works through semantic matching” simply
because its wording was saved. Describe it as retained intent for Agent analysis,
not a guaranteed candidate filter.
Candidate recall may be broader than the intent, and vector similarity is not
a strict boolean/exclusion engine. Never promise that every detailed natural-
language restriction will be enforced before the Agent reads candidates. If
the user requires a strict guarantee the current API cannot provide, explain
the limitation and clarify instead of silently broadening the subscription.

For a cadence/language-only edit, preserve both interest texts unchanged. For
an interest/source/include/exclude change, reconcile both texts with that
change; do not copy stale text that contradicts the new selectors. If no
semantic interest existed, do not invent one merely to change cadence.

The paired fields can both be `null` to explicitly clear semantic interest.
Never send only one field or one text with the other null. Do not clear text
unless requested or needed to avoid retaining an intent the user changed.

A paused Profile stays paused unless the user explicitly authorizes resume.
The current PUT resumes it: do not PUT preferences and then pause as a shortcut.
