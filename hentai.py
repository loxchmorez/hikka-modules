# meta developer: rain

from .. import loader, utils
from telethon.tl.types import Message
from telethon import Button
from PIL import Image
import aiohttp
from io import BytesIO

class hentai:
    @staticmethod
    def parse_tags(raw: str):
        return [t.strip().lower() for t in raw.replace(",", " ").split() if t.strip()]

    @staticmethod
    async def find_image(tags):
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
                                async with session.get(url) as img_resp:
                                    img_bytes = await img_resp.read()
                                    image = Image.open(BytesIO(img_bytes)).convert("RGBA")
                                    output = BytesIO()
                                    output.name = "image.png"
                                    image.save(output, format="PNG", optimize=True)
                                    output.seek(0)
                                    return output, tags
                            return url, tags
        except Exception as e:
            print(f"[nekosapi error] {e}")
        return None

@loader.tds
class HentaiMod(loader.Module):
    """Модуль для генерации хентай изображений"""

    strings = {
        "name": "HentaiMod",
        "lang": "EN",
        "looking_for": "🔍 Searching for an image by tags:",
        "no_tags": "❗️ Provide at least one tag. Example: `.hentai pussy`",
        "not_found": "⚠️ Nothing found by tags:",
        "more": "🔁 More",
        "tags": "#️⃣ Tags:"
    }

    strings_ru = {
        "lang": "RU",
        "looking_for": "🔍 Ищу изображение по тегам:",
        "no_tags": "❗️ Укажи хотя бы один тег. Пример: `.hentai pussy`",
        "not_found": "⚠️ Ничего не найдено по тегам:",
        "more": "🔁 Ещё",
        "tags": "#️⃣ Теги:"
    }

    genres_en = ["anal", "beach", "bikini", "black hair", "blonde hair", "blue hair", "boy", "brown hair", "bunny girl", "catgirl", "dick", "dress", "exposed anus", "exposed girl breasts", "flat chest", "flowers", "futanari", "girl", "glasses", "gloves", "guitar", "horsegirl", "ice cream", "kemonomimi", "kissing", "large breasts", "maid", "masturbating", "medium breasts", "mountain", "night", "pink hair", "plants", "purple hair", "pussy", "rain", "reading", "red hair", "school uniform", "shorts", "skirt", "small breasts", "sportswear", "sunny", "sword", "threesome", "tree", "usagimimi", "weapon", "wet", "white hair", "yuri"]
    genres_ru = ["анал", "пляж", "бикини", "чёрные волосы", "светлые волосы", "голубые волосы", "парень", "коричневые волосы", "девушка-кролик", "девушка-кошка", "пенис", "одежда", "обнаженный анус", "обнаженная женская грудь", "плоская грудь", "цветы", "гермафродит", "девушка", "очки", "перчатки", "гитара", "девушка-лошадь", "мороженое", "кемономими", "поцелуй", "большая грудь", "служанка", "мастурбировация", "средняя грудь", "гора", "ночь", "розовые волосы", "растения", "фиолетовые волосы", "киска", "дождь", "чтение", "красные волосы", "школьная форма", "шорты", "юбка", "маленькая грудь", "спортивная одежда", "солнечно", "меч", "тройка", "дерево", "усагимими", "оружие", "мокрое тело", "белые волосы", "юри"]

    def translate_tags(self, tags):
        lang = self.strings("lang")
        translation_map = dict(zip(self.genres_en, self.genres_ru)) if lang == "RU" else {}
        return ', '.join(f"`{translation_map.get(tag, tag).replace('_', ' ')}`" for tag in tags)

    @loader.command(ru_doc="Поиск по тегам", en_doc="Search by tags")
    async def hentai(self, message: Message):
        raw = utils.get_args_raw(message)
        if not raw:
            await message.edit(self.strings("no_tags"), parse_mode="md")
            return

        tags = hentai.parse_tags(raw)
        await message.edit(f"{self.strings('looking_for')} `{', '.join(tags)}`...", parse_mode="md")

        result = await hentai.find_image(tags)
        if not result:
            await message.edit(f"{self.strings('not_found')} `{', '.join(tags)}`.", parse_mode="md")
            return

        file, found_tags = result
        caption = f"**{self.strings('tags')}** {self.translate_tags(found_tags)}"
        btns = [[Button.inline(self.strings("more"), data="hentai:" + ",".join(tags))]]

        await message.client.send_file(
            message.chat_id,
            file,
            caption=caption,
            reply_to=message.reply_to_msg_id,
            buttons=btns,
            parse_mode="md"
        )
        await message.delete()

    @loader.command()
    async def is_premium(self, message: Message):
        if self._client.hikka_me.premium:
            await message.edit("👑 Вы **Premium** пользователь!", parse_mode="md")
        else:
            await message.edit("🕳️ Вы не **Premium** пользователь!", parse_mode="md")

    async def inline__hentai(self, call, args):
        if not args:
            await call.answer(self.strings("no_tags"), alert=True)
            return

        tags = args[0].split(",")
        result = await hentai.find_image(tags)
        if not result:
            await call.answer(self.strings("not_found"), alert=True)
            return

        file, found_tags = result
        caption = f"**{self.strings('tags')}** {self.translate_tags(found_tags)}"
        btns = [[Button.inline(self.strings("more"), data="hentai:" + ",".join(tags))]]

        await call.edit(file=file, text=caption, buttons=btns, parse_mode="md")