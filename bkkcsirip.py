#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import logging
from itertools import chain

import arrow
import requests
from redis import StrictRedis
from requests_oauthlib import OAuth1


BKK_API_URL = 'https://www.bkk.hu/apps/bkkinfo/lista-api.php'
TWITTER_UPDATE_URL = 'https://api.twitter.com/1.1/statuses/update.json'
REDIS = StrictRedis.from_url(os.getenv('BKKCSIRIP_REDIS_URL', 'redis://localhost:6379/0'))
TWEET_TEMPLATE = '{lines}: {body} {start} - {end}'
DATE_FORMAT = 'MMM. D. HH:MM'
DATE_LOCALE = os.getenv('BKKCSIRIP_DATE_LOCALE', 'hu_hu')

CHECK_INTERVAL = os.getenv('BKKCSIRIP_CHECK_INTERVAL', 60)


class Notice(object):

    def __init__(self, data):
        self.id = data['id']
        self.start = arrow.get(int(data['kezd']['epoch'])) if data['kezd'] else None
        self.end = arrow.get(int(data['vege']['epoch'])) if data['vege'] else None
        self.lines = chain.from_iterable(i['jaratok'] for i in data['jaratokByFajta'])
        self.body = data['elnevezes']
        self.timestamp = int(data['modositva']['epoch'])

    def save(self):
        REDIS.set(self.id, self.timestamp)

    @property
    def tweet(self):
        tweet = TWEET_TEMPLATE.format(
            lines=', '.join(self.lines),
            body=self.body,
            start=self.start.to('Europe/Budapest').format(DATE_FORMAT, locale=DATE_LOCALE),
            end=self.end.to('Europe/Budapest').format(DATE_FORMAT, locale=DATE_LOCALE) if self.end else '???',
        )
        return trim_tweet(tweet)

    @property
    def is_new(self):
        return not REDIS.exists(self.id)

    @property
    def is_updated(self):
        return int(REDIS.get(self.id)) < self.timestamp


def retrieve_notices():
    logging.info('Retrieving notices')
    response = requests.get(BKK_API_URL).json()
    raw_notices = response['active'] + response['soon'] + response['future']
    return (Notice(raw_notice) for raw_notice in raw_notices)


def trim_tweet(tweet):
    return tweet[:139] + "…" if len(tweet) > 140 else tweet


def post_tweet(tweet):
    if 'közlemény' in tweet:  # FIXME
        return

    auth = OAuth1(
        os.environ['BKKCSIRIP_TWITTER_APP_KEY'],
        os.environ['BKKCSIRIP_TWITTER_APP_SECRET'],
        os.environ['BKKCSIRIP_TWITTER_USER_KEY'],
        os.environ['BKKCSIRIP_TWITTER_USER_SECRET'],
    )

    logging.info('Posting tweet: %s', tweet)
    response = requests.post(TWITTER_UPDATE_URL, auth=auth, data={'status': tweet})
    return response.json()


def main():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(module)s.%(funcName)s - %(message)s')

    logging.info('Starting check loop')
    while True:
        for notice in retrieve_notices():
            if notice.is_new or notice.is_updated:
                try:
                    post_tweet(notice.tweet)
                except Exception as ex:
                    logging.exception('Exception while posting tweet')
                else:
                    notice.save()
        logging.info('Sleeping for %s seconds', CHECK_INTERVAL)
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
