import github
import logging
import multiprocessing
import time
import my_repo

import operator
from typing import Dict

# exception caught in search function
from requests.exceptions import ConnectionError


# activate debug logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)


def get_statistic():
    """Gets statistic from search() and processes output
    results updates if it's passed more than minute since previous call"""
    output = ''

    sorted_languages = sorted(languages.items(), key=operator.itemgetter(1), reverse=True)

    longest_word_length = 0
    for language in languages:
        if len(str(language)) > longest_word_length:
            longest_word_length = len(str(language))
    longest_number_length = len(str(sorted_languages[0][1]))
    total_languages_count = sum(languages.values())

    for language in sorted_languages:
        language_name, language_count = language
        percent = language_count * 100 // total_languages_count
        if percent == 0:
            percent = '< 1'
        first_space = ' ' * (longest_word_length - len(language_name) + 4)
        second_space = ' ' * (longest_number_length - len(str(language_count)) + 2)
        output += f'`{language_name}{first_space}{language_count}{second_space}{percent}%`\n'

    logging.info(output)
    return output


def get_random_repo():
    return last_repo[0].html_url


def generate_query(last_repository):
    return f'stars:<{last_repository.stargazers_count}'


def search():
    """searches languages"""

    global repositories
    while True:
        # number of last visited repo
        step = 0
        try:
            while True:
                repo = repositories[step]
                step += 1
                if repo.language is not None:
                    if repo.language not in languages:
                        languages[repo.language] = 0
                    languages[repo.language] += 1
                    last_repo[0] = repo
                    logging.info(f'stars: {repo.stargazers_count} {repo.language} {repo.name}')
        except github.GithubException:
            # github searching capacity is limited with 300 rep/min
            # if excess occurs, github.GithubException is thrown
            logging.info('GithubException occurred')
            time.sleep(60)
        except IndexError:
            # len(repositories) is about 1000
            # if step > 1000 (i.e. if IndexError occurred) then change query
            logging.info('IndexError occurred - change query')
            repositories = github.Github(login_or_token=my_repo.user, password=my_repo.password).search_repositories(
                query=generate_query(repositories[step - 1]))
        # there are some problems occur when joining multiprocessing and github api (ConnectionError)
        # I suppose it is connected with github api search limits
        # Anyway, it does not hinder program work, so just log this exception
        except ConnectionError as error:
            logging.info(f'ConnectionError occurred: {str(error)}')


def start_search():
    # create multiprocess
    continuous_search = multiprocessing.Process(target=search)
    # start multiprocess
    continuous_search.start()
    continuous_search.join()


# these variables are global, for they change during search() work and are available from any function
repositories = github.Github().search_repositories(query='stars:>1')
# dict of language -> count_language_pull_in_number
languages: Dict[str, int] = multiprocessing.Manager().dict()
# list of one element (if we use Manager().Value instead,
# we have to specify c_type field, but github.Repository in not instance of ctypes)
last_repo = multiprocessing.Manager().list(sequence=[repositories[0]])
