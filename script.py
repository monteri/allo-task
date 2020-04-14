import os
import sys
import django
import time
import string
from itertools import product

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tips.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

import asyncio
from requests_futures.sessions import FuturesSession

from orm.models import Tips

URL = 'https://allo.ua/ua/catalogsearch/ajax/suggest/?currentTheme=main&currentLocale=uk_UA'
FILE_NAME = 'query_string.txt'


def create_query_strings(file_name):
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r') as f:
                file = f.read()
                letter_list = file.split(',')
        except IOError:
            print("File not accessible")
    else:
        letters = string.ascii_lowercase
        letter_list = [x for x in letters]
        two_letter_list = product(letters, repeat=2)
        new_two_letter_list = []
        for two_letter in two_letter_list:
            new_two_letter_list.append(''.join(two_letter))
        three_letter_list = product(letters, repeat=3)
        new_three_letter_list = []
        for three_letter in three_letter_list:
            new_three_letter_list.append(''.join(three_letter))
        letter_list += new_two_letter_list + new_three_letter_list
        try:
            with open(file_name, 'w+') as f:
                f.write(','.join(letter_list))
        except IOError:
            print("File not accessible")
    return letter_list


def cut_existing(letters):
    last_tip = Tips.objects.all().last()
    index = letters.index(last_tip.key)
    new_letters = letters[index:]
    # Prevent duplicates
    Tips.objects.filter(key=last_tip.key).delete()
    return new_letters


def delete_tips():
    Tips.objects.all().delete()


async def write_db(key, value):
    Tips.objects.create(key=key, value=value)


async def main(argv=None):
    letter_list = create_query_strings(file_name=FILE_NAME)
    if argv:
        if argv[0] == 'p' or argv[0] == 'proceed':
            print('Proceeding...')
            letter_list = cut_existing(letter_list)
        elif argv[0] == 'n' or argv[0] == 'new':
            print('Clearing database...')
            delete_tips()
        else:
            print('Unknown parameter. ')
            print('Select argument:\n'
                  'p - proceed (from the last tip in the database)\n'
                  'n - new (clearing the database)')
            return
    else:
        print('Select argument:\n'
              'p - proceed (from the last tip in the database)\n'
              'n - new (clearing the database)')
        return
    with FuturesSession() as session:
        for letters in letter_list:
            t = time.perf_counter()
            while True:
                result = session.post(url=URL, data={'q': f'{letters}', 'isAjax': 1}).result()
                if result.status_code != 200:
                    pass
                else:
                    break
            print(result.json())
            if 'query' in result.json():
                for tip in result.json()['query']:
                    await write_db(key=letters, value=tip)
            t2 = time.perf_counter() - t
            print(f"Total time: {t2:0.2f} seconds")


if __name__ == '__main__':
    t = time.perf_counter()
    asyncio.run(main(sys.argv[1:]))
    t2 = time.perf_counter() - t
    print(f"Total time: {t2:0.2f} seconds")
