from bot.config import WEBHOOK_SECRET, WEBHOOK_URL
from bot.main import tw_bot

if __name__ == "__main__":
    tw_bot.remove_webhook()
    tw_bot.set_webhook(url=WEBHOOK_URL, secret_token=WEBHOOK_SECRET)
    print(tw_bot.get_webhook_info())
