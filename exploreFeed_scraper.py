import os
import sqlite3
from dotenv import load_dotenv
from sessionCreator import SessionCreator
from datetime import datetime

class ExploreFeedScraper:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        self.session_creator = None

    def login(self):
        """
        Initialize and log in to the session using provided credentials.
        """
        try:
            self.session_creator = SessionCreator(self.username, self.password)
            self.session_creator.login()
            print("Login successful!")
        except Exception as e:
            print("Initialization or login failed:", str(e))
            return False
        return True

    def find_pks(self, data):
        """
        Recursively search for 'pk' keys in the given data and return a list of 'pk' values.
        """
        pk_list = []

        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'pk' and isinstance(value, int) and len(str(value)) == 19:
                    pk_list.append(str(value))
                else:
                    pk_list.extend(self.find_pks(value))
        elif isinstance(data, list):
            for item in data:
                pk_list.extend(self.find_pks(item))

        return pk_list

    def fetch_and_process_data(self):
        """
        Fetch media data, process it, and store relevant information in the SQLite database.
        """
        try:
            # Fetch media data from the explore page
            media_data = self.session_creator.explore_page()
            directory = 'data'
            file_path = os.path.join(directory, f'timeline_explore_ids_{self.username}.txt')

            # Ensure the directory exists
            os.makedirs(directory, exist_ok=True)

            # Create a connection to the SQLite database
            conn = sqlite3.connect('posts_database.db')
            cursor = conn.cursor()

            pk_list = self.find_pks(media_data)
            with open(file_path, 'w') as f:
                for pk in pk_list:
                    print(f"Processing PK: {pk}")
                    f.write(f"{pk}\n")

                    # Fetch additional data using media_info
                    info = self.session_creator.media_info_v1(pk)
                    caption_text = info.caption_text if info.caption_text else ''
                    username = info.user.username if info.user else ''
                    like_count = info.like_count if info.like_count else 0
                    taken_at = info.taken_at.strftime('%Y-%m-%d %H:%M:%S.%f') if info.taken_at else None
                    code = info.code if info.code else None
                    post_url = f"https://www.instagram.com/p/{code}" if code else None

                    # Skip entry if like_count is 0 and caption_text is empty
                    if like_count == 0 and caption_text == '':
                        continue

                    # Insert the pk_id and additional data into the Post table
                    query = '''INSERT INTO Post(pk_id, scraped_at, user_name, post_text, creator_id, like_count, posted_at, post_url) 
                               VALUES(?, ?, ?, ?, ?, ?, ?, ?)'''
                    cursor.execute(query, (pk, datetime.now(), self.username, caption_text, username, like_count, taken_at, post_url))

            # Commit the changes and close the connection
            conn.commit()
            conn.close()

        except Exception as e:
            print(f"An error occurred: {e}")

    def run(self):
        """
        Run the scraper: log in and fetch/process data.
        """
        if not self.login():
            return
        self.fetch_and_process_data()

if __name__ == "__main__":
    scraper = ExploreFeedScraper()
    scraper.run()
