import psycopg2
conn=psycopg2.connect(
    host="localhost",
    database="story_app",
    user="tannehjah"
)
cursor=conn.cursor()
cursor.execute("SELECT * FROM stories")
rows =cursor.fetchall()
print(rows)