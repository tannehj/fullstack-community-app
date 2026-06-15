from flask import Flask, jsonify, request
from flask_cors import CORS

app= Flask(__name__)
CORS(app)

#json test stories

stories=[{"id":1,
         "name": "Tanneh",
         "story": "This is my first backend"
     
}]

@app.route("/stories", methods=["GET"])
def get_stories():
    return jsonify(stories)


@app.route("/stories", methods=["POST"])
def create_story():
     data=request.get_json()
     stories.append(data)
     return jsonify({"message": "Story added"})

if __name__== "__main__":
     app.run(debug=True, port=5000)
