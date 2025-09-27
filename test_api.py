import requests

url = "http://localhost:8000/quiz/generate_quiz"
params = {
    "url": "https://youtu.be/yGWJo6a4g4w"  # query parameter
}

headers = {
    "gemini-api-key": "blackblack"  # your API key
}

response = requests.post(url, params=params, headers=headers)
print(response.json())
