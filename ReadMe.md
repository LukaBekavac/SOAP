# SOAP Instruction

**Repository for Paper:**  
[*From Walls to Windows: Creating Transparency to Understand Filter Bubbles in Social Media*](https://www.alexandria.unisg.ch/entities/publication/f41060db-3d3b-4071-ad92-8ac6bb1cc734/details)  
Proceedings of the Second Workshop on the Normative Design and Evaluation of Recommender Systems (NORMalize 2024), co-located with the 18th ACM Conference on Recommender Systems (RecSys 2024), Bari, Italy, October 18, 2024.

## Disclaimer

SOAP is currently under development, with new features and improvements being added. The following features are in progress:

- [ ] Adding new open-source multimodal large language models
- [ ] Expanding documentation
- [ ] Providing a guide for deploying SOAP on Cloud services and via cron jobs

## Set-Up

SOAP currently runs on Google Cloud Vertex AI, utilizing the multimodal model Gemini 1.5 flash. To run the code as-is, a Google Cloud account is required. The deductive coding component can also be replaced with another model (either self-hosted or on another platform). The following are needed to run the code as-is:

- Instagram account credentials (username and password). It is recommended to use bot/fake accounts as there is a risk of accounts being flagged for automated behavior, potentially resulting in restrictions or bans.
- Google Cloud:
  - `GOOGLE_APPLICATION_CREDENTIALS`
  - `BUCKET_NAME`
  - `PROJECT_NAME`
  - API credits for both storage (bucket) and LLM usage

## Running the System

The system is orchestrated and managed by the `orchestrator.py` script, which coordinates all the necessary components, as shown in "Figure 1: Agent Scenario for Creating Filter Bubbles based on Primer Prompts."

![SOAP system diagram](data/SOAP_system.png)

The following table outlines the key classes and their respective functions:

| **Class**               | **Function**                                             |
|-------------------------|----------------------------------------------------------|
| `explorefeed_scraper.py` | Scrapes Explore feed data from Instagram                 |
| `saveFeedCloud.py`       | Saves scraped feed data to Google Cloud Storage          |
| `VertexAi.py`            | Utilizes Google Cloud Vertex AI for multimodal analysis  |
| `steering_wheel.py`      | Interacts with Instagram by liking, reporting, or archiving flagged posts |

## Reliability Testing

Before deploying a new prompt for creating filter bubbles, it is recommended to conduct reliability testing with the prompt and the multimodal language model (LLM). Code for both inter-reliability and intra-reliability testing can be found in the `/reliability-evaluation/` directory.

## Reference

If you use/modify this source code or refer to our paper, please add a reference to our publication:
> Luka Bekavac, Kimberly Garcia, Jannis Strecker, Simon Mayer, and Aurelia Tamò-Larrieux. 2024. From Walls to Windows: Creating Transparency to Understand Filter Bubbles in Social Media. In NORMalize 2024: The Second Workshop on the Normative Design and Evaluation of Recommender Systems, co-located with the ACM Conference on Recommender Systems 2024 (RecSys 2024), October 18, 2024. Bari, Italy. https://www.alexandria.unisg.ch/handle/20.500.14171/120987

```bibtex
@inproceedings{bekavac2024,
  title = {From {{Walls}} to {{Windows}}: {{Creating Transparency}} to {{Understand Filter Bubbles}} in {{Social Media}}},
  booktitle = {{{NORMalize}} 2024: {{The Second Workshop}} on the {{Normative Design}} and {{Evaluation}} of {{Recommender Systems}}, Co-Located with the {{ACM Conference}} on {{Recommender Systems}} 2024 ({{RecSys}} 2024)},
  author = {Bekavac, Luka and Garcia, Kimberly and Strecker, Jannis and Mayer, Simon and {Tam{\`o}-Larrieux}, Aurelia},
  year = {2024},
  month = oct,
  address = {Bari, Italy},
  abstract = {Social media platforms play a significant role in shaping public opinion and societal norms. Understanding this influence requires examining the diversity of content that users are exposed to. However, studying filter bubbles in social media recommender systems has proven challenging, despite extensive research in this area. In this work, we introduce SOAP (System for Observing and Analyzing Posts), a novel system designed to collect and analyze very large online platforms (VLOPs) data to study filter bubbles at scale. Our methodology aligns with established definitions and frameworks, allowing us to comprehensively explore and log filter bubbles data. From an input prompt referring to a topic, our system is capable of creating and navigating filter bubbles using a multimodal LLM. We demonstrate SOAP by creating three distinct filter bubbles in the feed of social media users, revealing a significant decline in topic diversity as fast as in 60min of scrolling. Furthermore, we validate the LLM analysis of posts through an inter- and intra-reliability testing. Finally, we open source SOAP as a robust tool for facilitating further empirical studies on filter bubbles in social media.}
}
```

## Contact

If you have questions about the prototype or the publication, feel free to contact Luka Bekavac ([lukajurelars.bekavac@student.unisg.ch](mailto:lukajurelars.bekavac@student.unisg.ch)).

This research was conducted by the Interaction- and Communication-based Systems Group ([interactions.ics.unisg.ch](https://interactions.ics.unisg.ch)) at the University of St.Gallen ([ics.unisg.ch](https://ics.unisg.ch)) in collaboration with the Legal Design & Code Lab ([https://wp.unil.ch/legaldesignandcodelab/](https://wp.unil.ch/legaldesignandcodelab/)) at the University of Lausanne ([https://unil.ch](https://unil.ch)).

## License

All source code in this repository is licensed under the Apache License 2.0 (see [LICENSE](https://github.com/Interactions-HSG/blearvis/blob/main/LICENSE)) if not stated otherwise.
Included third-party code may be licensed differently (see the respective files and folders).
