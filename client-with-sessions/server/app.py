from flask import request, session, jsonify
from config import app, db, bcrypt
from models import User, Task
from math import ceil

# Authentication Routes
@app.post("/signup")
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    password_confirmation = data.get("password_confirmation")

    if not username or not password or password != password_confirmation:
        return jsonify({"errors": ["Invalid signup details"]}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"errors": ["Username already exists"]}), 409

    user = User(username=username)
    user.password_hash = password
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return jsonify({"id": user.id, "username": user.username}), 201

@app.post("/login")
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.authenticate(password):
        session["user_id"] = user.id
        return jsonify({"id": user.id, "username": user.username})
    return jsonify({"errors": ["Invalid credentials"]}), 401

@app.get("/check_session")
def check_session():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({"id": user.id, "username": user.username})
    return jsonify({}), 401

@app.delete("/logout")
def logout():
    session["user_id"] = None
    return {}, 204

# Task Routes (CRUD)
@app.get("/tasks")
def get_tasks():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 5))

    query = Task.query.filter_by(user_id=user_id)
    total_tasks = query.count()
    tasks = query.order_by(Task.id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    task_list = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description
        }
        for task in tasks
    ]

    return jsonify({
        "tasks": task_list,
        "page": page,
        "per_page": per_page,
        "total_pages": ceil(total_tasks / per_page)
    })

@app.post("/tasks")
def create_task():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    task = Task(title=title, description=description, user_id=user_id)
    db.session.add(task)
    db.session.commit()

    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description
    }), 201

@app.patch("/tasks/<int:id>")
def update_task(id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    task = Task.query.filter_by(id=id, user_id=user_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)

    db.session.commit()

    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description
    })

@app.delete("/tasks/<int:id>")
def delete_task(id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    task = Task.query.filter_by(id=id, user_id=user_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return {}, 204