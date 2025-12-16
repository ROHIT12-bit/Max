import logging
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from config import Config

logging.basicConfig(level=logging.INFO)

app = Client(
    "bypass_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins"),
)


@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Bypass Inline",
                    switch_inline_query_current_chat="bypass ",
                )
            ]
        ]
    )
    await message.reply_text(Config.START_TEXT, reply_markup=kb)


@app.on_inline_query()
async def inline_handler(client, inline_query):
    q = inline_query.query.strip()
    if not q.startswith("bypass "):
        return
    url = q[7:].strip()
    if not url:
        return

    result = InlineQueryResultArticle(
        title="Bypass this link",
        description=url,
        input_message_content=InputTextMessageContent(f"/bypass {url}"),
    )
    await inline_query.answer([result], cache_time=0)


if __name__ == "__main__":
    app.run()
