# meta developer: rain

from .. import loader, utils
from telethon.tl.types import Message
from telethon import Button
from PIL import Image
import aiohttp
import requests
from io import BytesIO

class HentaiNekosOnlyMod(loader.Module):
    strings = {"name": "HentaiNekos"}

    async def hentaicmd(self, message: Message):
        """<тег> — Получить hentai по тегу с nekosapi"""
        tag = utils.get_args_raw(message).strip().lower()
        if not tag:
            await message.edit("Укажи тег. Пример: `.hentai pussy`")
            return

        img_file = await self.get_image_file(tag)
        if not img_file:
            await message.edit(f"Изображение по тегу `{tag}` не найдено.")
            return

        btn = [[Button.inline("🔁 Ещё", data=f"hentai:{tag}")]]
        await message.respond(f"Тег: `{tag}`\nИсточник: nekosapi", file=img_file, buttons=btn)
        await message.delete()

    async def inline__hentai(self, call, args):
        if not args:
            await call.answer("Нет тега.", alert=True)
            return

        tag = args[0]
        img_file = await self.get_image_file(tag)
        if not img_file:
            await call.answer("Не найдено.", alert=True)
            return

        btn = [[Button.inline("🔁 Ещё", data=f"hentai:{tag}")]]
        await call.edit(f"Тег: `{tag}`\nИсточник: nekosapi", file=img_file, buttons=btn)

    async def get_image_file(self, tag: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.nekosapi.com/v4/images/random",
                    params={"rating": "explicit", "tags": tag, "limit": 1},
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if isinstance(data, list) and data:
                            url = data[0].get("url")
                            if url.endswith(".webp"):
                                # Конвертация webp → png
                                img_resp = requests.get(url)
                                image = Image.open(BytesIO(img_resp.content)).convert("RGBA")
                                png_image = BytesIO()
                                image.save(png_image, format="PNG")
                                png_image.name = "image.png"
                                png_image.seek(0)
                                return png_image
                            return url
        except Exception as e:
            print(f"[nekosapi error] {e}")
        return None

    async def hentai_tagscmd(self, message: Message):
        """Показать доступные теги"""
        try:
            r = requests.get("https://api.nekosapi.com/v4/tags")
            tags = sorted([tag["name"] for tag in r.json()])
            text = ", ".join(tags)
            await utils.answer(message, f"Доступные теги ({len(tags)}):\n{text}")
        except Exception:
            await utils.answer(message, "Не удалось загрузить теги.")
