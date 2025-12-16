import json
from urllib.parse import urlparse, quote_plus
import requests
import logging

from .xtra import sync_to_async

LOGGER = logging.getLogger("bypass_bot")

_BYPASS_CMD_TO_SERVICE = {
    "gdflix": "gdflix",
    "gdf": "gdflix",
    "extraflix": "extraflix",
    "hubcloud": "hubcloud",
    "hc": "hubcloud",
    "hubdrive": "hubdrive",
    "hd": "hubdrive",
    "hubcdn": "hubcdn",
    "hcdn": "hubcdn",
    "transfer_it": "transfer_it",
    "ti": "transfer_it",
    "vcloud": "vcloud",
    "vc": "vcloud",
    "driveleech": "driveleech",
    "dleech": "driveleech",
    "neo": "neo",
    "neolinks": "neo",
    "gdrex": "gdrex",
    "gdex": "gdrex",
    "pixelcdn": "pixelcdn",
    "pcdn": "pixelcdn",
    "extralink": "extralink",
    "luxdrive": "luxdrive",
    "nexdrive": "nexdrive",
    "nd": "nexdrive",
    "hblinks": "hblinks",
    "hbl": "hblinks",
}

_DOMAIN_TO_SERVICE = {
    # add domains like:
    # "filepress.in": "filepress",
}

_BYPASS_ENDPOINTS = {
    # By : Hgbots
    "gdflix": "https://hgbots.vercel.app/bypaas/gd.php?url=",
    "hubdrive": "https://hgbots.vercel.app/bypaas/hubdrive.php?url=",
    # By : NickUpdates
    "transfer_it": "https://transfer-it-henna.vercel.app/post",
    # By: PBX1
    "hubcloud": "https://pbx1botapi.vercel.app/api/hubcloud?url=",
    "vcloud": "https://pbx1botapi.vercel.app/api/vcloud?url=",
    "hubcdn": "https://pbx1botapi.vercel.app/api/hubcdn?url=",
    "driveleech": "https://pbx1botapi.vercel.app/api/driveleech?url=",
    "neo": "https://pbx1botapi.vercel.app/api/neo?url=",
    "gdrex": "https://pbx1botapi.vercel.app/api/gdrex?url=",
    "pixelcdn": "https://pbx1botapi.vercel.app/api/pixelcdn?url=",
    "extraflix": "https://pbx1botapi.vercel.app/api/extraflix?url=",
    "extralink": "https://pbx1botapi.vercel.app/api/extralink?url=",
    "luxdrive": "https://pbx1botapi.vercel.app/api/luxdrive?url=",
    "nexdrive": "https://pbx1botsapi2.vercel.app/api/nexdrive?url=",
    "hblinks": "https://pbx1botsapi2.vercel.app/api/hblinks?url=",
}


def _bp_label_from_key(key: str) -> str:
    mapping = {
        "instant_final": "Instant",
        "cloud_r2": "Cloud R2",
        "zip_final": "ZIP",
        "pixeldrain": "Pixeldrain",
        "telegram_file": "Telegram",
        "gofile_final": "Gofile",
    }
    if key in mapping:
        return mapping[key]
    return key.replace("_", " ").title()


def _bp_label_from_name(name: str) -> str:
    s = str(name).strip()
    low = s.lower()
    if "[" in s and "]" in s and "download" in low:
        i1 = s.find("[")
        i2 = s.rfind("]")
        if i1 != -1 and i2 != -1 and i2 > i1:
            inner = s[i1 + 1 : i2].strip()
            if inner:
                return inner
    if low.startswith("download "):
        return s[8:].strip() or s
    return s


def bp_links_text(links: dict) -> str:
    if not isinstance(links, dict) or not links:
        return "• No direct links found."
    lines = []
    for label, url in links.items():
        if not isinstance(url, str):
            continue
        u = url.strip()
        if not u.startswith(("http://", "https://")):
            continue
        lbl = str(label).strip() or "Link"
        lines.append(f"• {lbl}: [Click Here]({u})")
    if not lines:
        return "• No direct links found."
    return "
".join(lines)


