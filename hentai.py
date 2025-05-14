# meta developer: your_username

from .. import loader, utils
from telethon.tl.types import Message
from telethon import Button
import aiohttp

class HentaiOnlyNekosMod(loader.Module):
    strings = {"name": "HentaiNekos"}

    async def hentaicmd(self, message: Message):
        """<тег> — получить hentai из nekosapi по тегу"""
        tag = utils.get_args_raw(message).strip().lower()
        if not tag:
            await message.edit("Укажи тег. Например: `.hentai pussy`")
            return

        img_url = await self.get_nekosapi_image(tag)
        if not img_url:
            await message.edit(f"Изображение по тегу `{tag}` не найдено.")
            return

        btn = [[Button.inline("🔁 Обновить", data=f"hentai|{tag}")]]
        await message.respond(f"Тег: `{tag}`\nИсточник: nekosapi", file=img_url, buttons=btn)
        await message.delete()

    async def inline__hentai(self, call, args):
        if not args:
            await call.answer("Нет тега.", alert=True)
            return

        tag = args[0]
        img_url = await self.get_nekosapi_image(tag)
        if not img_url:
            await call.answer("Не найдено.", alert=True)
            return

        btn = [[Button.inline("🔁 Обновить", data=f"hentai|{tag}")]]
        await call.edit(f"Тег: `{tag}`\nИсточник: nekosapi", file=img_url, buttons=btn)

    async def get_nekosapi_image(self, tag):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.nekosapi.com/v4/images/random",
                    params={"rating": "explicit", "tags": tag, "limit": 1},
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if isinstance(data, list) and data:
                            return data[0].get("url")
        except Exception:
            pass
        return None
