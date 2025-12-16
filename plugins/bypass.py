from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import Message

from config import Config
from helper.bypsr import bp_info, bp_links_text


def _pretty_service(name: str | None) -> str | None:
    if not name:
        return None
    name = str(name).lower()
    mapping = {
        "gdflix": "GDFlix",
        "hubcloud": "HubCloud",
        "hubdrive": "HubDrive",
        "transfer_it": "Transfer.it",
        "vcloud": "VCloud",
        "hubcdn": "HubCDN",
        "driveleech": "DriveLeech",
        "neo": "NeoLinks",
        "gdrex": "GDRex",
        "pixelcdn": "PixelCDN",
        "extraflix": "ExtraFlix",
        "extralink": "ExtraLink",
        "luxdrive": "LuxDrive",
        "nexdrive": "NexDrive",
        "hblinks": "HBLinks",
    }
    return mapping.get(name, name.title())


def _extract_url_from_message(message: Message) -> str | None:
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    else:
        text = message.text or ""
    parts = text.split()
    for p in parts:
        if p.startswith("http://") or p.startswith("https://"):
            return p
    return None


@Client.on_message(filters.command(["bypass"]) & ~filters.edited)
async def bypass_cmd(client: Client, message: Message):
    if message.chat.type not in (
        ChatType.PRIVATE,
        ChatType.GROUP,
        ChatType.SUPERGROUP,
    ):
        return

    target_url = _extract_url_from_message(message)
    if not target_url:
        return await message.reply_text(
            """**Usage:**
/bypass <url>  or
Reply to a URL with `/bypass`"""
        )

    # NO f-strings here, plain .format()
    wait_msg = await message.reply_text(
        "*Processing:*
`{}`".format(target_url),
        disable_web_page_preview=True
    )

    info, err = await bp_info("bypass", target_url)
    if err:
        return await wait_msg.edit_text("**Error:**
`{}`".format(err))

    service = _pretty_service(info.get("service"))
    title = info.get("title")
    filesize = info.get("filesize")
    file_format = info.get("format")

    caption = Config.BYPASS_CAPTION.format(
        service=service or "Unknown",
        title=title or "N/A",
        filesize=filesize or "N/A",
        file_format=file_format or "N/A",
    )
    links_text = bp_links_text(info.get("links") or {})

    final_text = "{}

{}".format(caption, links_text)
    await wait_msg.edit_text(final_text, disable_web_page_preview=False)
