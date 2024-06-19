import sqlite3
import pandas as pd
from sklearn.metrics import cohen_kappa_score

def fetch_ratings_from_db():
    # Connect to the SQLite database
    conn = sqlite3.connect('../posts_database.db')
    cursor = conn.cursor()

    # SQL query to fetch ratings from two raters
    query = """
    Select inter_kittens.ID_Kittens, inter_kittens.Score_Mason, inter_kittens.Score_Luka
    from inter_kittens 
 """
    cursor.execute(query)
    rows = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()

    # Convert fetched data to a DataFrame
    data = pd.DataFrame(rows, columns=['ID_palestine', 'Score_Luka', 'Score_Jannis'])
    return data

def calculate_cohens_kappa(data):
    # Extract the ratings from the DataFrame
    ratings1 = data['Score_Luka']
    ratings2 = data['Score_Jannis']

    # Calculate Cohen's Kappa
    kappa = cohen_kappa_score(ratings1, ratings2)
    return kappa

def main():
    # Fetch ratings from the database
    data = fetch_ratings_from_db()

    # Calculate Cohen's Kappa
    kappa = calculate_cohens_kappa(data)

    print(f"Cohen's Kappa: {kappa:.4f}")

if __name__ == "__main__":
    main()
