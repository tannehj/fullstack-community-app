import sqlite3 #database
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

app= Flask(__name__)
CORS(app)

def get_db_connection():
    conn=psycopg2.connect(
    host="localhost",
    database="story_app",
    user="tannehjah")

    return conn

#database file create 
def init_db():
     conn=sqlite3.connect("stories.db")
     cursor=conn.cursor()
     cursor.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            story TEXT NOT NULL
        )
    """)
     conn.commit()
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
    cursor.execute("SELECT * FROM stories")

    rows=cursor.fetchall()

    conn.close()
    stories_list = []

    for row in rows:
        stories_list.append({
            "id": row[0],
            "name": row[1],
            "story": row[2]
        })
    
    return jsonify(stories_list)


@app.route("/stories", methods=["POST"])
def create_story():
     
     data=request.get_json()
     #conn=sqlite3.connect("stories.db")
     conn = get_db_connection()
     
     cursor=conn.cursor()

     cursor.execute(
    "INSERT INTO stories (name, story) VALUES (%s, %s)",
    (data["name"], data["story"]))
     conn.commit()

     new_id = cursor.lastrowid

     conn.close()

     new_story = {
        "id": new_id,
        "name": data["name"],
        "story": data["story"]
    }

     return jsonify(new_story)

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
    cursor.execute("UPDATE stories SET story=%s WHERE id =%s",(data["story"],story_id))
    conn.commit()
    conn.close()

    return jsonify({"id":story_id, "story": data["story"]})

     






if __name__== "__main__":
     init_db()
     app.run(debug=True, port=5000)
