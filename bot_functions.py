# python-telegram-bot to work with Telegram api
from telegram import (
    # core
    Update,
)
from telegram.ext import (
    # core
    ContextTypes,
)
from telegram.error import (
    # to make an exception to reduce logging pollution
    BadRequest,
)
# get and set a time
from datetime import (
    datetime,
)

# for easier time management in a 'job_queue'
from options import (
    job_time_first,
    job_time_second,
)
# for easier text management
from text_responses import (
    birthday_set_keyboard_text,
    birthday_set_keyboard_final_text,
    celebrate,
    remove_fail,
    remove_success,
    sechude_active,
    write_success,
)
# for easier keyboard management
from bot_keyboards import (
    birthday_set_keyboard_months,
    birthday_set_keyboard_apr_may_jun,
    birthday_set_keyboard_jan_feb_mar,
    birthday_set_keyboard_jul_aug_sep,
    birthday_set_keyboard_oct_nov_dec,
    birthday_set_keyboard_days,
    birthday_set_keyboard_day_1_to_6,
    birthday_set_keyboard_day_7_to_12,
    birthday_set_keyboard_day_13_to_18,
    birthday_set_keyboard_day_19_to_24,
    birthday_set_keyboard_day_25_to_31,
    birthday_set_keyboard_final,
)
# for syncing the callback names with keyboard
from button_manager import (
    ControlButton,
)
# to access a session
from session_functions import (
    session_start,
    session_user_data_extract,
    session_user_data_write,
)
# to access a database
from database_functions import (
    database_remove,
    database_search_by_date,
    database_search_by_name,
    database_write,
)


async def birthday_loop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiates the bot's checking cycle with 'jobQueue'.

    Returns nothing.
    Raises no errors.
    """
    # message destination is a chat where it was used
    target_chat = update.effective_message.chat_id

    # check if the database already exist
    try:
        # 'r' == 'read'
        open('databases/' + str(target_chat) + '.txt', 'r').close()

    except FileNotFoundError:
        # creates a new text file with the name equal to the id of the chat
        # 'w' == 'overwrite'
        open('databases/' + str(target_chat) + '.txt', 'w').close()

    # tell the bot to run a job repeatedly
    context.job_queue.run_daily(
        # which job
        callback=birthday_yell,
        # at what time
        time=job_time_first(),
        # where the text will be sent
        chat_id=target_chat,
        # to distinguish jobs from one another
        name='Morning Check',
    )

    # 'run_daily' allows to run only a single job
    # at a time so just invoke it a second time
    context.job_queue.run_daily(
        # which job
        callback=birthday_yell,
        # at what time
        time=job_time_second(),
        # where the text will be sent
        chat_id=target_chat,
        # to distinguish jobs from one another
        name='Evening Check',
    )

    # send a reply message to the user
    await context.bot.send_message(
        chat_id=target_chat,
        text=sechude_active(),
    )


async def birthday_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set a birthday date.

    Takes no arguments.

    If the user is already present in a database,
    tell the user their birthday date.

    If there's no such user,
    bring up a message with a keyboard for
    the user to enter their birthday date.

    Returns nothing.
    Raises no errors.
    """
    keyboard = birthday_set_keyboard_months()
    message = birthday_set_keyboard_text()
    username = update.effective_user.username
    target_chat = update.effective_chat.id

    session_start(username)

    birthday_date = database_search_by_name(username, target_chat)
    if birthday_date:
        message = birthday_date
        keyboard = None

    await update.message.reply_text(
        text=message,
        reply_markup=keyboard
    )


