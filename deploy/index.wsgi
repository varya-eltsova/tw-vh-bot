# Точка входа для Apache (mod_wsgi) на виртуальном хостинге Timeweb.
# Кладётся в ~/<сайт>/public_html/ рядом с .htaccess, права 755.
# Проект лежит рядом: ~/<сайт>/tw-vh-bot/ (не в public_html!).
import os
import sys

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "tw-vh-bot")
)
SITE_PACKAGES = os.path.join(
    PROJECT_DIR, ".venv", "lib", "python3.10", "site-packages"
)

sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, SITE_PACKAGES)

from bot.webhook import app as application  # noqa: E402
