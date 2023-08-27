import os
from langchain.chat_models import ChatOpenAI
from typing import List, Optional

from utils.general import clean_and_split_comment, read_yaml

OPENAI_MODEL = "gpt-4"
#OPENAI_MODEL = "gpt-3.5-turbo" # cheaper and faster - use this in dev


class OpenAI:
    """
    A class for handling interactions with OpenAI.
    """

    def __init__(self, context_path: str):
        """
        Initialize the OpenAI interaction class.

        Args:
            context_path (str): The relative path (to root) of the context to use for the LLM.
        """
        self.context = read_yaml(context_path)

        token_key = "OPENAI_TOKEN"
        assert (
            token_key in os.environ
        ), f"{token_key} environment variable does not exist."
        assert os.environ[token_key] not in {
            None,
            "",
        }, f"{token_key} environment variable is empty."

        self.llm = ChatOpenAI(
            openai_api_key=os.environ[token_key], model_name=OPENAI_MODEL
        )

    def build_context(self, node_type: Optional[str] = None) -> str:
        """
        Build the LLM context based on the node type provided.

        Args:
            node_type (str, optional): The type of the node. Can be function, method, class, or None.

        Returns:
            str: The built context.
        """
        prompt = self.context["prompt"] + "\n"
        if not node_type:
            return prompt

        context_mapping = {
            "function": self.context["function_context"],
            "method": self.context["function_context"],
            "class": self.context["class_context"],
        }
        assert node_type in context_mapping.keys()

        context = context_mapping["node_type"]

        return context + prompt

    def predict(
        self, docstring: str, temperature: float = 0.0, node_type: Optional[str] = None
    ) -> List[str]:
        """
        Predict comments based on the provided docstring and context.

        Args:
            docstring (str): The docstring to predict comments for.
            temperature (float, optional): The temperature parameter for prediction. Defaults to 0.0.
            node_type (str, optional): The type of the node for which the prediction is made.

        Returns:
            List[str]: The predicted comments.
        """
        prompt = self.build_context(node_type) + docstring
        prediction = self.llm.predict(prompt, temperature=temperature)
        return clean_and_split_comment(prediction)
