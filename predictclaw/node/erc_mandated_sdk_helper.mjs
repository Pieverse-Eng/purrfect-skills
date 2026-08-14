import * as sdk from '@erc-mandated/sdk'

function isObject(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function normalizeForJson(value) {
  const walk = (input) => {
    if (typeof input === 'bigint') return input.toString()
    if (
      input === null ||
      typeof input === 'string' ||
      typeof input === 'number' ||
      typeof input === 'boolean'
    ) {
      return input
    }
    if (Array.isArray(input)) return input.map((item) => walk(item))
    if (typeof input === 'object') {
      const out = {}
      for (const [k, v] of Object.entries(input)) out[k] = walk(v)
      return out
    }
    return String(input)
  }
  return walk(value)
}

function toToolError(code, message, details) {
  return { code, message, details }
}

async function handleToolCall(toolName, args) {
  switch (toolName) {
    case 'agent_account_context_create':
      return await sdk.createAgentAccountContext(args)
    case 'agent_funding_policy_create':
      return await sdk.createAgentFundingPolicy(args)
    case 'vault_bootstrap':
      // Pure plan/encode path. Broadcast is owned by the platform wallet adapter,
      // not by this helper; the Python bridge rejects execute mode.
      return await sdk.bootstrapVault(args)
    case 'agent_build_fund_and_action_plan':
      return await sdk.buildFundAndActionPlan(args)
    case 'agent_fund_and_action_session_create':
      return await sdk.createFundAndActionExecutionSession(args)
    case 'agent_fund_and_action_session_apply_event':
      return await sdk.applyFundAndActionExecutionEvent(args)
    case 'agent_fund_and_action_session_next_step':
      return await sdk.resolveFundAndActionExecutionTask(args)
    case 'agent_follow_up_action_result_create':
      return await sdk.createFollowUpActionResult(args)
    case 'vault_asset_transfer_result_create':
      return await sdk.createAssetTransferResult(args)
    case 'vault_check_asset_transfer_policy':
      return await sdk.checkAssetTransferAgainstFundingPolicy(args)
    case 'vault_health_check':
      return await sdk.healthCheckVault(args)
    case 'factory_predict_vault_address':
      return await sdk.predictVaultAddress(args)
    case 'factory_create_vault_prepare':
      return await sdk.prepareCreateVaultTx(args)
    case 'mandate_build_sign_request':
      return await sdk.buildMandateSignRequest(args)
    case 'vault_build_asset_transfer_plan':
      return await sdk.buildAssetTransferPlan(args)
    case 'vault_build_asset_transfer_plan_from_context':
      return await sdk.buildAssetTransferPlanFromAccountContext(args)
    case 'vault_simulate_asset_transfer_from_context': {
      const plan = await sdk.buildAssetTransferPlanFromAccountContext({
        ...args,
        executeContext: {
          from: args.from,
          signature: args.signature,
          adapterProofs: args.adapterProofs,
        },
      })
      if (!plan.result.simulateExecuteInput) {
        return {
          error: toToolError(
            'INTERNAL_PLAN_ERROR',
            'Asset transfer plan did not produce simulate input.',
            { tool: toolName },
          ),
        }
      }
      const simulation = await sdk.simulateExecuteVault(plan.result.simulateExecuteInput)
      return {
        result: {
          accountContext: plan.result.accountContext,
          action: plan.result.action,
          erc20Call: plan.result.erc20Call,
          humanReadableSummary: plan.result.humanReadableSummary,
          signRequest: plan.result.signRequest,
          simulate: simulation.result,
        },
      }
    }
    case 'vault_prepare_asset_transfer_from_context': {
      const plan = await sdk.buildAssetTransferPlanFromAccountContext({
        ...args,
        executeContext: {
          from: args.from,
          signature: args.signature,
          adapterProofs: args.adapterProofs,
        },
      })
      if (!plan.result.prepareExecuteInput) {
        return {
          error: toToolError(
            'INTERNAL_PLAN_ERROR',
            'Asset transfer plan did not produce prepare input.',
            { tool: toolName },
          ),
        }
      }
      const prepared = await sdk.prepareExecuteTx(plan.result.prepareExecuteInput)
      return {
        result: {
          accountContext: plan.result.accountContext,
          action: plan.result.action,
          erc20Call: plan.result.erc20Call,
          humanReadableSummary: plan.result.humanReadableSummary,
          signRequest: plan.result.signRequest,
          txRequest: prepared.result.txRequest,
        },
      }
    }
    default:
      return {
        error: toToolError(
          'NOT_IMPLEMENTED',
          `${toolName} is not implemented by the one-shot SDK helper`,
          { tool: toolName },
        ),
      }
  }
}

async function main() {
  const chunks = []
  for await (const chunk of process.stdin) chunks.push(chunk)
  const inputText = Buffer.concat(chunks).toString('utf8')
  let request
  try {
    request = JSON.parse(inputText)
  } catch {
    process.stdout.write(JSON.stringify({ error: { code: 'INVALID_REQUEST', message: 'stdin is not valid JSON' } }))
    return
  }
  const toolName = typeof request.tool === 'string' ? request.tool : ''
  const args = isObject(request.arguments) ? request.arguments : {}
  try {
    const result = await handleToolCall(toolName, args)
    process.stdout.write(JSON.stringify(normalizeForJson(result)))
  } catch (error) {
    process.stdout.write(
      JSON.stringify({
        error: {
          code: error?.code ?? 'SDK_ERROR',
          message: error instanceof Error ? error.message : String(error),
          details: isObject(error?.details) ? error.details : undefined,
        },
      }),
    )
  }
}

main().catch((error) => {
  process.stdout.write(
    JSON.stringify({
      error: { code: 'FATAL', message: error instanceof Error ? error.message : String(error) },
    }),
  )
  process.exit(1)
})
