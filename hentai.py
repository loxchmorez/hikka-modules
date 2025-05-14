# meta developer: rain

from .. import loader, utils
from telethon.tl.types import Message
from telethon import Button
import aiohttp
import asyncio
import random

class HentaiGenMod(loader.Module):
    strings = {"name": "HentaiGen"}

    waifu_tags = ["waifu", "neko", "trap", "blowjob"]
    nekosapi_endpoint = "https://api.nekosapi.com/v4/images/random"
    nekosapi_rating = "explicit"

    async def hentaicmd(self, message: Message):
        """<тег> — сгенерировать hentai картинку"""
        tag = utils.get_args_raw(message).strip().lower()

        if not tag:
            await message.edit("Укажи тег, например `.hentai neko`")
            return

        img_url, source = await self.get_random_image(tag)

        if not img_url:
            await message.edit(f"Не удалось найти изображение по тегу {tag}.")
            return

        btn = [[Button.inline(f"🔁 Обновить ({source})", data=f"hentai|{tag}")]]
        await message.respond(f"Тег: `{tag}`\nИсточник: `{source}`", file=img_url, buttons=btn)
        await message.delete()

    async def inline__hentai(self, call, args):
        if not args:
            await call.answer("Ошибка в аргументах кнопки.", alert=True)
            return

        tag = args[0]
        img_url, source = await self.get_random_image(tag)

        if not img_url:
            await call.answer("Ошибка при загрузке.", alert=True)
            return

        btn = [[Button.inline(f"🔁 Обновить ({source})", data=f"hentai|{tag}")]]
        await call.edit(f"Тег: `{tag}`\nИсточник: `{source}`", file=img_url, buttons=btn)

    async def get_random_image(self, tag):
        sources = ["nekosapi", "waifu.pics"]
        random.shuffle(sources)

        for source in sources:
            try:
                if source == "nekosapi":
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