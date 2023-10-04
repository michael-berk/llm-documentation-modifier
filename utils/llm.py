import os
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

from mlflow.gateway import set_gateway_uri, query


_SYSTEM_PROMPT = "You are an python software developer that converts doctsrings to the google style format."
_REQUEST_TO_LLM = "Convert the below docstring args and returns to google style."
_RULES = """
- Don't exceed 100 character length.
- If there are no parameters/returns, don't include an Args/Returns section.
- Do not modify .. blocks or bullet lists within the Args/Returns section.
- Don't include types.
- Indenting should be consistent for each argument or return value.
- Don't drop any wording or code examples.
"""

_TEMPERATURE = 0.0


@dataclass
class Context:
    """
    Chat context creation without chat prompt formatting.

    This class handles state for a given chat interaction.
    """

    messages: List[Dict] = field(default_factory=list)
    prompts: List[Tuple[str, str]] = field(default_factory=list)

    def append_message(self, role: str, content: str):
        assert role in {"system", "user", "assistant"}, f"{role} role is not supported."
        self.messages.append({"role": role, "content": content})

    def append_messages(self, messages: List[Tuple[str, str]]):
        for role_and_message in messages:
            assert len(role_and_message) == 2
            self.append_message(*role_and_message)

    def has_prompts(self):
        return len(self.prompts) > 0

    def increment_prompt(self, response: str = None):
        if self.has_prompts():
            current_prompt = self.prompts.pop(0)
            if response is not None:
                self.append_message(role="assistant", content=response)
            self.append_messages(current_prompt)
        else:
            raise IndexError("There are no more prompts left in the context.")


@dataclass
class DocstringReformatContext(Context):
    docstring: str = field(default="")
    system_prompt: str = field(default="")
    rules: str = field(default="")
    request_to_llm: str = field(default="")

    def __post_init__(self):
        self.prompts = [
            self._first_prompt(),
            self._second_prompt(),
            self._third_prompt(),
        ]

    def _first_prompt(self):
        return [
            ("system", self.system_prompt),
            ("user", f"Follow these rules:\n{self.rules}"),
            ("user", self.request_to_llm),
            ("user", self.docstring),
        ]

    def _second_prompt(self):
        return [
            (
                "user",
                (
                    "Validate that you have met the criteria above."
                    "If the output is correct repeat the output."
                    "If the output is incorrect, fix it."
                ),
            )
        ]

    def _third_prompt(self):
        return [
            (
                "user",
                (
                    "Only display the docstring, as described by the rules above."
                    'Surround the value with three double quotes: """'
                ),
            )
        ]

    @staticmethod
    def extract_docstring(docstring: str, delim: str = '"""') -> str:
        parts = docstring.split(delim)
        assert len(parts) > 2
        return delim.join(parts[1:-1]).strip("\n")


class OpenAI:
    def __init__(self, gateway_uri: str, gateway_route_name: str):
        set_gateway_uri(gateway_uri=gateway_uri)
        self.gateway_route_name = gateway_route_name

    def predict(self, docstring: str):
        context = DocstringReformatContext(
            docstring=docstring,
            system_prompt=_SYSTEM_PROMPT,
            rules=_RULES,
            request_to_llm=_REQUEST_TO_LLM,
        )

        response = None
        while context.has_prompts():
            context.increment_prompt(response=response)
            raw_response = query(
                self.gateway_route_name,
                {"messages": context.messages, "temperature": _TEMPERATURE},
            )
            response = raw_response["candidates"][0]["message"]["content"]

        response_clean = context.extract_docstring(response)
        return response_clean
