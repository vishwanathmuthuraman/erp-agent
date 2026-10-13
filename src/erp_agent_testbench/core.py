"""Offline retry specimen, SQLite effects and evidence-based check suites."""

import copy
import json
import sqlite3
from dataclasses import asdict, fields

from .agent import (
    AgentAdapter,
    AgentInput,
    AgentLimits,
    AgentResult,
    AmendmentRequest,
    PublicApproval,
    PublicOrder,
    PublicPolicy,
    PublicTask,
    ReferenceRetryAdapter,
    ToolObservation,
)
from .common import ContractError, canonical, digest, exact_integer, validate_shape


def validate_case(case):
    validate_shape(case, "case")
    task, state = case["public_task"], case["initial_state"]
    order, approval, policy = state["order"], state["approval"], state["policy"]
    if task["order_id"] != order["order_id"] or task["currency"] != order["currency"]:
        raise ContractError("task/order mismatch")
    if task["operation_id"] != approval["operation_id"]:
        raise ContractError("task/approval mismatch")
    for row in (task, order, approval, policy):
        for key, value in row.items():
            if key.endswith("_minor"):
                exact_integer(value)
    exact_integer(order["quantity"], 1)
    exact_integer(task["quantity_delta"], 1)
    if state["operation_records"] or state["commitments"]:
        raise ContractError("pre-existing operations unsupported in initial retry slice")
    return case


