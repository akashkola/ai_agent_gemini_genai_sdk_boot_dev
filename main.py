import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import call_function
from functions.get_files_info import GetFilesInfoFunction
from functions.get_file_content import GetFileContentFunction
from functions.write_file import WriteFileFunction
from functions.run_python_file import RunPythonFunction

MAX_ITERS = 10

system_prompt = """"
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read the content of a file
- Write to a file (create or overwrite)
- Run a Python file with optional arguments

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
""".strip()

working_directory_tool = types.Tool(
    function_declarations=[
        GetFileContentFunction.schema(),
        GetFilesInfoFunction.schema(),
        WriteFileFunction.schema(),
        RunPythonFunction.schema(),
    ]
)


def main(prompt: str, verbose_flag: bool) -> None:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        error_message = "API KEY 'GEMINI_API_KEY' is missing"
        raise Exception(error_message)

    client = genai.Client(api_key=api_key)

    messages = [types.Content(role="user", parts=[types.Part(text=prompt.strip())])]

    if verbose_flag:
        print(f"User prompt: {prompt}")

    for _ in range(MAX_ITERS):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[working_directory_tool],
                system_instruction=system_prompt,
            ),
        )

        if response is None or response.usage_metadata is None:
            error_message = "reponse is malformed, not able to view usage metadata"
            raise Exception(error_message)

        if verbose_flag:
            print(f"Prompt token: {response.usage_metadata.prompt_token_count}")
            print(f"Response token: {response.usage_metadata.candidates_token_count}")

        for candidate in response.candidates or []:
            if not candidate.content:
                continue
            for part in candidate.content.parts or []:
                if not part or not part.text:
                    continue
                print(f"AI: {part.text}\n")

            messages.append(candidate.content)

        if response.function_calls:
            for function_call_part in response.function_calls:
                print(
                    f"Calling function: {function_call_part.name}({function_call_part.args})\n"
                )

                response = call_function(function_call_part=function_call_part)
                print(f"Tool: {response}\n")
                messages.append(response)
        else:
            return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        error_message = "Prompt required"
        raise Exception(error_message)

    verbose_flag = False
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag = True

    prompt = sys.argv[1]
    main(prompt, verbose_flag)
