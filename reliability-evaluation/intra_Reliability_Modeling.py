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


class IntraReliabilityModeling:

    # Configure logging
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)

    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.bucket_name = os.getenv('BUCKET_NAME')
        self.username = os.getenv('USERNAME')
        self.project = os.getenv('PROJECT_NAME')
        self.primer_template = """You are analyzing Social Media videos that feature cute and adorable kittens.
        Post Description: {post_text}
        Username: {creator_id}
        Please answer the following questions:
        - Does the video feature or relate to cute and adorable kittens? (0 for No and 1 for Yes)
        - What is your reasoning for the score?

        Consider the following topics as examples and rate higher if the video prominently features, but limietd to, these topics:
        - Kitten antics (e.g., playful behavior, funny moments)
        - Kitten care (e.g., grooming tips, health advice, feeding information)
        - Kitten milestones (e.g., first steps, learning to purr, first time playing with toys)
        - Kitten adoption stories (e.g., rescue tales, adoption success stories)
        - Kitten interactions with humans and other animals (e.g., cuddling with owners, playing with other pets)
        - Kitten habitats (e.g., cozy beds, playful environments, safe outdoor explorations)

        For example:
        - A video showing kittens playing with each other should be rated 1.
        - A video providing tips on how to care for a new kitten should be rated 1.
        - A video showing a kitten being adopted into a loving home should be rated 1.
        - A video presenting a kitten's first time exploring a new environment should be rated 1.
        - A video exploring different types of kitten toys and how kittens interact with them should be rated 1.

        Give your answer precisely in the following format:
        "Score:Reasoning". For example, "1:The video is entirely about kittens playing and showing their adorable antics." Do not say 'Score' or 'Reasoning' in the answer.
        """

        vertexai.init(project=self.project, location="us-central1")
        self.model = GenerativeModel("gemini-1.5-flash")

    def list_files(self, prefix):
        """List all files in a GCS bucket with a given prefix."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]

    def process_response(self, response):
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
        last_part = file_name.split("_")[-1]
        pk = last_part.split(".")[0]
        return pk

    def fetch_posts_from_db(self):
        conn = sqlite3.connect('../posts_database.db')
        cursor = conn.cursor()
        query = '''
        SELECT pk_id, post_name, post_text, creator_id FROM Post
        where is_uploaded = 1
          AND user_name = 'Dustin_Henderson44'
          group by pk_id limit 100
        '''
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results

    def insert_into_interpretation_reliability(self, content_id, score, interpretation, prompt, session):
        conn = sqlite3.connect('../posts_database.db')
        cursor = conn.cursor()
        query = '''INSERT INTO Interpretation_reliability_kittens(pk_id, score, interpretation, interpreted_at, prompt, session) VALUES(?, ?, ?, ?, ?, ?)'''
        cursor.execute(query, (content_id, score, interpretation, datetime.now(), prompt, session))
        conn.commit()
        conn.close()

    def process_files(self, videos, pk, post_text, creator_id):
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
        for session in range(1, 6):  # Repeat the process 5 times for intra-reliability
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
                self.insert_into_interpretation_reliability(pk, score, interpretation, primer, session)
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

    def generate(self, mode='db'):
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
                video_uris = [f"gs://{self.bucket_name}/{file_name}" for file_name in file_names]
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
        conn = sqlite3.connect('../posts_database.db')
        cursor = conn.cursor()
        query = '''
        SELECT post_text, creator_id FROM Post 
        WHERE pk_id = ?
        '''
        cursor.execute(query, (pk,))
        result = cursor.fetchone()
        conn.close()
        return {'post_text': result[0], 'creator_id': result[1]} if result else {}

    def run(self, mode='db'):
        self.generate(mode)


if __name__ == "__main__":
    intra_reliability_modeller = IntraReliabilityModeling()
    intra_reliability_modeller.run(mode='db')
