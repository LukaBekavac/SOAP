import json
import re
import logging
import os
import time
import sqlite3
from google.api_core.exceptions import InvalidArgument, PermissionDenied, ResourceExhausted
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
from dotenv import load_dotenv
from datetime import datetime

from login import logger
from primer_prompts import primer_prompts  # Import the dictionary

class VertexAIProcessor:
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.bucket_name = os.getenv('BUCKET_NAME')
        self.username = os.getenv('USERNAME')
        self.project = os.getenv('PROJECT_NAME')

        # Set the primer template based on the username
        self.primer_template = primer_prompts.get(self.username, "")

        vertexai.init(project=self.project, location="us-central1")
        self.model = GenerativeModel("gemini-1.5-flash")

    def list_files(self, prefix):
        """List all files in a GCS bucket with a given prefix."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]

    def process_response(self, response):
        """Process the response from the generative model."""
        response = response.replace("\n", " ")
        if ":" in response:
            reversed_response = response[::-1]
            reversed_score, reversed_interpretation = reversed_response.split(":", 1)
            interpretation = reversed_interpretation[::-1].strip()
            score = reversed_score[::-1].strip()
        else:
            interpretation, score = None, "formatting error"
        return interpretation, score

    def get_pk_from_filename(self, file_name):
        """Extract the pk from the filename."""
        last_part = file_name.split("_")[-1]
        pk = last_part.split(".")[0]
        return pk

    def fetch_posts_from_db(self):
        """Fetch posts from the database that are uploaded but not yet interpreted."""
        conn = sqlite3.connect('posts_database.db')
        cursor = conn.cursor()
        query = '''
        SELECT pk_id, post_name, post_text, creator_id FROM Post 
        WHERE is_uploaded = 1 AND pk_id NOT IN (SELECT pk_id FROM Interpretation) AND user_name = ?
        '''
        cursor.execute(query, (self.username,))
        results = cursor.fetchall()
        conn.close()
        return results

    def insert_into_interpretation(self, content_id, score, interpretation, prompt):
        """Insert the interpretation result into the database."""
        conn = sqlite3.connect('posts_database.db')
        cursor = conn.cursor()
        query = '''INSERT INTO Interpretation(pk_id, score, interpretation, interpreted_at, prompt) VALUES(?, ?, ?, ?, ?)'''
        cursor.execute(query, (content_id, score, interpretation, datetime.now(), prompt))
        conn.commit()
        conn.close()

    def process_files(self, videos, pk, post_text, creator_id):
        """Process the video files and generate interpretations using the model."""
        primer = self.primer_template.format(
            post_text=post_text if post_text else "No description provided",
            creator_id=creator_id if creator_id else "Unknown user"
        )
        generation_config = {
            "max_output_tokens": 2048,
            "temperature": 1,
            "top_p": 0.95,
        }
        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        try:
            response = self.model.generate_content(
                videos + [primer],  # Combine videos with the primer
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False,
            )

            # Process the response normally if no safety filters were triggered
            score, interpretation = self.process_response(response.text)

            logger.info(f"Videos: {videos}")
            logger.info(f"Primary Prompt: {primer}")
            logger.info(f"Score: {score}, Interpretation: {interpretation}")
            self.insert_into_interpretation(pk, score, interpretation, primer)
        except InvalidArgument as e:
            logger.error(f"Invalid argument error: {e}")
            # Log the error or handle it as needed, but do not update the database
        except PermissionDenied as e:
            if "rate limit" in str(e):
                logger.warning(f"Rate limit reached: {e}. Waiting for 60 seconds before retrying.")
                time.sleep(60)
            else:
                logger.error(f"Permission denied error: {e}")
        except ResourceExhausted as e:
            logger.warning(f"Quota exceeded error: {e}. Waiting for 60 seconds before retrying.")
            time.sleep(60)
        except Exception as e:
            if "SAFETY" in str(e):
                score = "5"
                interpretation = "Safety filters triggered"
                # Check safety ratings to find blocked categories
                # Implement custom logic to handle the blocked categories
                # ToDo
            else:
                logger.error(f"Unexpected error: {e} for PK: {pk}")

    def generate(self, mode='bucket'):
        """Generate interpretations based on the specified mode."""
        if mode == 'bucket':
            prefix = f"{self.username}/"
            files = self.list_files(prefix)
            pk_to_files = {}
            for file_name in files:
                if file_name.endswith(('.mp4', '.mov', '.avi', '.jpg')):
                    pk = self.get_pk_from_filename(file_name)
                    if pk not in pk_to_files:
                        pk_to_files[pk] = []
                    pk_to_files[pk].append(file_name)
            for pk, file_names in pk_to_files.items():
                video_uris = [f"gs://{self.bucket_name}/{file_name}" for filenames in file_names]
                videos = [Part.from_uri(mime_type="video/mp4", uri=uri) for uri in video_uris]
                # Fetch post details for the primer context
                post_details = self.fetch_post_details(pk)
                self.process_files(videos, pk, post_details.get('post_text'), post_details.get('creator_id'))
        elif mode == 'db':
            posts = self.fetch_posts_from_db()
            pk_to_posts = {}
            for pk, post_name, post_text, creator_id in posts:
                if pk not in pk_to_posts:
                    pk_to_posts[pk] = []
                pk_to_posts[pk].append((post_name, post_text, creator_id))
            for pk, post_details in pk_to_posts.items():
                video_uris = [f"gs://{self.bucket_name}/{self.username}/{post_name}" for post_name, _, _ in post_details]
                videos = [Part.from_uri(mime_type="video/mp4", uri=uri) for uri in video_uris]
                # Use the first post's text and creator_id for the primer
                first_post = post_details[0]
                self.process_files(videos, pk, first_post[1], first_post[2])
        else:
            print("Invalid mode selected. Choose 'bucket' or 'db'.")

    def fetch_post_details(self, pk):
        """Fetch post details from the database based on pk_id."""
        conn = sqlite3.connect('posts_database.db')
        cursor = conn.cursor()
        query = '''
        SELECT post_text, creator_id FROM Post 
        WHERE pk_id = ?
        '''
        cursor.execute(query, (pk,))
        result = cursor.fetchone()
        conn.close()
        return {'post_text': result[0], 'creator_id': result[1]} if result else {}

    def run(self, mode='bucket'):
        """Run the process to generate interpretations."""
        self.generate(mode)

if __name__ == "__main__":
    vertex_ai_processor = VertexAIProcessor()
    vertex_ai_processor.run(mode='db')
