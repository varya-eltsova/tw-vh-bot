# Точка входа для Apache (mod_wsgi) на виртуальном хостинге Timeweb.
# Кладётся в ~/<сайт>/public_html/ рядом с .htaccess, права 755.
# Проект лежит рядом: ~/<сайт>/tw-vh-bot/ (не в public_html!).
#
# Пути ниже - для аккаунта ch81104 и сайта tw_api.
# Замените их на свои: /home/<первая буква логина>/<логин>/<сайт>/tw-vh-bot
import sys

sys.path.insert(0, "/home/c/ch81104/tw_api/tw-vh-bot")
sys.path.insert(0, "/home/c/ch81104/tw_api/tw-vh-bot/.venv/lib/python3.10/site-packages")

from bot.webhook import app as application  # noqa: E402
