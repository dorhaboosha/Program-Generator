# How to run (Windows EXE)

This release contains a pre-built Windows executable of **Program Generator**.

The app generates Python programs using the OpenAI API, saves the generated code to `code_generate.py`,
runs it automatically, and retries up to 5 times if the generated code fails.

---

## 1) Extract the ZIP

1. Download the release `.zip`
2. Right‑click → **Extract All…**
3. Open the extracted folder

You should see something like:
- `ProgramGenerator.exe`
- `.env.example`
- `How to run.md`

---

## 2) Create your `.env` file

In the same folder as `ProgramGenerator.exe`, create a file named **`.env`**
and add your OpenAI API key:

```env
OPENAI_API_KEY=your_key_here
```

✅ Important: The `.env` file must be next to the `.exe`.

---

## 3) Run the app

Double‑click `ProgramGenerator.exe`.

- If you press **Enter** at the prompt, the app will choose a random program idea.
- Otherwise, type your own program request and press Enter.

---

## Output

When generation succeeds:
- `code_generate.py` will be created in the same folder
- The file will include assert‑based tests
- The file is formatted with Black
- The file may open automatically after success (Windows)

If generation fails:
- You’ll see the error output
- The app retries up to 5 times
- Final message: `Code generation FAILED after 5 attempts.`

---

## Common issues

### “Missing OPENAI_API_KEY”
- Make sure `.env` exists
- Make sure it’s named **.env** (not `.env.txt`)
- Make sure it’s in the same folder as `ProgramGenerator.exe`

### “Invalid OPENAI_API_KEY (401)”
- Your key is wrong/expired.
- Update the value inside `.env`.

---

## Security note

This app **executes AI-generated Python code** on your machine.
Only run it in an environment you trust.
