#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Playing around with Markov chains"""

from random import random, choice
from pickle import dump, load

class StateError(Exception):
    pass

class ProbabilityError(Exception):
    pass

class ChainTermination(Exception):
    pass


class Markov:
    """A base Markov chain class."""
    
    def set_prob(self, now, nxt, prob=0):
        if (now not in self.states) or (nxt not in self.states):
            raise StateError("State does not exist")
        if (type(prob) not in (float, int)) or (prob > 100):
            raise ProbabilityError("Invalid entry for probability")
        if prob > 1:
            prob /= 100
        if prob + sum(self.states[now].values()) > 1:
            raise ProbabilityError("Total probability would be greater than one")
        
        self.states[now][nxt] = prob
    
    def add_state(self, state, start=False):
        if start:
            self.starts.add(state[0])
        if state not in self.states:
            self.states[state] = {}
    
    def set_state(self, state=None):
        # NB: Does not work with new self.cur_state
        if state is None:
            state = choice(list(self.states.keys()))
        elif state not in self.states:
            raise StateError("State does not exist")
        self.cur_state = state
            
    def get_state(self):
        return self.cur_state
    
    def save(self, file=None):
        file = file or self.save_file
        with open(file, 'wb') as f:
            dump(self.states, f)
    
    def load(self, file=None):
        file = file or self.save_file
        try:
            with open(file, 'rb') as f:
                self.states = load(f)
        except (IOError, ValueError, EOFError):
            # Save file does not exist or is corrupted
            return
    
    def step(self, choose=False, start=False):
        if start:
            # This is the first word of the text; choose from a list of first words.
            try:
#                print(self.starts)
                self.cur_two = choice(list(self.starts))
            except IndexError:
                raise ChainTermination
        elif choose:
            # Choose a link from the list, each word having equal probability.
            try:
                # Sometimes (namely at the start), self.cur_two is a tuple of two words;
                # other times, it is a tuple of a word and a tuple of two words. Why?
                # This solution is hacky as shit
                if isinstance(self.cur_two[1], tuple):
                    self.cur_two = self.cur_two[1]
                self.cur_two = choice(list(self.states[self.cur_two].keys()))
#                print(self.cur_two)
            except IndexError:
#                print(self.cur_two)
#                print(self.states[self.cur_two])
                raise ChainTermination
        else:
            # Choose a link based on the set probabilities.
            # NB: Does not work with new self.cur_state
            nxts = []       # potential next words
            probs = []      # probability of each word being chosen
            for state in self.states[self.cur_state]:
                nxts.append(state)
                probs.append(self.states[self.cur_state][state])
            rand = random()
            run_tot = 0
            for i in range(len(probs)):
                run_tot += probs[i]
                if rand < run_tot:
                    self.cur_state = nxts[i]
                    if self.cur_state is None:  # None means end of chain
                        raise ChainTermination
                    else:
                        return
            raise ChainTermination("Chain terminated") #after %s" % self.cur_state)

    @property
    def cur_state(self):
        return self.cur_two[0]
            
    def __init__(self, save_file=None):
        self.save_file = save_file
        self.states = {}
        self.starts = set()
        self.cur_two = None

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
    return x.get_text(200)
    
if __name__ == '__main__':
    print(test())
