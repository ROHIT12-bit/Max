# Bypass Bot

Simple Telegram bot to bypass supported link shorteners / drive indexes.

## Commands

- `/start` – Show intro + inline button.
- `/bypass <url>` – Bypass supported links. Reply to a message with `/bypass` also works.

## Config

Set environment variables:

- `API_ID`
- `API_HASH`
- `BOT_TOKEN`
- `BOT_OWNER_ID` (optional)

Customize result caption in `config.py` via `BYPASS_CAPTION`.
