import os
from typing import Optional, override

from google.genai import types

from functions.function_interface import CodingToolFunctionInterface
from utils import generate_fault_message, generate_success_message


class WriteFileFunction(CodingToolFunctionInterface):
    file_path_key: str = "file_path"
    content_key: str = "content"

    @override
    @classmethod
    def name(cls) -> str:
        return "write_file"

    @override
    @classmethod
    def schema(cls) -> types.FunctionDeclaration:
        return types.FunctionDeclaration(
            name=cls.name(),
            description="Overwrites an existing file or writes to a new file if it doesn't exist (and creates required parent dirs safely), constrained to the current directory.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    cls.file_path_key: types.Schema(
                        type=types.Type.STRING,
                        description="The path to the file to write.",
                    ),
                    cls.content_key: types.Schema(
                        type=types.Type.STRING,
                        description="The contents to write to the file as a string.",
                    ),
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

        if self.content_key not in args:
            return generate_fault_message(
                function_name=self.name(),
                message=f"{self.content_key} is a required arguemnt for this function call",
            )

        response = self._handle(
            working_directory=self.working_directory,
            file_path=args[self.file_path_key],
            content=args[self.content_key],
        )

        return generate_success_message(function_name=self.name(), message=response)

    def _handle(self, working_directory: str, file_path: str, content: str) -> str:
        abs_working_directory = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

        if not abs_file_path.startswith(abs_working_directory):
            return f"Error: Oops, requested file is not inside the working directory and you can't access files outside working directory."

        parent_dir = os.path.dirname(abs_file_path)
        try:
            os.makedirs(name=parent_dir, exist_ok=True)
        except Exception as e:
            return f"Error: couldn't create parent dirs '{parent_dir}' for the file '{file_path}' ==> {e}"

        try:
            with open(abs_file_path, "w") as f:
                f.write(content)
        except Exception as e:
            return (
                f"Error: failed to write the content to the file '{file_path}' ==> {e}"
            )

        return f"Successfully wrote to '{file_path}' {len(content)} characters"


def write_file(working_directory: str, file_path: str, content: str) -> str:
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not abs_file_path.startswith(abs_working_directory):
        return f"Error: Oops, requested file is not inside the working directory and you can't access files outside working directory."

    parent_dir = os.path.dirname(abs_file_path)
    try:
        os.makedirs(parent_dir, exist_ok=True)
    except Exception as e:
        return f"Error: couldn't create parent dirs '{parent_dir}' for the file '{file_path}' ==> {e}"

    try:
        with open(abs_file_path, "w") as f:
            f.write(content)
    except Exception as e:
        return f"Error: failed to write the content to the file '{file_path}' ==> {e}"

    return f"Successfully wrote to '{file_path}' {len(content)} characters"
