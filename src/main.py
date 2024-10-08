import telegram.ext as tl
import os
import dotenv
import logging

import bot_functions

BOT_OPTIONS: dict = {
    'app language': 'RUS',
    'time zone/offset': '+7',
    'time of instance(s) in hours': (
        8, 20,
    ),
}

# bot's key can now be accessed via 'getenv'
dotenv.load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)


if __name__ == '__main__':
    bot = tl.ApplicationBuilder().token(os.getenv('TOKEN')).build()

    # tell the bot how it should react to certain things
    birthday_set_handler = tl.CommandHandler(
        'ya_rodilsa', bot_functions.birthday_set)
    birthday_loop_handler = tl.CommandHandler(
        'start', bot_functions.birthday_start)
    birthday_remove_handler = tl.CommandHandler(
        'ya_oshibsa', bot_functions.birthday_remove)

    birthday_button_handler = tl.CallbackQueryHandler(
        bot_functions.birthday_button)

    # POSITION MATTERS: the bot will check them in order of appearence
    bot.add_handler(birthday_button_handler)
    bot.add_handler(birthday_set_handler)
    bot.add_handler(birthday_remove_handler)
    bot.add_handler(birthday_loop_handler)

    bot.run_polling(poll_interval=2.0)
