import sqlite3
import os
import time

from dotenv import load_dotenv
from login import InstagramLogin  # Import the InstagramLogin class from login.py

class SteeringWheel:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        # Initialize database connection
        self.conn = sqlite3.connect('posts_database.db')
        self.cursor = self.conn.cursor()
        # Initialize Instagram login
        self.insta_login = InstagramLogin()

    def login(self):
        """Login to Instagram and set the client delay range."""
        # Login to Instagram
        self.insta_login.login_user()
        # Get Instagram client from InstagramLogin instance
        self.client = self.insta_login.client
        self.client.delay_range = [1, 3]  # Set delay range for client

    def get_high_score_interpretations(self):
        """Fetch pk_ids with high score interpretations that have not been liked."""
        # Prepare the SELECT statement
        query = '''SELECT Distinct Interpretation.pk_id FROM Interpretation join Post on Interpretation.pk_id = Post.pk_id WHERE score > 3 and liked = 0 and user_name = ?'''
        # Execute the SELECT statement
        self.cursor.execute(query, (self.username,))

        # Fetch all rows
        rows = self.cursor.fetchall()

        # Extract pk_id from each row and return as a list
        return [row[0] for row in rows]

    def like_high_score_videos(self):
        """Like videos with high score interpretations and update the database."""
        # Get pk_ids with high score interpretations
        pk_ids = self.get_high_score_interpretations()

        # For each pk_id, get the media_id and like the video
        for pk_id in pk_ids:
            try:
                # Get media_id from pk_id
                media_id = self.client.media_id(pk_id)
                print(f"Fetching media_id for pk_id: {pk_id} which is {media_id}")


                # Like the video
                self.client.media_like(media_id)
                print(f"Liked media with media_id: {media_id}")

                # Archive the media
                # self.client.media_archive(media_id)
                # print(f"Archived media with media_id: {media_id}")

                # Update Interpretation with liked = 1
                query = f"UPDATE Interpretation SET liked = 1 WHERE pk_id = {pk_id}"
                self.cursor.execute(query)
                self.conn.commit()  # Commit the change to the database
                print(f"Interpretation with pk_id {pk_id} updated with liked = 1")

            except Exception as e:
                print(f"An error occurred while processing media with pk_id {pk_id}: {e}")

    def close_connection(self):
        """Close the database connection."""
        self.conn.close()

    def run(self):
        self.login()
        self.like_high_score_videos()
        self.close_connection()

if __name__ == "__main__":
    steering_wheel = SteeringWheel()
    steering_wheel.run()
