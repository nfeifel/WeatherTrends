import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Store each key in its own variable
    api_key_openweathermap = os.getenv('OPENWEATHERMAP_KEY')
    api_key_google_maps = os.getenv('GOOGLE_MAPS_KEY')

def load_apis():
    with open('apis.json', 'r') as file:
        return json.load(file)

config = Config()
apis = load_apis()
