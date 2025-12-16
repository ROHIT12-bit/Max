import os

class Config:
    API_ID = int(os.getenv("API_ID", "26047636"))
    API_HASH = os.getenv("API_HASH", "d8b1ed69ae1f937c5dd4d3cc8c8de440")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8329949144:AAFFCkR2QRW7ZRiKTy4yVr1_eZRcQ1s16eA")
    BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "8367080346"))

    # Caption template for bypass results
    # Available placeholders: {service}, {title}, {filesize}, {file_format}
    BYPASS_CAPTION = """
**✺Source:** {service}

**File:** {title}
`Size:` {filesize} | `Format:` {file_format}
"""

    START_TEXT = """
Hey, I can bypass supported links.
Use /bypass <url> or reply /bypass to a link.
"""
