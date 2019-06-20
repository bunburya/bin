#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Some helper functions for doing basic financial analysis.

from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import quandl

def quandl_get_close(ticker, start=None, end=None):
    return quandl.get('WIKI/{}.11'.format(ticker.upper()), start_date=start,
                        end_date=end)

def get_close_multi(tickers, start=None, end=None, data=None):
    if not data:
        data = [quandl_get_close(t, start=start, end=end) for t in tickers]
    stocks = pd.concat(data, axis=1)
    stocks.columns = tickers
    return stocks

def get_quandl_data(tickers, start=None, end=None):
    return OrderedDict([
        (t, quandl.get('WIKI/{}'.format(t.upper()), start_date=start,
                        end_date=end)) for t in tickers])


class UnweightedBasket:
    
    """Represents an unweighted basket of securities."""
    
    #TODO NEXT:  Code to use optimisation to find efficient frontier
    
    ADJ_CLOSE = 'Adj. Close'
    
    def __init__(self, data):
        """Takes a dict or OrderedDict of tickers and DataFrames 
        containing stock information (as returned by Quandl (for now))."""
        self.all_data = data
        self.tickers = data.keys()
        self.close_data = pd.concat([data[t][self.ADJ_CLOSE] for t in self.tickers], axis=1)
        self.close_data.columns = self.tickers
        self.log_returns = np.log(self.close_data/self.close_data.shift(1))
        self.figure = None
    
    def monte_carlo_weights(self, runs=5000):
        """Monte Carlo simulation that randomly generates stock
        weightings and calculates the returns, volatility and Sharpe
        ration for each.
        
        Code taken from https://www.udemy.com/python-for-finance-and-trading-algorithms
        """
        n_stocks = len(self.close_data.columns)
        all_weights = np.zeros((runs, n_stocks))
        ret_arr = np.zeros(runs)
        vol_arr = np.zeros(runs)
        sharpe_arr = np.zeros(runs)
        for i in range(runs):
            weights = np.array(np.random.random(n_stocks))
            weights /= np.sum(weights)
            all_weights[i,:] = weights
            ret_arr[i], vol_arr[i], sharpe_arr[i] = self.get_ret_vol_sr(weights)
    
        return {'weights': all_weights, 'returns': ret_arr, 
                'volatility': vol_arr, 'sharpe': sharpe_arr}
    
    def plot_mcw(self, results=None, show=True, new_fig=False):

        if (not self.figure) or new_fig:
            self.figure = plt.figure()
        
        if not results:
            results = self.monte_carlo_weights()
        
        plt.scatter(results['volatility'], results['returns'],
            c=results['sharpe'], cmap='plasma')
        plt.colorbar(label='Sharpe Ratio')
        plt.xlabel('Volatility')
        plt.ylabel('Return')
                
        max_sharpe_i = results['sharpe'].argmax()
        max_sharpe_vol = results['volatility'][max_sharpe_i]
        max_sharpe_ret = results['returns'][max_sharpe_i]
        plt.scatter(max_sharpe_vol, max_sharpe_ret, c='red', s=50,
                        edgecolors='black')
        
        if show:
            plt.show()

    def get_ret_vol_sr(self, weights):
        weights = np.array(weights)
        ret = np.sum((self.log_returns.mean() * weights) * 252)
        vol = np.sqrt(np.dot(weights.T, np.dot(self.log_returns.cov() * 252, weights)))
        sr = ret / vol
        return np.array([ret, vol, sr])
    
    def _neg_sharpe(self, weights):
        return self.get_ret_vol_sr(weights)[2] * -1
    
    def _neg_return(self, weights):
        return self.get_ret_vol_sr(weights)[0] * -1
    
    def _check_sum(self, weights):
        return np.sum(weights) - 1
    
    def optimised_weights(self, min_func, n_weights=None, bounds=None,
                            init_guess=None):
        """Return the set of weightings that are optimised for min_func,
        along with a tuple containing the return, volatility and Sharpe
        ratio that those weightings yield."""
        if n_weights is None:
            n_weights = len(self.tickers)
        if bounds is None:
            bounds = ((0,1),) * n_weights
        if init_guess is None:
            init_guess = [1 / n_weights for _ in range(n_weights)]
        cons = ({'type': 'eq', 'fun': self._check_sum},)
        results = minimize(min_func, init_guess, method='SLSQP',
            bounds=bounds, constraints=cons)
        opt_weights = results.x
        return opt_weights, self.get_ret_vol_sr(opt_weights)

    def optimised_weights_sr(self, n_weights=None, bounds=None, init_guess=None):
        """Return the set of weightings that are optimised for Sharpe ratio."""
        return self.optimised_weights(self._neg_sharpe, n_weights, bounds, init_guess)
    
    def optimised_weights_ret(self, n_weights=None, bounds=None, init_guess=None):
        """Return the set of weightings that are optimised for return."""
        return self.optimised_weights(self._neg_return, n_weights, bounds, init_guess)

    def minimised_weights_ret(self, n_weights=None, bounds=None, init_guess=None):
        """Return the set of weightings that yields the lowest return."""
        return self.optimised_weights(lambda w: self.get_ret_vol_sr(w)[0],
                    n_weights, bounds, init_guess)

    def efficient_frontier(self, intervals=50):
        n_weights = len(self.tickers)
        init_guess = [1 / n_weights for _ in range(n_weights)]
        bounds = ((0,1),) * n_weights
        max_ret = self.optimised_weights_ret(n_weights, bounds, init_guess)[1][0]
        min_ret = self.minimised_weights_ret(n_weights, bounds, init_guess)[1][0]
        frontier_y = np.linspace(min_ret, max_ret, intervals)
        frontier_vol = []
        for r in frontier_y:
            cons = ({'type': 'eq', 'fun': self._check_sum},
                    {'type': 'eq', 'fun': lambda w: self.get_ret_vol_sr(w)[0]-r})
            result = minimize(lambda w: self.get_ret_vol_sr(w)[1], init_guess,
                        method='SLSQP', bounds=bounds, constraints=cons)
            frontier_vol.append(result['fun'])
        return frontier_vol, frontier_y
    
    def plot_ef(self, results=None, show=True, new_fig=False):
        if (not self.figure) or new_fig:
            self.figure = plt.figure()
        if not results:
            results = self.efficient_frontier()
        frontier_vol, frontier_y = results
        plt.plot(frontier_vol, frontier_y, 'g--')
        if show:
            plt.show()

def test_run(tickers):
    print('Fetching data...')
    data = get_quandl_data(tickers)
    print('Initialising UnweightedBasket...')
    ub = UnweightedBasket(data)
    print('Running Monte Carlo simulation...')
    mcw = ub.monte_carlo_weights()
    print('Getting efficient frontier...')
    ef = ub.efficient_frontier()
    print('Generating Monte Carlo plot...')
    ub.plot_mcw(mcw, show=False)
    print('Generating efficient frontier plot...')
    ub.plot_ef(ef)
