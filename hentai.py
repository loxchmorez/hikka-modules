# meta developer: rain

from .. import loader, utils
from telethon.tl.types import Message
from telethon import Button
from PIL import Image
import aiohttp
from io import BytesIO
from dataclasses import dataclass

@dataclass
class Pair:
    first: str
    second: str

    def __iter__(self):
        return iter((self.first, self.second))

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
        "looking_for": "{} Searching for an image by tags:",
        "no_tags": "{} Provide at least one tag. Example: <code>.hentai pussy</code>",
        "not_found": "{} Nothing found by tags:",
        "more": "{} More",
        "tags": "{} Tags:"
    }

    strings_ru = {
        "lang": "RU",
        "looking_for": "{} Ищу изображение по тегам:",
        "no_tags": "{} Укажи хотя бы один тег. Пример: <code>.hentai pussy</code>",
        "not_found": "{} Ничего не найдено по тегам:",
        "more": "{} Ещё",
        "tags": "{} <b>Теги:</b>"
    }

    format_map = {
        "looking_for": Pair("🔎", "<emoji document_id=5231012545799666522>🔍</emoji>"),
        "no_tags": Pair("❌", "![❌](tg://emoji?id=5210952531676504517)"),
        "not_found": Pair("⚠️", "![⚠️](tg://emoji?id=5447644880824181073)"),
        "more": Pair("🔁", "🔁"),
        "tags": Pair("#️⃣", "![📎](tg://emoji?id=5305265301917549162)")
    }

    def format_string(self, string_name: str):
        string = self.strings(string_name)
        e1, e2 = self.format_map[string_name]
        if self._client.hikka_me.premium:
            return string.format(e2)
        else:
            return string.format(e1)

    genres_en = ["anal", "beach", "bikini", "black hair", "blonde hair", "blue hair", "boy", "brown hair", "bunny girl", "catgirl", "dick", "dress", "exposed anus", "exposed girl breasts", "flat chest", "flowers", "futanari", "girl", "glasses", "gloves", "guitar", "horsegirl", "ice cream", "kemonomimi", "kissing", "large breasts", "maid", "masturbating", "medium breasts", "mountain", "night", "pink hair", "plants", "purple hair", "pussy", "rain", "reading", "red hair", "school uniform", "shorts", "skirt", "small breasts", "sportswear", "sunny", "sword", "threesome", "tree", "usagimimi", "weapon", "wet", "white hair", "yuri"]
    genres_ru = ["анал", "пляж", "бикини", "чёрные волосы", "светлые волосы", "голубые волосы", "парень", "коричневые волосы", "девушка-кролик", "девушка-кошка", "пенис", "одежда", "обнаженный анус", "обнаженная женская грудь", "плоская грудь", "цветы", "гермафродит", "девушка", "очки", "перчатки", "гитара", "девушка-лошадь", "мороженое", "кемономими", "поцелуй", "большая грудь", "служанка", "мастурбировация", "средняя грудь", "гора", "ночь", "розовые волосы", "растения", "фиолетовые волосы", "киска", "дождь", "чтение", "красные волосы", "школьная форма", "шорты", "юбка", "маленькая грудь", "спортивная одежда", "солнечно", "меч", "тройка", "дерево", "усагимими", "оружие", "мокрое тело", "белые волосы", "юри"]

    def translate_tags(self, tags):
        lang = self.strings("lang")
        translation_map = dict(zip(self.genres_en, self.genres_ru)) if lang == "RU" else {}
        return ', '.join(f"<code>{translation_map.get(tag, tag).replace('_', ' ')}</code>" for tag in tags)

    @loader.command(ru_doc="Поиск по тегам", en_doc="Search by tags")
    async def hentai(self, message: Message):
        raw = utils.get_args_raw(message)
        if not raw:
            await message.edit(self.format_string("no_tags"), parse_mode="html")
            return

        tags = hentai.parse_tags(raw)
        await message.edit(f"{self.format_string('looking_for')} <code>{', '.join(tags)}</code>...", parse_mode="html")

        result = await hentai.find_image(tags)
        if not result:
            await message.edit(f"{self.format_string('not_found')} <code>{', '.join(tags)}</code>.", parse_mode="html")
            return

        file, found_tags = result
        caption = f"{self.format_string('tags')} {self.translate_tags(found_tags)}"
        btns = [[Button.inline(self.format_string("more"), data="hentai:" + ",".join(tags))]]

        await message.client.send_file(
            message.chat_id,
            file,
            caption=caption,
            reply_to=message.reply_to_msg_id,
            buttons=btns,
            parse_mode="html"
        )
        await message.delete()

    async def inline__hentai(self, call, args):
        if not args:
            await call.answer(self.format_string("no_tags"), alert=True)
            return

        tags = args[0].split(",")
        result = await hentai.find_image(tags)
        if not result:
            await call.answer(self.format_string("not_found"), alert=True)
            return

        file, found_tags = result
        caption = f"{self.format_string('tags')} {self.translate_tags(found_tags)}"
        btns = [[Button.inline(self.format_string("more"), data="hentai:" + ",".join(tags))]]

        await call.edit(file=file, text=caption, buttons=btns, parse_mode="html")