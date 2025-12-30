import os
from typing import Optional, override

from google.genai import types

from functions.function_interface import CodingToolFunctionInterface
from utils import generate_fault_message, generate_success_message


class GetFilesInfoFunction(CodingToolFunctionInterface):
    directory_key: str = "directory"

    @override
    @classmethod
    def name(cls) -> str:
        return "get_files_info"

    @override
    @classmethod
    def schema(cls) -> types.FunctionDeclaration:
        return types.FunctionDeclaration(
            name=cls.name(),
            description="List files in the specified directory along with their sizes, constrained to the working directory.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    cls.directory_key: types.Schema(
                        type=types.Type.STRING,
                        description="The directory to list files from, relative to the working directory. If not provided, list files in the working directory itself.",
                    )
                },
            ),
        )

    @override
    def handle_function_call(self, args: Optional[dict]) -> types.Content:
        directory = ""
        if not args or self.directory_key not in args:
            directory = "."
        else:
            directory = args[self.directory_key]

        response = self._handle(
            working_directory=self.working_directory,
            directory=directory,
        )

        return generate_success_message(function_name=self.name(), message=response)

    def _handle(self, working_directory: str, directory: str):
        abs_working_directory = os.path.abspath(working_directory)
        abs_directory = os.path.abspath(os.path.join(working_directory, directory))

        if not abs_directory.startswith(abs_working_directory):
            return f"Error: Oops, requested directory '{directory}' is not inside the working directory and you can't access files outside working directory."

        if not os.path.isdir(abs_directory):
            return f"Error: can't find directory '{directory}' in working directory"

        final_response: str = ""
        for content in os.listdir(abs_directory):
            content_path = os.path.join(abs_directory, content)
            is_dir = os.path.isdir(content_path)
            size = os.path.getsize(content_path)

            response = f" - {content}: file_size={size} bytes, is_dir={is_dir}\n"
            final_response += response

        return final_response