def _bp_norm(data: dict, service: str) -> dict:
    root = data
    if isinstance(data, dict) and isinstance(data.get("final"), dict):
        root = data["final"]

    title = (
        root.get("title")
        or data.get("title")
        or root.get("file_name")
        or data.get("file_name")
        or "N/A"
    )
    filesize = (
        root.get("filesize")
        or data.get("filesize")
        or root.get("file_size")
        or data.get("file_size")
        or "N/A"
    )
    file_format = (
        root.get("format")
        or root.get("file_format")
        or data.get("format")
        or data.get("file_format")
        or "N/A"
    )

    links_clean = {}
    raw_links = None

    if isinstance(root, dict) and "links" in root:
        raw_links = root.get("links")
    elif isinstance(data, dict) and "links" in data:
        raw_links = data.get("links")

    if not raw_links and isinstance(data, dict) and "results" in data:
        results = data.get("results")
        if isinstance(results, list):
            for item in results:
                if not isinstance(item, dict):
                    continue
                lbl = item.get("quality") or item.get("name") or "Link"
                url = item.get("link") or item.get("url")
                if isinstance(url, str):
                    u = url.strip()
                    if u.startswith(("http://", "https://")):
                        links_clean[str(lbl).strip()] = u
        return {
            "title": str(data.get("title") or title or "N/A"),
            "filesize": str(data.get("filesize") or filesize or "N/A"),
            "format": str(data.get("format") or file_format or "N/A"),
            "links": links_clean,
            "service": service,
        }

    if isinstance(raw_links, list):
        for item in raw_links:
            if not isinstance(item, dict):
                continue
            lbl = item.get("type") or item.get("name") or "Link"
            url = item.get("url") or item.get("link")
            if not isinstance(url, str):
                continue
            u = url.strip()
            if not u.startswith(("http://", "https://")):
                continue
            links_clean[str(lbl).strip()] = u
    elif isinstance(raw_links, dict):
        for k, v in raw_links.items():
            if not isinstance(v, (str, dict)):
                continue
            url = None
            lbl = _bp_label_from_key(k)
            if isinstance(v, str):
                url = v.strip()
            elif isinstance(v, dict):
                url = (
                    v.get("link")
                    or v.get("url")
                    or v.get("google_final")
                    or v.get("edited")
                    or v.get("telegram_file")
                    or v.get("gofile_final")
                )
                if v.get("name"):
                    lbl = _bp_label_from_name(v["name"])
            if not url or not isinstance(url, str):
                continue
            u = url.strip()
            if not u.startswith(("http://", "https://")):
                continue
            links_clean[lbl] = u

    if not links_clean and isinstance(root, dict):
        skip = {
            "title",
            "filesize",
            "format",
            "file_format",
            "success",
            "links",
            "file_name",
            "file_size",
        }
        for k, v in root.items():
            if k in skip:
                continue
            url = None
            lbl = str(k)
            if isinstance(v, dict):
                url = (
                    v.get("link")
                    or v.get("url")
                    or v.get("google_final")
                    or v.get("edited")
                    or v.get("telegram_file")
                    or v.get("gofile_final")
                )
                if v.get("name"):
                    lbl = _bp_label_from_name(v["name"])
            elif isinstance(v, str) and v.startswith(("http://", "https://")):
                url = v
                lbl = _bp_label_from_key(k)
            if not url or not isinstance(url, str):
                continue
            u = url.strip()
            if not u.startswith(("http://", "https://")):
                continue
            links_clean[lbl] = u

    return {
        "title": str(title),
        "filesize": str(filesize),
        "format": str(file_format),
        "links": links_clean,
        "service": service,
    }


def _resolve_service(cmd_name: str, target_url: str) -> str | None:
    cmd = (cmd_name or "").lower().lstrip("/")
    if cmd in _BYPASS_CMD_TO_SERVICE:
        return _BYPASS_CMD_TO_SERVICE[cmd]
    try:
        parsed = urlparse(target_url)
        host = parsed.netloc.lower()
    except Exception:
        host = ""
    if host in _DOMAIN_TO_SERVICE:
        return _DOMAIN_TO_SERVICE[host]
    if host.startswith("www.") and host[4:] in _DOMAIN_TO_SERVICE:
        return _DOMAIN_TO_SERVICE[host[4:]]
    return None


async def bp_info(cmd_name: str, target_url: str):
    service = _resolve_service(cmd_name, target_url)
    if not service:
        return None, "Unknown platform for this command."
    base = _BYPASS_ENDPOINTS.get(service)
    if not base:
        return None, "Bypass endpoint not configured for this service."

    try:
        parsed = urlparse(target_url)
        if not parsed.scheme or not parsed.netloc:
            return None, "Invalid URL."
    except Exception:
        return None, "Invalid URL."

    api_url = base if service == "transfer_it" else f"{base}{quote_plus(target_url)}"
    LOGGER.info("Bypassing via [%s] -> %s", service, api_url)

    try:
        if service == "transfer_it":
            resp = await sync_to_async(
                requests.post, api_url, json={"url": target_url}, timeout=20
            )
        else:
            resp = await sync_to_async(requests.get, api_url, timeout=20)
    except Exception as e:
        LOGGER.error("Bypass HTTP error: %s", e, exc_info=True)
        return None, "Failed to reach bypass service."

    if resp.status_code != 200:
        LOGGER.error("Bypass API returned %s: %s", resp.status_code, resp.text[:200])
        return None, "Bypass service error."

    try:
        data = resp.json()
    except json.JSONDecodeError as e:
        LOGGER.error("Bypass JSON parse error: %s", e)
        return None, "Invalid response from bypass service."

    if not isinstance(data, dict):
        return None, "Unexpected response from bypass service."

    if "success" in data and not data.get("success"):
        return None, data.get("message") or "Bypass failed."

    if service == "transfer_it":
        direct = data.get("url")
        if not direct:
            return None, "File Expired or File Not Found"
        fake = {
            "title": "N/A",
            "filesize": "N/A",
            "format": "N/A",
            "links": {"Direct Link": str(direct)},
        }
        return _bp_norm(fake, service), None

    if service == "hblinks":
        direct = data.get("url")
        if not direct:
            return None, "File Expired or Link Not Found"
        fake = {
            "title": "N/A",
            "filesize": "N/A",
            "format": "N/A",
            "links": {data.get("provider", "Direct Link"): str(direct)},
        }
        return _bp_norm(fake, service), None

    norm = _bp_norm(data, service)
    return norm, None
