import os
import shutil

from google.genai import types

from functions.get_file_content import GetFileContentFunction
from functions.get_files_info import GetFilesInfoFunction
from functions.run_python_file import RunPythonFunction
from functions.write_file import WriteFileFunction


def test_get_files_info():
    working_dir = "calculator"
    function: GetFilesInfoFunction = GetFilesInfoFunction(working_directory=working_dir)

    # case 1
    content: types.Content = function.handle_function_call(
        args={GetFilesInfoFunction.directory_key: ""}
    )
    print(content.parts[0].function_response.response["result"])

    # case 2
    content: types.Content = function.handle_function_call(
        args={GetFilesInfoFunction.directory_key: "pkg"}
    )
    print(content.parts[0].function_response.response["result"])

    # case 3
    content: types.Content = function.handle_function_call(
        args={GetFilesInfoFunction.directory_key: "/bin"}
    )
    print(content.parts[0].function_response.response["result"])

    # case 4
    content: types.Content = function.handle_function_call(
        args={GetFilesInfoFunction.directory_key: "not_exists"}
    )
    print(content.parts[0].function_response.response["result"])

    # case 5
    content: types.Content = function.handle_function_call(
        args={GetFilesInfoFunction.directory_key: "../"}
    )
    print(content.parts[0].function_response.response["result"])


def test_get_file_content():
    working_dir = "calculator"
    function = GetFileContentFunction(working_directory=working_dir)

    # case 1
    content: types.Content = function.handle_function_call(
        args={GetFileContentFunction.file_path_key: "main.py"}
    )
    print(content.parts[0].function_response.response["result"])

    # case 2
    content: types.Content = function.handle_function_call(
        args={GetFileContentFunction.file_path_key: "pkg/calculator.py"}
    )
    print(content.parts[0].function_response.response["result"])

    # case 3
    content: types.Content = function.handle_function_call(
        args={GetFileContentFunction.file_path_key: "pkg/not_exists.py"}
    )
    print(content.parts[0].function_response.response["result"])

    # case 4
    content: types.Content = function.handle_function_call(
        args={GetFileContentFunction.file_path_key: "/bin/cat"}
    )
    print(content.parts[0].function_response.response["result"])


def test_write_file():
    working_dir = "calculator"
    function = WriteFileFunction(working_directory=working_dir)

    # case 1
    content: types.Content = function.handle_function_call(
        args={
            WriteFileFunction.file_path_key: "lorem.txt",
            WriteFileFunction.content_key: "lorem text",
        }
    )
    print(content.parts[0].function_response.response["result"])

    # case 2
    shutil.rmtree(os.path.join(working_dir, "non_existing"))
    content: types.Content = function.handle_function_call(
        args={
            WriteFileFunction.file_path_key: "non_existing/lorem.txt",
            WriteFileFunction.content_key: "lorem text",
        }
    )
    print(content.parts[0].function_response.response["result"])

    # case 3
    existing_dir = os.path.join(working_dir, "existing")
    os.makedirs(existing_dir, exist_ok=True)
    content: types.Content = function.handle_function_call(
        args={
            WriteFileFunction.file_path_key: "existing/lorem.txt",
            WriteFileFunction.content_key: "lorem text",
        }
    )
    print(content.parts[0].function_response.response["result"])

    # case 4
    existing_dir = os.path.join(working_dir, "existing")
    os.makedirs(existing_dir, exist_ok=True)
    content: types.Content = function.handle_function_call(
        args={
            WriteFileFunction.file_path_key: "/tmp/test.txt",
            WriteFileFunction.content_key: "lorem text",
        }
    )
    print(content.parts[0].function_response.response["result"])


def test_run_python_file():
    working_dir = "calculator"
    function = RunPythonFunction(working_directory=working_dir)

    # case 1
    content: types.Content = function.handle_function_call(
        args={
            RunPythonFunction.python_file_path_key: "main.py",
            RunPythonFunction.args_key: ["3 + 5"],
        }
    )
    print(content.parts[0].function_response.response["result"])

    # case 2
    content: types.Content = function.handle_function_call(
        args={RunPythonFunction.python_file_path_key: "tests.py"}
    )
    print(content.parts[0].function_response.response["result"])

    # case 3
    content: types.Content = function.handle_function_call(
        args={RunPythonFunction.python_file_path_key: "../main.py"}
    )
    print(content.parts[0].function_response.response["result"])

    # case 4
    content: types.Content = function.handle_function_call(
        args={RunPythonFunction.python_file_path_key: "/main.py"}
    )
    print(content.parts[0].function_response.response["result"])

    # case 5
    content: types.Content = function.handle_function_call(
        args={RunPythonFunction.python_file_path_key: "nonexistent.py"}
    )
    print(content.parts[0].function_response.response["result"])


test_get_file_content()
test_get_files_info()
test_write_file()
test_run_python_file()
