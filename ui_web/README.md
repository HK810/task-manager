# Task Manager UI (Flask)

## Quick start

1. Create a virtual environment (recommended) and install dependencies:

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: . .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

2. Run the server from this folder:

```bash
set FLASK_APP=app.py
set FLASK_ENV=development
# Optional: set custom JSON path (defaults to ../tasks.json)
# set TASKS_JSON_PATH=D:\\STUDY FILES\\PROGRAMMING\\hack_2025\\task-manager_ui\\tasks.json
python app.py
```

3. Open the app at `http://localhost:5000`.

## Notes

- The UI reuses the existing `TaskManager` class and reads/writes the shared `tasks.json`.
- Configure `TASKS_JSON_PATH` env var to point elsewhere if needed.
