# import sqlite3 #database
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

load_dotenv() #lRead the .env file and make
#those variables available to my program.



app= Flask(__name__)

frontend_origin = os.environ.get("FRONTEND_ORIGIN")

allowed_origins = [
    "http://127.0.0.1:5500"
]

if frontend_origin:
    allowed_origins.append(frontend_origin)


CORS(app,
     origins=allowed_origins,
     supports_credentials=True)

app.secret_key = os.getenv("SECRET_KEY")

def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    sslmode = os.getenv("DB_SSLMODE")

    connection_options = {}

    if sslmode:
        connection_options["sslmode"] = sslmode

    if database_url:
        return psycopg2.connect(
            database_url,
            **connection_options
        )

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432"),
        **connection_options
    )




#json test stories

stories=[{"id":1,
         "name": "Tanneh",
         "story": "This is my first backend"

}]

@app.route("/stories", methods=["GET"])
def get_stories():
    user_id =session.get("user_id")
    if not user_id:
        return jsonify({"error": "user not authentiated"}), 401


    conn = get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""
    SELECT stories.id, stories.user_id, users.name, stories.story, stories.created_at
    FROM stories
    JOIN users ON stories.user_id = users.id
    ORDER BY stories.created_at DESC
""")


    rows=cursor.fetchall()

    conn.close()
    stories_list = []

    for row in rows:
        stories_list.append({
            "id": row[0],
            "user_id": row[1],
            "name": row[2],
            "story": row[3],
            "created_at": row[4].isoformat()
        })


    return jsonify(stories_list)


@app.route("/stories", methods=["POST"])
def create_story():
     user_id = session.get("user_id")

     if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

     data=request.get_json(silent=True)

     if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

     story=data.get("story")

     if not isinstance(story, str):
        return jsonify({"error": "Story must be a string"}), 400

     story=story.strip()

     if not story or len(story) > 500:
        return jsonify({"error": "Story must be between 1 and 500 characters"}), 400

     conn = get_db_connection()

     cursor=conn.cursor()

     cursor.execute("SELECT name FROM users WHERE id =%s", (user_id,))

     registered_name=cursor.fetchone()

     if not registered_name:
         session.pop("user_id", None)
         conn.close()
         return jsonify({"error": "User not authenticated"}), 401

     cursor.execute(
   """
    INSERT INTO stories (user_id, story)
    VALUES (%s, %s)
    RETURNING id, story, created_at, user_id
""",  ( user_id, story))



     new_story = cursor.fetchone()
     conn.commit()
     conn.close()

     return jsonify({
    "id": new_story[0],
    "name": registered_name[0],
    "story": new_story[1],
    "created_at": new_story[2].isoformat(),
    "user_id":new_story[3]
}), 201

@app.route("/register", methods=["POST"])
def register():
    data=request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Request body must be a valid JSON object"}), 400

    name=data.get("name")
    username=data.get("username")
    password=data.get("password")

    if not all(isinstance(value, str) for value in (name, username, password)):
        return jsonify({"message": "Name, username, and password must be strings"}), 400

    name=name.strip()
    username=username.strip()

    #validate
    if not name or not username or not password:
        return jsonify({"message": "All fields are required"}), 400
    if len(name) > 100:
       return jsonify({"message": "Name must be 100 characters or fewer"}), 400
    if len(username) > 30:
       return jsonify({"message": "Username must be 30 characters or fewer"}), 400
    if len(password) < 8 or len(password) > 128:
       return jsonify({"message": "Password must be between 8 and 128 characters"}), 400
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT id FROM users "
            "WHERE username=%s" ,(username,)
            )
    exsiting_user=cursor.fetchone()
    if exsiting_user:
            conn.close()
            return jsonify({"message":"Username already exists"}),400


    password_hash=generate_password_hash(password)
    cursor.execute("INSERT INTO users "
    "(name,username,password_hash)VALUES"
    " (%s, %s,%s)",
    (name,username,password_hash))
    conn.commit()
    conn.close()
    return jsonify({"message":"Account created"}),201

@app.route("/login", methods=["POST"])
def app_login():
    data=request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body."}), 400

    username=data.get("username")
    password=data.get("password")

    if not username or not password:
        return jsonify({"error": "Username or password is missing."}), 400

    conn=get_db_connection()
    cursor=conn.cursor()

    cursor.execute("SELECT id, password_hash FROM users WHERE username =%s", (username,) )

    user=cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "wrong username or password"}), 401
    if not check_password_hash(user[1], password):
        conn.close()
        return jsonify({"error": "wrong username or password"}), 401

    session["user_id"]=user[0]

    conn.close()
    return jsonify({"message": "Login successful"}), 200

@app.route("/logout", methods=["POST"])

def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/current-user", methods=["GET"])
def current_user():
 user_id=session.get("user_id")

 if not user_id:
     return jsonify({"error": "User not authenticated"}), 401
 conn =get_db_connection()
 cursor=conn.cursor()

 cursor.execute(
    "SELECT id, name FROM users WHERE id = %s",
    (user_id,)
)
 user=cursor.fetchone()

 if not user:
    session.pop("user_id", None)
    conn.close()
    return jsonify({"error": "User not authenticated"}), 401

 conn.close()
 return jsonify({
    "id": user[0],
    "name":user[1]}), 200

@app.route("/stories/<int:story_id>", methods=["DELETE"])
def delete_story(story_id):
    user_id=session.get("user_id")
    if not user_id:
        return jsonify({"error":"user is not authorized"}), 401

    conn = get_db_connection()
    cursor=conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id=%s ",
                   (user_id,))

    user =cursor.fetchone()
    if not user:
        session.pop("user_id", None)
        conn.close()
        return jsonify({"error": "user not found"}), 401

    cursor.execute("SELECT user_id FROM stories WHERE id =%s",
                   (story_id,))
    found_story=cursor.fetchone()

    if not found_story:
        conn.close()
        return({"error":"story not found"}), 404

    found_id=found_story[0]

    if found_id != user_id:
        conn.close()
        return({"error" : "not authorized to delete this story"}), 403


    cursor.execute("DELETE FROM stories WHERE id=%s",
                   (story_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Story deleted"}), 200

@app.route("/stories/<int:story_id>", methods=["PATCH"])
def update_story(story_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "User is not authorized"}), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

    story = data.get("story")

    if not isinstance(story, str):
        return jsonify({"error": "Story must be a string"}), 400

    story = story.strip()

    if not story or len(story) > 500:
        return jsonify({"error": "Story must be between 1 and 500 characters"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id FROM users WHERE id = %s",
            (user_id,)
        )

        existing_user = cursor.fetchone()

        if not existing_user:
            session.pop("user_id", None)
            return jsonify({"error": "No user found"}), 401

        cursor.execute(
            "SELECT user_id FROM stories WHERE id = %s",
            (story_id,)
        )

        story_owner = cursor.fetchone()

        if not story_owner:
            return jsonify({"error": "Story not found"}), 404

        if story_owner[0] != user_id:
            return jsonify({
                "error": "Not authorized to edit this story"
            }), 403

        cursor.execute("""
            UPDATE stories
            SET story = %s
            WHERE id = %s
            RETURNING id, story, created_at, user_id
        """, (story, story_id))

        updated_story = cursor.fetchone()
        conn.commit()

        return jsonify({
            "id": updated_story[0],
            "story": updated_story[1],
            "created_at": updated_story[2],
            "user_id": updated_story[3]
        }), 200

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()







if __name__== "__main__":
     app.run(debug=True, port=5000)
