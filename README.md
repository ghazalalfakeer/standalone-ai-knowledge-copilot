# Standalone AI Knowledge Copilot

A modular Python project that will progressively evolve into a standalone AI-powered Knowledge Copilot.

This repository currently contains **Task 1 / Week 1: Python Engineering Foundations**.

## Task 1 Objectives

- Modular Python project structure
- Python virtual environment
- Dependency management with `requirements.txt`
- JSON file reading and writing
- JSON data modification
- Data validation
- Exception handling
- Custom exceptions
- Python type hints
- Sample knowledge data
- Runnable `main.py`
- `.gitignore`
- Git/GitHub-ready project

## Project Structure

```text
standalone-ai-knowledge-copilot/
│
├── data/
│   └── sample_knowledge.json
│
├── src/
│   ├── __init__.py
│   └── storage.py
│
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## Requirements

Python 3.10 or newer.

Check your Python version:

```bash
python --version
```

## Create Virtual Environment

### Windows

```powershell
python -m venv .venv
```

### macOS / Linux

```bash
python3 -m venv .venv
```

## Activate Virtual Environment

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
.venv\Scripts\activate.bat
```

### macOS / Linux

```bash
source .venv/bin/activate
```

## Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Task 1 currently uses only the Python standard library, so no external packages are required.

## Run the Project

```bash
python main.py
```

The application demonstrates:

1. Reading valid JSON
2. Validation
3. Adding a knowledge item
4. Updating a knowledge item
5. Deleting a knowledge item
6. Missing-file error handling
7. Malformed JSON error handling
8. Validation-error handling

## Git Setup

```bash
git init
git add .
git commit -m "Complete Task 1 Python engineering foundations"
git branch -M main
```

Create an empty repository on GitHub, then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/standalone-ai-knowledge-copilot.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Deactivate Virtual Environment

```bash
deactivate
```
