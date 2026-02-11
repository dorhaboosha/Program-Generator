import os
import random
import subprocess
import sys
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

MODEL = "gpt-4o-mini"  # safer than gpt-3.5-turbo

PROGRAMS_LIST = [
    """Given two strings str1 and str2, prints all interleavings of the given
two strings. You may assume that all characters in both strings are
different. Input: str1 = "AB", str2 = "CD" ...""",
    "A program that checks if a number is a palindrome",
    "A program that finds the kth smallest element in a given binary search tree",
    "A program that gets number and check if it is prime",
    "A program that calculate the GCD of two numbers",
]

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

        # Optional: stop on quota/billing issues too (uncomment if you want)
        # if "insufficient_quota" in msg or "quota" in msg or "billing" in msg:
        #     raise SystemExit(
        #         "❌ No available quota / billing issue.\n"
        #         "Check your OpenAI plan/billing and try again."
        #     ) from e

        raise

    content = resp.choices[0].message.content or ""
    parts = content.split("@@D")
    if len(parts) < 3:
        raise ValueError(f"Model did not wrap code with @@D. Got:\n{content[:500]}")
    return parts[1].strip()


def get_program() -> str:
    user_input = input("Tell me what program you want. Press Enter for a random one: ").strip()
    return user_input if user_input else random.choice(PROGRAMS_LIST)


def run_generated_file(file_name: str):
    """
    Run the generated file.
    - In dev: uses "python"
    - In PyInstaller: uses the running executable path (sys.executable)
    """
    python_exe = sys.executable if getattr(sys, "frozen", False) else "python"
    return subprocess.run([python_exe, file_name], capture_output=True, text=True)


def main():
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
            # For invalid key (or other fatal exits), stop immediately.
            raise
        except Exception as e:
            errors.append(str(e))
            print(f"{Fore.RED}OpenAI response error: {e}{Fore.RESET}")
            continue

        print(f"{Fore.BLUE}Generated code:\n{run_code}{Fore.RESET}")

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(run_code)

        result = run_generated_file(file_name)

        if result.returncode == 0:
            print(f"{Fore.GREEN}Code creation completed successfully!{Fore.RESET}")

            formatted_code = black.format_file_contents(run_code, fast=False, mode=black.FileMode())
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(formatted_code)

            success = True
            try:
                os.startfile(file_name)  # Windows convenience
            except Exception:
                pass
            break
        else:
            errors.append(result.stderr)
            print(f"{Fore.RED}Error running generated code:\n{result.stderr}{Fore.RESET}")
            try:
                os.remove(file_name)
            except FileNotFoundError:
                pass

    if not success:
        print(f"{Fore.RED}Code generation FAILED after 5 attempts.{Fore.RESET}")


if __name__ == "__main__":
    main()
