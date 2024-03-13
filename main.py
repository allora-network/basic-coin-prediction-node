import os
import requests
import sys
import json

INFERENCE_ADDRESS = os.environ["INFERENCE_API_ADDRESS"]


def process(token_name):
    response = requests.get(f"{INFERENCE_ADDRESS}/inference/{token_name}")
    content = response.text
    print(content)


if __name__ == "__main__":
    # Your code logic with the parsed argument goes here
    try:
        if len(sys.argv) >= 3:
            # Not using to discriminate by topicId for simplicity.
            # topic_id = sys.argv[1]
            token_name = sys.argv[2]
        else:
            token_name = "ETH"
        process(token_name=token_name)
    except Exception as e:
        response = json.dumps({"error": {str(e)}})
        print(response)
