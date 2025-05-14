# meta developer: your_username
# meta pic: https://i.imgur.com/DSZ7uzU.png

from telethon.tl.types import Message
from .. import loader, utils
import aiohttp
import random
import asyncio

try:
    from hmtai import Hmtai
    hmtai_available = True
    hmtai_client = Hmtai()
except ImportError:
    hmtai_available = False

class HentaiApiMod(loader.Module):
    strings = {"name": "HentaiGen"}

    def __init__(self):
        self.apis = [
            ("waifu.pics", "https://api.waifu.pics/nsfw/{tag}", "json", "url"),
            ("nekos.life", "https://nekos.life/api/v2/img/{tag}", "json", "url")
        ]
        self.hmtai_tags = [
            "anal", "ass", "bdsm", "cum", "femdom", "foot", "gangbang", "hentai",
            "incest", "masturbation", "neko", "orgy", "panties", "pussy", "school",
            "tentacles", "thighs", "uglyBastard", "uniform", "yuri"
        ]

    async def hentaicmd(self, message: Message):
        """<тег> - сгенерировать NSFW изображение по тегу (если доступен)"""
        args = utils.get_args_raw(message).strip()
        if not args:
            await message.edit("Укажи тег, например `.hentai waifu`")
            return

        media_url, api_used = await self._fetch_image(args)
        if not media_url:
            await message.edit(f"Невозможно найти изображение по тегу `{args}`.")
            return

        btn = [
            [
                {
                    "text": f"🔁 Обновить ({api_used})",
                    "callback": self._hentai_cb,
                    "args": (args,),
                }
            ]
        ]

        await self._send_pic(message, media_url, f"Тег: `{args}`\nИсточник: `{api_used}`", btn)

    async def _hentai_cb(self, call, tag):
        media_url, api_used = await self._fetch_image(tag)
        if not media_url:
            await call.edit(f"Ошибка при получении изображения с тегом `{tag}`.")
            return
        btn = [
            [
                {
                    "text": f"🔁 Обновить ({api_used})",
                    "callback": self._hentai_cb,
                    "args": (tag,),
                }
            ]
        ]
        await call.edit(f"Тег: `{tag}`\nИсточник: `{api_used}`", media=media_url, buttons=btn)

    async def _fetch_image(self, tag):
        sources = []

        for name, url_template, resp_type, key in self.apis:
            sources.append(("api", name, url_template, resp_type, key))

        if hmtai_available and tag in self.hmtai_tags:
            sources.append(("hmtai", "hmtai", None, None, None))

        random.shuffle(sources)

        for source in sources:
            if source[0] == "api":
                _, name, url_template, resp_type, key = source
                url = url_template.format(tag=tag)
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as resp:
                            if resp.status != 200:
                                continue
                            if resp_type == "json":
                                data = await resp.json()
                                return data.get(key), name
                except:
                    continue
            elif source[0] == "hmtai":
                try:
                    loop = asyncio.get_event_loop()
                    image_url = await loop.run_in_executor(None, lambda: hmtai_client.get("hmtai", tag))
                    return image_url, "hmtai"
                except:
                    continue

        return None, None

    async def _send_pic(self, message, url, text, buttons):
        try:
            await utils.answer(message, text, media=url, buttons=buttons)
        except Exception as e:
            await utils.answer(message, f"Ошибка отправки: {e}")
