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

This project also includes a script to generate AI prompts from your pull request data.

### 1. Add Your OpenAI API Key

Add your OpenAI API key to your `.env` file:
```
OPENAI_API_KEY="your_openai_api_key_here"
```

### 2. Run the Script

After running the `pr_extractor.py` script, you can generate prompts by running:
```bash
python prompt_generator.py
```

The script will read the `pr_data.json` file, and for each pull request, it will generate a concise, actionable prompt.

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
