# meta developer: rain
# meta name: Demotivator
# meta description: Создаёт демотиватор из изображения в ответе

from PIL import Image, ImageDraw, ImageFont, ImageOps
from .. import loader, utils
import requests, io, os

def get_assets_dir() -> str:
    base_dir: str = os.getcwd()
    assets_dir: str = os.path.join(base_dir, "rain-assets")

    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    return assets_dir

def dl_asset(asset_name: str) -> bool:
    assets_dir: str = get_assets_dir()
    asset_path: str = os.path.join(assets_dir, asset_name)
    url = "https://github.com/loxchmorez/hikka-modules/raw/refs/heads/main/assets/" + asset_name.replace("/", "")

    response = requests.get(url, stream=True)
    if not response.ok:
        return False
    
    with open(asset_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    return True

def get_asset(asset_name: str) -> str:
    asset_path: str = os.path.join(get_assets_dir(), asset_name)
    if os.path.isfile(asset_path):
        return asset_path
    else:
        success: bool = dl_asset(asset_name)
        if os.path.isfile(asset_path):
            return asset_path

    return ""

class DemotivatorMod(loader.Module):
    strings = {"name": "Demotivator"}

    async def demotivatorcmd(self, message):
        args = utils.get_args_raw(message)
        parts = [p.strip() for p in args.split("|")] if args else []
        title = parts[0] if parts else "Демотиватор"
        subtitle = parts[1] if len(parts) > 1 else ""

        reply = await message.get_reply_message()
        if not reply or not reply.photo:
            await message.edit("❗ **Ответь на изображение**", parse_mode="md")
            return

        img = await reply.download_media(bytes)
        image = Image.open(io.BytesIO(img)).convert("RGB")

        image = ImageOps.expand(image, border=4, fill="white")

        padding_top = 60
        padding_bottom = 120
        padding_sides = 60
        text_spacing = 10
        width, height = image.size
        total_width = width + 2 * padding_sides
        total_height = height + padding_top + padding_bottom

        result = Image.new("RGB", (total_width, total_height), "black")
        result.paste(image, (padding_sides, padding_top))

        font: str = get_asset("Times New Roman.ttf")
        if font == "":
            await message.edit("❌ **Ошибка загрузки ассета!**", parse_mode="md")
            return
        font_title = ImageFont.truetype(font, 40)
        font_sub = ImageFont.truetype(font, 24)

        draw = ImageDraw.Draw(result)

        """
        def draw_centered(text, y, font):
            bbox = draw.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
            draw.text(((width - w) / 2, y), text, font=font, fill="white"
        """

        if title:
            w, h = draw.textbbox((0, 0), title, font=font)
            draw.text(((total_width - w) / 2, height + padding_top + text_spacing), title, font=font_title, fill="white")

        if subtitle:
            w2, h2 = draw.textbbox((0, 0), subtitle, font=font_sub)
            draw.text(((total_width - w2) / 2, height + padding_top + 40 + text_spacing), subtitle, font=font_sub, fill="white")

        output = io.BytesIO()
        output.name = "demotivator.jpg"
        result.save(output, "JPEG")
        output.seek(0)

        await message.client.send_file(message.chat_id, output, reply_to=reply.id)
        await message.delete()
