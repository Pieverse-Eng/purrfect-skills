from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .config import PredictConfig, redact_text
from .platform_wallet import PlatformWalletClient
from .mandated_sdk_client import MandatedSdkClient, MandatedSdkError, SUPPORTED_SDK_TOOLS


MANDATED_V1_REQUIRED_TOOLS = frozenset(
    {
        "factory_predict_vault_address",
        "factory_create_vault_prepare",
        "vault_health_check",
    }
)
MANDATED_BOOTSTRAP_REQUIRED_TOOLS = frozenset({"vault_bootstrap"})

MANDATED_AGENT_SESSION_TOOLS = frozenset(
    {
        "agent_account_context_create",
        "agent_funding_policy_create",
        "agent_build_fund_and_action_plan",
        "agent_fund_and_action_session_create",
        "agent_fund_and_action_session_next_step",
        "agent_fund_and_action_session_apply_event",
        "agent_follow_up_action_result_create",
    }
)

MANDATED_ASSET_TRANSFER_TOOLS = frozenset(
    {
        "vault_asset_transfer_result_create",
        "vault_check_asset_transfer_policy",
        "vault_build_asset_transfer_plan_from_context",
        "vault_simulate_asset_transfer_from_context",
        "vault_prepare_asset_transfer_from_context",
    }
)



class MandatedVaultBridgeError(RuntimeError):
    pass


class MandatedVaultBridgeUnavailableError(MandatedVaultBridgeError):
    pass


class MandatedVaultBridgeMissingToolsError(MandatedVaultBridgeError):
    def __init__(
        self,
        missing_tools: Sequence[str],
        *,
        operation: str | None = None,
    ) -> None:
        unique_tools = tuple(sorted(set(missing_tools)))
        self.missing_tools = frozenset(unique_tools)
        missing = ", ".join(unique_tools)
        if operation:
            message = f"Mandated SDK bridge cannot perform {operation}; missing required tools: {missing}."
        else:
            message = f"Mandated SDK bridge is missing required tools: {missing}."
        super().__init__(message)


class _BridgeModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class BridgeToolError(_BridgeModel):
    code: str
    message: str
    details: dict[str, Any] | None = None
    suggestion: str | None = None


class BridgeTxRequest(_BridgeModel):
    from_address: str = Field(alias="from")
    to: str
    data: str
    value: str
    gas: str | None = None


class FactoryPredictVaultAddressResult(_BridgeModel):
    predictedVault: str


class FactoryCreateVaultPrepareResult(_BridgeModel):
    predictedVault: str
    txRequest: BridgeTxRequest


class VaultHealthCheckResult(_BridgeModel):
    blockNumber: int
    vault: str
    mandateAuthority: str
    authorityEpoch: str
    pendingAuthority: str
    nonceThreshold: str
    totalAssets: str


VaultBootstrapMode = Literal["plan", "execute"]
VaultBootstrapAuthorityMode = Literal["single_key", "dual_key"]
VaultBootstrapDeploymentStatus = Literal[
    "planned", "submitted", "confirmed", "reverted", "receipt_unknown"
]
VaultBootstrapReceiptStatus = Literal["success", "reverted", "timeout"]


class VaultBootstrapAuthorityConfig(_BridgeModel):
    mode: VaultBootstrapAuthorityMode
    authority: str
    executor: str


class VaultBootstrapCreateTx(_BridgeModel):
    mode: VaultBootstrapMode
    txRequest: BridgeTxRequest | None = None
    txHash: str | None = None
    receiptStatus: VaultBootstrapReceiptStatus | None = None
    blockNumber: int | None = None
    confirmations: int | None = None
    receipt: dict[str, Any] | None = None


class VaultBootstrapResult(_BridgeModel):
    chainId: int
    mode: VaultBootstrapMode
    factory: str
    asset: str
    signerAddress: str
    predictedVault: str
    deployedVault: str
    alreadyDeployed: bool
    deploymentStatus: VaultBootstrapDeploymentStatus
    authorityConfig: VaultBootstrapAuthorityConfig
    createTx: VaultBootstrapCreateTx | None = None
    vaultHealth: VaultHealthCheckResult | None = None
    accountContext: AgentAccountContext | None = None
    fundingPolicy: AgentFundingPolicy | None = None
    envBlock: str
    configBlock: str


