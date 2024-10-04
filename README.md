# IFT401 Capstone Project Repo

## Overview

Capstone project for a stock trading system.

## Cloning Locally

1. Clone the repo
2. Open the folder in VS Code and allow it to run the workspace file, it should prompt in bottom right corner
3. Wait for VS Code to reload the workspace, and wait for the "recommended extensions" notification to appear
    1. If it does not prompt, navigate to the "extensions" screen (`CTRL + SHIFT + X`) and type `@recommended` in the search bar
    2. Click the cloud download button on the "workspace recommendations" tab to enable the extensions
4. Open the Command Palette (`CTRL + SHIFT + P`) and type "environment"
    1. Select "Python: Create Environment..."
    2. Go through the environment settings to create your `venv` using your locally installed Python version
    3. Select `requirements.txt` when it asks which requirements you would like to use
5. Fully close VS Code and reopen it, allow the workspace to initialize
6. Your terminal should reload automatically and display `(capstone )`, you are now using your venv
7. Open the GitHub extension and log-in
    - This will allow your to work on issues.

## Running Locally

1. Ensure that your `venv` is active and all requirements are installed
2. Run `flask --app app\app.py run --debug`

## Writing Commits

This repository uses [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/#summary).

> The Conventional Commits specification is a lightweight convention on top of commit messages. It provides an easy set of rules for creating an explicit commit history; which makes it easier to write automated tools on top of. This convention dovetails with [SemVer](http://semver.org/), by describing the features, fixes, and breaking changes made in commit messages.

### Breaking Changes

If you are implementing changes that may break the codebase, please create a Pull Request to allow others to review your changes first.

You can create a Pull Request in VS Code by committing your changes and pressing the "Create Pull Request" button in the Source Control tab header.

## Technologies Used

- Python
- Flask
- MySQL
- Jinja2
- Bootstrap
- HTML
- CSS
- TODO: #2 Finish Technologies Section in README

## Operational Instructions

- TODO: #3 Finish Operational Instructions Section in README
