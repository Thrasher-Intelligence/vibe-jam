import os
import json
import tempfile
import subprocess

from dotenv import load_dotenv
from openai import OpenAI

# Schema for Ghostty theme (as a string to be embedded in the prompt)
# This schema is based on vibejam/schemas/ghostty.json
GHOSTTY_SCHEMA_DESCRIPTION = """
{
  "palette": {
    "0": "HEX_COLOR_STRING",   // background dark
    "1": "HEX_COLOR_STRING",   // red - error
    "2": "HEX_COLOR_STRING",   // green - success
    "3": "HEX_COLOR_STRING",   // yellow - warning
    "4": "HEX_COLOR_STRING",   // blue - info
    "5": "HEX_COLOR_STRING",   // magenta - accent
    "6": "HEX_COLOR_STRING",   // cyan - alt background
    "7": "HEX_COLOR_STRING",   // white - foreground light
    "8": "HEX_COLOR_STRING",   // bright black - UI muted
    "9": "HEX_COLOR_STRING",   // bright red - highlights
    "10": "HEX_COLOR_STRING",  // bright green
    "11": "HEX_COLOR_STRING",  // bright yellow
    "12": "HEX_COLOR_STRING",  // bright blue
    "13": "HEX_COLOR_STRING",  // bright magenta
    "14": "HEX_COLOR_STRING",  // bright cyan
    "15": "HEX_COLOR_STRING"   // bright white
  },
  "background": "HEX_COLOR_STRING",
  "foreground": "HEX_COLOR_STRING",
  "cursor-color": "HEX_COLOR_STRING",
  "selection-background": "HEX_COLOR_STRING",
  "selection-foreground": "HEX_COLOR_STRING"
}
// All color values must be valid 6-digit hexadecimal color codes, e.g., "#RRGGBB".
// The comments (like "// ...") are for explanation and MUST NOT be included in the final JSON output.
"""

def load_api_key():
    """Loads the OpenAI API key from the .env file at ~/vibejam/.env."""
    # Construct the path to ~/vibejam/.env
    env_path = os.path.join(os.path.expanduser('~'), 'vibejam', '.env')
    # Load the .env file from the specified path.
    # load_dotenv will not raise an error if the file is not found,
    # but will return False. It will return True if found and loaded.
    # The subsequent check for api_key handles cases where the key isn't loaded.
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # env_path is defined earlier in this function's scope.
        print(f"Error: OPENAI_API_KEY not found.")
        print(f"Please ensure the API key is set as an environment variable,")
        print(f"or that the file '{env_path}' exists and contains:")
        print(f"OPENAI_API_KEY=your_actual_key")
        exit(1)
    # Basic check for placeholder key
    if "YOUR_API_KEY_HERE" in api_key:
        print("Error: Placeholder API key detected. Please replace 'YOUR_API_KEY_HERE' in .env with your actual OpenAI API key.")
        exit(1)
    return api_key

def get_theme_name():
    """Prompts the user for a single-word theme name."""
    while True:
        theme_name = input("Enter a single-word theme name (e.g., 'brogrammer', 'dungeon', 'vaporwave'): ").strip().lower()
        if theme_name and not any(c in theme_name for c in [' ', '/', '\\', '.', ':', '*', '?', '"', '<', '>', '|']):
            # Replace any potentially problematic characters for filenames, though the check above is quite strict
            theme_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in theme_name)
            return theme_name
        else:
            print("Invalid theme name. Please enter a single word containing only letters, numbers, hyphens, or underscores.")

def generate_ghostty_theme_json(api_key, theme_name):
    """
    Generates a Ghostty theme JSON using OpenAI.
    """
    client = OpenAI(api_key=api_key)

    prompt_content = f"""
    You are a helpful assistant that generates color themes for the Ghostty terminal.
    The user wants a theme inspired by the keyword: "{theme_name}".

    Please generate a valid JSON configuration for a Ghostty theme.
    The JSON output MUST strictly adhere to the following schema and structure:
    {GHOSTTY_SCHEMA_DESCRIPTION}

    Ensure all color values are 6-digit hexadecimal strings starting with '# (e.g., "#RRGGBB").
    Do NOT include any comments (like "// ...") in the JSON output.
    Do NOT output any text or explanations before or after the JSON object.
    The output must be only the JSON object itself, parseable by a standard JSON parser.
    """

    try:
        print(f"\nGenerating theme '{theme_name}' using OpenAI GPT-4o...")
        completion = client.chat.completions.create(
            model="gpt-4o", # Using a modern model that supports JSON mode well
            messages=[
                {"role": "system", "content": "You are an expert JSON generator. You will be given a schema description and a theme keyword. You must return a valid JSON object matching the schema, inspired by the keyword. Only output the JSON object, with no surrounding text or markdown."},
                {"role": "user", "content": prompt_content}
            ],
            response_format={"type": "json_object"} # Request JSON output
        )

        theme_json_string = completion.choices[0].message.content

        # Validate if the response is indeed JSON and parse it
        theme_data = json.loads(theme_json_string)
        print("Theme JSON successfully generated and parsed.")
        return theme_data

    except json.JSONDecodeError as e:
        print(f"Error: OpenAI API did not return valid JSON. {e}")
        print("Raw response from API was:")
        # Only print response string if it was assigned
        if 'theme_json_string' in locals() and theme_json_string:
            print(theme_json_string)
        else:
            print("(No response string captured from API)")
        return None
    except Exception as e:
        print(f"An error occurred while communicating with OpenAI: {e}")
        return None

