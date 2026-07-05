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
CORS(app)

app.secret_key = os.getenv("SECRET_KEY")

def get_db_connection():
    conn=psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER")
    )

    return conn

#database file create 
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            story TEXT NOT NULL
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
     

#json test stories

stories=[{"id":1,
         "name": "Tanneh",
         "story": "This is my first backend"
     
}]

@app.route("/stories", methods=["GET"])
def get_stories():

    #conn=sqlite3.connect("stories.db")
    conn = get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""
    SELECT id, name, story, created_at
    FROM stories
    ORDER BY id DESC
""")
   

    rows=cursor.fetchall()

    conn.close()
    stories_list = []

    for row in rows:
        stories_list.append({
            "id": row[0],
            "name": row[1],
            "story": row[2],
            "created_at": row[3].isoformat()
        })
       
    
    return jsonify(stories_list)


@app.route("/stories", methods=["POST"])
def create_story():
     
     data=request.get_json()
    
     conn = get_db_connection()
     
     cursor=conn.cursor()

     cursor.execute(
   """
    INSERT INTO stories (name, story)
    VALUES (%s, %s)
    RETURNING id, name, story, created_at
""", (data["name"], data["story"]))
     
     

     new_story = cursor.fetchone()
     conn.commit()
     conn.close()
     
     

     return jsonify({
    "id": new_story[0],
    "name": new_story[1],
    "story": new_story[2],
    "created_at": new_story[3].isoformat()
}), 201

@app.route("/register", methods=["POST"])
def register():
    data=request.get_json()
    name=data["name"]
    username=data["username"]
    password=data["password"]
    #validate 
    if not name or not username or not password:
        return jsonify({"message": "All fields are required"}), 400
    if len(password) < 8:
       return jsonify({"message": "Password must be at least 8 characters"}), 400
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

@app.route("/stories/<int:story_id>", methods=["DELETE"])
def delete_story(story_id):
     
    #conn=sqlite3.connect("stories.db")
    conn = get_db_connection()
    cursor=conn.cursor()

    cursor.execute("DELETE FROM stories WHERE id=%s",
                   (story_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Story deleted"})

@app.route("/stories/<int:story_id>", methods=["PATCH"])
def edit_story(story_id):
    data=request.get_json()
    #conn=sqlite3.connect("stories.db")
    conn = get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""
    UPDATE stories
    SET story = %s
    WHERE id = %s
    RETURNING id, name, story, created_at
""", (data["story"], story_id))
    
    updated_story=cursor.fetchone()

    conn.commit()
    conn.close()

    return jsonify({
    "id": updated_story[0],
    "name": updated_story[1],
    "story": updated_story[2],
    "created_at": updated_story[3]
})

     






if __name__== "__main__":
     init_db()
     app.run(debug=True, port=5000)
