from pathlib import Path

import yaml


def test_tool_using_agents_have_enough_iterations_to_finish_after_tool_calls():
    agents = yaml.safe_load(Path("configs/agents.yaml").read_text())

    assert agents["market_research_specialist"]["max_iter"] >= 2
    assert agents["competitive_intelligence_analyst"]["max_iter"] >= 2
    assert agents["customer_insights_researcher"]["max_iter"] >= 2


def test_context_only_agents_stay_single_pass_without_tools():
    agents = yaml.safe_load(Path("configs/agents.yaml").read_text())

    assert agents["research_manager"]["max_iter"] == 1
    assert agents["strategy_manager"]["max_iter"] == 1