def save_theme_to_file(theme_name, theme_data):
    """Saves the theme JSON to a file."""
    # Assumes script is run from project root (e.g., vibejam/), so paths are relative
    output_dir = os.path.join("themes", "ghostty")

    # Ensure the directory exists (it should have been created by the assistant earlier)
    # For robustness, we can ensure it here too.
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {output_dir}: {e}")
        return

    file_path = os.path.join(output_dir, f"{theme_name}.json")

    try:
        with open(file_path, 'w') as f:
            json.dump(theme_data, f, indent=2) # Using indent=2 for readability
        print(f"Theme '{theme_name}' saved successfully to {file_path}")
    except IOError as e:
        print(f"Error saving theme file {file_path}: {e}")

def convert_theme_to_conf(theme_data):
    """Converts the parsed theme JSON data into Ghostty's flat .conf style string."""
    lines = []

    # Handle palette entries first (indices 0-15 in order)
    palette = theme_data.get("palette", {})
    for i in range(16):
        hex_code = palette.get(str(i))
        if not hex_code:
            print(f"Warning: Palette index {i} missing in generated theme data.")
            continue
        lines.append(f"palette = {i}={hex_code}")

    # Handle the remaining top-level keys (background, foreground, etc.)
    for key, value in theme_data.items():
        if key == "palette":
            continue  # already handled
        lines.append(f"{key} = {value}")

    # Join with newlines and ensure trailing newline for POSIX friendliness
    return "\n".join(lines) + "\n"

def save_conf_to_ghostty(theme_name, conf_content):
    """Saves the stripped-down .conf content to Ghostty's themes directory."""
    ghostty_themes_dir = "/Applications/Ghostty.app/Contents/Resources/themes"
    file_path = os.path.join(ghostty_themes_dir, theme_name.lower())  # No extension per requirement

    # Ensure the destination directory exists (Ghostty installer should create it, but be safe)
    try:
        os.makedirs(ghostty_themes_dir, exist_ok=True)
    except OSError as e:
        print(f"Error ensuring Ghostty themes directory exists at {ghostty_themes_dir}: {e}")
        # If permission denied, offer to elevate using sudo
        if isinstance(e, PermissionError) or e.errno == 13:
            prompt_and_attempt_sudo_save(theme_name, conf_content)
        return

    try:
        with open(file_path, "w") as f:
            f.write(conf_content)
        print(f"Stripped theme saved successfully to {file_path}")
    except IOError as e:
        print(f"Error writing stripped theme to {file_path}: {e}")
        # Permission error? Offer sudo escalation
        if isinstance(e, PermissionError) or getattr(e, 'errno', None) == 13:
            prompt_and_attempt_sudo_save(theme_name, conf_content)

def prompt_and_attempt_sudo_save(theme_name: str, conf_content: str):
    """Prompts the user to attempt saving via sudo and performs the action if agreed."""
    resp = input("It looks like we don't have permission to write to Ghostty's theme directory. Attempt to save using sudo? (y/N): ").strip().lower()
    if resp != 'y':
        print("Skipping sudo attempt. The stripped theme was NOT saved to the Ghostty directory.")
        return

    ghostty_themes_dir = "/Applications/Ghostty.app/Contents/Resources/ghostty/themes"
    target_path = os.path.join(ghostty_themes_dir, theme_name.lower())

    try:
        _attempt_save_with_sudo(conf_content, ghostty_themes_dir, target_path)
    except Exception as ex:
        print(f"sudo attempt failed: {ex}")

def _attempt_save_with_sudo(conf_content: str, dir_path: str, file_path: str):
    """Uses sudo to mkdir -p dir_path and write conf_content to file_path."""
    # Ensure directory exists with sudo
    print("Requesting administrator privileges to write theme file via sudo...")
    mkdir_cmd = ["sudo", "mkdir", "-p", dir_path]
    result = subprocess.run(mkdir_cmd)
    if result.returncode != 0:
        raise RuntimeError(f"sudo mkdir returned non-zero exit status {result.returncode}")

    # Write content using a temporary file then sudo mv
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(conf_content.encode())
        tmp_path = tmp.name

    mv_cmd = ["sudo", "mv", tmp_path, file_path]
    result = subprocess.run(mv_cmd)
    if result.returncode != 0:
        # Clean up temp file if mv fails
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise RuntimeError(f"sudo mv returned non-zero exit status {result.returncode}")

    print(f"Stripped theme saved successfully via sudo to {file_path}")

def main():
    """Main function to run the script."""
    print("Ghostty Theme Generator")
    print("-----------------------")

    api_key = load_api_key()
    if not api_key:
        return # Error message already printed by load_api_key

    theme_name = get_theme_name()

    theme_data = generate_ghostty_theme_json(api_key, theme_name)

    if theme_data:
        # Save full JSON for development/readability
        save_theme_to_file(theme_name, theme_data)

        # Convert to flat .conf string and save to Ghostty themes directory
        conf_content = convert_theme_to_conf(theme_data)
        save_conf_to_ghostty(theme_name, conf_content)
    else:
        print(f"Failed to generate theme data for '{theme_name}'.")

if __name__ == "__main__":
    main()
