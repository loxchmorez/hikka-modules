# meta developer: rain
# meta name: Demotivator
# meta description: Создаёт демотиватор из изображения в ответе

from PIL import Image, ImageDraw, ImageFont, ImageOps
from .. import loader, utils
import io

class DemotivatorMod(loader.Module):
    strings = {"name": "Demotivator"}

    async def demotivatorcmd(self, message):
        args = utils.get_args_raw(message)
        parts = [p.strip() for p in args.split("|")] if args else []
        title = parts[0] if parts else "Демотиватор"
        subtitle = parts[1] if len(parts) > 1 else ""

        reply = await message.get_reply_message()
        if not reply or not reply.photo:
            await message.edit("❗Ответь на изображение")
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

        try:
            font_title = ImageFont.truetype("times.ttf", 40)
            font_sub = ImageFont.truetype("times.ttf", 24)
        except:
            font_title = ImageFont.truetype("arial.ttf", 40)
            font_sub = ImageFont.truetype("arial.ttf", 24)

        draw = ImageDraw.Draw(result)

        if title:
            w, h = draw.textsize(title, font=font_title)
            draw.text(((total_width - w) / 2, height + padding_top + text_spacing), title, font=font_title, fill="white")

        if subtitle:
            w2, h2 = draw.textsize(subtitle, font=font_sub)
            draw.text(((total_width - w2) / 2, height + padding_top + 40 + text_spacing), subtitle, font=font_sub, fill="white")

        output = io.BytesIO()
        output.name = "demotivator.jpg"
        result.save(output, "JPEG")
        output.seek(0)

        await message.client.send_file(message.chat_id, output, reply_to=reply.id)
        await message.delete()
