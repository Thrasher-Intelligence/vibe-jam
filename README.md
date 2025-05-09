# Ghostty Theme Generator (Loom)

Generate custom colour themes for the [Ghostty](https://ghostty.io/) terminal emulator in one command using OpenAI-powered prompts.

> ⚠️  This began life as a one-hour hackathon experiment, so expect rough edges. Pull requests welcome!

---

## How it works

1. `main.py` prompts you for a one-word theme name – e.g. `minecraft`, `vaporwave`, `brogrammer`.
2. The script calls the OpenAI Chat Completion API (JSON-mode, GPT-4o) with a carefully curated schema description.
3. GPT returns a valid Ghostty theme **JSON** object.
4. We keep that JSON for development readability (`themes/ghostty/<name>.json`).
5. The theme is also flattened into Ghosttyʼs native **.conf** format (key = value). That file is saved to:

```
/Applications/Ghostty.app/Contents/Resources/ghostty/themes/<name>
```

   • No extension, filename is lowercase.
   • If macOS denies permission, the script offers to rerun the copy step with `sudo`.

6. Finally you switch to the theme inside Ghosttyʼs UI (Preferences ▸ Themes ▸ Select your new theme).

---

## Repository layout

```
├── main.py                     # entry point – generates & installs themes
├── schemas/
│   └── ghostty.json            # JSON schema used in the prompt (for reference)
├── themes/
│   └── ghostty/                # generated JSON themes are stored here
├── requirements.txt            # Python dependencies
└── README.md                   # you are here
```

---

## Prerequisites

• Python 3.9+
• A valid OpenAI API key with GPT-4 access
• Ghostty installed (macOS only for now)

---

## Setup

```bash
# 1. clone & enter
$ git clone https://github.com/Thrasher-Intelligence/vibe-jam
$ cd vibejam

# 2. (optional) virtualenv
$ python -m venv venv && source venv/bin/activate

# 3. install deps
$ pip install -r requirements.txt

# 4. add your OpenAI key
$ echo "OPENAI_API_KEY=sk-..." > .env
```

---

## Usage

```bash
python main.py
```

You will be asked for a theme name:

```
Enter a single-word theme name (e.g., 'brogrammer', 'dungeon', 'vaporwave'): minecraft
```

The script prints progress, writes the files, and (optionally) elevates to `sudo` when macOS blocks writes inside the Ghostty bundle.

Once complete, open Ghostty ▸ Preferences ▸ Themes and choose your newly-generated theme.

---

## Troubleshooting

• **Permission denied** – select `y` when asked to install via sudo.
• **API quota / model errors** – ensure your key has GPT-4 access.
• **Theme doesnʼt look right** – inspect the JSON in `themes/ghostty/<name>.json` and tweak values manually.

---

## License

MIT – see `LICENSE` (coming soon).
