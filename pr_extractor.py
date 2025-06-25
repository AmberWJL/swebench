#!/usr/bin/env python3
"""
GitHub PR Extractor - Extract PR descriptions and comments from GitHub PR URLs
"""

import os
import re
import sys
import argparse
import csv
import json
import urllib3
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from github import Github, GithubException
from urllib3.exceptions import InsecureRequestWarning

class GitHubPRExtractor:
    """Extract PR descriptions and comments from GitHub PR URLs."""

    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None, verify: bool = True):
        """Initialize the extractor with optional GitHub token and base URL."""
        self.token = token
        self.base_url = base_url

        github_kwargs = {"verify": verify}
        if base_url:
            github_kwargs["base_url"] = base_url

        if token:
            github_kwargs["login_or_token"] = token

        self.github = Github(**github_kwargs)

    def parse_pr_url(self, pr_url: str) -> Tuple[str, str, int]:
        """
        Parse GitHub PR URL to extract owner, repo, and PR number.

        Args:
            pr_url: GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)

        Returns:
            Tuple of (owner, repo, pr_number)

        Raises:
            ValueError: If URL format is invalid
        """
        patterns = [
            r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)",
            r"https://([^/]+\.github\.com)/([^/]+)/([^/]+)/pull/(\d+)",
            r"https://([^/]+)/([^/]+)/([^/]+)/pull/(\d+)",
            r"github\.com/([^/]+)/([^/]+)/pull/(\d+)",
            r"([^/]+)/([^/]+)/pull/(\d+)",
            r"([^/]+)/([^/]+)#(\d+)",
        ]

        for pattern in patterns:
            match = re.match(pattern, pr_url.strip())
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    owner, repo, pr_number = groups
                elif len(groups) == 4:
                    _, owner, repo, pr_number = groups
                return owner, repo, int(pr_number)

        raise ValueError(f"Invalid GitHub PR URL format: {pr_url}")

    def extract_pr_data(self, pr_url: str) -> Dict:
        """
        Extract PR description and comments from GitHub PR URL.

        Args:
            pr_url: GitHub PR URL

        Returns:
            Dictionary containing PR data
        """
        try:
            owner, repo, pr_number = self.parse_pr_url(pr_url)

            repository = self.github.get_repo(f"{owner}/{repo}")
            pull_request = repository.get_pull(pr_number)

            pr_data = {
                "repo_name": repo,
                "url": pr_url,
                "title": pull_request.title,
                "description": pull_request.body or "No description provided",
                # "author": pull_request.user.login,
                "state": pull_request.state,
                "created_at": pull_request.created_at.isoformat(),
                "updated_at": pull_request.updated_at.isoformat(),
                "comments": [],
            }

            comments = pull_request.get_issue_comments()
            for comment in comments:
                comment_data = {
                    "author": comment.user.login,
                    "body": comment.body,
                    "created_at": comment.created_at.isoformat(),
                    "updated_at": comment.updated_at.isoformat(),
                }
                pr_data["comments"].append(comment_data)

            review_comments = pull_request.get_review_comments()
            for review_comment in review_comments:
                comment_data = {
                    "author": review_comment.user.login,
                    "body": review_comment.body,
                    "created_at": review_comment.created_at.isoformat(),
                    "updated_at": review_comment.updated_at.isoformat(),
                    "file": review_comment.path,
                    "line": review_comment.line,
                    "type": "review_comment",
                }
                pr_data["comments"].append(comment_data)

            pr_data["comments"].sort(key=lambda x: x["created_at"])

            return pr_data

        except GithubException as e:
            raise Exception(f"GitHub API error: {e}")
        except Exception as e:
            raise Exception(f"Error extracting PR data: {e}")

def main():
    """Main function to run the PR extractor."""
    parser = argparse.ArgumentParser(
        description="Extracts descriptions and comments from GitHub PRs listed in a CSV file."
    )
    parser.add_argument("--input-file", help="Path to the input CSV file.", default="prs_to_extract.csv")
    parser.add_argument("--output-file", help="Path to the output JSON file.", default="pr_data.json")
    parser.add_argument("--verify", action="store_true", help="Enable SSL certificate verification (disabled by default).")
    args = parser.parse_args()

    load_dotenv()

    token = os.getenv("GITHUB_TOKEN")
    base_url = os.getenv("GITHUB_BASE_URL")
    verify = args.verify

    if not token:
        print("Error: GITHUB_TOKEN not found. Please set it in your .env file.", file=sys.stderr)
        sys.exit(1)

    if not verify:
        urllib3.disable_warnings(InsecureRequestWarning)

    all_pr_data = []
    try:
        with open(args.input_file, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            pr_urls = [row['pr_url'] for row in reader]

        extractor = GitHubPRExtractor(token, base_url, verify=verify)

        for pr_url in pr_urls:
            print(f"Extracting PR data for: {pr_url}", file=sys.stderr)
            try:
                pr_data = extractor.extract_pr_data(pr_url)
                all_pr_data.append(pr_data)
            except Exception as e:
                print(f"Could not process {pr_url}: {e}", file=sys.stderr)

        grouped_data = {}
        for pr_item in all_pr_data:
            repo_name = pr_item.pop("repo_name", "unknown_repo")
            if repo_name not in grouped_data:
                grouped_data[repo_name] = []
            grouped_data[repo_name].append(pr_item)

        with open(args.output_file, "w", encoding="utf-8") as f:
            json.dump(grouped_data, f, indent=4)
        print(f"Output written to {args.output_file}", file=sys.stderr)

    except FileNotFoundError:
        print(f"Error: Input file not found at {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