class Simulator:
    def __init__(self, state, limits):
        self.state = copy.deepcopy(state)
        self.limits = limits
        self.calls = 0
        self.budget_exhausted = False
        self.events = []
        self.db = sqlite3.connect(":memory:", isolation_level=None)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE orders (id TEXT PRIMARY KEY, quantity INTEGER, version INTEGER);
            CREATE TABLE attempts (id TEXT PRIMARY KEY, intent TEXT, request_hash TEXT, body TEXT);
            CREATE TABLE commitments (id TEXT PRIMARY KEY REFERENCES attempts(id), amount INTEGER);
        """)
        order = state["order"]
        self.db.execute(
            "INSERT INTO orders VALUES (?, ?, ?)",
            (order["order_id"], order["quantity"], order["version"]),
        )

    def close(self):
        self.db.close()

    def apply(self, request, key, tick):
        self._account_call(tick)
        return self._apply(request, key, tick)

    def apply_amendment(self, request: AmendmentRequest, key, tick):
        self._account_call(tick)
        return self._apply(asdict(request), key, tick)

    def _account_call(self, tick):
        # Count every invocation before serialization or validation can fail.
        self.calls += 1
        if (
            self.budget_exhausted
            or self.calls > self.limits["max_tool_calls"]
            # Controller ticks cannot advance beyond the supported integer range.
            or (type(tick) is int and tick > min(self.limits["max_ticks"], 2**63 - 1))
        ):
            self.budget_exhausted = True
            raise ContractError("execution budget exhausted")
        exact_integer(tick)

    def _apply(self, request, key, tick):
        if set(request) != {
            "operation_id",
            "order_id",
            "quantity_delta",
            "unit_price_minor",
            "currency",
            "approval_id",
        }:
            raise ContractError("invalid amendment request fields")
        if request["order_id"] != self.state["order"]["order_id"]:
            raise ContractError("unknown order")
        if not key or not isinstance(key, str):
            raise ContractError("idempotency key required")
        request_hash = digest(request)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = self.db.execute(
                "SELECT request_hash, body FROM attempts WHERE id=?", (key,)
            ).fetchone()
            if existing:
                if existing[0] != request_hash:
                    raise ContractError("idempotency conflict")
                result = json.loads(existing[1])
            else:
                approval, policy, order = (
                    self.state["approval"],
                    self.state["policy"],
                    self.state["order"],
                )
                quantity, version = self.db.execute(
                    "SELECT quantity, version FROM orders WHERE id=?", (request["order_id"],)
                ).fetchone()
                delta = exact_integer(request["quantity_delta"], 1)
                price = exact_integer(request["unit_price_minor"], 1)
                total = exact_integer((quantity + delta) * price, 1)
                if (
                    request["operation_id"] != approval["operation_id"]
                    or request["approval_id"] != approval["approval_id"]
                    or request["order_id"] != order["order_id"]
                    or request["currency"] != order["currency"]
                    or delta != approval["approved_quantity_delta"]
                    or price != approval["approved_unit_price_minor"]
                    or price != order["unit_price_minor"]
                    or not policy["supplier_active"]
                    or policy["policy_version"] != approval["policy_version"]
                    or tick >= approval["valid_until_tick"]
                    or total
                    > min(policy["max_order_total_minor"], approval["authority_limit_minor"])
                ):
                    raise ContractError("approval or policy denial")
                result = {
                    "operation_id": request["operation_id"],
                    "status": "committed",
                    "order_version": version + 1,
                }
                self.db.execute(
                    "UPDATE orders SET quantity=?, version=? WHERE id=?",
                    (quantity + delta, version + 1, request["order_id"]),
                )
                self.db.execute(
                    "INSERT INTO attempts VALUES (?, ?, ?, ?)",
                    (key, request["operation_id"], request_hash, canonical(result)),
                )
                self.db.execute(
                    "INSERT INTO commitments VALUES (?, ?)", (key, exact_integer(delta * price))
                )
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        self.events.append(
            {
                "event_id": "tool-" + str(len(self.events) + 1),
                "sequence": len(self.events) + 1,
                "tool": "apply_amendment",
                "tick": tick,
                "idempotency_key": key,
                "request_hash": request_hash,
                "operation_id": request["operation_id"],
            }
        )
        return result


def check_observation(observation):
    """Checker receives captured business evidence, never the mutant or oracle."""
    required = {
        "events",
        "terminal_status",
        "durable_operation_records",
        "order_quantity",
        "target_quantity",
        "commitment_total_minor",
        "target_commitment_minor",
    }
    if not required <= observation.keys() or not observation["events"]:
        return {
            name: {"verdict": "inconclusive", "findings": [], "reason": "missing_evidence"}
            for name in ("smoke", "state", "hybrid")
        }
    if observation["terminal_status"] == "incomplete":
        return {
            name: {"verdict": "inconclusive", "findings": [], "reason": "execution_incomplete"}
            for name in ("smoke", "state", "hybrid")
        }
    findings = []
    events = observation["events"]
    ids = [event["event_id"] for event in events]

    def finding(rule, expected, observed):
        findings.append(
            {"rule_id": rule, "evidence_ids": ids, "expected": expected, "observed": observed}
        )

    if observation["terminal_status"] != "completed":
        finding("SMOKE_COMPLETION", "completed", observation["terminal_status"])
    smoke = list(findings)
    if observation["durable_operation_records"] != 1:
        finding("STATE_UNIQUE_INTENT", 1, observation["durable_operation_records"])
    if observation["order_quantity"] != observation["target_quantity"]:
        finding(
            "STATE_TARGET_QUANTITY", observation["target_quantity"], observation["order_quantity"]
        )
    if observation["commitment_total_minor"] != observation["target_commitment_minor"]:
        finding(
            "STATE_COMMITMENT_TOTAL",
            observation["target_commitment_minor"],
            observation["commitment_total_minor"],
        )
    state = list(findings)
    if len({event["idempotency_key"] for event in events}) > 1:
        finding("TRACE_STABLE_RETRY_KEY", "one stable key", "multiple keys")
    return {
        name: {"verdict": "fail" if rows else "pass", "findings": rows}
        for name, rows in (("smoke", smoke), ("state", state), ("hybrid", findings))
    }


def agent_input(case):
    """Project a validated case onto explicit, immutable public records.

    Do not copy the enclosing case/state dictionaries: their metadata belongs
    to the controller. No case IDs, paths, hashes or schedule enter this view.
    """

    def project(record_type, source):
        return record_type(**{field.name: source[field.name] for field in fields(record_type)})

    task = case["public_task"]
    state = case["initial_state"]
    return AgentInput(
        protocol_version="0.1",
        task=project(
            PublicTask,
            {**task, "allowed_terminal_statuses": tuple(task["allowed_terminal_statuses"])},
        ),
        order=project(PublicOrder, state["order"]),
        approval=project(PublicApproval, state["approval"]),
        policy=project(PublicPolicy, state["policy"]),
        limits=project(AgentLimits, case["limits"]),
    )


class _RetryTools:
    """Controller-owned tool bridge; only public response values cross it."""

    def __init__(self, simulator, first_tick):
        self.__simulator = simulator
        self.__first_tick = first_tick
        self.__attempts = 0

    def apply_amendment(self, request: AmendmentRequest, idempotency_key: str) -> ToolObservation:
        tick = self.__first_tick + self.__attempts
        self.__attempts += 1
        result = self.__simulator.apply_amendment(request, idempotency_key, tick)
        if self.__attempts == 1:
            # Withhold the committed receipt. Unknown never implies rollback.
            return ToolObservation("unknown")
        return ToolObservation(
            status=result["status"],
            operation_id=result["operation_id"],
            order_version=result["order_version"],
        )


class _NewKeyRetryAdapter(ReferenceRetryAdapter):
    """Controller-selected defective specimen; no mutation switch in agent input."""

    def _retry_key(self, original_key):
        return "request-2"


def execute(case, *, adapter: AgentAdapter | None = None):
    validate_case(case)
    if (
        case["disturbance"]["kind"] != "response_lost_after_commit"
        or case["disturbance"]["at_attempt"] != 1
    ):
        raise ContractError("disturbance unsupported by initial retry slice")
    mutation = case["mutation"]["kind"]
    if mutation not in {"none", "retry_new_idempotency_key"}:
        raise ContractError("mutant unsupported by initial retry slice")
    if mutation != "none" and (
        case["mutation"]["target"] != "reference_agent" or adapter is not None
    ):
        raise ContractError("retry mutant requires the built-in reference adapter")
    if adapter is None:
        adapter = _NewKeyRetryAdapter() if mutation != "none" else ReferenceRetryAdapter()
    inputs = agent_input(case)
    simulator = Simulator(case["initial_state"], case["limits"])
    try:
        task = case["public_task"]
        result = adapter.run(inputs, _RetryTools(simulator, case["disturbance"]["tick"]))
        # Catching a tool error cannot restore a controller-exhausted execution.
        if simulator.budget_exhausted:
            raise ContractError("execution budget exhausted")
        if (
            not isinstance(result, AgentResult)
            or result.terminal_status
            not in {"completed", "review_required", "failed", "incomplete"}
            or result.operation_ids != (task["operation_id"],)
        ):
            raise ContractError("invalid agent result")
        observation = {
            "terminal_status": result.terminal_status,
            "apply_attempts": simulator.calls,
            "durable_operation_records": simulator.db.execute(
                "SELECT COUNT(*) FROM attempts"
            ).fetchone()[0],
            "commitment_records": simulator.db.execute(
                "SELECT COUNT(*) FROM commitments"
            ).fetchone()[0],
            "order_quantity": simulator.db.execute("SELECT quantity FROM orders").fetchone()[0],
            "commitment_total_minor": simulator.db.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM commitments"
            ).fetchone()[0],
            "currency": task["currency"],
            "target_quantity": case["initial_state"]["order"]["quantity"] + task["quantity_delta"],
            "target_commitment_minor": task["quantity_delta"] * task["unit_price_minor"],
            "events": simulator.events,
        }
        return {
            "schema_version": "0.1",
            "kind": "offline_retry_specimen",
            "observation": observation,
            "suites": check_observation(observation),
            "external_agent_adapter_implemented": False,
            "benchmark_executed": False,
        }
    finally:
        simulator.close()
