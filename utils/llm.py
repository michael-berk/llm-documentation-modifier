import os
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

from mlflow.gateway import set_gateway_uri, query

from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import (
    BaseMessage,
    AIMessage,
    SystemMessage,
    HumanMessage,
)

from langchain.memory import ChatMessageHistory


_MODEL_NAME = "chat-gpt-3.5-turbo"
# _MODEL_NAME = 'chat-gpt-4"
_TOKEN_KEY = "OPENAI_API_KEY"
_TEMPERATURE = 0.0

_SYSTEM_PROMPT = "You are an python software developer that converts doctsrings to the google style format."
_REQUEST_TO_LLM = "Convert the below docstring args and returns to google style."
_RULES = """
- Don't exceed 100 character length.
- If there are no parameters/returns, don't include an Args/Returns section.
"""


def parse_prompt(response: str) -> str:
    n_double_quotes = response.count('"""')
    assert (
        n_double_quotes >= 2
    ), f"Response is not properly formatted. It only has {n_double_quotes} triple quotes."

    start_index = response.index('"""') + 3
    end_index = response.index('"""', start_index)
    return response[start_index:end_index]


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


# @dataclass
# class Context:
#     prompts: List[BaseChatPromptTemplate] = None
#     messages: List[BaseMessage] = field(default_factory=list)
#     context_config: Dict = field(default_factory=dict)

#     def _create_first_prompt(self) -> List[BaseChatPromptTemplate]:
#         system_message_prompt = SystemMessagePromptTemplate.from_template(
#             "{system_prompt}"
#         )
#         rules_prompt = HumanMessagePromptTemplate.from_template(
#             "Make sure to follow these rules:\n{rules}"
#         )
#         convert_prompt = HumanMessagePromptTemplate.from_template("{request}\n")
#         docstring_prompt = HumanMessagePromptTemplate.from_template("{docstring}")

#         return system_message_prompt + rules_prompt + convert_prompt + docstring_prompt

#     def _create_second_prompt(self) -> List[BaseChatPromptTemplate]:
#         return HumanMessagePromptTemplate.from_template(
#             "Validate that you have met the criteria based on the above rules. If not, fix the output."
#         )

#     def _create_third_prompt(self) -> List[BaseChatPromptTemplate]:
#         return HumanMessagePromptTemplate.from_template(
#             'Only show the args and returns, as described in the rules. Surround the value with three double quotes: """'
#         )

#     def __post_init__(self):
#         self.prompts = [
#             self._create_first_prompt(),
#             self._create_second_prompt(),
#             self._create_third_prompt(),
#         ]

#     def build_context_kwargs(self, context_path: str, docstring: str) -> None:
#         self.context_kwargs = dict(
#             system_prompt=_SYSTEM_PROMPT, request=_REQUEST_TO_LLM, rules=_RULES
#         )
#         self.context_kwargs.update({"docstring": docstring})

#     def _convert_response_to_prompt(self, response: str) -> AIMessagePromptTemplate:
#         print("HERE!!!!!!!!!")
#         print(response)
#         response = response.replace("{", "").replace("}", "")
#         return AIMessagePromptTemplate.from_template(response)

#     def _increment_messages(self, response_content: str = None) -> None:
#         prompt = self.prompts.pop(0)
#         if response_content is None:
#             self.messages += [prompt]
#             return

#         response = self._convert_response_to_prompt(response_content)
#         self.messages += [response, prompt]

#     def _format_prompt(self):
#         prompt_template = ChatPromptTemplate.from_messages(self.messages)
#         prompt = prompt_template.format_messages(**self.context_kwargs)
#         return prompt

#     def build_and_get_prompt(self, response_text: str = None) -> List[BaseMessage]:
#         self._increment_messages(response_text)
#         prompt = self._format_prompt()
#         return prompt


class OpenAI:
    def __init__(self):
        set_gateway_uri(gateway_uri="http://localhost:5000")

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
                _MODEL_NAME, {"messages": context.messages, "temperature": _TEMPERATURE}
            )
            response = raw_response["candidates"][0]["message"]["content"]
            print(response)
            print("----------------")

        return response


# class OpenAI:
#     def __init__(self):
#         self.model = ChatOpenAI(
#             model_name=_MODEL_NAME,
#             temperature=_TEMPERATURE,
#             openai_api_key=os.environ[_TOKEN_KEY],
#         )

#     def predict(self, context_path: str, docstring: str):
#         self.context = Context()
#         self.context.build_context_kwargs(context_path, docstring)

#         request_1 = self.context.build_and_get_prompt()
#         result_1 = self.model(request_1).content
#         print(result_1)
#         print("--------------\n" * 5)
#         request_2 = self.context.build_and_get_prompt(response_text=result_1)
#         result_2 = self.model(request_2).content
#         print(result_2)
#         print("--------------\n" * 5)
#         request_3 = self.context.build_and_get_prompt(response_text=result_2)
#         result_3 = self.model(request_3).content
#         print(result_3)
#         print("--------------\n" * 5)
#         print(parse_prompt(result_3))
