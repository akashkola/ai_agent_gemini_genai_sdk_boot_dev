from typing import Optional
from google.genai import types

from config import WORKSPACE_DIR
from functions.function_interface import CodingToolFunctionInterface
from functions.get_file_content import GetFileContentFunction
from functions.get_files_info import GetFilesInfoFunction
from utils import generate_fault_message
from functions.run_python_file import RunPythonFunction
from functions.write_file import WriteFileFunction


def call_function(function_call_part: types.FunctionCall) -> types.Content:
    working_directory = WORKSPACE_DIR

    coding_tool_function: Optional[CodingToolFunctionInterface] = None

    if function_call_part.name == GetFileContentFunction.name():
        coding_tool_function = GetFileContentFunction(
            working_directory=working_directory
        )
        return coding_tool_function.handle_function_call(args=function_call_part.args)

    if function_call_part.name == GetFilesInfoFunction.name():
        coding_tool_function = GetFilesInfoFunction(working_directory=working_directory)
        return coding_tool_function.handle_function_call(args=function_call_part.args)

    if function_call_part.name == WriteFileFunction.name():
        coding_tool_function = WriteFileFunction(working_directory=working_directory)
        return coding_tool_function.handle_function_call(args=function_call_part.args)

    if function_call_part.name == RunPythonFunction.name():
        coding_tool_function = RunPythonFunction(working_directory=working_directory)
        return coding_tool_function.handle_function_call(args=function_call_part.args)

    return generate_fault_message(
        function_call_part.name or "undefined function name",
        message="Hey! this function is not avaiable in the provided coding agent tool. Please check again and retry",
    )
