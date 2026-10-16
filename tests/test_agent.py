import copy
import json
from dataclasses import FrozenInstanceError, asdict, replace
from pathlib import Path

import pytest

from erp_agent_testbench import core
from erp_agent_testbench.agent import (
    AgentResult,
    AmendmentRequest,
    ReferenceRetryAdapter,
    ToolObservation,
)
from erp_agent_testbench.common import ContractError

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def case():
    return json.loads((ROOT / "examples/clean-retry.case.json").read_text())


class ScriptedTools:
    """Public responses only; no simulator or controller needed by this adapter."""

    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def apply_amendment(self, request, idempotency_key):
        self.requests.append((request, idempotency_key))
        return next(self.responses)


@pytest.mark.parametrize("lost_response", [False, True])
def test_reference_uses_receipt_and_stable_key(case, lost_response):
    inputs = core.agent_input(case)
    receipt = ToolObservation("committed", inputs.task.operation_id, 2)
    tools = ScriptedTools(([ToolObservation("unknown")] if lost_response else []) + [receipt])
    result = ReferenceRetryAdapter().run(inputs, tools)
    assert result == AgentResult("completed", (inputs.task.operation_id,))
    assert len(tools.requests) == (2 if lost_response else 1)
    assert all(key == "request-1" for _, key in tools.requests)
    assert len({request for request, _ in tools.requests}) == 1
    request = tools.requests[0][0]
    assert request.quantity_delta == 3
    assert request.unit_price_minor == 1000
    assert request.approval_id == inputs.approval.approval_id


def test_two_unknown_responses_do_not_claim_completion(case):
    tools = ScriptedTools([ToolObservation("unknown"), ToolObservation("unknown")])
    result = ReferenceRetryAdapter().run(core.agent_input(case), tools)
    assert result.terminal_status == "incomplete"
    assert len(tools.requests) == 2


@pytest.mark.parametrize(
    "response",
    [
        ToolObservation("committed", "other-operation", 2),
        ToolObservation("committed", "op-example-001", True),
        ToolObservation("committed", "op-example-001", None),
        ToolObservation("committed", "op-example-001", 0),
        ToolObservation("committed", "op-example-001", 1),
        ToolObservation("unknown", "op-example-001", 2),
        ToolObservation("unexpected-status"),
    ],
)
def test_invalid_tool_observation_cannot_claim_completion(case, response):
    tools = ScriptedTools([response])
    with pytest.raises(ContractError, match="invalid"):
        ReferenceRetryAdapter().run(core.agent_input(case), tools)
    assert len(tools.requests) == 1


def test_unknown_agent_protocol_stops_before_tools(case):
    tools = ScriptedTools([])
    inputs = replace(core.agent_input(case), protocol_version="unsupported")
    with pytest.raises(ContractError, match="protocol version"):
        ReferenceRetryAdapter().run(inputs, tools)
    assert tools.requests == []


def test_public_projection_is_recursive_and_retains_business_records(case):
    baseline = core.agent_input(case)
    # Defense in depth at the projection itself; execute separately rejects
    # unknown case fields before this boundary is reached.
    tainted = copy.deepcopy(case)
    for row in (
        tainted,
        tainted["public_task"],
        tainted["initial_state"],
        tainted["initial_state"]["order"],
        tainted["initial_state"]["policy"],
        tainted["initial_state"]["approval"],
        tainted["limits"],
    ):
        row["metadata"] = {"ground_truth": {"expected_rule": "private-sentinel"}}
    projected = core.agent_input(tainted)
    assert projected == baseline
    assert "private-sentinel" not in json.dumps(asdict(projected))
    assert asdict(projected.order) == case["initial_state"]["order"]
    assert asdict(projected.policy) == case["initial_state"]["policy"]
    assert asdict(projected.approval) == case["initial_state"]["approval"]
    assert projected.task.allowed_terminal_statuses == ("completed",)


