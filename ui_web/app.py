git #!/usr/bin/env python3

import os
from pathlib import Path
from typing import Dict

from flask import Flask, render_template, request, redirect, url_for, flash

# Ensure we can import TaskManager from sibling directory
import sys
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from task_manager import TaskManager  # noqa: E402


def create_app() -> Flask:
    app = Flask(__name__, template_folder=str(CURRENT_DIR / "templates"), static_folder=str(CURRENT_DIR / "static"))
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

    data_file_env = os.environ.get("TASKS_JSON_PATH")
    if data_file_env:
        task_manager = TaskManager(data_file=data_file_env)
    else:
        task_manager = TaskManager(data_file=str(PROJECT_ROOT / "tasks.json"))

    @app.context_processor
    def inject_globals() -> Dict:
        return {
            "APP_NAME": "Task Manager UI"
        }

    @app.route("/")
    def index():
        status = request.args.get("status") or None
        priority = request.args.get("priority") or None
        query = request.args.get("q") or None

        if query:
            tasks = task_manager.search_tasks(query)
        else:
            tasks = task_manager.list_tasks(status=status, priority=priority)

        stats = task_manager.get_stats()
        return render_template("index.html", tasks=tasks, stats=stats, status=status, priority=priority, query=query)

    @app.post("/tasks")
    def create_task():
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        priority = (request.form.get("priority") or "medium").strip().lower()
        if not title:
            flash("Title is required", "danger")
            return redirect(url_for("index"))
        if priority not in ["high", "medium", "low"]:
            priority = "medium"
        task_manager.add_task(title=title, description=description, priority=priority)
        flash("Task created", "success")
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/update")
    def update_task(task_id: int):
        task = task_manager.get_task(task_id)
        if not task:
            flash("Task not found", "danger")
            return redirect(url_for("index"))

        new_title = (request.form.get("title") or task["title"]).strip()
        new_desc = (request.form.get("description") or task.get("description", "")).strip()
        new_priority = (request.form.get("priority") or task.get("priority", "medium")).strip().lower()
        new_status = (request.form.get("status") or task.get("status", "pending")).strip().lower()

        if new_priority not in ["high", "medium", "low"]:
            new_priority = task.get("priority", "medium")
        if new_status not in ["pending", "completed"]:
            new_status = task.get("status", "pending")

        task_manager.update_task(task_id, title=new_title, description=new_desc, priority=new_priority, status=new_status)
        flash("Task updated", "success")
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/toggle")
    def toggle_task(task_id: int):
        task = task_manager.get_task(task_id)
        if not task:
            flash("Task not found", "danger")
            return redirect(url_for("index"))
        new_status = "completed" if task.get("status") != "completed" else "pending"
        task_manager.update_task(task_id, status=new_status)
        flash("Task status toggled", "info")
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id: int):
        ok = task_manager.delete_task(task_id)
        if ok:
            flash("Task deleted", "warning")
        else:
            flash("Task not found", "danger")
        return redirect(url_for("index"))

    @app.get("/stats")
    def stats():
        stats_data = task_manager.get_stats()
        return render_template("stats.html", stats=stats_data)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

