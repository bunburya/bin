#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import pandas as pd

#%matplotlib qt5

# TODO:  Add new plot showing net monthly change, once sufficient data
# available

XLSX_FILE = argv[1]

def get_data():
    return pd.read_excel(XLSX_FILE, header=[0, 1], index_col=0, parse_dates=True) 

def generate_plots(df):

    fig = plt.figure(figsize=(20, 10))
    
    totals_ax = plt.subplot2grid(shape=(2,6), loc=(0,0), colspan=2)
    change_ax = plt.subplot2grid((2,6), (0,2), colspan=2)
    pie_ax = plt.subplot2grid((2,6), (0,4), colspan=2)
    boi_ax = plt.subplot2grid((2,6), (1,1), colspan=2)
    others_ax = plt.subplot2grid((2,6), (1,3), colspan=2)
    
    time_plots = [totals_ax, change_ax, boi_ax, others_ax]
    
    #totals_ax: Total amounts, separated by cash and non-cash
    totals_ax.set_title('Total')
    tcols = [df['Totals']['Total cash'], df['Totals']['Total non-cash']]
    totals_ax.stackplot(df.index, tcols, labels=['Total cash', 'Total non-cash'])
    totals_ax.legend()
    change_ax.xaxis_date()

    # change_ax: Weekly change of total assets
    change_data = df['Totals']['Total'] - df['Totals']['Total'].shift(1)
    change_data.dropna(inplace=True)
    ewma10 = change_data.ewm(span=10).mean()
    change_ax.set_title('Net weekly change (10-week EWMA)')
    change_ax.bar(change_data.index, change_data, width=5)
    change_ax.plot(ewma10, ls='--', color='black')
    change_ax.xaxis_date()

    # pie_ax: Amounts held with each entity, as pie chart
    pie_labels = df.columns.levels[0][:6] # exclude Totals
    pie_data = [df[i].iloc[-1].sum() for i in pie_labels]
    pie_ax.set_title('Breakdown by institution')
    pie_ax.pie(pie_data, labels=pie_labels)
    
    # boi_ax: Amounts held with Bank of Ireland (main bank accounts)
    boi_ax.set_title('Bank of Ireland')
    for subcol in df['Bank of Ireland']:
        boi_ax.plot_date(df.index, df['Bank of Ireland'][subcol], '-', label=subcol)
    boi_ax.legend()

    # other_ax: Amounts held other than with Bank of Ireland
    others_ax.set_title('Others')
    for col in df.columns.levels[0].drop(['Bank of Ireland', 'Totals']):
        others_ax.plot_date(df.index, df[col].sum(axis=1), '-', label=col)
    others_ax.legend()
    
    for a in time_plots:
        a.xaxis.set_major_locator(dates.MonthLocator())
        a.xaxis.set_major_formatter(dates.DateFormatter('%b-%y'))
    
    # automft_xdate turns off x labels on the top plots so don't call
    #fig.autofmt_xdate()
    
    for a in time_plots:
        plt.setp(a.get_xticklabels(), rotation='horizontal',
                    horizontalalignment='center', visible=True)

    fig_mgr = plt.get_current_fig_manager()
    fig_mgr.window.showMaximized()
    #plt.subplots_adjust(#top=0.948,
    #                    bottom=0.102,
    #                    left=0.051,
    #                    right=0.985,
    #                    hspace=0.266)
    #                    wspace=0.471)
    plt.tight_layout()
    plt.show()
    #plt.savefig('finances.png')

if __name__ == '__main__':
    df = get_data()
    generate_plots(df)
