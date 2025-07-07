import requests

access_token = " ZcWf6qWsJCYhKd1uFtDvPKKSXrQZIA"  # paste from previous output
url = "http://127.0.0.1:8000/brapi/v2/samples?sampleName=leaf&germplasmDbId=G123&page=0&pageSize=10"

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("✅ API call successful!")
    print(response.json())
else:
    print("❌ API call failed")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
