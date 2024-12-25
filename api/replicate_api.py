import os
from dotenv import load_dotenv
import replicate

load_dotenv(override=True)
api_token = os.getenv("REPLICATE_API_TOKEN")


def llama3_8b(prompt):
    replicate_client = replicate.Client(api_token=api_token)
    output = replicate_client.run(
        "meta/meta-llama-3-8b-instruct",
        input={"max_tokens": 2000, "temperature": 0, "top_p": 1, "prompt": prompt},
    )
    return "".join(output)


def llama3_70b(prompt):
    replicate_client = replicate.Client(api_token=api_token)
    output = replicate_client.run(
        "meta/meta-llama-3-70b-instruct", input={"max_tokens": 2000, "prompt": prompt}
    )
    return "".join(output)
