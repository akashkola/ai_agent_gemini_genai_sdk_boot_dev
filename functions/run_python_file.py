import os
import subprocess
from typing import Optional, override

from google.genai import types

from functions.function_interface import CodingToolFunctionInterface
from utils import generate_fault_message, generate_success_message


class RunPythonFunction(CodingToolFunctionInterface):
    python_file_path_key = "python_file_path"
    args_key = "args"

    @override
    @classmethod
    def name(cls) -> str:
        return "run_python_file"

    @override
    @classmethod
    def schema(cls) -> types.FunctionDeclaration:
        return types.FunctionDeclaration(
            name=cls.name(),
            description="Runs a python file with the python3 interpreter. Accepts additional CLI args as an optional array.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    cls.python_file_path_key: types.Schema(
                        type=types.Type.STRING,
                        description="The file to run, relative to the working directory.",
                    ),
                    cls.args_key: types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                        description="An optional array of strings to be used as the CLI args for the Python file.",
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

        if self.python_file_path_key not in args:
            return generate_fault_message(
                function_name=self.name(),
                message=f"{self.python_file_path_key} is a required arguemnt for this function call",
            )

        response = self._handle(
            working_directory=self.working_directory,
            python_file_path=args[self.python_file_path_key],
            args=args.get(self.args_key),
        )

        return generate_success_message(function_name=self.name(), message=response)

    def _handle(
        self,
        working_directory: str,
        python_file_path: str,
        args: Optional[list[str]] = None,
    ) -> str:
        abs_working_directory = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(
            os.path.join(working_directory, python_file_path)
        )

        if not abs_file_path.startswith(abs_working_directory):
            return f"Error: Oops, requested file is not inside the working directory and you can't access files outside working directory."

        if not os.path.isfile(abs_file_path):
            return f"Error: can't find file '{python_file_path}' in working directory"

        if not python_file_path.endswith(".py"):
            return f"Error: {python_file_path} is not a Python file"

        try:
            args = [python_file_path] if args is None else [python_file_path] + args
            output = subprocess.run(
                ["python3"] + args,
                cwd=abs_working_directory,
                timeout=30,
                capture_output=True,
            )
        except Exception as e:
            return f"Error: executing Python file {e}"

        result = f"""
STDOUT: {output.stdout}
STDERR: {output.stderr}\n
""".strip()

        if not output.stdout and not output.stderr:
            result = "No output produced.\n"

        if output.returncode != 0:
            result += f"Process exited with code {output.returncode}"

        return result
