# SOAP Instruction
Anonymous repository for Paper: 
From Walls to Windows: Creating Transparency to Understand Filter Bubbles in Social Media
Proceedings of the Second Workshop on the Normative Design and Evaluation of Recommender Systems (NORMalize 2024) co-located with the 18th ACM Conference on Recommender Systems (RecSys 2024) Bari, Italy, October 18, 2024

## Disclaimer
SOAP is currently under construction with new features and improvements being added.
Following features are currently being worked on:
- [ ] Adding new open-source multimodal larege language models
- [ ] Adding thorough documentation
- [ ] Adding guide for deploying SOAP on Cloud and via cronjobs
- 

## Set-up

Currently, SOAP runs over the Google Cloud Vertex AI platform using the multimodal model Gemini 1.5 flash. To run the code as is, a Google Cloud account is needed. The deductive coding part can also be swapped for another model (self-hosted or other platform). The following is needed to run the code as is:

- Instagram account credentials (Username & Password). It is advised to use bot/fake accounts, as there is a possibility of getting flagged for automated behavior and the account being restricted/banned.
- Google Cloud:
  - `GOOGLE_APPLICATION_CREDENTIALS`
  - `BUCKET_NAME`
  - `PROJECT_NAME`
  - API credit for bucket and LLM usage

## Run the system

The system is orchestrated and managed by the `orchestrator.py` class. It calls all classes needed for the process depicted in "Figure 1: Agent Scenario for creating Filter Bubbles based on Primer Prompts".
![alt text](data/SOAP_system.png)

The classes and their functions are as follows:


| **Class**              | **Function**                                             |
|------------------------|----------------------------------------------------------|
| `explorefeed_scraper.py` | Scrapes explore feed data from Instagram                 |
| `saveFeedCloud.py`      | Saves scraped feed data to Google Cloud Storage          |
| `VertexAi.py`           | Utilizes Google Cloud Vertex AI for multimodal analysis  |
| `steering_wheel.py`     | Interacts through liking/reporting/archive flagged posts |

## Reliability Testing

Before deploying a new prompt for creating filter bubbles, it is recommended to perform reliability testing with the prompt and the multimodal language model (LLM). The code for conducting inter-reliability and intra-reliability testing is located in the `/reliability-evaluation/` directory.