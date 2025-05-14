# meta developer: your_username

from .. import loader, utils
from telethon.tl.types import Message
from telethon import Button
from PIL import Image
import aiohttp
import requests
from io import BytesIO

class HentaiNekosMod(loader.Module):
    strings = {"name": "HentaiNekos"}

    async def hentaicmd(self, message: Message):
        """<тег> — Получить hentai по тегу с nekosapi"""
        tag = utils.get_args_raw(message).strip().lower()
        if not tag:
            await message.edit("Укажи тег. Пример: `.hentai pussy`")
            return

        await message.edit(f"🔍 Ищу изображение по тегу `{tag}`...")

        image_data = await self.get_nekosapi_image(tag)
        if not image_data:
            await message.edit(f"Изображение по тегу `{tag}` не найдено.")
            return

        img_file, tags = image_data
        tags_str = ", ".join(f"`{t}`" for t in tags)
        btn = [[Button.inline("🔁 Ещё", data=f"hentai:{tag}")]]
        await message.respond(f"Теги: {tags_str}", file=img_file, buttons=btn)
        await message.delete()

    async def inline__hentai(self, call, args):
        if not args:
            await call.answer("Нет тега.", alert=True)
            return

        tag = args[0]
        image_data = await self.get_nekosapi_image(tag)
        if not image_data:
            await call.answer("Не найдено.", alert=True)
            return

        img_file, tags = image_data
        tags_str = ", ".join(f"`{t}`" for t in tags)
        btn = [[Button.inline("🔁 Ещё", data=f"hentai:{tag}")]]
        await call.edit(f"Теги: {tags_str}", file=img_file, buttons=btn)

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
                            image_info = data[0]
                            url = image_info.get("url")
                            tags = image_info.get("tags", [])
                            if url.endswith(".webp"):
                                img_resp = requests.get(url)
                                image = Image.open(BytesIO(img_resp.content)).convert("RGBA")
                                png_image = BytesIO()
                                image.save(png_image, format="PNG")
                                png_image.name = "image.png"
                                png_image.seek(0)
                                return png_image, tags
                            return url, tags
        except Exception as e:
            print(f"[nekosapi error] {e}")
        return None
