import requests
from requests import Response

"""
This file is use to contact an LLM if we need to request some thinking or some more complex voice control
"""

def request_llm_answer(data:dict, url:str ="http://localhost:11434/api/generate") -> dict:
    """
    This function request Ollama service to answer a question
    :param data: Dictionary of data to send to Ollama as example : {
    "model": "deepseek-r1:8b",  # Replace with your model name (e.g., "deepseek", "llama2", etc.)
    "prompt": "Explain quantum computing in simple terms.",
    "stream": False  # Set to False to get the entire response at once
}
    :param url: String containing the url of the service
    :return: dictionary containing the answer to the question
    """
    response: Response = requests.post(url, json=data)
    # If the request was successful
    if response.status_code != 200:
        return {}

    return response.json()

