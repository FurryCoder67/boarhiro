import requests

def ask_boarhiro(prompt, url):
    try:
        response = requests.post(f"{url}/generate", json={"prompt": prompt})
        return response.json().get("response", "System Timeout.")
    except:
        return "Connection Error: Check your Colab link."