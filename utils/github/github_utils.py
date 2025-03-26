#!/usr/bin/env python3
"""
GitHub Utilities - Simple helper functions for Git operations
"""

import os
import sys
import subprocess
import argparse

# GitHub repository information
REPO_URL = "https://github.com/AliBadawy/Datajar-Beta-V1.git"

def run_command(command):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def push_to_github(branch="main", message=None, force=False):
    """Push local changes to GitHub"""
    print(f"Pushing to GitHub repository: {REPO_URL}")
    
    # Check status
    status = run_command("git status --porcelain")
    if status:
        # There are uncommitted changes
        print("Uncommitted changes detected.")
        commit_message = message or input("Enter commit message: ")
        if not commit_message:
            commit_message = "Update files"
        
        print("Adding all changes...")
        run_command("git add .")
        
        print(f"Committing with message: {commit_message}")
        run_command(f'git commit -m "{commit_message}"')
    else:
        print("No changes to commit.")
    
    # Push to GitHub
    force_flag = "--force" if force else ""
    print(f"Pushing to {branch} branch...")
    run_command(f"git push origin {branch} {force_flag}")
    print("Push completed successfully!")

def pull_from_github(branch="main"):
    """Pull latest changes from GitHub"""
    print(f"Pulling from GitHub repository: {REPO_URL}")
    
    # Pull from GitHub
    print(f"Pulling from {branch} branch...")
    run_command(f"git pull origin {branch}")
    print("Pull completed successfully!")

def main():
    """Main function to parse arguments and execute commands"""
    parser = argparse.ArgumentParser(description="GitHub Helper Script")
    parser.add_argument("action", choices=["push", "pull"], 
                        help="Action to perform: push or pull")
    parser.add_argument("--branch", default="main", 
                        help="Branch to push to or pull from (default: main)")
    parser.add_argument("--message", "-m", 
                        help="Commit message for push (optional)")
    parser.add_argument("--force", action="store_true", 
                        help="Force push (use with caution)")
    
    args = parser.parse_args()
    
    if args.action == "push":
        push_to_github(args.branch, args.message, args.force)
    elif args.action == "pull":
        pull_from_github(args.branch)

if __name__ == "__main__":
    main()
