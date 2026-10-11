from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
app = Flask(__name__)
CORS(app)

load_dotenv(
    os.path.join(os.path.dirname(__file__), "..", ".env")
)


def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "productivity_db"),
        ssl_disabled=False
    )


@app.route("/")
def home():
    return "AI Productivity Assistant Backend is Running! 🚀"

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE email=%s",
        (email,)
    )

    if cursor.fetchone():
        cursor.close()
        db.close()
        return jsonify({"message": "Email already registered"}), 409

    hashed_password = generate_password_hash(password)

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (name, email, hashed_password)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Registration successful!"}), 201
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    db.close()

    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    from werkzeug.security import check_password_hash

    if not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful!",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }), 200

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    user_id = request.args.get("user_id")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM tasks WHERE user_id=%s ORDER BY id DESC",
        (user_id,)
    )

    tasks = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(tasks), 200
# ================= Task API =================

@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.json

    user_id = data.get("user_id")
    name = data.get("name")
    priority = data.get("priority", "Medium")
    due_date = data.get("due_date")

    if not user_id or not name:
        return jsonify({"message": "Task name is required"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """INSERT INTO tasks (user_id, name, priority, due_date)
           VALUES (%s, %s, %s, %s)""",
        (user_id, name, priority, due_date)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Task added successfully!"}), 201
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    completed = data.get("completed")

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE tasks SET completed=%s WHERE id=%s",
        (completed, task_id)
    )

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Task updated!"}), 200


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=%s",
        (task_id,)
    )

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Task deleted!"}), 200
@app.route("/api/notes", methods=["GET"])
def get_notes():
    user_id = request.args.get("user_id")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM notes WHERE user_id=%s ORDER BY id DESC",
        (user_id,)
    )

    notes = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(notes), 200


