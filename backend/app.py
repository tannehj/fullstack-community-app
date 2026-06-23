import sqlite3 #database
from flask import Flask, jsonify, request
from flask_cors import CORS

app= Flask(__name__)
CORS(app)


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

    conn=sqlite3.connect("stories.db")
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
     conn=sqlite3.connect("stories.db")
     cursor=conn.cursor()

     cursor.execute(
    "INSERT INTO stories (name, story) VALUES (?, ?)",
    (data["name"], data["story"])
)
     conn.commit()

     conn.close()

     return jsonify({"message": "Story inserted"})
     #stories.append(data)

@app.route("/stories/<int:story_id>", methods=["DELETE"])
def delete_story(story_id):
     
    conn=sqlite3.connect("stories.db")
    cursor=conn.cursor()

    cursor.execute("DELETE FROM stories WHERE id=?",
                   (story_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Story deleted"})
     

if __name__== "__main__":
     init_db()
     app.run(debug=True, port=5000)
