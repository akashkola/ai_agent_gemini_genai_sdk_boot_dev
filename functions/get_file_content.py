import os
from typing import Optional, override

from google.genai import types

from config import MAX_CHARS_TO_READ_FROM_FILE
from functions.function_interface import CodingToolFunctionInterface
from utils import generate_fault_message, generate_success_message


class GetFileContentFunction(CodingToolFunctionInterface):
    file_path_key: str = "file_path"

    @classmethod
    @override
    def name(cls) -> str:
        return "get_file_content"

    @classmethod
    @override
    def schema(cls) -> types.FunctionDeclaration:
        return types.FunctionDeclaration(
            name=cls.name(),
            description="Gets the contents of the given file as a string, constrained to the working directory.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    cls.file_path_key: types.Schema(
                        type=types.Type.STRING,
                        description="The path to the file, from the working directory.",
                    )
                },
            ),
        )

    @override
    def handle_function_call(self, args: Optional[dict]) -> types.Content:
        if not args:
            return generate_fault_message(
                function_name=self.name(),
                message="args are empty for the functional call, but this function requires arguments",
            )

        if self.file_path_key not in args:
            return generate_fault_message(
                function_name=self.name(),
                message=f"{self.file_path_key} is a required arguemnt for this function call",
            )

        response = self._handle(
            working_directory=self.working_directory,
            file_path=args[self.file_path_key],
        )

        message = generate_success_message(function_name=self.name(), message=response)
        return message

    def _handle(self, working_directory: str, file_path: str) -> str:
        abs_working_directory = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

        if not abs_file_path.startswith(abs_working_directory):
            return f"Error: Oops, requested file '{file_path}' is not inside the working directory and you can't access files outside working directory."

        if not os.path.isfile(abs_file_path):
            return f"Error: can't find file '{file_path}' in working directory"

        try:
            with open(abs_file_path, "r") as file:
                file_content = file.read(MAX_CHARS_TO_READ_FROM_FILE)
        except Exception as e:
            return f"Exception raised while reading the file: {e}"

        return file_content
