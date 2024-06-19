primer_prompts = {
    "peterpan6048": """You are analyzing Social Media videos about aviation and aircrafts.
    Post Description: {post_text}
    Username: {creator_id}
    Please answer the following Questions:
    - How much is the video about aviation/aircrafts/flying on a scale of 1 to 5? (1 being not at all about aviation and 5 being completely about aviation)
    - What is your reasoning for the score?
    Either the video in itself or the description should contain aviation/aircrafts/flying related content.
    Give your answer precisely in the following format:
    "Score:Reasoning". For example, "5:The video is entirely about different types of aircraft and their mechanisms. Do not say Score or Reasoning in the answer."
    """,

    "smblackbox2": """You are analyzing Social Media videos about the Palestine/Israel conflict.
    Post Description: {post_text}
    Username: {creator_id}
    Please answer the following Questions:
    - How much is the video about the Palestine/Israel conflict on a scale of 1 to 5? (1 being not at all about the conflict and 5 being completely about the conflict)
    - What is your reasoning for the score?
    Either the video itself or the description should contain content related to the Palestine/Israel conflict. It is also enough if the video is about the events and issues surrounding the conflict, like providing aid to Gaza.
    Give your answer precisely in the following format:
    "Score:Reasoning". For example, "5:The video is entirely about the events and issues surrounding the Palestine/Israel conflict. Do not say Score or Reasoning in the answer."
    """,

    "smblackbox3": """You are analyzing Social Media videos related to OnlyFans-style content.
    Post Description: {post_text}
    Username: {creator_id}
    Please answer the following Questions:
    - How much does the video feature women showing a lot of skin, presenting their boobs, or wearing bikinis on a scale of 1 to 5? (1 being not at all and 5 being entirely focused on this content)
    - What is your reasoning for the score?
    Either the video itself or the photos should contain content that matches this theme. Do not include pregnant women or being naked for medical purposes in your rating.
    Give your answer precisely in the following format:
    "Score:Reasoning". For example, "5:The video is entirely about women showing a lot of skin and wearing bikinis. Do not say Score or Reasoning in the answer."
    """,

    "smblackbox6": """You are analyzing Social Media videos related to the UEFA EURO24 Football Championship.
    Post Description: {post_text}
    Username: {creator_id}
    Please answer the following questions:
    - How much does the video feature content related to the UEFA EURO24 Football Championship on a scale of 1 to 5? (1 being not at all and 5 being entirely focused on this content)
    - What is your reasoning for the score?
    The video should contain content that matches this theme, such as game highlights, player interviews, fan reactions, assembling of fans in drinking halls or public spaces, fan groups, or critical actions/voices regarding the event.
    Give your answer precisely in the following format:
    "Score:Reasoning". For example, "5:The video is entirely about the UEFA EURO24 Football Championship, showing game highlights, player interviews, and fan gatherings in public spaces. Do not say Score or Reasoning in the answer."
    """,

    "smblackbox7": """You are analyzing Social Media videos related to Israel or Jewish culture.
    Post Description: {post_text}
    Username: {creator_id}
    Please answer the following questions:
    - On a scale of 0 to 5, how much is the video related to Israel or Jewish culture? (0 being not at all related and 5 being entirely focused on this theme)
    - What is your reasoning for the score?
    If the post is related to the Israel-Palestine conflict and is positively associated with Israel, rate it higher. Jewish comedy or positive content about Israel or Jewish culture should also be rated high.
    Give your answer precisely in the following format:
    "Score:Reasoning". For example, "5:The video is entirely about positive aspects of Israeli culture." Do not say 'Score' or 'Reasoning' in the answer."
    """,

    "Will_Byers44": """You are analyzing Social Media videos related to the US election and US politics from the perspective of a left-voting US American.
    Post Description: {post_text}
    Username: {creator_id}
    Please answer the following questions:
    - On a scale of 0 to 5, how much is the video related to the US election, US politics, or the US voters in general? (0 being not at all related and 5 being entirely focused on this theme)
    - What is your reasoning for the score?
    If the post is related to the US election or US politics and is in favor of left-leaning views, rate it higher. Videos that feature US politicians, political debates, or legislative updates should also be rated high.
    Give your answer precisely in the following format:
    "Score:Reasoning". For example, "5:The video is entirely about positive aspects of left-leaning US politics." Do not say 'Score' or 'Reasoning' in the answer."
    """,

    "Will_Byers44_v2": """You are analyzing Social Media videos that mention the US.
    Post Description: {post_text}
    Username: {creator_id}
    Please answer the following questions:
    - On a scale of 0 to 5, how much does the video mention or relate to the US? (0 being not at all and 5 being entirely focused on the US)
    - What is your reasoning for the score?
    Consider the following topics and rate higher if the video prominently features:
    - US celebrities (e.g., news about Hollywood stars, American musicians, sports figures)
    - Statistics about the US (e.g., economic data, health statistics, demographic information)
    - Travel and national parks in the US (e.g., tourist attractions, natural landmarks, travel guides)
    - US politics (e.g., elections, political debates, legislative updates)
    - US foreign affairs (e.g., international relations, US policies impacting other countries)
    - Cultural aspects of the US (e.g., American traditions, holidays, cultural events)
    For example:
    - A video discussing the latest Hollywood gossip should be rated higher.
    - A video providing travel tips for visiting Yellowstone National Park should be rated higher.
    - A video analyzing the recent US presidential debate should be rated higher.
    - A video presenting statistics about the US economy should be rated higher.
    - A video exploring US foreign policy in the Middle East should be rated higher.
    Give your answer precisely in the following format:
    "Score:Reasoning". For example, "5:The video is entirely about the US national parks and provides travel tips." Do not say 'Score' or 'Reasoning' in the answer."
    """,

    "Dustin_Henderson44": """You are analyzing Social Media videos that feature cute and adorable kittens.
    Post Description: {post_text}
    Username: {creator_id}
    Please answer the following questions:
    - On a scale of 0 to 5, how much does the video feature or relate to cute and adorable kittens? (0 being not at all and 5 being entirely focused on kittens)
    - What is your reasoning for the score?
    Consider the following topics and rate higher if the video prominently features:
    - Kitten antics (e.g., playful behavior, funny moments)
    - Kitten care (e.g., grooming tips, health advice, feeding information)
    - Kitten milestones (e.g., first steps, learning to purr, first time playing with toys)
    - Kitten adoption stories (e.g., rescue tales, adoption success stories)
    - Kitten interactions with humans and other animals (e.g., cuddling with owners, playing with other pets)
    - Kitten habitats (e.g., cozy beds, playful environments, safe outdoor explorations)
    For example:
    - A video showing kittens playing with each other should be rated higher.
    - A video providing tips on how to care for a new kitten should be rated higher.
    - A video showing a kitten being adopted into a loving home should be rated higher.
    - A video presenting a kitten's first time exploring a new environment should be rated higher.
    - A video exploring different types of kitten toys and how kittens interact with them should be rated higher.
    Give your answer precisely in the following format:
    "Score:Reasoning". For example, "5:The video is entirely about kittens playing and showing their adorable antics." Do not say 'Score' or 'Reasoning' in the answer."
    """
}
