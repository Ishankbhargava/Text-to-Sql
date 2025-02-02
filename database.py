import sqlite3

#Create Database
connection = sqlite3.connect("student.db")

# Create cursor
cursor = connection.cursor()

create_table_query="""
CREATE TABLE IF NOT EXISTS STUDENT (
    NAME    VARCHAR(25),
    COURSE   VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS   INT
);
"""


cursor.execute(create_table_query)

#insert records
sql_query = """INSERT INTO STUDENT (NAME, COURSE, SECTION, MARKS) VALUES (?, ?, ?, ?)"""
values = [
    ('Student1', 'Data Science', 'A', 90),
    ('Student2', 'Data Science', 'B', 100),
    ('Student3', 'Data Science', 'A', 86),
    ('Student4', 'DEVOPS', 'A', 50),
    ('Student5', 'DEVOPS', 'A', 35)
]

cursor.executemany(sql_query,values)
connection.commit()

data = cursor.execute("""Select * from STUDENT""")

for row in data:
    print(row)

if connection:
    connection.close()