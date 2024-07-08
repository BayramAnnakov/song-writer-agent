
import requests

# replace your vercel domain
base_url = 'YOUR_SUNO_API_URL'


def custom_generate_audio(lyrics:str, style: str, title:str):
    url = f"{base_url}/api/custom_generate"


    payload = {
        "prompt": lyrics,
        "tags": style,
        "title": title,
        "make_instrumental": False,
        "wait_audio": True
    }
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})


    return response.json()





