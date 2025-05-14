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
            await message.edit("❗️ **Ответь на изображение**", parse_mode="md")
            return

        img = await reply.download_media(bytes)
        image = Image.open(io.BytesIO(img)).convert("RGB")

        image = ImageOps.expand(image, border=6, fill="black")
        image = ImageOps.expand(image, border=2, fill="white")

        padding_top = 60
        padding_sides = 60
        text_spacing = 10
        width, height = image.size
        total_width = width + 2 * padding_sides

        font_path = get_asset("Times New Roman.ttf")
        if font_path == "":
            await message.edit("❌ **Ошибка загрузки шрифта**", parse_mode="md")
            return

        font_title = ImageFont.truetype(font_path, 40)
        font_sub = ImageFont.truetype(font_path, 24)

        dummy_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        title_h = dummy_draw.textbbox((0, 0), title, font=font_title)[3] if title else 0
        subtitle_h = dummy_draw.textbbox((0, 0), subtitle, font=font_sub)[3] if subtitle else 0
        total_text_height = title_h + subtitle_h + (text_spacing * (1 if subtitle else 0))

        total_height = height + padding_top + total_text_height + 40

        result = Image.new("RGB", (total_width, total_height), "black")
        result.paste(image, (padding_sides, padding_top))

        draw = ImageDraw.Draw(result)
        current_y = padding_top + height + text_spacing

        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            w = bbox[2] - bbox[0]
            draw.text(((total_width - w) / 2, current_y), title, font=font_title, fill="white")
            current_y += title_h + text_spacing

        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            w = bbox[2] - bbox[0]
            draw.text(((total_width - w) / 2, current_y), subtitle, font=font_sub, fill="white")

        output = io.BytesIO()
        output.name = "demotivator.jpg"
        result.save(output, "JPEG")
        output.seek(0)

        await message.client.send_file(message.chat_id, output, reply_to=reply.id)
        await message.delete()
