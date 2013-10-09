#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from markov import Markov, ChainTermination
from random import choice

class TextGenerator(Markov):
    """Pseudo-random text generator."""

    def parse(self, text):
        """Parses text and splits it into matching pairs."""
        words = text.split(' ')
        matches = {}
        try:
            start = (words[0], words[1])
        except IndexError:
            return {}
        self.starts.add(start)
        try:
            matches[start] = [(words[1], words[2])]
        except IndexError:
            matches[start] = []
        for i in range(1, len(words)-1):
            two = (words[i], words[i+1])
            if two not in matches:
                matches[two] = []
            try:
                matches[two].append(words[i+2])
            except IndexError:
                matches[two].append(None)
        return matches
                
    def digest(self, matches):
        """Takes table of matching words and adds to the pool of states."""
        for two in matches:
            self.add_state(two)
            for match in matches[two]:
                self.add_state((two[1], match))
                self.set_prob(two, (two[1], match))
    
    def learn(self, text):
        """This is the one which is called externally."""
        matches = self.parse(text)
#        print(matches)
        self.digest(matches)
    
    def get_text(self, count=100, terminate=True):
        if not self.states.keys():
            print('no states')
            return None
        text = []
        try:
            self.step(choose=True, start=True)
        except ChainTermination:
            return ' '.join(text)
        for i in range(count):
            text.append(self.cur_state)
            try:
                self.step(choose=True)
            except ChainTermination:
#                print('step raised Term')
                return ' '.join(text)
#                self.step(choose=True, start=True)
#        print('got to end of count')
        return ' '.join(text)
    
def test():
    from os.path import expanduser
    with open(expanduser('~/bin/aiw')) as f:
        t = f.read()
    lines = t.splitlines()
    x = TextGenerator()
    for line in lines:
#        print('LINE')
#        print(line)
        x.learn(line)
#    print(x.states)
    return x.get_text(400)
    
if __name__ == '__main__':
    print(test())
