# meta developer: rain

from .. import loader, utils
from telethon.tl.types import Message
from telethon import Button
from PIL import Image
import aiohttp
import requests
from io import BytesIO

class hentai:
    def parse_tags(raw: str):
        return [t.strip().lower() for t in raw.replace(",", " ").split() if t.strip()]

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

@loader.tds
class HentaiMod(loader.Module):
    """Модуль для генерации хентай изображений"""

    strings = {
        "name": "HentaiMod",
        "lang": "EN",
        "looking_for": "🔍 Searching for an image by tags:",
        "no_tags": "❗️ Provide at least one tag. Example: `.hentai pussy`",
        "not_found": "⚠️ Ничего не найдено по тегам",
        "more": "🔁 More",
        "tags": "Tags:"
    }

    strings_ru = {
        "lang": "RU",
        "looking_for": "🔍 Ищу изображение по тегам:",
        "no_tags": "❗️ Укажи хотя бы один тег. Пример: `.hentai pussy`",
        "not_found": "⚠️ Nothing found by tags",
        "more": "🔁 Ещё",
        "tags": "Теги:"
    }

    # i parsed 10k posts to extract them all (nekosapi sorry for server load)
    genres_en = [
        "anal",
        "beach",
        "bikini",
        "black_hair",
        "blonde_hair",
        "blue_hair",
        "boy",
        "brown_hair",
        "bunny_girl",
        "catgirl",
        "dick",
        "dress",
        "exposed_anus",
        "exposed_girl_breasts",
        "flat_chest",
        "flowers",
        "futanari",
        "girl",
        "glasses",
        "gloves",
        "guitar",
        "horsegirl",
        "ice_cream",
        "kemonomimi",
        "kissing",
        "large_breasts",
        "maid",
        "masturbating",
        "medium_breasts",
        "mountain",
        "night",
        "pink_hair",
        "plants",
        "purple_hair",
        "pussy",
        "rain",
        "reading",
        "red_hair",
        "school_uniform",
        "shorts",
        "skirt",
        "small_breasts",
        "sportswear",
        "sunny",
        "sword",
        "threesome",
        "tree",
        "usagimimi",
        "weapon",
        "wet",
        "white_hair",
        "yuri"
    ]
    genres_ru = [
        "RU",
        "анал",
        "пляж",
        "бикини",
        "чёрные волосы",
        "светлые волосы",
        "голубые волосы",
        "парень",
        "коричневые волосы",
        "девушка-кролик",
        "девушка-кошка",
        "пенис",
        "одежда",
        "обнаженный анус",
        "обнаженная женская грудь",
        "плоская грудь",
        "цветы",
        "гермафродит",
        "девушка",
        "очки",
        "перчатки",
        "гитара",
        "девушка-лошадь",
        "мороженое",
        "кемономими",
        "поцелуй",
        "большая грудь",
        "служанка",
        "мастурбирование",
        "средняя грудь",
        "гора",
        "ночь",
        "розовые волосы",
        "растения",
        "фиолетовые волосы",
        "киска",
        "дождь",
        "чтение",
        "красные волосы",
        "школьная форма",
        "шорты",
        "юбка",
        "маленькая грудь",
        "спортивная одежда",
        "солнечно",
        "меч",
        "тройка",
        "дерево",
        "усагимими",
        "оружие",
        "мокрое тело",
        "белые волосы",
        "юри"
    ]
    
    def translate_tags(self, tags):
        lang = self.strings("lang")
        
        translated = []
        for tag in tags:
            search_tag = tag.replace('_', ' ')
            
            if lang == "RU":
                try:
                    index = genres_en.index(search_tag.lower())
                    translated_tag = genres_ru[index]
                except ValueError:
                    translated_tag = search_tag
            else:
                translated_tag = search_tag
            
            translated.append(f"`{translated_tag}`")
        
        return ', '.join(translated)

    @loader.command(
        ru_doc = "<тег1> [тег2] [...] — Найти hentai по тегам",
        en_doc = "<tag1> [tag2] [...] — Find hentai by tags",
    )
    async def hentai(self, message: Message):
        raw_tags = utils.get_args_raw(message).strip()
        if not raw_tags:
            await message.edit(self.strings("no_tags"), parse_mode="md")
            return

        tags = hentai.parse_tags(raw_tags)
        await message.edit(f"{self.strings('looking_for')} `{', '.join(tags)}`...", parse_mode="md")

        image_data = await hentai.find_image(tags)
        if not image_data:
            await message.edit(f"{self.strings('not_found')} `{', '.join(tags)}`.", parse_mode="md")
            return

        img_file, found_tags = image_data
        tags_str = self.translate_tags(found_tags)
        btns = [[Button.inline(self.strings("more"), data="hentai:" + ",".join(tags))]]

        await message.client.send_file(
            message.chat_id,
            img_file,
            caption=f"**{self.strings('tags')}:** {tags_str}",
            reply_to=message.reply_to_msg_id,
            parse_mode="md",
            buttons=btns
        )
        await message.delete()

    async def inline__hentai(self, call, args):
        if not args:
            await call.answer(self.strings("not_found"), alert=True)
            return

        tags = args[0].split(",")
        image_data = await hentai.find_image(tags)
        if not image_data:
            await call.answer(self.strings("not_found"), alert=True)
            return

        img_file, found_tags = image_data
        tags_str = self.translate_tags(found_tags)
        btns = [[Button.inline(self.strings("more"), data="hentai:" + ",".join(tags))]]

        await call.edit(
            file=img_file,
            text=f"**{self.strings('tags')}:** {tags_str}",
            parse_mode="md",
            buttons=btns
        )
