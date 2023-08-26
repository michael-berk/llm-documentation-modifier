import os
from langchain.chat_models import ChatOpenAI
from typing import List, Optional

from constants import CONTEXT_PATH, OPENAI_ENVIRON_KEY, OPENAI_MODEL
from utils.general import clean_and_split_comment, read_yaml


class OpenAI:
    """
    A class for handling interactions with OpenAI.
    """

    def __init__(self):
        """
        Initialize the OpenAI interaction class.
        """
        self.context = read_yaml(CONTEXT_PATH)
        self.llm = ChatOpenAI(
            openai_api_key=os.environ[OPENAI_ENVIRON_KEY], model_name=OPENAI_MODEL
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
