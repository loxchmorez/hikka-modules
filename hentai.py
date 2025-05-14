# meta developer: rain

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
        """<тег1> [тег2] [...] — Получить hentai по тегам"""
        raw_tags = utils.get_args_raw(message).strip()
        if not raw_tags:
            await message.edit("Укажи хотя бы один тег. Пример: `.hentai pussy neko`")
            return

        tags = self.parse_tags(raw_tags)
        await message.edit(f"🔍 Ищу изображение по тегам: `{', '.join(tags)}`...")

        image_data = await self.get_nekosapi_image(tags)
        if not image_data:
            await message.edit(f"⚠️ Ничего не найдено по тегам `{', '.join(tags)}`.")
            return

        img_file, found_tags = image_data
        tags_str = ", ".join(f"`{t}`" for t in found_tags)
        btns = [[Button.inline("🔁 Ещё", data="hentai:" + ",".join(tags))]]

        await message.client.send_file(
            message.chat_id,
            img_file,
            caption=f"**Теги:** {tags_str}",
            reply_to=message.reply_to_msg_id,
            parse_mode="md",
            buttons=btns
        )
        await message.delete()

    async def inline__hentai(self, call, args):
        if not args:
            await call.answer("Нет тегов.", alert=True)
            return

        tags = args[0].split(",")
        image_data = await self.get_nekosapi_image(tags)
        if not image_data:
            await call.answer("Не найдено.", alert=True)
            return

        img_file, found_tags = image_data
        tags_str = ", ".join(f"`{t}`" for t in found_tags)
        btns = [[Button.inline("🔁 Ещё", data="hentai:" + ",".join(tags))]]

        await call.edit(
            file=img_file,
            text=f"**Теги:** {tags_str}",
            parse_mode="md",
            buttons=btns
        )

    def parse_tags(self, raw: str):
        return [t.strip().lower() for t in raw.replace(",", " ").split() if t.strip()]

    async def get_nekosapi_image(self, tags):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.nekosapi.com/v4/images/random",
                    params={"rating": "explicit", "tags": ",".join(tags), "limit": 1},
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
                                png_image.name = "image.png"
                                image.save(png_image, format="PNG")
                                png_image.seek(0)
                                return png_image, tags
                            return url, tags
        except Exception as e:
            print(f"[nekosapi error] {e}")
        return None
