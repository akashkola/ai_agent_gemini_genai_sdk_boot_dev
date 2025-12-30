# AIAgent — Documentation

## What is this?
A simple AI coding agent powered by **Google Gemini 2.0 Flash**. Give it a natural language prompt, and it will use function calling to read/write files and run Python scripts in a sandboxed `working_directory` (e.g., `calculator`).

## Quick start
1. **Install dependencies with `uv`**:
   ```bash
   uv sync
   ```
2. **Set your Gemini API key**:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   # or add to .env
   echo "GEMINI_API_KEY=your-api-key" > .env
   ```
3. **Run**:
   ```bash
   uv run python main.py "List all files in the calculator directory"
   uv run python main.py "Create a script that adds 1+1" --verbose
   uv run python main.py "Run my tests and check for errors"
   ```

## How it works
- **main.py**: agentic loop (max 10 iterations) that sends prompts + tool schemas to Gemini 2.0 Flash.
- **call_function.py**: routes function calls to the correct tool handler (all within `working_directory`).
- **functions/**: four tool implementations inheriting from `CodingToolFunctionInterface`.
- **utils.py**: helpers for wrapping success/error responses as Gemini-compatible `types.Content`.
- **config.py**: constants like `MAX_CHARS_TO_READ_FROM_FILE`.

**Flow**:
```
User prompt → Gemini (with tool schemas) → Gemini calls a function
→ Execute locally in working_directory → Send result to Gemini
→ Repeat (max 10 iterations) or return
```

## Tools available

All tools inherit from `CodingToolFunctionInterface` and validate paths stay within `working_directory`.

### GetFileContentFunction
- **Name**: `get_file_content`
- **Purpose**: read and return file content.
- **Parameters**: `file_path` (string, required) — relative path to the file.
- **Returns**: file content (capped at `MAX_CHARS_TO_READ_FROM_FILE`=1800 chars), or error.
- **Path validation**: rejects absolute paths and traversal attempts (e.g., `../`).

### GetFilesInfoFunction
- **Name**: `get_files_info`
- **Purpose**: list files/directories with sizes and type info.
- **Parameters**: `directory` (string, optional, defaults to `.`) — relative directory path.
- **Returns**: formatted list with `name`, `file_size` (bytes), `is_dir` flag per item.
- **Path validation**: rejects paths outside working directory.

### WriteFileFunction
- **Name**: `write_file`
- **Purpose**: create or overwrite a file with given content.
- **Parameters**:
  - `file_path` (string, required) — relative path.
  - `content` (string, required) — file content.
- **Returns**: success message with character count, or error.
- **Features**: automatically creates parent directories; validates path safety.

### RunPythonFunction
- **Name**: `run_python_file`
- **Purpose**: execute a Python script with `python3`.
- **Parameters**:
  - `python_file_path` (string, required) — relative path to `.py` file.
  - `args` (array of strings, optional) — CLI arguments for the script.
- **Returns**: stdout/stderr combined, or error message.
- **Features**: 30-second timeout; runs with `cwd=working_directory`; validates `.py` extension and file existence.

**Security**: All tools enforce relative paths and validate against traversal (e.g., `/bin/cat`, `../../../etc` rejected).

## Design: Decoupled tools via abstract base class

Each tool inherits from `CodingToolFunctionInterface`, making it easy to add new tools without modifying the core agentic loop—just implement `name()`, `schema()`, and `handle_function_call()`, then register the schema.

## Configuration

- **MAX_ITERS** (main.py): max 10 iterations of the agentic loop (prevents infinite loops).
- **MAX_CHARS_TO_READ_FROM_FILE** (config.py): 1800 chars max per file read (memory protection).
- **working_directory** (call_function.py): hardcoded to `"calculator"` (sandbox boundary).
- **System prompt** (main.py): instructs Gemini to make function call plans using only the four available tools.

## Working Directory Structure

The agent operates within a sandboxed `calculator/` directory:

```
calculator/
├── main.py               # Entry point; parses CLI args calls Calculator
├── tests.py              # Unit tests (unittest framework)
├── pkg/
│   ├── calculator.py     # Core Calculator class (infix expression evaluation)
│   └── render.py         # Output formatting (JSON)
└── README.md             # Minimal docs
```

### calculator/pkg/calculator.py
- **Calculator class**: evaluates mathematical expressions using operator precedence.
- **Operators**: `+`, `-`, `*`, `/` (with correct precedence: `*`/`/` > `+`/`-`).
- **Method `evaluate(expression)`**: parses space-separated tokens and returns float result.
- **Infix evaluation**: uses the shunting-yard algorithm for correct operator precedence and left-to-right associativity.

### calculator/tests.py
- **9 unit tests** covering:
  - Basic operations (addition, subtraction, multiplication, division).
  - Complex/nested expressions with multiple operators.
  - Edge cases (empty expressions, invalid operators, insufficient operands).
- **Run with**: `uv run python tests.py` (within `calculator/` working directory).

## Usage examples

### Example 1: Simple read
```bash
uv run python main.py "What's in main.py?"
```

### Example 2: Fix and verify (real-world scenario)
```bash
uv run python main.py "Hey my calculator is misbehaving, as well as previously written unit tests are also failing. Could you please check the issue?"
```

**Agent flow**:
1. Lists files in `calculator/` → sees `main.py`, `tests.py`, `pkg/`
2. Reads `main.py` → understands entry point
3. Reads `tests.py` → sees unit test expectations
4. Reads `pkg/calculator.py` → identifies precedence bug (addition had precedence 3 instead of 1)
5. Fixes the bug in `pkg/calculator.py` → writes corrected version
6. Runs `tests.py` → verifies all 9 tests pass ✓

### Example 3: Write and run
```bash
uv run python main.py "Create a script called hello.py that prints 'Hello, World!' and run it"
```

### Example 4: Verbose output (show tokens and function calls)
```bash
uv run python main.py "List all Python files in the directory" --verbose
```

## Project setup

- **Python version**: 3.12+ (see `.python-version`).
- **Package manager**: `uv` with `uv.lock` for reproducible builds.
- **Dependencies**:
  - `google-genai==1.12.1` — Gemini 2.0 Flash SDK.
  - `python-dotenv==1.1.0` — `.env` support for API key.
- **Dev dependencies**:
  - `ruff>=0.14.10` — linter and formatter (clean code!).

## Code quality

Your code is **already clean**:
- Strong typing throughout (Gemini SDK types used precisely).
- Clear function contracts via abstract base.
- No broad `Any` types.
- Path validation hardened against traversal.
- Focused, single-responsibility functions.
- Infix expression evaluation uses correct operator precedence and associativity.

Lint & format:
```bash
uv run ruff check .
uv run ruff format .
```

## Testing

Manual tests in `tests.py` (root level) cover:
- `test_get_file_content()` — read existing/non-existing files, path traversal rejection.
- `test_get_files_info()` — list directory, invalid paths, parent traversal.
- `test_write_file()` — create files, nested dirs, path safety.
- `test_run_python_file()` — execute scripts with args, timeout, validation.

Run:
```bash
uv run python tests.py
```

Calculator unit tests in `calculator/tests.py`:
```bash
cd calculator && uv run python tests.py
```

## Troubleshooting

- **"API KEY 'GEMINI_API_KEY' is missing"**: Set `export GEMINI_API_KEY=your-key` or add to `.env`.
- **"Prompt required"**: Usage is `uv run python main.py "your prompt"`.
- **Agent doesn't terminate**: Check `MAX_ITERS=10` in main.py; increase if needed.
- **File read truncated**: Check `MAX_CHARS_TO_READ_FROM_FILE=1800` in config.py.
- **Path rejected**: All paths must be relative to `working_directory` (default: `calculator`); no absolute paths or `../` allowed.
- **Function not found**: Ensure tool schema is in `working_directory_tool.function_declarations` in main.py.
- **Timeout on script execution**: RunPythonFunction has a 30-second timeout; long-running scripts will error.
- **Calculator tests failing**: Check operator precedence in `calculator/pkg/calculator.py` (multiplication/division should be 2, addition/subtraction should be 1).
