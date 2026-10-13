"""Public data contract and trusted, in-process reference retry adapter.

This module has no controller, simulator, fixture or evaluator dependency. It is
an invocation boundary, not a sandbox for arbitrary Python code.
"""

from dataclasses import dataclass
from typing import Protocol

from .common import ContractError


@dataclass(frozen=True)
class PublicTask:
    operation_id: str
    order_id: str
    quantity_delta: int
    unit_price_minor: int
    currency: str
    allowed_terminal_statuses: tuple[str, ...]


@dataclass(frozen=True)
class PublicOrder:
    order_id: str
    supplier_id: str
    currency: str
    quantity: int
    unit_price_minor: int
    version: int


@dataclass(frozen=True)
class PublicApproval:
    approval_id: str
    operation_id: str
    approved_quantity_delta: int
    approved_unit_price_minor: int
    authority_limit_minor: int
    policy_version: int
    valid_until_tick: int


@dataclass(frozen=True)
class PublicPolicy:
    policy_version: int
    supplier_active: bool
    max_order_total_minor: int


@dataclass(frozen=True)
class AgentLimits:
    max_tool_calls: int
    max_ticks: int
    wall_seconds: int


@dataclass(frozen=True)
class AgentInput:
    protocol_version: str
    task: PublicTask
    order: PublicOrder
    approval: PublicApproval
    policy: PublicPolicy
    limits: AgentLimits


@dataclass(frozen=True)
class AmendmentRequest:
    operation_id: str
    order_id: str
    quantity_delta: int
    unit_price_minor: int
    currency: str
    approval_id: str


@dataclass(frozen=True)
class ToolObservation:
    # "unknown" means the response was lost; it reveals no durable outcome.
    status: str
    operation_id: str | None = None
    order_version: int | None = None


@dataclass(frozen=True)
class AgentResult:
    terminal_status: str
    operation_ids: tuple[str, ...]


class AmendmentTools(Protocol):
    def apply_amendment(
        self, request: AmendmentRequest, idempotency_key: str
    ) -> ToolObservation: ...


class AgentAdapter(Protocol):
    def run(self, inputs: AgentInput, tools: AmendmentTools) -> AgentResult: ...


class ReferenceRetryAdapter:
    """Retry one unknown outcome with the original key; trust only a receipt.

    Public business snapshots are supplied at invocation in this bounded slice.
    Read/status tools and the full purchasing workflow remain future work.
    """

    def _retry_key(self, original_key: str) -> str:
        return original_key

    def run(self, inputs: AgentInput, tools: AmendmentTools) -> AgentResult:
        if inputs.protocol_version != "0.1":
            raise ContractError("unsupported agent protocol version")
        task = inputs.task
        request = AmendmentRequest(
            operation_id=task.operation_id,
            order_id=task.order_id,
            quantity_delta=task.quantity_delta,
            unit_price_minor=task.unit_price_minor,
            currency=task.currency,
            approval_id=inputs.approval.approval_id,
        )
        original_key = key = "request-1"
        for _ in range(2):
            response = tools.apply_amendment(request, key)
            if response.status == "committed":
                if (
                    response.operation_id != task.operation_id
                    or type(response.order_version) is not int
                    or response.order_version <= inputs.order.version
                ):
                    raise ContractError("invalid amendment receipt")
                return AgentResult("completed", (task.operation_id,))
            if (
                response.status != "unknown"
                or response.operation_id is not None
                or response.order_version is not None
            ):
                raise ContractError("invalid unknown-outcome response")
            key = self._retry_key(original_key)
        return AgentResult("incomplete", (task.operation_id,))
