from llama_index.llms.gemini import Gemini
from dotenv import load_dotenv, find_dotenv
import os
from llama_index.core import Settings
load_dotenv(find_dotenv()) # read local .env file


Settings.llm = Gemini(model_name="models/gemini-pro", api_key=os.getenv("GEMINI_API_KEY"))

def use_llm(x):
    response = Settings.llm.complete(x)
    return response.text, response.additional_kwargs
