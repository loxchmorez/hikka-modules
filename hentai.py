# meta developer: rain
# requires: hmtai asyncio aiohttp

from .. import loader, utils
from telethon.tl.types import Message
import aiohttp
import asyncio
import random
from hmtai import Hmtai

class HentaiGenMod(loader.Module):
    strings = {"name": "HentaiGen"}
    hmtai = Hmtai()

    waifu_tags = ["waifu", "neko", "trap", "blowjob"]
    nekosapi_endpoint = "https://api.nekosapi.com/v4/images/random"
    nekosapi_rating = "explicit"
    hmtai_tags = [
        "anal", "ass", "bdsm", "cum", "femdom", "foot", "gangbang", "hentai",
        "incest", "masturbation", "neko", "orgy", "panties", "pussy", "school",
        "tentacles", "thighs", "uglyBastard", "uniform", "yuri"
    ]

    async def hentaicmd(self, message: Message):
        """<тег> — сгенерировать hentai картинку"""
        tag = utils.get_args_raw(message).strip().lower()

        if not tag:
            await message.edit("Укажи тег, например `.hentai pussy`")
            return

        img_url, source = await self.get_random_image(tag)

        if not img_url:
            await message.edit(f"Не удалось найти изображение по тегу {tag}.")
            return

        btn = [[{"text": f"🔁 Обновить ({source})", "callback": self._hentai_cb, "args": (tag,)}]]
        await utils.answer(message, f"Тег: `{tag}`\nИсточник: `{source}`", media=img_url, buttons=btn)

    async def _hentai_cb(self, call, tag):
        img_url, source = await self.get_random_image(tag)

        if not img_url:
            await call.edit(f"Ошибка при загрузке изображения с тегом `{tag}`")
            return

        btn = [[{"text": f"🔁 Обновить ({source})", "callback": self._hentai_cb, "args": (tag,)}]]
        await call.edit(f"Тег: `{tag}`\nИсточник: `{source}`", media=img_url, buttons=btn)

    async def get_random_image(self, tag):
        sources = ["hmtai", "nekosapi", "waifu.pics"]
        random.shuffle(sources)

        for source in sources:
            try:
                if source == "hmtai" and tag in self.hmtai_tags:
                    url = await asyncio.get_event_loop().run_in_executor(None, lambda: self.hmtai.get("hmtai", tag))
                    return url, "hmtai"

                elif source == "nekosapi":
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            self.nekosapi_endpoint,
                            params={"rating": self.nekosapi_rating, "tags": tag, "limit": 1},
                        ) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                if isinstance(data, list) and data:
                                    return data[0]["url"], "nekosapi"

                elif source == "waifu.pics" and tag in self.waifu_tags:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://api.waifu.pics/nsfw/{tag}") as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                return data.get("url"), "waifu.pics"

            except Exception:
                continue

        return None, None