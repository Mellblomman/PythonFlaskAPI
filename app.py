from flask import Flask, request, render_template, redirect, url_for, jsonify
import json
import os
from flask_basicauth import BasicAuth

app = Flask(__name__)
basic_auth = BasicAuth(app)

filename = "tasks.json"


def get_tasks():
    print(f"Current directory: {os.getcwd()}")
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({"tasks": []}, f, indent=2)
        return handle_errors("No file created, creating a file now", 404)
    try:
        with open(filename) as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return handle_errors("File not found!", 404)
    except json.JSONDecodeError:
        return handle_errors("Invalid JSON data in tasks file", 400)


@app.route("/")
def index():
    task_list = get_tasks()
    return render_template("index.html", tasks=task_list)


@app.route("/tasks", methods=["GET"])
def get_filtered_tasks():
    try:
        tasks = get_tasks()["tasks"]
        check_status = request.args.get("status")
        if check_status and check_status in ["completed", "pending"]:
            filtered_tasks = []
            for task in tasks:
                if task.get("status") == check_status:
                    filtered_tasks.append(task)
            if filtered_tasks:
                return {"tasks": filtered_tasks}
            else:
                return handle_errors(f"No {check_status} tasks found", 404)
        else:
            return {"tasks": tasks}
    except Exception as e:
        return handle_errors(f"Error while trying to get tasks: {e}", 500)


@app.route("/tasks", methods=["POST"])
def post_task():
    try:
        tasks = get_tasks()["tasks"]
        if request.content_type == 'application/json':
            new_description = request.json.get("description")
            new_category = request.json.get("category")
        else:
            new_description = request.form.get("description")
            new_category = request.form.get("category")
        new_task = {
            "id": len(tasks) + 1,
            "description": new_description,
            "category": new_category,
            "status": "pending"
        }
        tasks.append(new_task)
        with open(filename, "w") as f:
            json.dump({"tasks": tasks}, f, indent=2)

        if request.content_type == 'application/json':
            return {"message": "Task added successfully"}
        else:
            return redirect(url_for("index"))

    except Exception as e:
        return handle_errors(f"Error while adding task: {e}", 400)


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    try:
        tasks = get_tasks()["tasks"]
        for task in tasks:
            if task["id"] == int(task_id):
                return {"Task": task}
        return handle_errors("Task not found", 404)
    except Exception as e:
        return handle_errors(f"Error while trying to get tasks: {e}", 500)


app.config["BASIC_AUTH_USERNAME"] = "my_user"
app.config["BASIC_AUTH_PASSWORD"] = "mypassword"


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@basic_auth.required
def delete_task(task_id):
    try:
        tasks = get_tasks()["tasks"]
        updated_tasks = []
        found = False
        for task in tasks:
            if task["id"] != task_id:
                updated_tasks.append(task)
            else:
                found = True
        if not found:
            return handle_errors("Task not found", 404)
        with open(filename, "w") as f:
            json.dump({"tasks": updated_tasks}, f, indent=2)
        return handle_errors("Task deleted successfully!", 200)
    except Exception as e:
        return handle_errors(f"Error while deleting task: {e}", 500)


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        tasks = get_tasks()["tasks"]
        task_updated = False
        for task in tasks:
            if task["id"] == task_id:
                try:
                    task["description"] = request.json.get("description", task["description"])
                    task["category"] = request.json.get("category", task["category"])
                    task_updated = True
                except Exception as e:
                    return handle_errors(f"Error while updating task: {e}", 400)
        if task_updated:
            with open(filename, "w") as f:
                json.dump({"tasks": tasks}, f, indent=2)
            return handle_errors("Task updated successfully!", 200)
        else:
            return handle_errors("Task not found", 404)
    except Exception as e:
        return handle_errors(f"Error while updating task: {e}", 500)


@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def complete_task(task_id):
    try:
        tasks = get_tasks()["tasks"]
        task_found = False
        for task in tasks:
            if task["id"] == task_id:
                task["status"] = "completed"
                task_found = True
        if task_found:
            with open(filename, "w") as f:
                json.dump({"tasks": tasks}, f, indent=2)
            return handle_errors("Task completed successfully!", 200)
        else:
            return handle_errors("Task not found", 404)
    except Exception as e:
        return handle_errors(f"Error while completing task: {e}", 500)


@app.route("/tasks/categories", methods=["GET"])
def get_all_categories():
    try:
        tasks = get_tasks()["tasks"]
        categories = []
        for task in tasks:
            category = task["category"]
            if category not in categories:
                categories.append(category)
        return {"categories": categories}
    except Exception as e:
        return handle_errors(f"Error while trying to get categories: {e}", 500)


@app.route("/tasks/categories/<category_name>", methods=["GET"])
def get_tasks_by_category(category_name):
    try:
        tasks = get_tasks()["tasks"]
        tasks_in_category = []
        for task in tasks:
            if task["category"] == category_name:
                tasks_in_category.append(task)
        return {"tasks": tasks_in_category}
    except Exception as e:
        return handle_errors(f"Error while trying to get tasks by category: {e}", 500)


if __name__ == "__main__":
    app.run(debug=True)


def handle_errors(message, code):
    error_message = jsonify({"message": message})
    error_message.status_code = code
    return error_message
