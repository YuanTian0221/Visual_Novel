from langchain.prompts import PromptTemplate

import openai
import json
prompt_template = PromptTemplate(
    input_variables=["text"],
    template="""
You are a professional scriptwriter. Analyze the following novel text and divide it into multiple scenes.
Each scene should include:
- **Scene ID**
- **Scene Summary** (a brief description of what happens)
- **Main Characters**
- **Main Location**
- **Key Events**
- **Scene Transition Reason** (Why is this a new scene?)
- **Original Text** (The original text corresponding to this scene)

**Always return a strict JSON format** with **no extra text or explanations**, only pure JSON.
Return the output in **JSON format array**, following this example:
"scenes":[
    {{
        "scene_id": 1,
        "summary": "The protagonist finds a mysterious letter at home.",
        "characters": ["Protagonist"],
        "location": "Protagonist's house",
        "events": ["Finds the letter", "Reads the content"],
        "atmosphere": "Mysterious",
        "transition_reason": "A new event begins",
        "original_text": "He entered his home, only to find a dusty envelope on the table."
    }},
    {{
        "scene_id": 2,
        "summary": "The protagonist visits the mysterious location.",
        "characters": ["Protagonist", "Antagonist"],
        "location": "Mysterious forest",
        "events": ["Meets the antagonist", "Fights the antagonist"],
        "atmosphere": "Tense",
        "transition_reason": "The protagonist arrives at the location",
        "original_text": "He entered the forest, where he met the antagonist."
    }}
    ...
]

Here is the novel text:
{text}
"""
)


class Chatbot:
    def __init__(self, system_prompt):
        """
        Initializes the chatbot with a system prompt.

        Parameters:
            system_prompt (str): A predefined instruction that sets the chatbot's behavior.
        """
        self.system_prompt = system_prompt

    def generate_response(self, prompt):
        """
        Generates a response from OpenAI's GPT-4 Turbo model.

        Parameters:
            prompt (str): The user input message to which the chatbot responds.

        Returns:
            str: The generated response as a JSON-formatted string.
        """
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Uses the GPT-4 Turbo model for optimized performance
            messages=[
                {"role": "system", "content": self.system_prompt},  # Defines system-level behavior
                {"role": "user", "content": prompt}  # User input prompt
            ],
            temperature=0.5,  # Lowers randomness to ensure structured and stable responses
            top_p=0.9,  # Prevents extreme or highly unlikely outputs
            n=1,  # Generates only one response
            response_format={"type": "json_object"},  # Forces GPT to return a JSON object
            presence_penalty=0.2,  # Slightly encourages new content in responses
            frequency_penalty=0.2,  # Slightly reduces repetitive phrases
            stop=["\n\n"]  # Stops response at the end of a paragraph
        )

        try:
            # Convert the output from JSON string format to a Python dictionary
            # return json.loads(response.choices[0].message["content"])
            return response.choices[0].message["content"]
        except json.JSONDecodeError as e:
            print(f"JSON ERROR: {e}")  # Prints error message if JSON decoding fails
            return None

if __name__ == "__main__":
    # 读取 JSON 文件

    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    openai.api_key = config["KEY"]["OPENAI_API_KEY"]

    # 初始化 Chatbot 并测试解析小说
    chatbot = Chatbot(system_prompt="You are a screenplay expert. Return a structured JSON array.")
    novel_text = """My knowledge of the thing began in the winter of 1926-27 with the death
of my grand-uncle, George Gammell Angell, Professor Emeritus of Semitic
languages in Brown University, Providence, Rhode Island. Professor
Angell was widely known as an authority on ancient inscriptions, and
had frequently been resorted to by the heads of prominent museums; so
that his passing at the age of ninety-two may be recalled by many.
Locally, interest was intensified by the obscurity of the cause of
death. The professor had been stricken whilst returning from the
Newport boat; falling suddenly, as witnesses said, after having been
jostled by a nautical-looking negro who had come from one of the queer
dark courts on the precipitous hillside which formed a short cut from
the waterfront to the deceased's home in Williams Street. Physicians
were unable to find any visible disorder, but concluded after perplexed
debate that some obscure lesion of the heart, induced by the brisk
ascent of so steep a hill by so elderly a man, was responsible for
the end. At the time I saw no reason to dissent from this dictum, but
latterly I am inclined to wonder--and more than wonder."""
    # ✅ Generate the prompt required for GPT
    prompt = prompt_template.format(text=novel_text)

    # ✅ Get the JSON data generated by GPT after processing the prompt
    scene_data = chatbot.generate_response(prompt)

    # ✅ Output the parsed result
    print(scene_data)
    
    # 解析 JSON 数据
    scene_dict = json.loads(scene_data)
    scenes_only = scene_dict.get("scenes", [])
    print(f"共解析出 {len(scenes_only)} 个场景")
    print(scenes_only[0])