PayloadBinding = Literal["actionsDigest", "none"]
FollowUpActionExecutionMode = Literal["offchain-api", "custom"]
FollowUpActionExecutionStatus = Literal[
    "pending", "submitted", "succeeded", "failed", "skipped"
]
FundAndActionExecutionSessionStatus = Literal[
    "pendingFunding", "pendingFollowUp", "succeeded", "failed", "skipped"
]
FundAndActionExecutionCurrentStep = Literal[
    "fundTargetAccount", "followUpAction", "none"
]
FundAndActionFundingStepStatus = Literal[
    "pending", "submitted", "succeeded", "failed", "skipped"
]
FundAndActionFollowUpStepStatus = Literal[
    "pending", "submitted", "succeeded", "failed", "skipped"
]
FundAndActionExecutionTaskKind = Literal[
    "submitFunding",
    "pollFundingResult",
    "submitFollowUp",
    "pollFollowUpResult",
    "completed",
]
AssetTransferExecutionStatus = Literal[
    "pending", "submitted", "confirmed", "failed", "skipped"
]


class AccountContextDefaults(_BridgeModel):
    allowedAdaptersRoot: str | None = None
    maxDrawdownBps: str | None = None
    maxCumulativeDrawdownBps: str | None = None
    payloadBinding: PayloadBinding | None = None
    extensions: str | None = None


class AgentAccountContext(_BridgeModel):
    agentId: str
    chainId: int
    vault: str
    authority: str
    executor: str
    assetRegistryRef: str | None = None
    fundingPolicyRef: str | None = None
    defaults: AccountContextDefaults | None = None
    createdAt: str
    updatedAt: str


class AgentAccountContextCreateResult(_BridgeModel):
    accountContext: AgentAccountContext


class AgentFundingPolicy(_BridgeModel):
    policyId: str
    allowedTokenAddresses: list[str] | None = None
    allowedRecipients: list[str] | None = None
    maxAmountPerTx: str | None = None
    maxAmountPerWindow: str | None = None
    windowSeconds: int | None = None
    expiresAt: str | None = None
    repeatable: bool | None = None
    createdAt: str
    updatedAt: str


class AgentFundingPolicyCreateResult(_BridgeModel):
    fundingPolicy: AgentFundingPolicy


class PolicyViolation(_BridgeModel):
    code: str
    field: str
    message: str


class PolicyEvaluationContext(_BridgeModel):
    now: str | None = None
    currentSpentInWindow: str | None = None


class PolicyCheckResult(_BridgeModel):
    allowed: bool
    fundingPolicy: AgentFundingPolicy
    violations: list[PolicyViolation]


class FundAndActionBalanceSnapshot(_BridgeModel):
    snapshotAt: str
    maxStalenessSeconds: int
    observedAtBlock: str | None = None
    source: str | None = None


class FollowUpActionIntent(_BridgeModel):
    kind: str
    target: str | None = None
    payload: dict[str, Any] | None = None


class AssetRequirement(_BridgeModel):
    tokenAddress: str
    amountRaw: str


class FollowUpActionPlan(_BridgeModel):
    kind: str
    target: str | None = None
    executionMode: FollowUpActionExecutionMode
    summary: str
    assetRequirement: AssetRequirement | None = None
    payload: dict[str, Any] | None = None


class FollowUpActionExecutionReference(_BridgeModel):
    type: Literal["requestId", "orderId", "txHash", "custom"]
    value: str


class FollowUpActionExecutionError(_BridgeModel):
    code: str
    message: str
    retriable: bool | None = None
    details: dict[str, Any] | None = None


class FollowUpActionResult(_BridgeModel):
    kind: str
    target: str | None = None
    executionMode: FollowUpActionExecutionMode
    status: FollowUpActionExecutionStatus
    summary: str
    updatedAt: str
    startedAt: str | None = None
    completedAt: str | None = None
    attempt: int
    reference: FollowUpActionExecutionReference | None = None
    output: dict[str, Any] | None = None
    error: FollowUpActionExecutionError | None = None
    plan: FollowUpActionPlan


class FollowUpActionResultCreateResult(_BridgeModel):
    followUpActionResult: FollowUpActionResult


class Mandate(_BridgeModel):
    vault: str
    executor: str
    nonce: str
    deadline: str
    authorityEpoch: str
    allowedAdaptersRoot: str
    maxDrawdownBps: str
    maxCumulativeDrawdownBps: str
    payloadDigest: str
    extensionsHash: str


