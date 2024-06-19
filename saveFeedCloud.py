import os
import sqlite3
from google.cloud import storage
from dotenv import load_dotenv
from sessionCreator import SessionCreator
import imageio.v2 as imageio
from PIL import Image

class SaveFeedCloud:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        self.bucket_name = os.getenv('BUCKET_NAME')
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

    def upload_to_gcs(self, destination_blob_name, file_path):
        """
        Uploads a file to the specified Google Cloud Storage (GCS) bucket.
        """
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(str(file_path))  # Ensure file_path is a string
        print(f"File {file_path} uploaded to {destination_blob_name} in bucket {self.bucket_name}.")

    def convert_heic_to_jpg(self, heic_path):
        """
        Converts a HEIC file to JPG format.
        """
        heic_image = imageio.imread(heic_path)
        jpg_path = str(heic_path).replace('.heic', '.jpg')
        imageio.imwrite(jpg_path, heic_image)
        return jpg_path

    def process_and_upload_media(self):
        """
        Fetches media posts from the database, processes them, and uploads to GCS.
        """
        # Create a connection to the SQLite database
        conn = sqlite3.connect('posts_database.db')
        cursor = conn.cursor()

        # Fetch the pk_ids from the Post table where is_uploaded = 0
        cursor.execute("SELECT * FROM Post WHERE is_uploaded = 0 AND user_name = ?", (self.username,))
        rows = cursor.fetchall()

        queries = []

        for row in rows:
            media_pk = row[1]
            original_post = row

            try:
                # Fetch media information using the media pk
                media_info = self.session_creator.media_info_v1(int(media_pk))
                media_type = media_info.media_type

                # Download media based on its type
                if media_type == 1:
                    file_paths = [self.session_creator.photo_download(media_pk, '/tmp')]
                elif media_type == 2:
                    file_paths = [self.session_creator.clip_download(media_pk, '/tmp')]
                elif media_type == 8:
                    file_paths = self.session_creator.album_download(media_pk, '/tmp')
                else:
                    print(f"Unknown media type for ID {media_pk}")
                    continue

                for index, file_path in enumerate(file_paths):
                    file_path_str = str(file_path)
                    if file_path_str.lower().endswith('.heic'):
                        file_path = self.convert_heic_to_jpg(file_path)

                    destination_blob_name = f"{self.username}/{os.path.basename(file_path)}"
                    self.upload_to_gcs(destination_blob_name, file_path)
                    print(f"Uploaded media for ID {media_pk}, file: {file_path}")

                    # Prepare queries to update or insert post data in the database
                    if index > 0:
                        query = ('''
                            INSERT INTO Post (pk_id, user_name, post_name, post_text, post_url, posted_at, scraped_at, 
                                              creator_id, lang, possibly_sensitive, is_uploaded, like_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            original_post[1],  # pk_id
                            original_post[2],  # user_name
                            os.path.basename(file_path),  # post_name
                            original_post[4],  # post_text
                            original_post[5],  # post_url
                            original_post[6],  # posted_at
                            original_post[7],  # scraped_at
                            original_post[8],  # creator_id
                            original_post[9],  # lang
                            original_post[10],  # possibly_sensitive
                            1,  # is_uploaded
                            original_post[12]  # like_count
                        ))
                    else:
                        query = ('''
                            UPDATE Post
                            SET post_name = ?, is_uploaded = ?
                            WHERE pk_id = ?
                        ''', (os.path.basename(file_path), 1, original_post[1]))

                    queries.append(query)

            except Exception as e:
                print(f"Failed to process ID {media_pk} with error: {e}")

        # Execute all prepared queries
        for query, params in queries:
            cursor.execute(query, params)
            conn.commit()

        conn.close()
        print("All media IDs processed.")

    def run(self):
        """
        Run the scraper: log in and fetch/process data.
        """
        if not self.login():
            return
        self.process_and_upload_media()

if __name__ == "__main__":
    save_feed_cloud = SaveFeedCloud()
    save_feed_cloud.run()
