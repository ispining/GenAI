import uuid
from connection import *
import texts


def start_message(chat_id):
    lng = Language(chat_id).get()
    user = UserDB(user_id=chat_id,
                  balance="30",
                  last_message="None",
                  reg_date=str(datetime.datetime.now()),
                  status="regular")
    if not user.exists():
        user.add()
        print("[NEW USER] " + str(chat_id))

    k_b_m = kbm(resize_keyboard=True)
    k_b_m.add(kbm_btn(texts.Button.new_conversation[lng]), row_width=1)
    k_b_m.add(kbm_btn(texts.Button.balance[lng]), kbm_btn(texts.Button.settings[lng]), row_width=2)
    bot.send_photo(chat_id=chat_id,
                   caption=texts.Content.start_message1[lng],
                   photo="AgACAgEAAxkBAAPJZxzxTCI0o3omZQPJUUW4-Hfp6dMAAp6tMRugFuhED-YPCrYD1bkBAAMCAAN5AAM2BA",
                   reply_markup=k_b_m)

    s = Stage(chat_id)
    s.set(f"conversation||{str(uuid.uuid4())}")


def new_conversation(chat_id):
    s = Stage(chat_id)
    s.set(f"conversation||{str(uuid.uuid4())}")

    lng = Language(chat_id).get()
    bot.send_message(chat_id, texts.Content.start_message2[lng])


def settings(chat_id):
    lng = Language(chat_id).get()
    k = kmarkup()
    k.row(btn(texts.Button.language[lng], callback_data=f"language_selection_stage"))
    msg = texts.Content.settings[lng]
    bot.send_message(chat_id, msg, reply_markup=k)


def language_selection_stage(chat_id):
    lng = Language(chat_id).get()
    k = kmarkup()
    k.row(btn(texts.Button.ru, callback_data=f"new_lang||ru"), btn(texts.Button.en, callback_data=f"new_lang||en"))
    bot.send_message(chat_id, texts.Content.language, reply_markup=k)


def balance(chat_id):
    lng = Language(chat_id).get()

    k = kmarkup()
    user = UserDB(user_id=chat_id).get()
    msg = texts.Content.balance[lng].format(balance=str(user.balance))
    bot.send_message(chat_id, msg, reply_markup=k)

