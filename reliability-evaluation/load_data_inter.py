import pandas as pd
import sqlite3

# Read CSV data from file
csv_file = '/Users/lukabekavac/Desktop/HSG/Thesis/Inter-Reliability_study_results.csv'  # Replace with the actual path to your CSV file
data = pd.read_csv(csv_file, delimiter=';', dtype={'ID_aviation': str, 'ID_palestine': str})

# Connect to the SQLite database
conn = sqlite3.connect('../posts_database.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS inter_aviation (ID_aviation TEXT, Score_Luka INTEGER, Score_Kim INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS inter_palestine (ID_palestine TEXT, Score_Luka INTEGER, Score_Jannis INTEGER)''')

# Insert data into inter_aviation
aviation_data = data[['ID_aviation', 'Score_Luka_avi', 'Score_Kim']].values.tolist()
cursor.executemany('INSERT INTO inter_aviation (ID_aviation, Score_Luka, Score_Kim) VALUES (?, ?, ?)', aviation_data)

# Insert data into inter_palestine
palestine_data = data[['ID_palestine', 'Score_Luka_pal', 'Score_Jannis']].values.tolist()
cursor.executemany('INSERT INTO inter_palestine (ID_palestine, Score_Luka, Score_Jannis) VALUES (?, ?, ?)', palestine_data)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data inserted successfully")