class ExecuteBaseInput(_BridgeModel):
    chainId: int | None = None
    vault: str
    from_address: str = Field(alias="from")
    mandate: Mandate
    signature: str
    actions: list[dict[str, Any]]
    adapterProofs: list[list[str]]
    extensions: str


class AssetTransferSummary(_BridgeModel):
    kind: Literal["erc20Transfer"]
    tokenAddress: str
    to: str
    amountRaw: str
    symbol: str | None = None
    decimals: int | None = None


class SignRequestResult(_BridgeModel):
    typedData: dict[str, Any]
    mandate: Mandate
    mandateHash: str
    actionsDigest: str
    extensionsHash: str


class SimulateResult(_BridgeModel):
    ok: bool
    blockNumber: int
    preAssets: str | None = None
    postAssets: str | None = None
    revertDecoded: dict[str, Any] | None = None


class AssetTransferPlanResult(_BridgeModel):
    action: dict[str, Any]
    erc20Call: dict[str, Any]
    humanReadableSummary: AssetTransferSummary
    signRequest: SignRequestResult


class AssetTransferPlanWithContextResult(_BridgeModel):
    accountContext: AgentAccountContext
    action: dict[str, Any]
    erc20Call: dict[str, Any]
    humanReadableSummary: AssetTransferSummary
    signRequest: SignRequestResult
    policyCheck: PolicyCheckResult | None = None
    simulateExecuteInput: ExecuteBaseInput | None = None
    prepareExecuteInput: ExecuteBaseInput | None = None


class AssetTransferSimulateWithContextResult(_BridgeModel):
    accountContext: AgentAccountContext
    action: dict[str, Any]
    erc20Call: dict[str, Any]
    humanReadableSummary: AssetTransferSummary
    signRequest: SignRequestResult
    policyCheck: PolicyCheckResult | None = None
    simulate: SimulateResult


class AssetTransferPrepareWithContextResult(_BridgeModel):
    accountContext: AgentAccountContext
    action: dict[str, Any]
    erc20Call: dict[str, Any]
    humanReadableSummary: AssetTransferSummary
    signRequest: SignRequestResult
    policyCheck: PolicyCheckResult | None = None
    txRequest: BridgeTxRequest


class AssetTransferReceipt(_BridgeModel):
    blockNumber: str
    blockHash: str | None = None
    confirmations: int | None = None


class AssetTransferExecutionError(_BridgeModel):
    code: str
    message: str
    retriable: bool | None = None
    details: dict[str, Any] | None = None


class AssetTransferResult(_BridgeModel):
    status: AssetTransferExecutionStatus
    summary: str
    updatedAt: str
    submittedAt: str | None = None
    completedAt: str | None = None
    attempt: int
    chainId: int | None = None
    txHash: str | None = None
    receipt: AssetTransferReceipt | None = None
    output: dict[str, Any] | None = None
    error: AssetTransferExecutionError | None = None
    plan: AssetTransferPlanResult | AssetTransferPlanWithContextResult


class AssetTransferResultCreateResult(_BridgeModel):
    assetTransferResult: AssetTransferResult


class FundAndActionTargetResult(_BridgeModel):
    label: str
    recipient: str
    tokenAddress: str
    requiredAmountRaw: str
    currentBalanceRaw: str
    balanceSnapshot: FundAndActionBalanceSnapshot
    fundingShortfallRaw: str
    symbol: str | None = None
    decimals: int | None = None


class FundAndActionStep(_BridgeModel):
    kind: Literal["fundTargetAccount", "followUpAction"]
    status: Literal["required", "skipped", "pending"]
    summary: str


class FundAndActionPlanResult(_BridgeModel):
    accountContext: AgentAccountContext
    fundingPolicy: AgentFundingPolicy | None = None
    fundingTarget: FundAndActionTargetResult
    evaluatedAt: str
    fundingRequired: bool
    fundingPlan: AssetTransferPlanWithContextResult | None = None
    followUpAction: FollowUpActionIntent
    followUpActionPlan: FollowUpActionPlan
    steps: list[FundAndActionStep]


class FundAndActionFundingStepExecution(_BridgeModel):
    required: bool
    status: FundAndActionFundingStepStatus
    summary: str
    updatedAt: str
    result: AssetTransferResult | None = None


class FundAndActionFollowUpStepExecution(_BridgeModel):
    status: FundAndActionFollowUpStepStatus
    summary: str
    updatedAt: str
    reference: FollowUpActionExecutionReference | None = None
    result: FollowUpActionResult | None = None


