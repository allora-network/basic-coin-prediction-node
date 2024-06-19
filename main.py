import os
import requests
import sys
import json

INFERENCE_ADDRESS = os.environ["INFERENCE_API_ADDRESS"]


def process(token_name):
    response = requests.get(f"{INFERENCE_ADDRESS}/inference/{token_name}")
    content = response.text
    return content


if __name__ == "__main__":
    # Your code logic with the parsed argument goes here
    try:
        if len(sys.argv) < 5:
            value = json.dumps({"error": f"Not enough arguments provided: {len(sys.argv)}, expected 4 arguments: topic_id, blockHeight, blockHeightEval, default_arg"})
        else:
            topic_id = sys.argv[1]
            blockHeight = sys.argv[2]
            blockHeightEval = sys.argv[3]
            default_arg = sys.argv[4]
            
            response_inference = process(token_name=default_arg)
            response_dict = {"infererValue": response_inference}
            value = json.dumps(response_dict)
    except Exception as e:
        value = json.dumps({"error": {str(e)}})
    print(value)
