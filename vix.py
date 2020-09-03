#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import asyncio
from operator import gt, lt
from json import load, dump, JSONDecodeError
from datetime import datetime
from os import mkdir
from os.path import join, expanduser, dirname, exists

import telepot
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, per_application, per_chat_id, create_open
import requests
import bs4
import pandas

CONF_DIR = join(expanduser('~'), '.config', 'vix_telegram')
if not exists(CONF_DIR):
    mkdir(CONF_DIR)

STATE_PATH = join(CONF_DIR, 'state.json')

class Notification:

    def __init__(self, n_id, _type, benchmark, is_live=True):
        self.n_id = n_id
        self._type = _type
        self.benchmark = benchmark
        self.is_live = is_live

        if type == 'outside':
            self.notify_if = 'either'

        self.check_funcs = {
            'above': self.check_above,
            'below': self.check_below,
        }

    def check_above(self, v, benchmark=None):
        benchmark = benchmark or self.benchmark
        if v > benchmark:
            return f'above {benchmark} ({v})'
        else:
            return None

    def check_below(self, v, benchmark=None):
        benchmark = benchmark or self.benchmark
        if v < self.benchmark:
            return f'below {benchmark} ({v})'
        else:
            return None

    def check(self, v):
        match = self.check_funcs[self._type](v)
        if match is not None:
            if self.is_live:
                self.is_live = False
                return match
            else:
                if not self.is_live:
                    self.is_live = True
    
    def to_dict(self):
        return {
            'n_id': self.n_id,
            '_type': self._type,
            'benchmark': self.benchmark
        }

class Handler:

    """Handles data and loads and saves state, including about most recent data
    received and active notifications."""

    def __init__(self, state_path=None, data_provider=None):

        self.data_provider = data_provider or VIXData()
        self.state_path = state_path
        self.n_id = 0
        if state_path:
            self.load_state()

    def load_state(self, state_path=None):
        state_path = state_path or self.state_path
        try:
            with open(state_path) as f:
                state = load(f)
        except (FileNotFoundError, JSONDecodeError):
            state = self.init_state()
        self.historical_data = state['historical_data']
        self.last_value = state['last_value']
        self.last_value_timestamp = state['last_value_timestamp']
        self.notifications = [Notification(*n) for n in state['notifications']]
        self.n_id = state['n_id']

    def save_state(self, state_path=None):
        state_path = state_path or self.state_path
        state = {
            'last_value': self.last_value,
            'last_value_timestamp': self.last_value_timestamp,
            'historical_data': self.historical_data,
            'notifications': [n.to_dict() for n in self.notifications],
            'n_id': self.n_id
        }
        with open(state_path, 'w') as f:
            dump(state, f)

    def init_state(self):
        return {
            'last_value': None,
            'last_value_timestamp': None,
            'historical_data': {
                'upper_bol_20': None,
                'lower_bol_20': None,
                'moving_avg_20': None,
                'timestamp': None
            },
            'notifications': [],
            'n_id': 0
        }

    def get_historical_data(self):
        data = self.data_provider.get_historical_data()
        latest = data.iloc[-1]
        self.historical_data = {
            'upper_bol_20': latest['Upper Bol20 (Close)'],
            'lower_bol_20': latest['Lower Bol20 (Close)'],
            'moving_avg_20': latest['MA20 (Close)'],
            'timestamp': datetime.today().timestamp()
        }

    def get_current_value(self):
        self.last_value = self.data_provider.get_current_value()
        self.last_value_timestamp = datetime.today().timestamp()

    def new_notification(self, _type, benchmark):
        n = Notification(self.n_id, _type, benchmark)
        self.n_id += 1
        self.notifications.append(n)
        return n

    def check_notifications(self):
        results = []
        for n in self.notifications:
            r = n.check(self.last_value)
            if r is not None:
                results.append((n.n_id, r))
        return results
    
    def update_historical_data(self,override=False):
        try:
            last_date = datetime.fromtimestamp(self.historical_data['timestamp']).date()
            today = datetime.today().date()
            to_update = today > last_date
        except TypeError:
            to_update = True
        if to_update or override:
            self.get_historical_data()
    
    def update_last_value(self):
        self.get_current_value()
    
    def update_date(self, override_historical=False):
        self.update_historical_data(override_historical)
        self.update_last_value()
    
