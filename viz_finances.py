#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import pandas as pd

#matplotlib.use('Qt5Agg')

#%matplotlib qt5

# TODO:  Add new plot showing net monthly change, once sufficient data
# available

XLSX_FILE = argv[1]

PAYDAY = 8

def get_data():
    return pd.read_excel(XLSX_FILE, header=[0, 1], index_col=0, parse_dates=True) 

def generate_plots(df):

    fig = plt.figure(figsize=(20, 10))
    
    totals_ax = plt.subplot2grid(shape=(2,6), loc=(0,0), colspan=2)
    boi_ax = plt.subplot2grid((2,6), (0,2), colspan=2)
    others_ax = plt.subplot2grid((2,6), (0,4), colspan=2)
    weekly_ax = plt.subplot2grid((2,6), (1,0), colspan=2)
    monthly_ax = plt.subplot2grid((2,6), (1,2), colspan=2)
    pie_ax = plt.subplot2grid((2,6), (1,4), colspan=2)
    
    time_plots = [totals_ax, boi_ax, others_ax, weekly_ax, monthly_ax]
    
    # totals_ax: Total amounts, separated by cash and non-cash
    totals_ax.set_title('Total')
    tcols = [df['Totals']['Total cash'], df['Totals']['Total non-cash']]
    totals_ax.stackplot(df.index, tcols, labels=['Total cash', 'Total non-cash'])
    totals_ax.legend()
    totals_ax.xaxis_date()
    
    # totals_ax: Total amounts (monthly), separated by cash and non-cash
    #monthly_data = df.resample('M').apply(lambda m: m[-1])
    #monthly_data.dropna(inplace=True)
    #totals_ax.set_title('Total')
    #tcols = [monthly_data['Totals']['Total cash'], monthly_data['Totals']['Total non-cash']]
    #totals_ax.stackplot(monthly_data.index, tcols, labels=['Total cash', 'Total non-cash'])
    #totals_ax.legend()
    #totals_ax.xaxis_date()

    # weekly_ax: Weekly change of total assets
    weekly_change = df['Totals']['Total'] - df['Totals']['Total'].shift(1)
    weekly_change.dropna(inplace=True)
    ewma26 = weekly_change.ewm(span=26).mean()
    weekly_ax.set_title('Net weekly change (26-week EWMA)')
    weekly_ax.bar(weekly_change.index, weekly_change, width=5)
    weekly_ax.plot(ewma26, ls='--', color='black')
    weekly_ax.xaxis_date()
    
    # monthly_ax: Monthly change of total assets
    # TODO:  The ticks on this plot are wrong, off by one month.  Fix.
    monthly_data = df.resample('M').apply(lambda m: m[-1])
    monthly_data.dropna(inplace=True)
    print(monthly_data)
    monthly_change = monthly_data['Totals']['Total'] - monthly_data['Totals']['Total'].shift(1)
    monthly_change.dropna(inplace=True)
    print(monthly_change)
    print(monthly_change.index)
    ewma6 = monthly_change.ewm(span=6).mean()
    monthly_ax.set_title('Net monthly change (6-month EWMA)')
    monthly_ax.bar(monthly_change.index, monthly_change, width=1)
    monthly_ax.plot(ewma6, ls='--', color='black')
    monthly_ax.xaxis_date()    

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
