# Program Generator

A **CLI tool that generates Python programs using the OpenAI API**, saves the generated code to a file, **runs it automatically**, and retries up to **5 times** if the generated code fails.

This project is based on **"a Python program that writes Python programs”.** 

---

## What this project does

- Asks the user what Python program to generate (or picks a random idea from a list).
- Calls the OpenAI Chat Completions API to generate **Python code only**.
- Requires the generated code to include **assert-based unit tests** (at least **5 test cases**).
- Writes the generated code into `code_generate.py`.
- Runs `code_generate.py` via `subprocess.run`.
- If errors happen, it feeds the error back into the next prompt and retries up to **5 times**.
- On success, formats the file with **Black** and opens the generated file automatically (Windows).

It also includes:
- Console colors via **Colorama**
- Auto-formatting via **Black**

---

## Project files

- `superpythoncoder.py` — the main program
- `requirements.txt` — dependencies
- `.env.example` — environment variables template 
- `.env` — **your local secret key** 
- `programmer.ico` — icon used for `.exe` file

---

## Requirements

- Python **3.10+** recommended
- An OpenAI API key (`OPENAI_API_KEY`)

---

## Run from source (clone)

### 1) Clone
```bash
git clone https://github.com/dorhaboosha/Program-Generator.git
cd Program-Generator
```

### 2) Create & activate a virtual environment

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD)**
```bat
python -m venv .venv
.venv\Scripts\activate
```

### 3) Install dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Create `.env`
Create a file named `.env` **next to** `superpythoncoder.py` and add:
```env
OPENAI_API_KEY=your_key_here
```

### 5) Run
```bash
python superpythoncoder.py
```

---

## Output

If generation succeeds, you’ll see:
- A printed success message
- A new file: `code_generate.py`
- The generated file opens automatically (Windows)

If generation fails, you’ll see:
- Errors printed to the console
- Up to 5 retries
- Final message: `Code generation FAILED after 5 attempts.`

---

## Download & run (Release EXE)

A pre-built Windows **EXE** is available in the GitHub **Releases** section, so you can run the app without installing Python.

### Steps
1. Download the latest release `.zip`
2. Extract it
3. Put a `.env` file **in the same folder as the `.exe`**
   ```env
   OPENAI_API_KEY=your_key_here
   ```
4. Run the executable (double-click)

> The `.env` file must be next to the `.exe` so the program can load it.

---

## Notes & safety

This app **executes AI-generated Python code** on your machine. Only run it in an environment you trust.
