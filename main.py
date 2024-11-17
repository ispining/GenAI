
import os
import time
import threading
import stg
from connection import *
import texts
import BASE


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    print(chat_id)
    chat_type = message.chat.type

    if chat_type == 'private':

        stg.start_message(chat_id)


@bot.message_handler(commands=['add_balance'])
def add_balance(message):
    if message.chat.id in admins:
        user_id = int(message.text.split(" ")[1])
        amount = int(message.text.split(" ")[2])
        lng = Language(user_id).get()
        user = UserDB(user_id=user_id).get()

        if user:
            balance = int(user.balance) + amount
            UserDB(user_id=user_id, balance=balance).update()
            user_info = bot.get_chat(user_id)
            bot.send_message(user_id, texts.Content.balance_updated[lng].format(**{
                "user_id": str(user_id),
                "name": user_info.first_name,
                "username": str(user_info.username),
                "balance": str(user.balance),
                "amount": str(amount),
                "new_balance": str(balance)
            }))
        else:
            bot.send_message(message.chat.id, texts.Content.user_not_found[lng])


@bot.message_handler(commands=['users'])
def users(message):
    if message.chat.id in admins:
        all_users = UserDB().get_all()

        second_msg = "Users: " + str(len(all_users))
        bot.send_message(message.chat.id, second_msg)


@bot.message_handler(commands=['send_to_all'])
def send_to_all(message):
    if message.chat.id in admins:
        command_length = len(message.text.split(" ")[0])

        all_users = UserDB().get_all()
        _user_ok = []
        _user_fail = []
        for user in all_users:
            try:
                lng = Language(int(user.user_id)).get()

                msg = texts.Content.system_message[lng] + message.text[command_length:]
                bot.send_message(user.user_id, msg)

                _user_ok.append(user.user_id)

            except:
                _user_fail.append(user.user_id)

        second_msg = "Users confirmed: " + str(_user_ok) + "\nUsers failed: " + str(_user_fail)
        bot.send_message(message.chat.id, second_msg)


@bot.message_handler(content_types=['text'])
def text(message):
    chat_id = message.chat.id
    chat_type = message.chat.type
    lng = Language(chat_id).get()

    if message.chat.type == 'private':

        if message.text == texts.Button.new_conversation[lng]:
            stg.new_conversation(chat_id)
        elif message.text == texts.Button.balance[lng]:
            stg.balance(chat_id)
        elif message.text == texts.Button.settings[lng]:
            stg.settings(chat_id)

        else:
            cd = Stage(chat_id).get().split("||")
            if cd[0] == "conversation":
                user = UserDB(user_id=chat_id)
                balance = int(user.get().balance)
                if balance > 0:
                    wait_msg = bot.send_message(chat_id, texts.Content.generating[lng])

                    if cd[1] not in os.listdir("convers"):
                        titleAI = BASE.GenAI(texts.dgpt)
                        title = titleAI.generate_content(texts.conv_title_prompt)
                        title = title.replace("<b>", "")
                        title = title.replace("</b>", "")
                        title = title.replace("<i>", "")
                        title = title.replace("</i>", "")
                        title = title.replace("<u>", "")
                        title = title.replace("</u>", "")
                        title = title.replace("<html>", "")
                        title = title.replace("</html>", "")
                        title = title.replace("```", "")
                        title = title.replace("```python", "")
                        title = title.replace("```bash", "")

                        ConversationDB(conversation_id=cd[1], user_id=chat_id, conversation_title=title).new()

                    ai = BASE.GenAI(texts.dgpt)
                    if cd[1] in os.listdir("convers"):
                        ai.history = unpick(f"convers/{cd[1]}")

                    content = ai.generate_content(message.text)
                    content = content.replace("**", "")

                    balance -= 1
                    UserDB(user_id=chat_id, balance=balance).update()

                    pick(f"convers/{cd[1]}", ai.history)

                    bot.delete_message(chat_id, wait_msg.message_id)
                    bot.send_message(chat_id, content)

                elif balance == 0:
                    bot.send_message(chat_id, texts.Content.no_balance[lng])


@bot.message_handler(content_types=["photo"])
def photo(message):
    chat_id = message.chat.id
    chat_type = message.chat.type
    lng = Language(chat_id).get()

    cd = Stage(chat_id).get().split("||")

    if chat_type == 'private':
        if cd[0] == "conversation":

            user = UserDB(user_id=chat_id)
            balance = int(user.get().balance)
            if balance > 0:
                if message.caption in [None, ""]:
                    caption = "--uploaded image--"
                else:
                    caption = message.caption
                wait_msg = bot.send_message(chat_id, texts.Content.generating[lng])
                if cd[1] not in os.listdir("convers"):
                    titleAI = BASE.GenAI(texts.dgpt)
                    title = titleAI.generate_content(texts.conv_title_prompt)
                    title = title.replace("<b>", "")
                    title = title.replace("</b>", "")
                    title = title.replace("<i>", "")
                    title = title.replace("</i>", "")
                    title = title.replace("<u>", "")
                    title = title.replace("</u>", "")
                    title = title.replace("<html>", "")
                    title = title.replace("</html>", "")

                    ConversationDB(conversation_id=cd[1], user_id=chat_id, conversation_title=title).new()

                ai = BASE.GenAI(texts.dgpt)
                if cd[1] in os.listdir("convers"):
                    ai.history = unpick(f"convers/{cd[1]}")

                message_path = f"photos/{message.photo[-1].file_id}.jpg"
                file = bot.get_file(message.photo[-1].file_id)
                downloaded_file = bot.download_file(file.file_path)
                with open(message_path, 'wb') as new_file:
                    new_file.write(downloaded_file)
                time.sleep(1)
                content = ai.generate_content_from_image(message_path, caption)
                content = content.replace("**", "")

                balance -= 1
                UserDB(user_id=chat_id, balance=balance).update()

                pick(f"convers/{cd[1]}", ai.history)
                try:
                    bot.delete_message(chat_id, wait_msg.message_id)
                except:
                    pass
                bot.send_message(chat_id, content)
            else:
                bot.send_message(chat_id, texts.Content.no_balance[lng])


@bot.message_handler(content_types=["document",
                                    "video",
                                    "audio",
                                    "voice",
                                    "video_note",
                                    "location",
                                    "contact",
                                    "sticker"])
def documents(message):
    chat_id = message.chat.id
    chat_type = message.chat.type
    lng = Language(chat_id).get()

    cd = Stage(chat_id).get().split("||")

    if chat_type == 'private':
        if cd[0] == "conversation":

            bot.send_message(chat_id, texts.Content.not_supported[lng])


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id

    def dm():
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass

    cd = call.data.split("||")
    if cd[0] == "language_selection_stage":
        stg.language_selection_stage(chat_id)
        dm()
    elif cd[0] == "new_lang":
        Language(chat_id).set(cd[1])
        lng = Language(chat_id).get()
        k_b_m = kbm(resize_keyboard=True)
        k_b_m.add(kbm_btn(texts.Button.new_conversation[lng]), row_width=1)
        k_b_m.add(kbm_btn(texts.Button.balance[lng]), kbm_btn(texts.Button.settings[lng]), row_width=2)
        bot.send_message(chat_id, texts.Content.start_message2[lng], reply_markup=k_b_m)
        dm()


def main_thread():
    while True:
        try:
            print("STARTED")
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(15)
        except telebot.apihelper.ApiTelegramException as e:
            print(e)


threading.Thread(target=main_thread, daemon=True).start()


while True:
    try:
        time.sleep(120)
    except KeyboardInterrupt:
        exit()

