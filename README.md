# Loom

Loom is a Python application built for a 1-hour hackathon. It leverages the GPT-4 API to generate themes for the [Ghostty terminal emulator](https://ghostty.io/).

## Hackathon Project

This project was created as part of a 1-hour hackathon. The primary goal is to demonstrate a functional concept of using AI to generate terminal themes.

## How it Works

Loom uses Python to interact with the OpenAI GPT-4 API. You provide a prompt or some keywords, and Loom will instruct GPT-4 to generate a theme configuration compatible with Ghostty.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url> # Replace <repository-url> with the actual URL
    cd vibejam 
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(You'll need to create a `requirements.txt` file, typically including the `openai` package and `python-dotenv` for managing the API key).*
4.  **Set up your OpenAI API Key:**
    Create a `.env` file in the root of the project (`vibejam/.env`):
    ```env
    OPENAI_API_KEY='your_api_key_here'
    ```
    **Important:** Ensure `.env` is listed in your `.gitignore` file (which we created earlier!) to protect your API key.

## Usage

To run Loom (this is a conceptual example, the actual implementation might differ):

```bash
python main.py "Create a cyberpunk theme with neon pink and electric blue highlights" 
```
This would then output the Ghostty theme configuration.

## Disclaimer
This is a rapid prototype developed for a 1-hour hackathon. Functionality might be basic and error handling minimal.
