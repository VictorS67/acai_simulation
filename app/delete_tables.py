import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect('database.db')

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Retrieve a list of all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Iterate over the list of tables and delete all data from each table
for table_name in tables:
    print(f"Emptying table: {table_name[0]}")
    cursor.execute(f"DELETE FROM {table_name[0]};")

# Commit the changes
conn.commit()

# Close the connection
conn.close()

print("All tables have been emptied.")