async def birthday_yell(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Celebrate a birth day!

    Takes no arguments.

    Checks for someone's birthday today,
    sends a message if someone has a birthday,
    does nothing if nobody has a birthday this day.

    Returns nothing.
    Raises no errors.
    """
    target_chat = context.job.chat_id
    today = datetime.now()
    # '%d.%m' == 'DD.MM' == 'Day.Month', ex.: '31.12'
    today_day_and_month = today.strftime('%d.%m')

    # investigating a strange error like of
    # 'Text should be a string, got NoneType'
    try:
        birthday_people = database_search_by_date(
            today_day_and_month,
            target_chat,
        )
    except AttributeError:
        pass

    if birthday_people:
        await context.bot.send_message(
            chat_id=target_chat,
            text=celebrate(birthday_people),
        )
        # a feature requested
        if today == '12.12':
            for _ in range(9):
                await context.bot.send_message(
                    chat_id=target_chat,
                    text=celebrate(birthday_people),
                )


async def birthday_rm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Remove a birthday.

    Takes no arguments.

    Take a USER who called this function
    and check if they are in a database.

    If they are, remove their line from
    the database and aknowledge them of this.

    If they aren't, aknowledge them of this.

    Returns nothing.
    Raises no errors.
    """
    target_chat = update.effective_chat.id
    # there are two states of this message:
    # 0: the code failed
    # 1: the code succeed
    # having the initial value set as one of these states
    # allows to make one less check on the function's state
    message = remove_fail()

    username = update.effective_user.username
    target_line = database_search_by_name(username, target_chat)

    if target_line:
        database_remove(target_line, target_chat)
        message = remove_success()

    await context.bot.send_message(
        # message destination is a chat where it was used
        chat_id=target_chat,
        text=message,
    )


async def birthday_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Input to set a birthday date.

    Takes no arguments.

    Allows the user to change their birthday date
    by pressing buttons on the inline keyboard.

    If the operation was done successfully,
    tell the user that the operation was successful.

    If the operation wasn't done successfully,
    remove this bot's message.

    Returns nothing.
    Raises no errors.
    """
    # collection of keyboards to choose from
    keyboard_select_month = (
        birthday_set_keyboard_jan_feb_mar(),
        birthday_set_keyboard_apr_may_jun(),
        birthday_set_keyboard_jul_aug_sep(),
        birthday_set_keyboard_oct_nov_dec(),
    )
    keyboard_select_day = (
        birthday_set_keyboard_day_1_to_6(),
        birthday_set_keyboard_day_7_to_12(),
        birthday_set_keyboard_day_13_to_18(),
        birthday_set_keyboard_day_19_to_24(),
        birthday_set_keyboard_day_25_to_31(),
    )
    username = update.effective_user.username
    # default values to fall back to
    keyboard = birthday_set_keyboard_months()
    message = birthday_set_keyboard_text()

    # create, get and extract the user's input
    query = update.callback_query
    await query.answer()
    data = query.data

    session_data = session_user_data_extract(username)
    step = int(session_data[0])

    # there's so much 'elif's due to hard logic of this function
    if data == ControlButton.back()[1]:
        if step > 2:
            step = 2
            keyboard = birthday_set_keyboard_days()
        else:
            step = 0

    # operation is done successfully
    elif data == ControlButton.finish()[1]:
        message = write_success()
        keyboard = None
        target_chat = update.effective_chat.id
        database_write(username, target_chat)

    # operation is cancelled
    elif data == ControlButton.abort()[1]:
        await query.delete_message()

    # don't get confused: those conditions apply
    # AFTER the button press
    elif step == 0:
        index = int(data)
        keyboard = keyboard_select_month[index]
        step += 1

    elif step == 1:
        # month
        # '\n' == 'new line'
        session_data[2] = data + '\n'
        keyboard = birthday_set_keyboard_days()
        step += 1

    elif step == 2:
        index = int(data)
        keyboard = keyboard_select_day[index]
        step += 1

    elif step == 3:
        # day
        # '\n' == 'new line'
        session_data[1] = data + '\n'
        message = birthday_set_keyboard_final_text(username, session_data)
        keyboard = birthday_set_keyboard_final()

    # step
    # '\n' == 'new line'
    session_data[0] = str(step) + '\n'
    session_user_data_write(username, session_data)

    # try-except to suppress an expexted error message
    # from flooding the logs
    try:
        await query.edit_message_text(
            text=message,
            reply_markup=keyboard,
        )
    # when the message is deleted before editing
    except BadRequest:
        pass
