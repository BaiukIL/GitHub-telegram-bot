import github
from collections import defaultdict
import operator
import cachetools
import logging


# activate debug logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


@cachetools.cached(cache=cachetools.TTLCache(maxsize=100, ttl=60))
def get_statistic():
    """
    get statistic from search() and process output
    results updates if it's passed more than minute since previous call
    """
    output = str()

    search()

    sorted_languages = sorted(languages.items(), key=operator.itemgetter(1))
    sorted_languages.reverse()

    longest_word_letters_number = 0
    for language in languages:
        if len(str(language)) > longest_word_letters_number:
            longest_word_letters_number = len(str(language))
    longest_number = len(str(sorted_languages[0][1]))
    total_languages_count = sum(languages.values())

    for language in sorted_languages:
        language_name, language_count = language[0], language[1]
        percent = int(language_count / total_languages_count * 100)
        if percent == 0:
            percent = '< 1'
        first_space = ' ' * (longest_word_letters_number - len(language_name) + 4)
        second_space = ' ' * (longest_number - len(str(language_count)) + 2)
        output += '`{}{}{}{}{}%`\n'.format(language_name, first_space, language_count, second_space, percent)

    logging.info(output)
    return output


def search():
    """function searches repositories' languages"""
    global step, languages
    try:
        while True:
            repo = repositories[step]
            step += 1
            if repo.language is None:
                continue
            languages[repo.language] += 1
            logging.info('{} {}'.format(repo.language, repo.name))
    except github.GithubException:
        return


# these variables are global, for it must changes after search() work
# query='stars:>1' - search repo with more than 1 star, start from most-stared
repositories = github.Github().search_repositories(query='stars:>1')
# dict: language: str -> count_language_pull_in_number: int
languages = defaultdict(int)
# number of last visited repo
step = 0
