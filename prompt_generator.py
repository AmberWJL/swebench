import os
import json
import openai
import httpx
from dotenv import load_dotenv
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Suppress InsecureRequestWarning when SSL verification is disabled
urllib3.disable_warnings(InsecureRequestWarning)

def generate_prompt(pr_data: dict) -> str:
    """Generate a prompt for an AI tool based on PR data."""
    # Explicitly create an httpx client to handle corporate proxy environments.
    # SSL verification is disabled to accommodate proxies with self-signed certs.
    http_client = httpx.Client(verify=False)
    client = openai.OpenAI(http_client=http_client)

    title = pr_data.get('title', 'No Title')
    description = pr_data.get('description', 'No Description')

    content = f"""
    Generate a concise, one-sentence prompt for an AI tool to address the following pull request.
    The prompt should be a clear, actionable instruction.

    **Title:** {title}
    **Description:** {description}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise prompts for AI tools."},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating prompt: {e}"

def main():
    """Main function to run the prompt generator."""
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found. Please set it in your .env file.")
        return

    try:
        with open('pr_data.json', 'r') as f:
            data = json.load(f)

        for repo, prs in data.items():
            print(f"--- Repository: {repo} ---")
            for pr in prs:
                prompt = generate_prompt(pr)
                print(f"URL: {pr['url']}")
                print(f"Generated Prompt: {prompt}\n")

    except FileNotFoundError:
        print("Error: pr_data.json not found. Please run pr_extractor.py first.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