class VIXData:

    """Class for fetching, manipulating and returning VIX data."""

    HIST_URL = 'http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vixcurrent.csv'
    CURR_URL = 'http://www.cboe.com/vix'

    def get_historical_data(self):
        data = pandas.read_csv(self.HIST_URL, skiprows=1, index_col='Date')
        data['MA20 (Close)'] = data['VIX Close'].rolling(20).mean()
        data['STD20 (Close)'] = data['VIX Close'].rolling(20).std()
        data['Upper Bol20 (Close)'] = data['MA20 (Close)'] + data['STD20 (Close)']
        data['Lower Bol20 (Close)'] = data['MA20 (Close)'] - data['STD20 (Close)']
        self.historical_data = data
        return data
    
    def get_current_value(self):
        r = requests.get(self.CURR_URL)
        bs = bs4.BeautifulSoup(r.content, features='lxml')
        return float(bs.find('div', {'class': 'left-c'}).find('div', {'class': 'col2'}).text)
    
    def how_long(self, level, above=False):
        """Returns a list of tuples, containing:
        0:  date on which VIX closed below level; and
        1:  number of days for which VIX continued to close below level."""
        results = []
        crossed_level = False
        for_how_long = 0
        current_i = None
        oper = gt if above else lt
        for i in self.historical_data.index:
            c = self.historical_data['VIX Close'].loc[i]
            if oper(c, level) and not crossed_level:
                current_i = i
                crossed_level = True
                for_how_long = 1
            elif oper(c, level) and crossed_level:
                for_how_long += 1
            elif oper(level, c) and crossed_level:
                crossed_level = False
                results.append((current_i, for_how_long))
                for_how_long = 0
        return results

    def max_streak(self, level, above=False):
        return max(self.how_long(level, above), key=lambda r: r[1])

def test():
    s_path = 'vix_test.json'
    v = VIXData()
    h = Handler(v, s_path)
    n1 = h.new_notification('below', 11)
    n2 = h.new_notification('above', 12)
    h.get_current_value()
    print(h.last_value)
    h.get_historical_data()
    print(h.historical_data)
    print(h.check_notifications())
    print(h.check_notifications())
    print(h.check_notifications())
    h.save_state()
    h.load_state()
    print(h.historical_data)
    h.update_data()
"""
if __name__ == '__main__':
    test()
"""

async def send_foo(bot, _id):
    while 1:
        await bot.sendMessage(_id, 'foo')
        await asyncio.sleep(5)
        

class VIXBot:

    def __init__(self, confdir):

        self.confdir = confdir

        try:
            with open(join(self.confdir, 'bot_token')) as f:
                self.bot_token = f.read().strip()
            with open(join(self.confdir,'chat_id')) as f:
                self.valid_id = int(f.read())
        except FileNotFoundError:
            print('Token and / or valid ID file not found.')
            return
            
        state_path = join(confdir, 'state.json')
        self.data_handler = Handler(state_path)
                    
        self.run()
    
    async def handle_globally(self, content_type, msg):
        if content_type == 'text':
            print('Text is: {}'.format(msg['text']))
            await self.bot.sendMessage(self.valid_id, 'bar')
        else:
            self.handle_other(msg)
    
    def handle_other(self, msg):
        pass
    
    async def handle(self, msg):
    
        content_type, msg_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
        print('Got message of type {} from ID {}'.format(content_type, chat_id))
        
        if chat_id != self.valid_id:
            print('ID {} not valid.'.format(chat_id))
            self.bot.sendMessage(self.valid_id,
                'Unauthorised message {} from ID {}.'.format(chat_id, chat_id))
            return
        else:
            await self.handle_globally(content_type, msg)
    
    def run(self):
        
        self.bot = telepot.aio.Bot(self.bot_token)
        loop = asyncio.get_event_loop()
        loop.create_task(MessageLoop(self.bot, self.handle).run_forever())
        loop.create_task(send_foo(self.bot, self.valid_id))

        print('Listening.')

        loop.run_forever()



if __name__ == '__main__':
    b = VIXBot(CONF_DIR)

