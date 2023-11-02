from flask import Flask, request, render_template, redirect, url_for
import json
import os

app = Flask(__name__)

filename = "tasks.json"


def get_tasks():
    print(f"Current directory: {os.getcwd()}")
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({"tasks": []}, f, indent=2)
        return "No file created, creating a file now"
    try:
        with open(filename) as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {"message": "Tasks file not found!"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON data in tasks file"}


@app.route("/")
def index():
    task_list = get_tasks()
    return render_template("index.html", tasks=task_list)


@app.route("/submit", methods=["POST"])
def submit_task_from_html():
    tasks = get_tasks()["tasks"]
    new_task = {
        "id": len(tasks) + 1,
        "description": request.form.get("description"),
        "category": request.form.get("category"),
        "status": "pending"
    }
    tasks.append(new_task)

    with open(filename, "w") as f:
        json.dump({"tasks":tasks}, f, indent=2)

    return redirect(url_for("index"))


@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    tasks = get_tasks()
    return tasks


@app.route("/tasks", methods=["POST"])
def post_task():
    tasks = get_tasks()["tasks"]
    new_task = {
        "id": len(tasks) + 1,
        "description": request.json.get("description"),
        "category": request.json.get("category"),
        "status": "pending"
    }
    tasks.append(new_task)
    with open(filename, "w") as f:
        json.dump({"tasks": tasks}, f, indent=2)
    return {"msg": "Task added successfully"}


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    tasks = get_tasks()
    for task in tasks:
        if task["id"] == int(task_id):
            return {"Task": task}
    return {"message": "Task not found"}


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    tasks = get_tasks()
    updated_tasks = []
    for task in tasks:
        if task["id"] != int(task_id):
            updated_tasks.append(task)
    with open(filename, "w") as f:
        json.dump(updated_tasks, f, indent=2)
    return {"msg": "Task deleted successfully!"}


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    tasks = get_tasks()
    for task in tasks:
        if task["id"] == int(task_id):
            task["description"] = request.json.get("description", task.get("description"))
            task["category"] = request.json.get("category", task.get("category"))
            with open(filename, "w") as f:
                json.dump(tasks, f, indent=2)
                return {"message": "Task updated successfully"}
    return {"message": "Task not found"}


@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def complete_task(task_id):
    tasks = get_tasks()
    for task in tasks["tasks"]:
        if task["id"] == int(task_id):
            task["completed"] = True
    with open(filename, "w") as f:
        json.dump(tasks, f, indent=2)
    return {"message": "Task completed"}


@app.route("/tasks/categories", methods=["GET"])
def get_all_categories():
    tasks = get_tasks()
    categories = []
    for task in tasks:
        category = task["category"]
        if category not in categories:
            categories.append(category)
    return {"categories": categories}


@app.route("/tasks/categories/<category_name>", methods=["GET"])
def get_tasks_by_category(category_name):
    tasks = get_tasks()
    tasks_in_category = []
    for task in tasks:
        if task["category"] == category_name:
            tasks_in_category.append(task)
    return {"tasks": tasks_in_category}


if __name__ == "__main__":
    app.run(debug=True)