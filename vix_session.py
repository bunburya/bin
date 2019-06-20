# coding: utf-8
import quandl
help(quandl)
vx1_data = quandl.get('CHRIS/CBOE_VX1')
vx1_data
import matplotlib
get_ipython().run_line_magic('matplotlib', 'qt5')
vx1_data['open'].plot()
vx1_data
vx1_data['Close'].plot()
change = vx1_data['Close'].pct_change(1)
change
change.plot()
change.plot()
change[change < -0.5]
change['2007-03-27']
change['2007-03-27':]
vx1_data = vx1_data['2007-03-27':]
vx1_data.plot()
vx1_data['Close'].plot()
vx1_data['High'].plot()
vx1_data['Low'].max()
vx1_data['Low'].min()
vx1_data['High'].min()
vx1_data['High'].max()
vx1_data.resample('1M').mean()
vx1_data['Low'].resample('1M').mean()
vx1_data['Low'].resample('1M').min()
vx1_data
vx1_data['Low']
vx1_data['Low'].resample('1M').min()
vx1_data['Low'].resample('1M').min().plot()
vx1_data['Low'].resample('1M').min().hist()
vx1_data['Low'].resample('1M').min().kdr()
vx1_data['Low'].resample('1M').min().kdp()
help(vx1_data['Low'].resample('1M').min().plot)
vx1_data['Low'].resample('1M').min().plot.kdp()
vx1_data['Low'].resample('1M').min().plot.kde()
lows = vx1_data['Low'].resample('1M').min()
lows[lows < 10]
lows[lows < 11]
lows[lows < 12]
lows[lows < 13]
lows[lows < 10.5]
lows[lows < 10.3]
lows[lows < 10.2]
lows[lows < 10.1]
vx1_data['High'].resample('1M').min().plot.kde()
vx1_data['Open'].resample('1M').min().plot.kde()
vx1_data['Close'].resample('1M').min().plot.kde()
vx1_data['High'].resample('1M').max().plot.kde()
vx1_data['Low'].resample('1M').min().plot.kde()
vx1_data['Close'].mean()
vx1_data['Close'].std()
def how_long(data, level):
    results = []
    below_level = False
    for d in data:
        if d < level and not below_level:
            below_level = True
            
for t, d in vx1_data['Close']: print(t,d)
for i in vx1_data['Close'].index:print(i)
for i in vx1_data['Close'].index:print(i, vx1_data['Close'].iloc[i])
for i in vx1_data['Close'].index:print(i, vx1_data['Close'].loc[i])
vx1_data
for i in vx1_data['Close'].index:print(i, vx1_data['Close'].loc[i])
vx1_data['Close']
#for i in vx1_data['Close'].index:print(i, vx1_data['Close'].loc[i])
def how_long(data, level):
    results = []
    below_level = False
    for_how_long = 0
    current_i = None
    for i in data.index:
        d = data.loc[i]
        if d < level and not below_level:
            current_i = i
            below_level = True
            for_how_long = 1
        elif d < level:
            for_how_long += 1
        else:
            below_level = False
            results.append((current_i, for_how_long))
            for_how_long = 0
    return results
    
            
how_long(vx1_data['Close'], 11)
def how_long(data, level):
    results = []
    below_level = False
    for_how_long = 0
    current_i = None
    for i in data.index:
        d = data.loc[i]
        if d < level and not below_level:
            current_i = i
            below_level = True
            for_how_long = 1
        elif d < level and below_level:
            for_how_long += 1
        elif d > level and below_level:
            below_level = False
            results.append((current_i, for_how_long))
            for_how_long = 0
    return results
    
    
            
how_long(vx1_data['Close'], 12)
vx1_data['Close']
vx1_data['Close']['2017-11-21']
vx1_data['Close']['2017-11-22']
vx1_data['Close']['2017-11-23']
vx1_data['Close']['2017-11-25']
vx1_data['Close']['2017-11-26']
vx1_data['Close']['2017-11-27']
how_long(vx1_data['Close'], 12)
lengths = [x[1] for x in _]
lengths
import pandas as pd
lens = pd.Series(lengths)
lens
lens.mean()
lens.median()
lens.std()
df = pd.DataFrame()
df
data = vx1_data['Close']
for i in range(9, 30):
    lens = pd.Series([x[1] for x in how_long(data, i)])
    df[i]['Max'] = lens.max()
    df[i]['Mean'] = lens.mean()
    df[i]['Median'] = lens.median()
    
df
df.index = range(9, 30)
df.index = list(range(9, 30))
df.set_index(list(range(9, 30)))
df.set_index(list(range(9, 30)))
list(range(9, 30))
help(pd.DataFrame)
df pd.DataFrame(index=range(9,30))
df = pd.DataFrame(index=range(9,30))
df
for i in range(9, 30):
    lens = pd.Series([x[1] for x in how_long(data, i)])
    df[i]['Max'] = lens.max()
    df[i]['Mean'] = lens.mean()
    df[i]['Median'] = lens.median()
    
df
for i in range(9, 30):
    lens = pd.Series([x[1] for x in how_long(data, i)])
    df.loc[i]['Max'] = lens.max()
    df.loc[i]['Mean'] = lens.mean()
    df.loc[i]['Median'] = lens.median()
    
    
df
df
df[i]
i
df.loc(i)
df.loc[i]
df
df = pd.DataFrame(index=range(9, 30), columns=['Max', 'Mean', 'Median'])
df
df[3]
df[12]
df.loc[12]
df.loc[12]['Max']
df.loc[12]['Max'] = 4
df
for i in range(9, 30):
    lens = pd.Series([x[1] for x in how_long(data, i)])
    df.loc[i]['Max'] = lens.max()
    df.loc[i]['Mean'] = lens.mean()
    df.loc[i]['Median'] = lens.median()
    
df
df.plot()
get_ipython().run_line_magic('save', 'vix_session')
