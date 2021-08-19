import os
import requests

class NoTelegramEnvsError(Exception):
  def __init__(self):
    super().__init__("telegram bot id and/or chatid is not available.")

TELEGRAM_BOT_ID = os.environ.get("TELEGRAM_BOT_ID")
TELEGRAM_CHAT_ID = os.environ.get("TELGRAM_CHAT_ID")

def telegramQueryBuilder(message, method="sendMessage"):
  if TELEGRAM_BOT_ID and TELEGRAM_CHAT_ID:
    return f"https://api.telegram.org/bot{TELEGRAM_BOT_ID}/{method}?chat_id={TELEGRAM_CHAT_ID}&text={message}"
  else:
    raise NoTelegramEnvsError


def send_info(info: str) -> None:
  # Telegram excepts only 4096 chars for a message, so in case we provide chunks
  info_len = len(info)
  chunk_size = 4096
  full_chunks_num = info_len // chunk_size
  for full_chunk in range(full_chunks_num):
    requests.get(telegramQueryBuilder(info[full_chunk * chunk_size : (full_chunk + 1) * chunk_size]))
  requests.get(telegramQueryBuilder(info[full_chunks_num * chunk_size :]))
  return