@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.json

    user_id = data.get("user_id")
    title = data.get("title")
    text = data.get("text")

    if not user_id or not title or not text:
        return jsonify({"message": "All fields are required"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO notes (user_id, title, text) VALUES (%s, %s, %s)",
        (user_id, title, text)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Note added successfully!"}), 201


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id=%s",
        (note_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Note deleted!"}), 200
# ================= GOALS API =================

@app.route("/api/goals", methods=["GET"])
def get_goals():
    user_id = request.args.get("user_id")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM goals WHERE user_id=%s ORDER BY id DESC",
        (user_id,)
    )

    goals = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(goals), 200


@app.route("/api/goals", methods=["POST"])
def add_goal():
    data = request.json

    user_id = data.get("user_id")
    name = data.get("name")
    progress = data.get("progress", 0)

    if not user_id or not name:
        return jsonify({"message": "Goal name is required"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO goals (user_id, name, progress) VALUES (%s, %s, %s)",
        (user_id, name, progress)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Goal added successfully!"}), 201


@app.route("/api/goals/<int:goal_id>", methods=["PUT"])
def update_goal(goal_id):
    data = request.json
    progress = data.get("progress")

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE goals SET progress=%s WHERE id=%s",
        (progress, goal_id)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Goal updated successfully!"}), 200


@app.route("/api/goals/<int:goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM goals WHERE id=%s",
        (goal_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Goal deleted!"}), 200
# ================= CALENDAR API =================

@app.route("/api/events", methods=["GET"])
def get_events():

    user_id = request.args.get("user_id")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM calendar WHERE user_id=%s ORDER BY id DESC",
        (user_id,)
    )

    events = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(events), 200


@app.route("/api/events", methods=["POST"])
def add_event():

    data = request.json

    user_id = data.get("user_id")
    name = data.get("name")
    event_date = data.get("event_date")
    event_time = data.get("event_time")

    if not user_id or not name or not event_date or not event_time:
        return jsonify({"message": "All fields are required"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """INSERT INTO calendar
        (user_id, name, event_date, event_time)
        VALUES (%s, %s, %s, %s)""",
        (user_id, name, event_date, event_time)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Event added successfully!"}), 201


@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM calendar WHERE id=%s",
        (event_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Event deleted!"}), 200

#-----------existing code...------------
@app.route("/api/ai-suggestion/<int:user_id>", methods=["GET"])
def ai_suggestion(user_id):

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = %s",
            (user_id,)
        )
        tasks = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM goals WHERE user_id = %s",
            (user_id,)
        )
        goals = cursor.fetchall()

        pending = [
            task for task in tasks
            if int(task["completed"]) == 0
        ]

        high = [
            task for task in pending
            if str(task["priority"]).lower() == "high"
        ]

        if high:
            message = (
                "🤖 Focus on your high-priority task: "
                + high[0]["name"]
            )

        elif pending:
            message = (
                "📋 You have "
                + str(len(pending))
                + " pending tasks. Complete them one by one."
            )

        elif goals:
            message = "🎯 Great! Focus on your goals and keep making progress."

        else:
            message = "🎉 You are all caught up! Add a new task or goal."

        cursor.close()
        db.close()

        return jsonify({
            "suggestion": message,
            "pending_tasks": len(pending),
            "goals": len(goals)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai-reminder/<int:user_id>", methods=["GET"])
def ai_reminder(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = %s",
            (user_id,)
        )

        tasks = cursor.fetchall()

        cursor.close()
        db.close()

        high = [
            task for task in tasks
            if int(task["completed"]) == 0
            and str(task["priority"]).lower() == "high"
        ]

        if high:
            message = (
                "🔥 Reminder: Complete your high-priority task: "
                + high[0]["name"]
            )

        else:
            pending = [
                task for task in tasks
                if int(task["completed"]) == 0
            ]

            if pending:
                message = (
                    "🔔 Reminder: You have "
                    + str(len(pending))
                    + " pending tasks."
                )
            else:
                message = "🎉 No pending tasks. You are all caught up!"

        return jsonify({"reminder": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/ai-goal/<int:user_id>", methods=["GET"])
def ai_goal(user_id):

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM goals WHERE user_id = %s",
            (user_id,)
        )

        goals = cursor.fetchall()

        cursor.close()
        db.close()

        if not goals:
            message = "🎯 No goals added yet. Create a goal to start!"

        else:
            goal = min(
                goals,
                key=lambda x: int(x["progress"])
            )

            progress = int(goal["progress"])

            if progress == 100:
                message = (
                    "🎉 Congratulations! You achieved your goal: "
                    + goal["name"]
                )

            elif progress < 50:
                message = (
                    "🎯 Your goal '" +
                    goal["name"] +
                    "' is " +
                    str(progress) +
                    "% complete. Try to work on it today!"
                )

            else:
                message = (
                    "💪 Good progress on '" +
                    goal["name"] +
                    "' (" +
                    str(progress) +
                    "%). Keep going!"
                )

        return jsonify({"goal_suggestion": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai-calendar/<int:user_id>", methods=["GET"])
def ai_calendar(user_id):

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM calendar WHERE user_id = %s",
            (user_id,)
        )

        events = cursor.fetchall()

        cursor.close()
        db.close()

        if not events:
            message = "📅 No upcoming events found."

        else:
            event = events[0]

            message = (
                "📅 Upcoming Event: " +
                event["name"] +
                " on " +
                event["event_date"] +
                " at " +
                event["event_time"]
            )

        return jsonify({"calendar_suggestion": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai-summary/<int:user_id>", methods=["GET"])
def ai_summary(user_id):

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = %s",
            (user_id,)
        )
        tasks = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM goals WHERE user_id = %s",
            (user_id,)
        )
        goals = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM calendar WHERE user_id = %s",
            (user_id,)
        )
        events = cursor.fetchall()

        cursor.close()
        db.close()

        pending = [
            task for task in tasks
            if int(task["completed"]) == 0
        ]

        high = [
            task for task in pending
            if str(task["priority"]).lower() == "high"
        ]

        summary = (
            "📋 You have " +
            str(len(pending)) +
            " pending tasks. "
        )

        if high:
            summary += (
                "🔥 Focus first on: " +
                high[0]["name"] +
                ". "
            )

        if goals:
            goal = min(
                goals,
                key=lambda x: int(x["progress"])
            )

            summary += (
                "🎯 Your current goal '" +
                goal["name"] +
                "' is " +
                str(goal["progress"]) +
                "% complete. "
            )

        if events:
            event = events[0]

            summary += (
                "📅 Upcoming event: " +
                event["name"] +
                " on " +
                event["event_date"] +
                " at " +
                event["event_time"] +
                "."
            )

        return jsonify({
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai-priority/<int:user_id>", methods=["GET"])
def ai_priority(user_id):

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = %s AND completed = 0",
            (user_id,)
        )

        tasks = cursor.fetchall()

        cursor.close()
        db.close()

        priority_order = {
            "high": 1,
            "medium": 2,
            "low": 3
        }

        tasks.sort(
            key=lambda task:
            priority_order.get(
                str(task["priority"]).lower(), 2
            )
        )

        return jsonify({
            "tasks": tasks
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(debug=True)