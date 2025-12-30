from abc import ABC, abstractmethod
from typing import Optional

from google.genai import types


class CodingToolFunctionInterface(ABC):
    def __init__(self, working_directory: str) -> None:
        if not working_directory:
            raise Exception("working directory is mandated")

        self.working_directory = working_directory

    @classmethod
    def name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def schema(cls) -> types.FunctionDeclaration:
        raise NotImplementedError()

    @abstractmethod
    def handle_function_call(self, args: Optional[dict]) -> types.Content:
        raise NotImplementedError()
