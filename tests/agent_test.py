import pytest

@pytest.mark.integration
def test_at_least_one_model_works():
    from ai_agent.agent_runtime import MultiLLm
    from ai_agent.llm_wrappers import GloqLLM, OpenRouterLLM

    models = [
                GloqLLM("openai/gpt-oss-120b"),
                OpenRouterLLM("nvidia/nemotron-3-super-120b-a12b:free"),
                OpenRouterLLM("google/gemma-4-31b-it:free"),
                OpenRouterLLM("openrouter/free")
            ]
    orchestrator = MultiLLm(models)

    try:
        response = orchestrator.invoke(
            user="ping",
            system="Respond with pong."
        )
        # 3. Assert that we got a valid response back
        assert response is not None
        print("Success! At least one model in the chain is operational.")

    except Exception as e:
        pytest.fail(f"All models failed! Ultimate error was: {e}")