class FundAndActionExecutionSession(_BridgeModel):
    sessionId: str
    status: FundAndActionExecutionSessionStatus
    currentStep: FundAndActionExecutionCurrentStep
    createdAt: str
    updatedAt: str
    fundAndActionPlan: FundAndActionPlanResult
    fundingStep: FundAndActionFundingStepExecution
    followUpStep: FundAndActionFollowUpStepExecution


class FundAndActionSessionCreateResult(_BridgeModel):
    session: FundAndActionExecutionSession


class FundAndActionExecutionTask(_BridgeModel):
    kind: FundAndActionExecutionTaskKind
    summary: str
    fundingPlan: AssetTransferPlanWithContextResult | None = None
    assetTransferResult: AssetTransferResult | None = None
    followUpActionPlan: FollowUpActionPlan | None = None
    reference: FollowUpActionExecutionReference | None = None
    status: FundAndActionExecutionSessionStatus | None = None
    result: FollowUpActionResult | None = None


class FundAndActionSessionNextStepResult(_BridgeModel):
    session: FundAndActionExecutionSession
    task: FundAndActionExecutionTask


T_Result = TypeVar("T_Result", bound=BaseModel)


def _drop_none_values(value: Any) -> Any:
    if isinstance(value, Mapping):
        cleaned: dict[str, Any] = {}
        for key, nested_value in value.items():
            normalized = _drop_none_values(nested_value)
            if normalized is not None:
                cleaned[str(key)] = normalized
        return cleaned

    if isinstance(value, (list, tuple)):
        cleaned_items: list[Any] = []
        for nested_value in value:
            normalized = _drop_none_values(nested_value)
            if normalized is not None:
                cleaned_items.append(normalized)
        return cleaned_items

    return value


