# - *- coding: utf- 8 - *-
import copy
import logging
import random
from functools import wraps

import telegram
from telegram.ext import Updater, CommandHandler
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)


rules_text = "<b>Правила Секретного Санты:</b> \n" \
             + "<i>1. Санта Секретный - никому не говори, кто тебе выпал!</i>\n" \
             + "<i>2. Подарок должен быть не дороже 200 грн.</i>\n" \
             + "<i>3. Спрячь свой подарок в красный мешок (найдешь его под елкой)</i>.\n" \
             + "<i>4. Санта придет к тебе только после боя курантов</i>.\n"


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(*args, **kwargs):
        bot, update = args
        bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING)
        return func(bot, update, **kwargs)

    return command_func


@send_typing_action
def start(bot, update):
    if update.message.chat.type == "group":
        bot.send_message(chat_id=update.message.chat_id,
                         text="Я тайный помощник Санты. Для того , чтобы магия произошла, "
                              "кликни сюда ->  @" + str(bot.get_me()['username']) + " и нажми старт!")
        bot.send_message(chat_id=update.message.chat_id, text=rules_text,
                         parse_mode=telegram.ParseMode.HTML)

    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Круто, мы не забудем о тебе. Переходи в общий чат и регистрируйся.")


@send_typing_action
def rules(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=rules_text,
                     parse_mode=telegram.ParseMode.HTML)


people = []
pairs = dict()


@send_typing_action
def register(bot, update):
    u = User(update.effective_user.id, update.effective_user.username, update.effective_user.first_name,
             update.effective_user.last_name)
    if u not in people:
        # print(update.effective_user.id)
        # print(update.effective_user.username)
        # print(update.effective_user.first_name)
        # print(update.effective_user.last_name)
        people.append(u)
        bot.send_message(update.effective_user.id, "Ты добавлен в список Секретного Санты!")
    else:
        bot.send_message(update.effective_user.id, "Ты уже добавлен в мой список. Жди когда волшебство произойдет")


def info(bot, update):
    for p in people:
        print(p)
        print(p.last_name)


class User:
    def __init__(self, user_id, username, first_name, last_name):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    def __hash__(self):
        return hash(self.user_id)

    def __eq__(self, other):
        return self.user_id == other.user_id


def secret_santa(names):
    my_list = names
    choose = copy.copy(my_list)
    result = []
    for i in my_list:
        names = copy.copy(my_list)
        names.pop(names.index(i))
        chosen = random.choice(list(set(choose) & (set(names))))
        result.append((i, chosen))
        choose.pop(choose.index(chosen))
    return result


def magic(bot, update):
    try:
        if update.effective_user.username == "Yarbezl":
            print("Length " + str(len(people)))
            if len(people) == bot.get_chat_members_count(update.message.chat.id) - 1:
                for i in secret_santa(people):
                    if i[1].username is not None:
                        bot.send_message(i[0].user_id,
                                         "Ты должен подготовить подарок для @" + str(i[1].username).encode('utf-8'))
                    else:
                        bot.send_message(i[0].user_id,
                                         "Ты должен подготовить подарок для " + str(i[1].first_name).encode('utf-8'))

                print("Gifts almost here")
                bot.send_message(chat_id=update.message.chat_id,
                                 text="Супер! Каждый получил своего тайного санту! Остаеться ждать Нового Года!")
            else:
                print("Some later, now it's ")
                bot.send_message(update.effective_user.id, "Some later, now it's " + str(len(people)))
        else:
            print("You are not Santa's helper, I'm sorry ")
            bot.send_message(update.effective_user.id, "You are not Santa's helper, I'm sorry ")
    except Exception as inst:
        print(inst)
        print(people)
        print(secret_santa(people))



def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print(error)
        # handle malformed requests - read more below!
    except TimedOut:
        print(error)
        # handle slow connection problems
    except NetworkError:
        print(error)
        # handle other connection problems
    except ChatMigrated as e:
        print(error)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Create Updater object and attach dispatcher to it
    updater = Updater(token='673782777:AAEmRHnnJVe5npGALLSUquytHaRlQ-TfPh8')
    dispatcher = updater.dispatcher
    print("Bot started")

    # Add command handler to dispatcher
    start_handler = CommandHandler('start', start)
    register_handler = CommandHandler('register', register)
    info_handler = CommandHandler('info', info)
    rules_handler = CommandHandler('rules', rules)
    magic_handler = CommandHandler('magic', magic)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(register_handler)
    dispatcher.add_handler(info_handler)
    dispatcher.add_handler(rules_handler)
    dispatcher.add_handler(magic_handler)
    dispatcher.add_error_handler(error_callback)

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
