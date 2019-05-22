"""This bot gets info about most stared repositories' languages"""


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
import logging
import github_search
import my_token


# activate debug logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(bot, update):
    text = "I'm a bot which makes up languages pull-in frequency statistic based on GitHub most stared repositories.\n"\
           "Use /help to get know more about me."
    bot.send_message(chat_id=update.message.chat_id, text=text)


def show_help(bot, update):
    text = "You can ask me for languages pull-in frequency statistic by calling:\n/getstatistic\n" \
           "Also I can send it inline: just name me and choose `send statistic`.\n" \
           "/randomrepo returns random repository (note: it updates in a minute)."
    bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode="Markdown")


def get_statistic(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=github_search.get_statistic(), parse_mode="Markdown")


def get_random_repo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=github_search.get_random_repo())


def inline_statistic(bot, update):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query,
            title='send statistic',
            input_message_content=InputTextMessageContent(github_search.get_statistic(), parse_mode="Markdown")
        )
    )
    bot.answer_inline_query(update.inline_query.id, results)


def unknown_command(bot, update):
    text = "I don't understand this command, but I do understand some other ones.\n" \
           "Use /help to get know more about me."
    bot.send_message(chat_id=update.message.chat_id, text=text)


def unknown_message(bot, update):
    text = "I don't recognize natural language, but I understand a few commands which you can find at:\n/help\n"
    bot.send_message(chat_id=update.message.chat_id, text=text)


if __name__ == '__main__':
    if 'TOKEN' not in dir(my_token):
        logging.error(
            'No token found. Set it in my_token module as \n\tTOKEN = /* your telegram bot token in str format */')
        exit()
    updater = Updater(token=my_token.TOKEN)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    help_handler = CommandHandler('help', show_help)
    dispatcher.add_handler(help_handler)

    get_random_repo_handler = CommandHandler('randomrepo', get_random_repo)
    dispatcher.add_handler(get_random_repo_handler)

    get_statistic_handler = CommandHandler('getstatistic', get_statistic)
    dispatcher.add_handler(get_statistic_handler)

    inline_statistic_handler = InlineQueryHandler(inline_statistic)
    dispatcher.add_handler(inline_statistic_handler)

    unknown_command_handler = MessageHandler(Filters.command, unknown_command)
    dispatcher.add_handler(unknown_command_handler)

    unknown_message_handler = MessageHandler(Filters.text, unknown_message)
    dispatcher.add_handler(unknown_message_handler)

    continuous_search = github_search.multiprocessing.Process(target=github_search.search)
    updater.start_polling()

    # start Process of searching repo-s
    github_search.search()
