#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import sqrt

def primes(n):
    '''Return all the primes up to n.'''
    primes = [2]
    for i in range(3, n+1, 2):
        divisible = False
        for j in primes:
            if j > sqrt(i):
                break
            elif i % j == 0:
                divisible = True
                break
        if not divisible:
            primes.append(i)
            yield i

if __name__ == '__main__':
    from sys import argv
    print(list(primes(int(argv[1]))))
