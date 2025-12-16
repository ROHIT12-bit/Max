import os

class Config:
    API_ID = int(os.getenv("API_ID", "12345"))
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
    BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "123456789"))

    # Caption template for bypass results
    # Available placeholders: {service}, {title}, {filesize}, {file_format}
    BYPASS_CAPTION = (
        "**✺Source:** {service}
"
        "
"
        "**File:** {title}
"
        "`Size:` {filesize} | `Format:` {file_format}"
    )

    START_TEXT = (
        "Hey, I can bypass supported links.
"
        "Use /bypass <url> or reply /bypass to a link."
    )
