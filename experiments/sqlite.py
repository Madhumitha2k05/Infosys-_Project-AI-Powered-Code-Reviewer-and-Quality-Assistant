import sqlite3

# This will create employee.db in the same folder
conn = sqlite3.connect("employee.db")
cursor = conn.cursor()

# Create departments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT
);
""")

# Create employees table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_name TEXT NOT NULL,
    age INTEGER,
    salary INTEGER,
    join_date TEXT,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);
""")

conn.commit()
conn.close()

print("employee.db created with tables")













# import sqlite3

# conn = sqlite3.connect("employee.db")
# cursor = conn.cursor()

# cursor.executemany("""
# INSERT INTO departments (department_id, department_name)
# VALUES (?, ?)
# """, [
#     (1, "HR"),
#     (2, "IT"),
#     (3, "Finance")
# ])

# cursor.executemany("""
# INSERT INTO employees (emp_name, age, salary, join_date, department_id)
# VALUES (?, ?, ?, ?, ?)
# """, [
#     ("Ajay", 25, 50000, "2022-01-10", 2),
#     ("Ravi", 30, 80000, "2021-03-15", 2),
#     ("Kiran", 28, 45000, "2023-06-01", 1),
#     ("Sneha", 35, 70000, "2020-09-20", 3)
# ])

# conn.commit()
# conn.close()

# print("Data inserted")













# import sqlite3
# import pandas as pd

# conn = sqlite3.connect("employee.db")

# df = pd.read_sql("SELECT * FROM employees", conn)
# print(df)

# conn.close()