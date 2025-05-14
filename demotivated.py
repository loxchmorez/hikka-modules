# meta developer: @your_nickname
# requires: Pillow

from hikkatl.types import Message
from hikka import loader, utils
from PIL import Image, ImageDraw, ImageFont
import io

class DemotivatorMod(loader.Module):
    """Создаёт демотиватор из картинки"""
    strings = {"name": "Demotivator"}

    async def democmd(self, message: Message):
        """[верхний текст];[нижний текст] — превратить картинку в демотиватор"""
        reply = await message.get_reply_message()
        if not reply or not reply.photo:
            return await utils.answer(message, "Ответь на изображение!")

        args = (message.text or "").split(" ", maxsplit=1)
        title = "ДЕМОТИВАТОР"
        subtitle = "Когда всё идёт не по плану..."
        if len(args) > 1 and ";" in args[1]:
            title, subtitle = map(str.strip, args[1].split(";", 1))

        img_bytes = await reply.download_media(bytes)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        # Создание демотиватора
        width = 800
        aspect = img.width / img.height
        img_height = int(width / aspect)
        resized = img.resize((width - 100, img_height))

        padding = 50
        total_height = img_height + 2 * padding + 150
        background = Image.new("RGB", (width, total_height), "black")
        draw = ImageDraw.Draw(background)

        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)

        background.paste(resized, (50, padding))

        def draw_centered(text, y, font):
            w, h = draw.textsize(text, font=font)
            draw.text(((width - w) / 2, y), text, font=font, fill="white")

        draw_centered(title, img_height + padding + 10, font_title)
        draw_centered(subtitle, img_height + padding + 70, font_sub)

        output = io.BytesIO()
        output.name = "demotivator.jpg"
        background.save(output, "JPEG")
        output.seek(0)

        await reply.reply(file=output)
        await message.delete()
