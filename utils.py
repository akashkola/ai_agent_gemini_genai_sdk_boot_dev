from google.genai import types


def generate_fault_message(function_name: str, message: str) -> types.Content:
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name, response={"error": message}
            )
        ],
    )


def generate_success_message(function_name: str, message: str) -> types.Content:
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name, response={"result": message}
            )
        ],
    )
