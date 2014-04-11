#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import locale
from datetime import datetime

from redis import Redis
import requests
from requests_oauthlib import OAuth1

import config as CONF


class NoticeStore(Redis):

    def find_new_notices(self, notices):
        return [notice for notice in notices
                if not self.exists(notice['id']) or self.check_update(notice)]

    def save_new_notice(self, notice):
        self.set(notice['id'], int(notice['updated'].timestamp()))

    def check_update(self, notice):
        return int(self.get(notice['id'])) < int(notice['updated'].timestamp())


def get_bkk_info():
    rs = requests.get(CONF.bkk_api_url)
    return rs.json()


def parse_notice(notice):
    return {
        'id': notice['id'],
        'from': (datetime.fromtimestamp(int(notice['kezd']['epoch']))
                 if notice['kezd'] else None),
        'until': (datetime.fromtimestamp(int(notice['vege']['epoch']))
                  if notice['vege'] else None),
        'lines': sum([i['jaratok'] for i in notice['jaratokByFajta']], []),
        'description': notice['elnevezes'],
        'updated': datetime.fromtimestamp(int(notice['modositva']['epoch'])),
    }


def generate_tweet(notice):
    tweet_template = '{lines}: {description} {from} - {until}'
    time_template = '%b. %d. %H:%M'

    fields = {
        'lines': ', '.join(notice['lines']),
        'description': notice['description'],
        'from': notice['from'].strftime(time_template),
        'until': (notice['until'].strftime(time_template)
                  if notice['until'] else '???'),
    }

    return trim_tweet(tweet_template.format(**fields))


def trim_tweet(tweet):
    if len(tweet) > 140:
        return tweet[:137] + "..."
    else:
        return tweet


def post_tweet(tweet):
    if 'közlemény' in tweet:  # FIXME
        return

    auth = OAuth1(CONF.twitter_app_key, CONF.twitter_app_secret,
                  CONF.twitter_user_key, CONF.twitter_user_secret)

    rs = requests.post('https://api.twitter.com/1.1/statuses/update.json',
                      auth=auth, data={'status': tweet})

    return rs.json()


def main():
    locale.setlocale(locale.LC_TIME, CONF.date_locale)
    notice_store = NoticeStore(**CONF.redis_config)

    new_notices = notice_store.find_new_notices(
        sum([[parse_notice(notice) for notice in notice_set]
             for notice_set in get_bkk_info().values()], [])
    )

    for notice in new_notices:
        post_tweet(generate_tweet(notice))
        notice_store.save_new_notice(notice)

if __name__ == '__main__':
    main()
