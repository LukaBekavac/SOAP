import os
import time

from dotenv import load_dotenv
from exploreFeed_scraper import ExploreFeedScraper
from saveFeedCloud import SaveFeedCloud
from VertexAI import VertexAIProcessor
from steering_wheel import SteeringWheel

# Before starting for new account make sure following:
# 1. Change the account details in .env file
# 2. Add/Adjust the primer prompt in primer_prompts.py
# 3. Use right session file
# 3. Test the Gcloud and DB after running the code


class Orchestrator:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        self.bucket_name = os.getenv('BUCKET_NAME')
        self.project = os.getenv('PROJECT_NAME')

        # Initialize the classes
        self.explore_scraper = ExploreFeedScraper()
        self.save_feed = SaveFeedCloud()
        self.vertex_ai = VertexAIProcessor()
        self.steering_wheel = SteeringWheel()

    def run(self):
        start_time = time.time()

        # Timing ExploreFeedScraper
        print("Starting ExploreFeedScraper...")
        explore_start = time.time()
        self.explore_scraper.run()
        explore_end = time.time()
        print(f"ExploreFeedScraper completed in {explore_end - explore_start:.2f} seconds")

        # Timing SaveFeedCloud
        print("Starting SaveFeedCloud...")
        save_feed_start = time.time()
        self.save_feed.run()
        save_feed_end = time.time()
        print(f"SaveFeedCloud completed in {save_feed_end - save_feed_start:.2f} seconds")

        # Timing VertexAIProcessor
        print("Starting VertexAIProcessor...")
        vertex_ai_start = time.time()
        self.vertex_ai.run(mode='db')  # or 'bucket', depending on test case
        vertex_ai_end = time.time()
        print(f"VertexAIProcessor completed in {vertex_ai_end - vertex_ai_start:.2f} seconds")

        # Timing SteeringWheel
        print("Starting SteeringWheel...")
        steering_wheel_start = time.time()
        self.steering_wheel.run()
        steering_wheel_end = time.time()
        print(f"SteeringWheel completed in {steering_wheel_end - steering_wheel_start:.2f} seconds")

        end_time = time.time()
        print(f"Total process completed in {end_time - start_time:.2f} seconds")


if __name__ == "__main__":

    for i in range(5):
        orchestrator = Orchestrator()
        orchestrator.run()
    orchestrator = Orchestrator()
    orchestrator.run()
