import importlib
import sys
from types import ModuleType, SimpleNamespace


class _FakeLogger:
    def info(self, *args, **kwargs):
        return None


class _FakeCrew:
    last_instance = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.stream = None
        self.kickoff_inputs = None
        _FakeCrew.last_instance = self

    def kickoff(self, inputs):
        self.kickoff_inputs = dict(inputs)
        return "done"


def _identity_decorator(func=None, *args, **kwargs):
    if func is not None:
        return func

    def decorator(inner):
        return inner

    return decorator


def import_crew_with_fakes(monkeypatch):
    crewai = ModuleType("crewai")
    crewai.Agent = lambda *args, **kwargs: SimpleNamespace(args=args, kwargs=kwargs)
    crewai.Crew = _FakeCrew
    crewai.Process = SimpleNamespace(sequential="sequential")
    crewai.Task = lambda *args, **kwargs: SimpleNamespace(args=args, kwargs=kwargs)

    base_agent = ModuleType("crewai.agents.agent_builder.base_agent")
    base_agent.BaseAgent = object

    project = ModuleType("crewai.project")
    project.CrewBase = _identity_decorator
    project.agent = _identity_decorator
    project.crew = _identity_decorator
    project.task = _identity_decorator

    core_config = ModuleType("configs.core_config")
    core_config.AGENTS_CONFIG_PATH = {}
    core_config.TASKS_CONFIG_PATH = {}

    providers = ModuleType("src.llm.providers")
    providers.create_llm = lambda: "fake-llm"
    providers.create_ollama_llm = lambda: "fake-critic-llm"

    logger = ModuleType("src.utils.logger")
    logger.APP_LOGGER = _FakeLogger()
    logger.LLM_LOGGER = _FakeLogger()

    tools = ModuleType("src.workflow.tools")
    tools.tools = []

    dotenv = ModuleType("dotenv")
    dotenv.load_dotenv = lambda *args, **kwargs: None

    monkeypatch.setitem(sys.modules, "crewai", crewai)
    monkeypatch.setitem(sys.modules, "crewai.agents.agent_builder.base_agent", base_agent)
    monkeypatch.setitem(sys.modules, "crewai.project", project)
    monkeypatch.setitem(sys.modules, "configs.core_config", core_config)
    monkeypatch.setitem(sys.modules, "src.llm.providers", providers)
    monkeypatch.setitem(sys.modules, "src.utils.logger", logger)
    monkeypatch.setitem(sys.modules, "src.workflow.tools", tools)
    monkeypatch.setitem(sys.modules, "dotenv", dotenv)
    sys.modules.pop("src.workflow.crew", None)

    return importlib.import_module("src.workflow.crew")


def test_kickoff_with_state_sanitizes_inputs_before_crew_execution(monkeypatch):
    crew_module = import_crew_with_fakes(monkeypatch)
    crew = crew_module.MarketResearchCrew()
    crew.agents = []
    crew.tasks = []
    inputs = {
        "user_id": 123,
        "user_input": "Email jane@example.com about card 4242 4242 4242 4242",
        "product_idea": f"AI research tool using key {'b' * 32}",
    }

    result = crew.kickoff_with_state(inputs, stream=False)

    assert result == "done"
    assert crew.app_state.user_id == 123
    assert "jane@example.com" not in crew.app_state.user_input
    assert "4242 4242 4242 4242" not in crew.app_state.user_input
    assert "b" * 32 not in crew.app_state.product_idea
    assert _FakeCrew.last_instance.stream is False
    assert _FakeCrew.last_instance.kickoff_inputs == inputs
    assert "[REDACTED_EMAIL]" in inputs["user_input"]
    assert "[REDACTED_CREDIT_CARD]" in inputs["user_input"]
    assert "[REDACTED_API_KEY]" in inputs["product_idea"]


def test_task_callback_validates_agent_output_into_app_state(monkeypatch):
    crew_module = import_crew_with_fakes(monkeypatch)
    crew = crew_module.MarketResearchCrew()
    callback = crew._make_callback("market_research")

    callback("Evidence from [Source](https://example.com). Score: 8.5")

    assert crew.app_state.market_research.text.startswith("Evidence from")
    assert crew.app_state.market_research.score == 8.5
    assert crew.app_state.market_research.sources[0].url == "https://example.com"


def test_review_and_synthesis_agents_do_not_receive_tools(monkeypatch):
    crew_module = import_crew_with_fakes(monkeypatch)
    crew = crew_module.MarketResearchCrew()
    crew.agents_config = {
        "market_research_specialist": {"role": "researcher"},
        "competitive_intelligence_analyst": {"role": "competitor"},
        "customer_insights_researcher": {"role": "customer"},
        "research_manager": {"role": "reviewer"},
        "strategy_manager": {"role": "strategist"},
    }

    research_agent = crew.market_research_specialist()
    review_agent = crew.research_manager()
    synthesis_agent = crew.strategy_manager()

    assert "tools" in research_agent.kwargs
    assert "tools" not in review_agent.kwargs
    assert "tools" not in synthesis_agent.kwargs
