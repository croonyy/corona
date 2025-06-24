import gettext
import os
from config.settings import LANGUAGE
from pathlib import Path

# LANGUAGE= "zh"
BASE_DIR = Path(__file__).resolve().parent.parent

# 根据配置的语言加载翻译文件
# locale_path = os.path.join(os.path.dirname(__file__), "locales")
locale_path = os.path.join(BASE_DIR, "locales")
# print(f"locale_path:{locale_path}")
lang_translations = gettext.translation(
    "messages", localedir=locale_path, languages=[LANGUAGE]
)
lang_translations.install()
_ = lang_translations.gettext  # 获取翻译函数

# print(_("password for user[{username}] is incorrect.").format(username='aaa'))
