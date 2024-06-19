import pandas as pd
import sqlite3

# Read CSV data from file
csv_file = '/Users/XXXXX-3/Desktop/XXXXX-4/Thesis/Inter-Reliability_study_kittens.csv'
data = pd.read_csv(csv_file, delimiter=';', dtype={'ID_Kittens': str})

# Connect to the SQLite database
conn = sqlite3.connect('../posts_database.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS inter_kittens (ID_Kittens TEXT, Score_Luka INTEGER, Score_Mason INTEGER)''')

# Insert data into inter_kittens
kittens_data = data[['ID_Kittens', 'Score_Luka', 'Score_Mason']].values.tolist()
cursor.executemany('INSERT INTO inter_kittens (ID_Kittens, Score_Luka, Score_Mason) VALUES (?, ?, ?)', kittens_data)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data inserted successfully")
