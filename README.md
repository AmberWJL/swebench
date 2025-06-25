# GitHub PR Extractor

A Python script that reads a list of Pull Request URLs from a CSV file, extracts their data, and compiles it into a single JSON file.

## Features

- **Bulk Processing**: Efficiently processes a large number of PRs from a CSV input.
- **JSON Output**: Creates a structured JSON file, perfect for data analysis or integration with other tools.
- **GitHub Enterprise Ready**: Supports both GitHub.com and GitHub Enterprise, with credentials managed securely.
- **SSL Control**: SSL verification is disabled by default to support corporate networks, but can be re-enabled easily.

## Setup

### 1. Install Dependencies

Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

The script uses a `.env` file to handle your GitHub token and optional Enterprise URL.

1.  **Create a `.env` file** by copying the example:
    ```bash
    cp env.example .env
    ```
2.  **Edit the `.env` file** with your credentials:
    ```
    # Your GitHub Personal Access Token (PAT) is required.
    GITHUB_TOKEN="your_github_token_here"

    # Your GitHub Enterprise URL (only required for GHE).
    GITHUB_BASE_URL="https://github.company.com/api/v3"
    ```

### 3. Prepare Your Input CSV

Create a CSV file containing the PRs you want to process. The script expects a header row with at least a `pr_url` column.

A sample file, `prs_to_extract.csv`, is provided as a template:

```csv
repo_name,repo_url,pr_url
ziv0-gam-fund-commentary,https://rbcgithub.fg.rbc.com/rbc-to/ziv0-gam-fund-commentary,https://rbcgithub.fg.rbc.com/rbc-to/ziv0-gam-fund-commentary/pull/62
example-repo,https://github.com/user/example-repo,https://github.com/user/example-repo/pull/1
```

## Usage

Run the script from the command line. By default, it reads from `prs_to_extract.csv` and writes to `pr_data.json`.

### Basic Command

To run with default settings, no arguments are needed:
```bash
python pr_extractor.py
```

### Options

- `--input-file`: (Optional) Path to your input CSV file. Defaults to `prs_to_extract.csv`.
- `--output-file`: (Optional) Path for the output JSON file. Defaults to `pr_data.json`.
- `--verify`: (Optional) Add this flag to re-enable SSL certificate verification.

### Example with Custom Files

```bash
python pr_extractor.py --input-file ./path/to/my_prs.csv --output-file ./output/extracted_data.json
```

## Prompt Generation

This project includes scripts to generate AI prompts from your pull request data, with special focus on creating detailed prompts for AI coding agents.

### 1. Add Your OpenAI API Key

Add your OpenAI API key to your `.env` file:
```
OPENAI_API_KEY="your_openai_api_key_here"
```

### 2. Run the Basic Prompt Generator

After running the `pr_extractor.py` script, you can generate simple prompts by running:
```bash
python prompt_generator.py
```

The script will read the `pr_data.json` file, and for each pull request, it will generate a concise, actionable prompt.

### 3. Enhanced Coding Agent Prompts

The prompt generator has been enhanced to create detailed prompts specifically for AI coding agents. These prompts include:

- Technical details extracted from PR descriptions
- Code context from review comments
- Code snippets found in PR discussions
- Structured implementation guidance

#### Command Line Options

```bash
python prompt_generator.py --input-file pr_data.json --output-file coding_prompts.json --model gpt-4
```

#### Available Options

- `--input-file`: Path to the input JSON file (default: `pr_data.json`)
- `--output-file`: Path to save the generated prompts (default: `coding_prompts.json`)
- `--model`: OpenAI model to use (default: `gpt-4`, can use `gpt-3.5-turbo` for faster results)

#### Output Format

The enhanced prompt generator creates a structured JSON output with metadata:

```json
{
  "repo_name": [
    {
      "original_pr": {
        "title": "PR Title",
        "url": "PR URL"
      },
      "generated_prompt": "Detailed coding instructions...",
      "timestamp": "2025-06-25T15:22:45.123456",
      "model_used": "gpt-4"
    }
  ]
}
```

#### Note on Corporate Networks

If you're running this script in a corporate environment that restricts access to AI services, you may need to:

1. Use a non-corporate network connection
2. Configure a proxy in your environment
3. Run the script on a machine with unrestricted internet access

## Output Format

The script generates a JSON file where pull requests are grouped by repository name.

```json
{
    "ziv0-gam-fund-commentary": [
        {
            "url": "https://rbcgithub.fg.rbc.com/rbc-to/ziv0-gam-fund-commentary/pull/62",
            "title": "Optimize Workflows",
            "description": "...",
            "state": "closed",
            "created_at": "2024-09-18T16:28:26+00:00",
            "updated_at": "2025-03-07T13:48:44+00:00",
            "comments": []
        }
    ]
}
```
