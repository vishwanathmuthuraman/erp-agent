import copy
import json
from pathlib import Path

import pytest

from erp_agent_testbench.common import ContractError
from erp_agent_testbench.core import Simulator, check_observation, execute, validate_case

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def case():
    return json.loads((ROOT / "examples/clean-retry.case.json").read_text())


@pytest.mark.parametrize("name", ["clean-retry", "duplicate-retry"])
def test_released_retry_specimens_against_separate_oracle(name):
    case = json.loads((ROOT / f"examples/{name}.case.json").read_text())
    expected = json.loads((ROOT / f"examples/{name}.expected.json").read_text())
    result = execute(case)
    for key, value in expected["expected_observation"].items():
        assert result["observation"][key] == value
    for suite, verdict in expected["expected_suite_verdicts"].items():
        assert result["suites"][suite]["verdict"] == verdict
        assert [row["rule_id"] for row in result["suites"][suite]["findings"]] == expected[
            "expected_findings"
        ][suite]


def test_controller_expected_filename_is_never_used(case):
    before = execute(case)
    case["expected_result_file"] = "nonexistent.expected.json"
    assert execute(case) == before


def test_missing_observation_never_passes():
    assert all(row["verdict"] == "inconclusive" for row in check_observation({}).values())


def request_for(case):
    request = {
        key: value
        for key, value in case["public_task"].items()
        if key != "allowed_terminal_statuses"
    }
    request["approval_id"] = case["initial_state"]["approval"]["approval_id"]
    return request


def test_same_key_different_request_is_atomic_conflict(case):
    simulator = Simulator(case["initial_state"], case["limits"])
    request = request_for(case)
    simulator.apply(request, "one", 5)
    request["quantity_delta"] = 4
    with pytest.raises(ContractError, match="conflict"):
        simulator.apply(request, "one", 6)
    assert simulator.db.execute("SELECT quantity FROM orders").fetchone()[0] == 13
    assert simulator.db.execute("SELECT COUNT(*) FROM commitments").fetchone()[0] == 1
    simulator.close()


@pytest.mark.parametrize(
    "mutation", ["expiry", "policy", "binding", "amount", "currency", "inactive"]
)
def test_denial_has_no_business_effect(case, mutation):
    state = copy.deepcopy(case["initial_state"])
    request = request_for(case)
    if mutation == "expiry":
        state["approval"]["valid_until_tick"] = 5
    elif mutation == "policy":
        state["policy"]["policy_version"] = 2
    elif mutation == "binding":
        request["quantity_delta"] = 4
    elif mutation == "amount":
        state["policy"]["max_order_total_minor"] = 12999
    elif mutation == "currency":
        request["currency"] = "GBP"
    else:
        state["policy"]["supplier_active"] = False
    simulator = Simulator(state, case["limits"])
    with pytest.raises(ContractError):
        simulator.apply(request, "one", 5)
    assert simulator.db.execute("SELECT quantity FROM orders").fetchone()[0] == 10
    assert simulator.db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0] == 0
    simulator.close()


def test_budget_stops_retry(case):
    case["limits"]["max_tool_calls"] = 1
    with pytest.raises(ContractError, match="budget"):
        execute(case)


def test_invalid_float_money_rejected(case):
    case["public_task"]["unit_price_minor"] = 1000.0
    with pytest.raises(ContractError):
        validate_case(case)


def test_isolated_runs_and_repeatability(case):
    assert execute(case) == execute(case)
    changed = copy.deepcopy(case)
    changed["mutation"]["kind"] = "retry_new_idempotency_key"
    assert execute(changed)["observation"]["order_quantity"] == 16
    assert execute(case)["observation"]["order_quantity"] == 13
