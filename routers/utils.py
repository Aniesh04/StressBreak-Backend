import json
from google import genai
from google.genai.types import HttpOptions
import os
from jinja2 import Environment, FileSystemLoader

client = genai.Client(http_options=HttpOptions(api_version="v1"), api_key=os.environ.get('GOOGLE_GENAI_API_KEY')) 


def create_chat():
    return client.chats.create(
        model="gemini-2.0-flash-001",
    )


def generate_struct_model_response(user_input: str) -> dict | str:
    chat = create_chat()

    llm_response = chat.send_message(user_input)

    json_text = llm_response.text.split("```json")[1].split("```")[0]
    data_dict = json.loads(json_text)
    
    return data_dict


def generate_analyze_journal(journal_content: str) -> dict:
    env = Environment(loader=FileSystemLoader("./routers")) 
    template = env.get_template('journal_analyze.j2')

    variables = { "journal_content": journal_content }
    input_prompt = template.render(variables)

    response = generate_struct_model_response(input_prompt)
    response['journal_content'] = journal_content
    
    return response