class MandatedVaultBridge:
    def __init__(self, config: PredictConfig) -> None:
        self._config = config
        self._sdk_client: MandatedSdkClient | None = None
        self._available_tools: set[str] = set()

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    @property
    def available_tools(self) -> frozenset[str]:
        return frozenset(self._available_tools)

    @property
    def supports_vault_bootstrap(self) -> bool:
        return MANDATED_BOOTSTRAP_REQUIRED_TOOLS.issubset(self.available_tools)

    @property
    def missing_required_tools(self) -> frozenset[str]:
        if self.runtime_ready:
            return frozenset()
        return MANDATED_V1_REQUIRED_TOOLS.difference(self.available_tools)

    @property
    def runtime_ready(self) -> bool:
        return (
            self.supports_vault_bootstrap
            or not MANDATED_V1_REQUIRED_TOOLS.difference(self.available_tools)
        )

    async def connect(self) -> None:
        if self._sdk_client is not None:
            return
        self._sdk_client = MandatedSdkClient(self._config)
        self._available_tools = set(SUPPORTED_SDK_TOOLS)

    async def close(self) -> None:
        sdk_client = self._sdk_client
        self._sdk_client = None
        self._available_tools = set()
        if sdk_client is not None:
            await sdk_client.close()

    async def health_check(self, vault: str) -> VaultHealthCheckResult:
        structured = await self._call_tool(
            "vault_health_check",
            {"vault": vault, "chainId": self._chain_id_value()},
            tx_preparation=False,
        )
        return self._parse_result(
            "vault_health_check", structured, VaultHealthCheckResult
        )

    async def predict_vault_address(
        self,
        *,
        factory: str | None,
        asset: str,
        name: str,
        symbol: str,
        authority: str,
        salt: str,
    ) -> FactoryPredictVaultAddressResult:
        structured = await self._call_tool(
            "factory_predict_vault_address",
            {
                "chainId": self._chain_id_value(),
                "factory": factory,
                "asset": asset,
                "name": name,
                "symbol": symbol,
                "authority": authority,
                "salt": salt,
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "factory_predict_vault_address",
            structured,
            FactoryPredictVaultAddressResult,
        )

    async def prepare_create_vault(
        self,
        *,
        from_address: str,
        factory: str | None,
        asset: str,
        name: str,
        symbol: str,
        authority: str,
        salt: str,
    ) -> FactoryCreateVaultPrepareResult:
        structured = await self._call_tool(
            "factory_create_vault_prepare",
            {
                "chainId": self._chain_id_value(),
                "factory": factory,
                "from": from_address,
                "asset": asset,
                "name": name,
                "symbol": symbol,
                "authority": authority,
                "salt": salt,
            },
            tx_preparation=True,
        )
        return self._parse_result(
            "factory_create_vault_prepare",
            structured,
            FactoryCreateVaultPrepareResult,
        )

    async def vault_bootstrap(
        self,
        *,
        factory: str | None,
        asset: str,
        name: str,
        symbol: str,
        salt: str,
        signer_address: str | None = None,
        mode: VaultBootstrapMode = "plan",
        authority_mode: VaultBootstrapAuthorityMode | None = None,
        authority: str | None = None,
        executor: str | None = None,
        create_account_context: bool | None = None,
        create_funding_policy: bool | None = None,
        account_context_options: Mapping[str, Any] | None = None,
        funding_policy_options: Mapping[str, Any] | None = None,
    ) -> VaultBootstrapResult:
        plan_mode = "plan" if mode == "execute" else mode
        structured = await self._call_tool(
            "vault_bootstrap",
            {
                "chainId": self._chain_id_value(),
                "factory": factory,
                "asset": asset,
                "name": name,
                "symbol": symbol,
                "salt": salt,
                "signerAddress": signer_address,
                "mode": plan_mode,
                "authorityMode": authority_mode,
                "authority": authority,
                "executor": executor,
                "createAccountContext": create_account_context,
                "createFundingPolicy": create_funding_policy,
                "accountContextOptions": dict(account_context_options)
                if account_context_options is not None
                else None,
                "fundingPolicyOptions": dict(funding_policy_options)
                if funding_policy_options is not None
                else None,
            },
            tx_preparation=False,
            required_tools=tuple(MANDATED_BOOTSTRAP_REQUIRED_TOOLS),
        )
        result = self._parse_result(
            "vault_bootstrap", structured, VaultBootstrapResult
        )
        if mode != "execute":
            return result

        if result.createTx is None or result.createTx.txRequest is None:
            raise MandatedVaultBridgeUnavailableError(
                "vault_bootstrap --confirm could not obtain a platform-executable transaction request."
            )
        tx = result.createTx.txRequest
        platform = PlatformWalletClient(self._config)
        try:
            executed = platform.execute(
                [
                    {
                        "to": tx.to,
                        "data": tx.data,
                        "value": tx.value,
                        "chainId": self._chain_id_value(),
                    }
                ]
            )
        finally:
            platform.close()
        step_results = executed.get("results") or []
        tx_hash = None
        if isinstance(step_results, list) and step_results:
            first = step_results[0]
            if isinstance(first, dict):
                tx_hash = first.get("hash") or first.get("txHash")
        result.mode = "execute"
        result.deploymentStatus = "submitted"
        result.createTx.mode = "execute"
        result.createTx.txHash = str(tx_hash) if tx_hash else None
        result.createTx.receiptStatus = None
        return result

    async def create_agent_account_context(
        self,
        *,
        agent_id: str,
        vault: str,
        authority: str,
        executor: str,
        asset_registry_ref: str | None = None,
        funding_policy_ref: str | None = None,
        defaults: Mapping[str, Any] | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> AgentAccountContextCreateResult:
        structured = await self._call_tool(
            "agent_account_context_create",
            {
                "agentId": agent_id,
                "chainId": self._chain_id_value(),
                "vault": vault,
                "authority": authority,
                "executor": executor,
                "assetRegistryRef": asset_registry_ref,
                "fundingPolicyRef": funding_policy_ref,
                "defaults": defaults,
                "createdAt": created_at,
                "updatedAt": updated_at,
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "agent_account_context_create",
            structured,
            AgentAccountContextCreateResult,
        )

    async def create_agent_funding_policy(
        self,
        *,
        policy_id: str,
        allowed_token_addresses: Sequence[str] | None = None,
        allowed_recipients: Sequence[str] | None = None,
        max_amount_per_tx: str | None = None,
        max_amount_per_window: str | None = None,
        window_seconds: int | None = None,
        expires_at: str | None = None,
        repeatable: bool | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> AgentFundingPolicyCreateResult:
        structured = await self._call_tool(
            "agent_funding_policy_create",
            {
                "policyId": policy_id,
                "allowedTokenAddresses": list(allowed_token_addresses)
                if allowed_token_addresses is not None
                else None,
                "allowedRecipients": list(allowed_recipients)
                if allowed_recipients is not None
                else None,
                "maxAmountPerTx": max_amount_per_tx,
                "maxAmountPerWindow": max_amount_per_window,
                "windowSeconds": window_seconds,
                "expiresAt": expires_at,
                "repeatable": repeatable,
                "createdAt": created_at,
                "updatedAt": updated_at,
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "agent_funding_policy_create",
            structured,
            AgentFundingPolicyCreateResult,
        )

    async def build_agent_fund_and_action_plan(
        self,
        *,
        account_context: Mapping[str, Any],
        funding_target: Mapping[str, Any],
        funding_context: Mapping[str, Any],
        follow_up_action: Mapping[str, Any],
        funding_policy: Mapping[str, Any] | None = None,
    ) -> FundAndActionPlanResult:
        structured = await self._call_tool(
            "agent_build_fund_and_action_plan",
            {
                "accountContext": dict(account_context),
                "fundingPolicy": dict(funding_policy) if funding_policy else None,
                "fundingTarget": dict(funding_target),
                "fundingContext": dict(funding_context),
                "followUpAction": dict(follow_up_action),
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "agent_build_fund_and_action_plan",
            structured,
            FundAndActionPlanResult,
        )

    async def create_agent_fund_and_action_session(
        self,
        *,
        fund_and_action_plan: Mapping[str, Any],
        session_id: str | None = None,
        created_at: str | None = None,
    ) -> FundAndActionSessionCreateResult:
        structured = await self._call_tool(
            "agent_fund_and_action_session_create",
            {
                "fundAndActionPlan": dict(fund_and_action_plan),
                "sessionId": session_id,
                "createdAt": created_at,
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "agent_fund_and_action_session_create",
            structured,
            FundAndActionSessionCreateResult,
        )

    async def next_agent_fund_and_action_session_step(
        self,
        *,
        session: Mapping[str, Any],
    ) -> FundAndActionSessionNextStepResult:
        structured = await self._call_tool(
            "agent_fund_and_action_session_next_step",
            {"session": dict(session)},
            tx_preparation=False,
        )
        return self._parse_result(
            "agent_fund_and_action_session_next_step",
            structured,
            FundAndActionSessionNextStepResult,
        )

    async def apply_agent_fund_and_action_session_event(
        self,
        *,
        session: Mapping[str, Any],
        event: Mapping[str, Any],
    ) -> FundAndActionSessionCreateResult:
        structured = await self._call_tool(
            "agent_fund_and_action_session_apply_event",
            {
                "session": dict(session),
                "event": dict(event),
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "agent_fund_and_action_session_apply_event",
            structured,
            FundAndActionSessionCreateResult,
        )

    async def create_agent_follow_up_action_result(
        self,
        *,
        follow_up_action_plan: Mapping[str, Any],
        status: str,
        updated_at: str,
        started_at: str | None = None,
        completed_at: str | None = None,
        attempt: int | None = None,
        reference: Mapping[str, Any] | None = None,
        output: Mapping[str, Any] | None = None,
        error: Mapping[str, Any] | None = None,
    ) -> FollowUpActionResultCreateResult:
        structured = await self._call_tool(
            "agent_follow_up_action_result_create",
            {
                "followUpActionPlan": dict(follow_up_action_plan),
                "status": status,
                "updatedAt": updated_at,
                "startedAt": started_at,
                "completedAt": completed_at,
                "attempt": attempt,
                "reference": dict(reference) if reference else None,
                "output": dict(output) if output else None,
                "error": dict(error) if error else None,
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "agent_follow_up_action_result_create",
            structured,
            FollowUpActionResultCreateResult,
        )

    async def create_vault_asset_transfer_result(
        self,
        *,
        asset_transfer_plan: Mapping[str, Any],
        status: str,
        updated_at: str,
        submitted_at: str | None = None,
        completed_at: str | None = None,
        attempt: int | None = None,
        chain_id: int | None = None,
        tx_hash: str | None = None,
        receipt: Mapping[str, Any] | None = None,
        output: Mapping[str, Any] | None = None,
        error: Mapping[str, Any] | None = None,
    ) -> AssetTransferResultCreateResult:
        structured = await self._call_tool(
            "vault_asset_transfer_result_create",
            {
                "assetTransferPlan": dict(asset_transfer_plan),
                "status": status,
                "updatedAt": updated_at,
                "submittedAt": submitted_at,
                "completedAt": completed_at,
                "attempt": attempt,
                "chainId": chain_id,
                "txHash": tx_hash,
                "receipt": dict(receipt) if receipt else None,
                "output": dict(output) if output else None,
                "error": dict(error) if error else None,
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "vault_asset_transfer_result_create",
            structured,
            AssetTransferResultCreateResult,
        )

    async def check_vault_asset_transfer_policy(
        self,
        *,
        funding_policy: Mapping[str, Any],
        token_address: str,
        to: str,
        amount_raw: str,
        now: str | None = None,
        current_spent_in_window: str | None = None,
    ) -> PolicyCheckResult:
        structured = await self._call_tool(
            "vault_check_asset_transfer_policy",
            {
                "fundingPolicy": dict(funding_policy),
                "tokenAddress": token_address,
                "to": to,
                "amountRaw": amount_raw,
                "now": now,
                "currentSpentInWindow": current_spent_in_window,
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "vault_check_asset_transfer_policy",
            structured,
            PolicyCheckResult,
        )

    async def build_vault_asset_transfer_plan_from_context(
        self,
        *,
        account_context: Mapping[str, Any],
        token_address: str,
        to: str,
        amount_raw: str,
        nonce: str,
        deadline: str,
        authority_epoch: str,
        funding_policy: Mapping[str, Any] | None = None,
        allowed_adapters_root: str | None = None,
        max_drawdown_bps: str | None = None,
        max_cumulative_drawdown_bps: str | None = None,
        payload_binding: PayloadBinding | None = None,
        extensions: str | None = None,
        symbol: str | None = None,
        decimals: int | None = None,
        policy_evaluation: Mapping[str, Any] | None = None,
    ) -> AssetTransferPlanWithContextResult:
        structured = await self._call_tool(
            "vault_build_asset_transfer_plan_from_context",
            {
                "accountContext": dict(account_context),
                "fundingPolicy": dict(funding_policy) if funding_policy else None,
                "tokenAddress": token_address,
                "to": to,
                "amountRaw": amount_raw,
                "nonce": nonce,
                "deadline": deadline,
                "authorityEpoch": authority_epoch,
                "allowedAdaptersRoot": allowed_adapters_root,
                "maxDrawdownBps": max_drawdown_bps,
                "maxCumulativeDrawdownBps": max_cumulative_drawdown_bps,
                "payloadBinding": payload_binding,
                "extensions": extensions,
                "symbol": symbol,
                "decimals": decimals,
                "policyEvaluation": dict(policy_evaluation)
                if policy_evaluation
                else None,
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "vault_build_asset_transfer_plan_from_context",
            structured,
            AssetTransferPlanWithContextResult,
        )

    async def simulate_vault_asset_transfer_from_context(
        self,
        *,
        account_context: Mapping[str, Any],
        token_address: str,
        to: str,
        amount_raw: str,
        nonce: str,
        deadline: str,
        authority_epoch: str,
        signature: str,
        adapter_proofs: Sequence[Sequence[str]],
        funding_policy: Mapping[str, Any] | None = None,
        from_address: str | None = None,
        allowed_adapters_root: str | None = None,
        max_drawdown_bps: str | None = None,
        max_cumulative_drawdown_bps: str | None = None,
        payload_binding: PayloadBinding | None = None,
        extensions: str | None = None,
        symbol: str | None = None,
        decimals: int | None = None,
        policy_evaluation: Mapping[str, Any] | None = None,
    ) -> AssetTransferSimulateWithContextResult:
        structured = await self._call_tool(
            "vault_simulate_asset_transfer_from_context",
            {
                "accountContext": dict(account_context),
                "fundingPolicy": dict(funding_policy) if funding_policy else None,
                "from": from_address,
                "tokenAddress": token_address,
                "to": to,
                "amountRaw": amount_raw,
                "nonce": nonce,
                "deadline": deadline,
                "authorityEpoch": authority_epoch,
                "allowedAdaptersRoot": allowed_adapters_root,
                "maxDrawdownBps": max_drawdown_bps,
                "maxCumulativeDrawdownBps": max_cumulative_drawdown_bps,
                "payloadBinding": payload_binding,
                "extensions": extensions,
                "symbol": symbol,
                "decimals": decimals,
                "policyEvaluation": dict(policy_evaluation)
                if policy_evaluation
                else None,
                "signature": signature,
                "adapterProofs": [list(group) for group in adapter_proofs],
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "vault_simulate_asset_transfer_from_context",
            structured,
            AssetTransferSimulateWithContextResult,
        )

    async def prepare_vault_asset_transfer_from_context(
        self,
        *,
        account_context: Mapping[str, Any],
        token_address: str,
        to: str,
        amount_raw: str,
        nonce: str,
        deadline: str,
        authority_epoch: str,
        signature: str,
        adapter_proofs: Sequence[Sequence[str]],
        funding_policy: Mapping[str, Any] | None = None,
        from_address: str | None = None,
        allowed_adapters_root: str | None = None,
        max_drawdown_bps: str | None = None,
        max_cumulative_drawdown_bps: str | None = None,
        payload_binding: PayloadBinding | None = None,
        extensions: str | None = None,
        symbol: str | None = None,
        decimals: int | None = None,
        policy_evaluation: Mapping[str, Any] | None = None,
    ) -> AssetTransferPrepareWithContextResult:
        structured = await self._call_tool(
            "vault_prepare_asset_transfer_from_context",
            {
                "accountContext": dict(account_context),
                "fundingPolicy": dict(funding_policy) if funding_policy else None,
                "from": from_address,
                "tokenAddress": token_address,
                "to": to,
                "amountRaw": amount_raw,
                "nonce": nonce,
                "deadline": deadline,
                "authorityEpoch": authority_epoch,
                "allowedAdaptersRoot": allowed_adapters_root,
                "maxDrawdownBps": max_drawdown_bps,
                "maxCumulativeDrawdownBps": max_cumulative_drawdown_bps,
                "payloadBinding": payload_binding,
                "extensions": extensions,
                "symbol": symbol,
                "decimals": decimals,
                "policyEvaluation": dict(policy_evaluation)
                if policy_evaluation
                else None,
                "signature": signature,
                "adapterProofs": [list(group) for group in adapter_proofs],
            },
            tx_preparation=False,
        )
        return self._parse_result(
            "vault_prepare_asset_transfer_from_context",
            structured,
            AssetTransferPrepareWithContextResult,
        )

    async def _call_tool(
        self,
        tool_name: str,
        arguments: Mapping[str, Any],
        *,
        tx_preparation: bool,
        required_tools: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        await self.connect()
        self._assert_tool_available(
            tool_name,
            tx_preparation=tx_preparation,
            required_tools=required_tools,
        )

        filtered_arguments = _drop_none_values(arguments)
        if not isinstance(filtered_arguments, dict):
            raise MandatedVaultBridgeUnavailableError(
                f"Mandated SDK bridge {tool_name} arguments did not normalize to an object."
            )

        try:
            return await self._require_client().call(tool_name, filtered_arguments)
        except MandatedSdkError as error:
            raise MandatedVaultBridgeUnavailableError(str(error)) from error

    def _assert_tool_available(
        self,
        tool_name: str,
        *,
        tx_preparation: bool,
        required_tools: Sequence[str] | None = None,
    ) -> None:
        if tool_name not in self._available_tools:
            raise MandatedVaultBridgeMissingToolsError([tool_name], operation=tool_name)

        if required_tools is not None:
            missing = frozenset(required_tools).difference(self.available_tools)
            if missing:
                raise MandatedVaultBridgeMissingToolsError(
                    sorted(missing),
                    operation=tool_name,
                )
            return

        if tx_preparation and self.missing_required_tools:
            raise MandatedVaultBridgeMissingToolsError(
                sorted(self.missing_required_tools),
                operation=tool_name,
            )

    def _require_client(self) -> MandatedSdkClient:
        if self._sdk_client is None:
            raise MandatedVaultBridgeUnavailableError(
                "Mandated SDK bridge is not connected."
            )
        return self._sdk_client

    def _chain_id_value(self) -> int:
        return self._config.mandated_chain_id or int(self._config.chain_id)

    def _parse_result(
        self,
        tool_name: str,
        structured: Mapping[str, Any],
        model: type[T_Result],
    ) -> T_Result:
        tool_error = structured.get("error")
        if isinstance(tool_error, dict):
            parsed_error = BridgeToolError.model_validate(tool_error)
            raise MandatedVaultBridgeError(
                f"Mandated SDK bridge tool {tool_name} failed: {parsed_error.code} {parsed_error.message}"
            )

        payload = structured.get("result")
        if not isinstance(payload, dict):
            raise ValueError(f"Malformed {tool_name} response: missing result object.")

        try:
            return model.model_validate(payload)
        except ValidationError as error:
            raise ValueError(f"Malformed {tool_name} response: {error}") from error
