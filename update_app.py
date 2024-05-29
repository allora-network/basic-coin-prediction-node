import os
import requests

inference_address = os.environ["INFERENCE_API_ADDRESS"]
url = f"{inference_address}/update"

print("UPDATING INFERENCE WORKER DATA")

response = requests.get(url)
if response.status_code == 200:
    # Request was successful
    content = response.text

    if content == "0":
        print("Response content is '0'")
        exit(0)
    else:
        exit(1)
else:
    # Request failed
    print(f"Request failed with status code: {response.status_code}")
    exit(1)
