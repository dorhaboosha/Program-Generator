"""
Super Python Coder — generate and run Python programs via OpenAI.

This script prompts for a program description (or picks a random example),
calls the OpenAI API to generate Python code, runs it in-process, and
optionally retries with error feedback. Successful code is written to
`code_generate.py`, formatted with Black, and opened (on Windows).
Requires OPENAI_API_KEY in a .env file next to the script or executable.
"""

import os
import random
import sys
import traceback
from functools import lru_cache
from pathlib import Path

import black
from colorama import Fore
from dotenv import load_dotenv
from openai import OpenAI


def load_env():
    """
    Load .env from the same folder as the script (dev) or the .exe (PyInstaller).
    """
    base_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    env_path = base_dir / ".env"
    load_dotenv(dotenv_path=env_path)


load_env()

# OpenAI model used for code generation (gpt-4o-mini is cheaper and reliable).
MODEL = "gpt-4o-mini"

# Example program descriptions shown when the user presses Enter without typing.
PROGRAMS_LIST = [
    """Given two strings str1 and str2, prints all interleavings of the given
two strings. You may assume that all characters in both strings are
different. Input: str1 = "AB", str2 = "CD" ...""",
    "A program that checks if a number is a palindrome",
    "A program that finds the kth smallest element in a given binary search tree",
    "A program that gets number and check if it is prime",
    "A program that calculate the GCD of two numbers",
]

# Instructions sent to the model so it returns only code wrapped in @@D markers.
SYSTEM_PROMPT = (
    "You are a Python developer. Output ONLY Python code.\n"
    "Include assert-based tests (at least 5 different test cases).\n"
    "Wrap the FULL code between @@D markers like:\n"
    "@@D\n<code>\n@@D\n"
    "Do not add explanations or extra text."
)


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    """
    Lazily create and cache the OpenAI client.
    This prevents import-time failure during offline tests (mocking).
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY. Put it in a .env file next to this script/exe.")
    return OpenAI(api_key=api_key)


def code_from_openai(request: str) -> str:
    """
    Call OpenAI and extract the code wrapped between @@D markers.

    Important:
    - If the API key is invalid (401), stop immediately (no point retrying).
    - For other errors, raise normally so the retry loop can handle it.
    """
    client = get_client()

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request},
            ],
            temperature=0.4,
        )
    except Exception as e:
        msg = str(e).lower()

        # Stop immediately on auth/key issues
        if "401" in msg or "invalid_api_key" in msg or "incorrect api key" in msg:
            raise SystemExit(
                "❌ Invalid OPENAI_API_KEY (401).\n"
                "Fix your .env file and try again.\n"
                "Example:\n"
                "OPENAI_API_KEY=your_real_key_here"
            ) from e

        raise

    content = resp.choices[0].message.content or ""
    parts = content.split("@@D")
    if len(parts) < 3:
        raise ValueError(f"Model did not wrap code with @@D. Got:\n{content[:500]}")
    return parts[1].strip()


def get_program() -> str:
    """
    Ask the user for a program description; if empty, return a random item from PROGRAMS_LIST.
    """
    user_input = input("Tell me what program you want. Press Enter for a random one: ").strip()
    return user_input if user_input else random.choice(PROGRAMS_LIST)


def run_generated_code(code: str) -> tuple[bool, str]:
    """
    Execute the generated code in-process (works in both .py and .exe).
    Returns (success, error_message).

    This avoids trying to call "python" from a bundled EXE (which may not exist),
    and avoids re-running the EXE recursively via sys.executable.
    """
    try:
        compiled = compile(code, "code_generate.py", "exec")
        exec_globals = {"__name__": "__main__"}
        exec(compiled, exec_globals)
        return True, ""
    except Exception:
        return False, traceback.format_exc()


def main():
    """
    Main flow: get program description, call OpenAI (up to 5 times with error feedback),
    run generated code, format with Black, and save to code_generate.py.
    """
    program = get_program()
    errors = []
    run_code = ""
    success = False
    file_name = "code_generate.py"

    for _ in range(5):
        if errors:
            request = (
                "I ran your previous code and got an error.\n\n"
                f"ERROR:\n{errors[-1]}\n\n"
                f"CODE I RAN:\n{run_code}\n\n"
                "Please return the FULL fixed code with assert tests.\n"
                "Remember: wrap code with @@D."
            )
        else:
            request = (
                f"Write this program in Python: {program}\n"
                "Include assert tests with 5 different inputs.\n"
                "Wrap code with @@D."
            )

        print(f"{Fore.CYAN}{request}{Fore.RESET}")

        try:
            run_code = code_from_openai(request)
        except SystemExit:
            raise
        except Exception as e:
            errors.append(str(e))
            print(f"{Fore.RED}OpenAI response error: {e}{Fore.RESET}")
            continue

        print(f"{Fore.BLUE}Generated code:\n{run_code}{Fore.RESET}")

        # Write the raw code first (useful even if execution fails)
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(run_code)

        ok, err = run_generated_code(run_code)

        if ok:
            print(f"{Fore.GREEN}Code creation completed successfully!{Fore.RESET}")

            try:
                formatted_code = black.format_file_contents(run_code, fast=False, mode=black.FileMode())
            except black.NothingChanged:
                formatted_code = run_code
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(formatted_code)

            success = True
            try:
                os.startfile(file_name)  # Windows convenience
            except Exception:
                pass
            break
        else:
            errors.append(err)
            print(f"{Fore.RED}Error running generated code:\n{err}{Fore.RESET}")
            try:
                os.remove(file_name)
            except FileNotFoundError:
                pass

    if not success:
        print(f"{Fore.RED}Code generation FAILED after 5 attempts.{Fore.RESET}")


def pause_if_frozen():
    """
    When running as a built .exe, keep the console window open so the user can read errors.
    """
    if getattr(sys, "frozen", False):
        input("\nPress Enter to close...")


if __name__ == "__main__":
    # Run main; on .exe, pause so the user can read any error before the window closes.
    try:
        main()
    except SystemExit as e:
        if str(e):
            print(f"\n{Fore.RED}{e}{Fore.RESET}")
        pause_if_frozen()
        raise
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Fore.RESET}")
        pause_if_frozen()
        raise
