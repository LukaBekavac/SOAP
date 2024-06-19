import sqlite3
import pandas as pd
from pingouin import cronbach_alpha

# Connect to the SQLite database
conn = sqlite3.connect('../posts_database.db')

# Load data from SQLite into a DataFrame
query = """SELECT *
FROM Interpretation_reliability_kittens
"""
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Add 'iteration' column that indicates the number of each entry per pk_id
df['iteration'] = df.groupby('pk_id').cumcount() + 1

# Pivot the DataFrame to have one row per pk_id with separate columns for each iteration
df_pivot = df.pivot(index='pk_id', columns='iteration', values='score')

# Ensure the column names are properly set for the iteration
df_pivot.columns = [f'Rating{iteration}' for iteration in df_pivot.columns]

print(df_pivot.head(20))

# Calculate Cronbach's Alpha for internal consistency across the iterations
alpha, ci = cronbach_alpha(data=df_pivot)

# Print the results
print(f"Cronbach's Alpha: {alpha:.3f}")
print(f"95% CI: {ci}")
