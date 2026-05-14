import anthropic
from app.config import settings

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def complete(system: str, user: str, smart: bool = False) -> tuple[str, float]:
    """Returns (response_text, cost_usd). Uses Haiku by default, Sonnet if smart=True."""
    model = settings.smart_model if smart else settings.fast_model
    response = _client.messages.create(
        model=model,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    cost = _cost(model, response.usage.input_tokens, response.usage.output_tokens)
    return response.content[0].text, cost


def _cost(model: str, input_tokens: int, output_tokens: int) -> float:
    if "haiku" in model:
        return (input_tokens * 0.0000008) + (output_tokens * 0.000004)
    return (input_tokens * 0.000003) + (output_tokens * 0.000015)