def test_public_records_are_immutable_and_detached(case):
    inputs = core.agent_input(case)
    for record, field, value in (
        (inputs, "protocol_version", "changed"),
        (inputs.task, "quantity_delta", 99),
        (inputs.order, "quantity", 99),
        (inputs.approval, "authority_limit_minor", 0),
        (inputs.policy, "supplier_active", False),
        (inputs.limits, "max_tool_calls", 999),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(record, field, value)
    case["public_task"]["allowed_terminal_statuses"].append("failed")
    case["initial_state"]["order"]["quantity"] = 999
    assert inputs.task.allowed_terminal_statuses == ("completed",)
    assert inputs.order.quantity == 10
    response = ToolObservation("unknown")
    with pytest.raises(FrozenInstanceError):
        response.status = "committed"


def test_controller_metadata_never_reaches_agent_or_suites(case, monkeypatch):
    captured_inputs, captured_responses, captured_bundles = [], [], []
    reference_run = ReferenceRetryAdapter.run
    check = core.check_observation

    def capture_run(self, inputs, tools):
        captured_inputs.append(asdict(inputs))

        class RecordingTools:
            def apply_amendment(self, request, idempotency_key):
                response = tools.apply_amendment(request, idempotency_key)
                captured_responses.append(asdict(response))
                return response

        return reference_run(self, inputs, RecordingTools())

    def capture_check(observation):
        captured_bundles.append(copy.deepcopy(observation))
        return check(observation)

    monkeypatch.setattr(ReferenceRetryAdapter, "run", capture_run)
    monkeypatch.setattr(core, "check_observation", capture_check)
    clean = core.execute(case)
    changed = copy.deepcopy(case)
    changed.update(
        case_id="private-case-sentinel",
        template_group="private-group-sentinel",
        split="heldout",
        seed=999,
        expected_result_file="private-oracle-sentinel.expected.json",
    )
    assert core.execute(changed) == clean
    changed["mutation"]["kind"] = "retry_new_idempotency_key"
    faulty = core.execute(changed)
    assert captured_inputs[0] == captured_inputs[1] == captured_inputs[2]
    # Identical first observations conceal whether the controller chose a mutant.
    assert (
        captured_responses[0]
        == captured_responses[2]
        == captured_responses[4]
        == {
            "status": "unknown",
            "operation_id": None,
            "order_version": None,
        }
    )
    serialized = json.dumps([captured_inputs, captured_responses, captured_bundles])
    for forbidden in (
        "private-",
        "heldout",
        "mutation",
        "disturbance",
        "expected_result_file",
        "template_group",
        "case_id",
        "retry_new_idempotency_key",
    ):
        assert forbidden not in serialized
    assert clean["observation"]["order_quantity"] == 13
    assert faulty["observation"]["order_quantity"] == 16
    assert [row["verdict"] for row in clean["suites"].values()] == ["pass", "pass", "pass"]
    assert [row["verdict"] for row in faulty["suites"].values()] == ["pass", "fail", "fail"]
    assert captured_bundles[-1]["events"][1]["idempotency_key"] == "request-2"


def test_independent_stub_uses_same_public_boundary(case):
    class StubAdapter:
        def run(self, inputs, tools):
            task = inputs.task
            request = AmendmentRequest(
                task.operation_id,
                task.order_id,
                task.quantity_delta,
                task.unit_price_minor,
                task.currency,
                inputs.approval.approval_id,
            )
            assert tools.apply_amendment(request, "stub-key") == ToolObservation("unknown")
            response = tools.apply_amendment(request, "stub-key")
            assert response == ToolObservation("committed", task.operation_id, 2)
            return AgentResult("completed", (task.operation_id,))

    result = core.execute(case, adapter=StubAdapter())
    assert result["observation"]["durable_operation_records"] == 1
    assert result["observation"]["order_quantity"] == 13
    assert result["observation"]["commitment_total_minor"] == 3000
    assert all(row["verdict"] == "pass" for row in result["suites"].values())


@pytest.mark.parametrize("limit,value", [("max_tool_calls", 2), ("max_ticks", 6)])
@pytest.mark.parametrize("attempts", [2, 3])
def test_caught_budget_exhaustion_cannot_become_completion(case, limit, value, attempts):
    case["limits"][limit] = value

    class CatchingAdapter:
        def run(self, inputs, tools):
            task = inputs.task
            request = AmendmentRequest(
                task.operation_id,
                task.order_id,
                task.quantity_delta,
                task.unit_price_minor,
                task.currency,
                inputs.approval.approval_id,
            )
            self.responses, self.errors = [], []
            for _ in range(attempts):
                try:
                    self.responses.append(tools.apply_amendment(request, "same-key"))
                except ContractError as exc:
                    self.errors.append(str(exc))
            self.result = AgentResult("completed", (task.operation_id,))
            return self.result

    adapter = CatchingAdapter()
    if attempts > 2:
        with pytest.raises(ContractError, match="execution budget exhausted"):
            core.execute(case, adapter=adapter)
    else:
        result = core.execute(case, adapter=adapter)
        assert result["observation"]["apply_attempts"] == 2
        assert result["observation"]["durable_operation_records"] == 1
        assert result["observation"]["order_quantity"] == 13
        assert result["observation"]["commitment_total_minor"] == 3000
        assert all(row["verdict"] == "pass" for row in result["suites"].values())
    operation_id = case["public_task"]["operation_id"]
    assert adapter.responses == [
        ToolObservation("unknown"),
        ToolObservation("committed", operation_id, 2),
    ]
    assert adapter.errors == ["execution budget exhausted"] * (attempts - 2)
    assert adapter.result == AgentResult("completed", (operation_id,))


@pytest.mark.parametrize("limit,exact_limit", [("max_tool_calls", 3), ("max_ticks", 7)])
@pytest.mark.parametrize("over_budget", [False, True])
def test_caught_rejected_request_cannot_bypass_budgets(
    case, monkeypatch, limit, exact_limit, over_budget
):
    case["limits"][limit] = exact_limit - int(over_budget)

    class CatchingAdapter:
        def run(self, inputs, tools):
            task = inputs.task
            request = AmendmentRequest(
                task.operation_id,
                task.order_id,
                task.quantity_delta,
                task.unit_price_minor,
                task.currency,
                inputs.approval.approval_id,
            )
            assert tools.apply_amendment(request, "same-key") == ToolObservation("unknown")
            assert tools.apply_amendment(request, "same-key") == ToolObservation(
                "committed", task.operation_id, 2
            )
            try:
                tools.apply_amendment(replace(request, order_id="unknown-order"), "same-key")
            except ContractError as exc:
                self.error = str(exc)
            self.result = AgentResult("completed", (task.operation_id,))
            return self.result

    adapter = CatchingAdapter()
    if over_budget:

        def no_suites(observation):
            pytest.fail("exhausted execution must not reach the suites")

        monkeypatch.setattr(core, "check_observation", no_suites)
        with pytest.raises(ContractError, match="execution budget exhausted"):
            core.execute(case, adapter=adapter)
    else:
        result = core.execute(case, adapter=adapter)
        observation = result["observation"]
        assert observation["apply_attempts"] == 3
        assert observation["durable_operation_records"] == 1
        assert observation["commitment_records"] == 1
        assert observation["order_quantity"] == 13
        assert observation["commitment_total_minor"] == 3000
        assert [event["tick"] for event in observation["events"]] == [5, 6]
        assert all(row["verdict"] == "pass" for row in result["suites"].values())
    assert adapter.error == ("execution budget exhausted" if over_budget else "unknown order")
    assert adapter.result == AgentResult("completed", (case["public_task"]["operation_id"],))


@pytest.mark.parametrize("limit", ["max_tool_calls", "max_ticks"])
@pytest.mark.parametrize("permitted_calls", [2, 3, 4])
@pytest.mark.parametrize("rejection", ["plain_dict", "uncopyable_field"])
def test_serialization_failure_cannot_bypass_budgets(
    case, monkeypatch, limit, permitted_calls, rejection
):
    case["limits"][limit] = permitted_calls + (4 if limit == "max_ticks" else 0)

    class Uncopyable:
        def __deepcopy__(self, memo):
            raise TypeError("synthetic serialization failure")

    class CatchingAdapter:
        def run(self, inputs, tools):
            task = inputs.task
            request = AmendmentRequest(
                task.operation_id,
                task.order_id,
                task.quantity_delta,
                task.unit_price_minor,
                task.currency,
                inputs.approval.approval_id,
            )
            assert tools.apply_amendment(request, "same-key") == ToolObservation("unknown")
            receipt = ToolObservation("committed", task.operation_id, 2)
            assert tools.apply_amendment(request, "same-key") == receipt
            invalid_request = (
                asdict(request)
                if rejection == "plain_dict"
                else replace(request, currency=Uncopyable())
            )
            try:
                tools.apply_amendment(invalid_request, "unused-key")
            except (TypeError, ContractError) as exc:
                self.error = exc
            if permitted_calls == 4:
                # A serialization error inside the budget does not prevent recovery.
                assert tools.apply_amendment(request, "same-key") == receipt
            self.result = AgentResult("completed", (task.operation_id,))
            return self.result

    adapter = CatchingAdapter()
    if permitted_calls == 2:

        def no_suites(observation):
            pytest.fail("serialization failure must not hide an exhausted execution")

        monkeypatch.setattr(core, "check_observation", no_suites)
        with pytest.raises(ContractError, match="execution budget exhausted"):
            core.execute(case, adapter=adapter)
        assert type(adapter.error) is ContractError
        assert str(adapter.error) == "execution budget exhausted"
    else:
        result = core.execute(case, adapter=adapter)
        observation = result["observation"]
        assert observation["apply_attempts"] == permitted_calls
        assert observation["durable_operation_records"] == 1
        assert observation["commitment_records"] == 1
        assert observation["order_quantity"] == 13
        assert observation["commitment_total_minor"] == 3000
        assert [event["tick"] for event in observation["events"]] == (
            [5, 6, 8] if permitted_calls == 4 else [5, 6]
        )
        assert all(row["verdict"] == "pass" for row in result["suites"].values())
        assert type(adapter.error) is TypeError
        assert str(adapter.error) == (
            "asdict() should be called on dataclass instances"
            if rejection == "plain_dict"
            else "synthetic serialization failure"
        )
    assert adapter.result == AgentResult("completed", (case["public_task"]["operation_id"],))


@pytest.mark.parametrize("max_tool_calls", [2, 20])
@pytest.mark.parametrize("max_ticks", [2**63 - 1, 2**63 + 1])
@pytest.mark.parametrize("attempts", [2, 3])
def test_controller_tick_overflow_cannot_become_completion(
    case, monkeypatch, max_tool_calls, max_ticks, attempts
):
    case["disturbance"]["tick"] = 2**63 - 2
    case["initial_state"]["approval"]["valid_until_tick"] = 2**63 - 1
    case["limits"].update(max_tool_calls=max_tool_calls, max_ticks=max_ticks)

    class CatchingAdapter:
        def run(self, inputs, tools):
            task = inputs.task
            request = AmendmentRequest(
                task.operation_id,
                task.order_id,
                task.quantity_delta,
                task.unit_price_minor,
                task.currency,
                inputs.approval.approval_id,
            )
            self.responses, self.errors = [], []
            for _ in range(attempts):
                try:
                    self.responses.append(tools.apply_amendment(request, "same-key"))
                except ContractError as exc:
                    self.errors.append(str(exc))
            self.result = AgentResult("completed", (task.operation_id,))
            return self.result

    adapter = CatchingAdapter()
    if attempts == 3:

        def no_suites(observation):
            pytest.fail("controller tick overflow must not reach the suites")

        monkeypatch.setattr(core, "check_observation", no_suites)
        with pytest.raises(ContractError, match="execution budget exhausted"):
            core.execute(case, adapter=adapter)
    else:
        result = core.execute(case, adapter=adapter)
        observation = result["observation"]
        assert observation["apply_attempts"] == 2
        assert observation["durable_operation_records"] == 1
        assert observation["commitment_records"] == 1
        assert observation["order_quantity"] == 13
        assert observation["commitment_total_minor"] == 3000
        assert [event["tick"] for event in observation["events"]] == [2**63 - 2, 2**63 - 1]
        assert all(row["verdict"] == "pass" for row in result["suites"].values())
    operation_id = case["public_task"]["operation_id"]
    assert adapter.responses == [
        ToolObservation("unknown"),
        ToolObservation("committed", operation_id, 2),
    ]
    assert adapter.errors == ["execution budget exhausted"] * (attempts - 2)
    assert adapter.result == AgentResult("completed", (operation_id,))


def test_unknown_outcome_remains_inconclusive_despite_durable_effect(case):
    class StopAfterTimeout:
        def run(self, inputs, tools):
            task = inputs.task
            request = AmendmentRequest(
                task.operation_id,
                task.order_id,
                task.quantity_delta,
                task.unit_price_minor,
                task.currency,
                inputs.approval.approval_id,
            )
            assert tools.apply_amendment(request, "one") == ToolObservation("unknown")
            return AgentResult("incomplete", (task.operation_id,))

    result = core.execute(case, adapter=StopAfterTimeout())
    assert result["observation"]["order_quantity"] == 13
    assert result["observation"]["durable_operation_records"] == 1
    assert result["observation"]["terminal_status"] == "incomplete"
    for suite in result["suites"].values():
        assert suite == {
            "verdict": "inconclusive",
            "findings": [],
            "reason": "execution_incomplete",
        }


@pytest.mark.parametrize("wrong_target", [False, True])
def test_mutation_cannot_silently_target_another_adapter(case, monkeypatch, wrong_target):
    case["mutation"]["kind"] = "retry_new_idempotency_key"
    if wrong_target:
        case["mutation"]["target"] = "connector"

    def no_simulator(*args):
        pytest.fail("must reject unsupported target before allocating simulator")

    monkeypatch.setattr(core, "Simulator", no_simulator)
    with pytest.raises(ContractError, match="built-in reference"):
        core.execute(case, adapter=None if wrong_target else ReferenceRetryAdapter())


@pytest.mark.parametrize(
    "path",
    [
        (),
        ("public_task",),
        ("initial_state", "order"),
        ("initial_state", "approval"),
        ("initial_state", "policy"),
        ("limits",),
    ],
)
def test_nested_truth_in_case_is_rejected_before_adapter(case, path):
    row = case
    for key in path:
        row = row[key]
    row["ground_truth"] = {"label": "private-sentinel"}

    class UnreachableAdapter:
        def run(self, inputs, tools):
            pytest.fail("invalid case must not invoke the adapter")

    with pytest.raises(ContractError, match="schema violation"):
        core.execute(case, adapter=UnreachableAdapter())


@pytest.mark.parametrize(
    "result",
    [None, AgentResult("invented", ("op-example-001",)), AgentResult("completed", ("other",))],
)
def test_invalid_adapter_result_is_an_error(case, result):
    class BadResultAdapter:
        def run(self, inputs, tools):
            return result

    with pytest.raises(ContractError, match="invalid agent result"):
        core.execute(case, adapter=BadResultAdapter())


def _stub(calls, status="completed"):
    class Stub:
        def run(self, inputs, tools):
            task = inputs.task
            request = AmendmentRequest(
                task.operation_id,
                task.order_id,
                task.quantity_delta,
                task.unit_price_minor,
                task.currency,
                inputs.approval.approval_id,
            )
            for _ in range(calls):
                tools.apply_amendment(request, "stub-key")
            return AgentResult(status, (task.operation_id,))

    return Stub()


@pytest.mark.parametrize("calls", [0, 1])
def test_completion_without_receipt_is_rejected(case, calls):
    # With one call the effect is durable, but the receipt was withheld.
    with pytest.raises(ContractError, match="without receipt"):
        core.execute(case, adapter=_stub(calls))


def test_completion_with_receipt_counterpart_passes(case):
    result = core.execute(case, adapter=_stub(2))
    assert all(row["verdict"] == "pass" for row in result["suites"].values())


def test_incomplete_claim_without_receipt_remains_inconclusive(case):
    result = core.execute(case, adapter=_stub(1, "incomplete"))
    assert result["observation"]["durable_operation_records"] == 1
    assert all(row["verdict"] == "inconclusive" for row in result["suites"].values())
