# meta developer: rain
# requires: hikka

from hikka import loader, utils
import re

class BFGCaseOpener(loader.Module):
    """Автоматическое открытие кейсов в @bforgame_bot"""
    
    strings = {
        "name": "BFGCaseOpener"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_repeat", True, lambda: "Покупать заново, если есть деньги"
            )
        )
        self._case_info = {}

    async def watcher(self, message):
        if not message or not message.chat or message.sender_id != 1721358063:
            return

        if not message.text:
            return

        text = message.text.strip()
        user = (await self._client.get_me()).first_name

        buy_match = re.match(r"Кейс купить (\d+) (\d+)", text)
        if buy_match:
            case_id, amount = map(int, buy_match.groups())
            self._case_info[message.chat.id] = {
                "case_id": case_id,
                "to_open": amount,
                "opened": 0
            }
            return

        if m := re.match(rf"{user}, вы успешно купили .+? \((\d+) шт.\) за .+ ✅", text):
            amount = int(m.group(1))
            info = self._case_info.get(message.chat.id)
            if info:
                info["to_open"] = amount
                await self._open_cases(message.chat.id)

        if m := re.match(rf"{user}, вы открыли (\d+) .+?:", text):
            opened_now = int(m.group(1))
            info = self._case_info.get(message.chat.id)
            if info:
                info["opened"] += opened_now
                await self._open_cases(message.chat.id)

        if f"{user}, у вас недостаточно средств" in text:
            self._case_info.pop(message.chat.id, None)

        info = self._case_info.get(message.chat.id)
        if info and info["opened"] >= info["to_open"]:
            await message.reply("Продать рейтинг все")
            if self.config["auto_repeat"]:
                await message.reply(f"Кейс купить {info['case_id']} {info['to_open']}")

    async def _open_cases(self, chat_id):
        info = self._case_info.get(chat_id)
        if not info:
            return
        to_open = min(6, info["to_open"] - info["opened"])
        if to_open > 0:
            await self._client.send_message(chat_id, f"Кейс открыть {info['case_id']} {to_open}")
