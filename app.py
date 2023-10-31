from flask import Flask, request
import json
import os

app = Flask(__name__)


def get_tasks():
    filename = "tasks.json"
    print(f"Current directory: {os.getcwd()}")
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(filename) as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {"message": "Tasks file not found!"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON data in tasks file"}


@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    tasks = get_tasks()
    return {"All tasks": tasks}


@app.route("/tasks", methods=["POST"])
def post_task():
    tasks = get_tasks()
    new_task = {
        "id": len(tasks) + 1,
        "description": request.json.get("description"),
        "category": request.json.get("category"),
        "status": "pending"
    }
    tasks.append(new_task)
    with open("tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)
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
    with open("tasks.json", "w") as f:
        json.dump(updated_tasks, f, indent=2)
    return {"msg": "Task deleted successfully!"}


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    tasks = get_tasks()
    for task in tasks:
        if task["id"] == int(task_id):
            task["description"] = request.json.get("description", task.get("description"))
            task["category"] = request.json.get("category", task.get("category"))
            with open("tasks.json", "w") as f:
                json.dump(tasks, f, indent=2)
                return {"message": "Task updated successfully"}
    return {"message": "Task not found"}


@app.route("/error-route", methods=["GET"])
def raise_error():
    raise (RuntimeError)


if __name__ == "__main__":
    app.run(debug=True)