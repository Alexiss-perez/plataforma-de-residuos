from __future__ import annotations

from app.agents.ecomatch_agent import EcoMatchAgent
from app.agents.llm_client import MockLLMClient


def test_agent_analyze_material_with_mock(db_session):
    agent = EcoMatchAgent(db_session, client=MockLLMClient())
    result = agent.analyze_material("Tengo tablas de madera y una puerta.")
    assert len(result.materials) >= 1
    assert 0 <= result.materials[0].confidence <= 1


def test_agent_interpret_need_with_mock(db_session):
    agent = EcoMatchAgent(db_session, client=MockLLMClient())
    result = agent.interpret_need("Necesitamos madera para construir seis mesas.")
    assert 0 <= result.confidence <= 1


def test_agent_explain_match_with_mock(db_session):
    agent = EcoMatchAgent(db_session, client=MockLLMClient())
    result = agent.explain_match(material_id=1, need_id=1)
    assert 0 <= result.confidence <= 1


def test_agent_handle_contingency_no_pickup(db_session):
    agent = EcoMatchAgent(db_session, client=MockLLMClient())
    result = agent.handle_contingency(pickup_id=999)
    assert "action" in result


def test_agent_chat_mock(db_session):
    agent = EcoMatchAgent(db_session, client=MockLLMClient())
    result = agent.chat("Hola")
    assert "response" in result
