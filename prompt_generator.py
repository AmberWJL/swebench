import os
import json
import openai
import httpx
import argparse
from dotenv import load_dotenv
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime

# Suppress InsecureRequestWarning when SSL verification is disabled
urllib3.disable_warnings(InsecureRequestWarning)

def extract_code_context(comments):
    """Extract code snippets and relevant context from PR comments."""
    code_snippets = []
    review_context = []
    
    for comment in comments:
        # Extract code review comments which often contain important context
        if comment.get('type') == 'review_comment':
            file_path = comment.get('file', '')
            line_num = comment.get('line', '')
            body = comment.get('body', '')
            author = comment.get('author', '')
            
            if body and ('```' in body or '`' in body):
                # This likely contains code snippets
                code_snippets.append({
                    'file': file_path,
                    'line': line_num,
                    'code': body,
                    'author': author
                })
            
            review_context.append(f"File: {file_path}, Line: {line_num}, Comment: {body}")
    
    return code_snippets, review_context

def generate_coding_prompt(pr_data: dict, model: str = "gpt-4") -> dict:
    """Generate a detailed prompt for an AI coding agent based on PR data."""
    # Explicitly create an httpx client to handle corporate proxy environments.
    # SSL verification is disabled to accommodate proxies with self-signed certs.
    http_client = httpx.Client(verify=False)
    client = openai.OpenAI(http_client=http_client)

    # Extract key information from PR data
    title = pr_data.get('title', 'No Title')
    description = pr_data.get('description', 'No Description')
    url = pr_data.get('url', '')
    comments = pr_data.get('comments', [])
    
    # Extract code context from comments
    code_snippets, review_context = extract_code_context(comments)
    
    # Prepare a structured prompt for coding tasks
    system_prompt = """
    You are an expert AI coding assistant that helps developers implement solutions based on pull request information.
    Your task is to create a clear, detailed coding prompt that will guide an AI agent to implement the requested changes.
    Focus on technical details, code architecture, and specific implementation requirements.
    """
    
    # Create a rich context for the coding task
    user_prompt = f"""
    Based on the following pull request information, create a detailed prompt for an AI coding agent.
    The prompt should include specific coding tasks, technical requirements, and implementation guidance.
    
    ## Pull Request Details
    **Title:** {title}
    **URL:** {url}
    **Description:**
    {description}
    
    ## Code Context
    {', '.join(review_context) if review_context else 'No specific code review comments found.'}
    
    ## Code Snippets
    {json.dumps(code_snippets, indent=2) if code_snippets else 'No code snippets found in comments.'}
    
    Create a prompt that clearly explains what code needs to be written, modified, or fixed.
    Include any specific requirements, constraints, or best practices that should be followed.
    The prompt should be detailed enough for an AI coding agent to implement the solution without additional context.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Return a structured response with metadata
        return {
            "original_pr": {
                "title": title,
                "url": url
            },
            "generated_prompt": response.choices[0].message.content.strip(),
            "timestamp": datetime.now().isoformat(),
            "model_used": model
        }
    except Exception as e:
        return {
            "original_pr": {
                "title": title,
                "url": url
            },
            "error": f"Error generating prompt: {e}",
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Main function to run the coding prompt generator."""
    parser = argparse.ArgumentParser(
        description="Generates coding prompts for AI agents based on PR data."
    )
    parser.add_argument("--input-file", help="Path to the input JSON file.", default="pr_data.json")
    parser.add_argument("--output-file", help="Path to save the generated prompts JSON file.", default="coding_prompts.json")
    parser.add_argument("--model", help="OpenAI model to use.", default="gpt-4")
    args = parser.parse_args()
    
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found. Please set it in your .env file.")
        return

    try:
        with open(args.input_file, 'r') as f:
            data = json.load(f)

        all_prompts = {}
        
        for repo, prs in data.items():
            print(f"--- Repository: {repo} ---")
            repo_prompts = []
            
            for pr in prs:
                print(f"Processing PR: {pr['url']}")
                prompt_data = generate_coding_prompt(pr, model=args.model)
                repo_prompts.append(prompt_data)
                
                # Print a preview of the generated prompt
                if "generated_prompt" in prompt_data:
                    preview = prompt_data["generated_prompt"][:200] + "..." if len(prompt_data["generated_prompt"]) > 200 else prompt_data["generated_prompt"]
                    print(f"Generated Prompt Preview: {preview}\n")
                else:
                    print(f"Error: {prompt_data.get('error', 'Unknown error')}\n")
            
            all_prompts[repo] = repo_prompts
        
        # Save all prompts to a JSON file
        with open(args.output_file, 'w') as f:
            json.dump(all_prompts, f, indent=2)
            
        print(f"\nAll prompts saved to {args.output_file}")

    except FileNotFoundError:
        print(f"Error: {args.input_file} not found. Please run pr_extractor.py first.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
