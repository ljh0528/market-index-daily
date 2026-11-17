import matplotlib.pyplot as plt
import pandas as pd
import os
import matplotlib.dates as mdates
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False
data1=pd.read_csv('data/raw/上证指数_sh000001.csv')
data2=pd.read_csv("data/raw/创业板指_sz399006.csv")
data3=pd.read_csv("data/raw/沪深300_sh000300.csv")
#去除缺失值
def drop_empty(df):
    return df.dropna(how='all')
#去重
def drop_repeat(df):
    return df.drop_duplicates()
#统一日期格式
def clean_date(df):
    df['date']= pd.to_datetime(df['date'], errors='coerce')
    return df.sort_values(by=['date']).reset_index(drop=True)
data1=drop_empty(data1)
data2=drop_empty(data2)
data3=drop_empty(data3)
data1=drop_repeat(data1)
data2=drop_repeat(data2)
data3=drop_repeat(data3)
data1=clean_date(data1)
data2=clean_date(data2)
data3=clean_date(data3)
recent1=data1.tail(250).reset_index(drop=True)
recent2=data2.tail(250).reset_index(drop=True)
recent3=data3.tail(250).reset_index(drop=True)
dict1={'上证指数':recent1,'创业板指':recent2,'沪深300':recent3}
recent1['norm']=recent1['close']/recent1['close'].iloc[0]*100
recent2['norm']=recent2['close']/recent2['close'].iloc[0]*100
recent3['norm']=recent3['close']/recent3['close'].iloc[0]*100
fig,ax=plt.subplots(figsize=(12,6))
for name,df in dict1.items():
    ax.plot(df['date'],df['norm'],label=name)
ax.axhline(y=100,color='gray',linestyle='--')
ax.set_title("三大指数近一年走势")
ax.set_ylabel("相对起点")
ax.legend()
ax.grid(alpha=0.3)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.setp(ax.get_xticklabels(),rotation=45,ha="right")
os.makedirs('docs/img',exist_ok=True)
fig.savefig('docs/img/trend.png',dpi=300,bbox_inches='tight')
columns_frame=pd.read_csv('output/metrics.csv')
#print(columns_frame)
values=[i for i in columns_frame['当日%']]
names=[i for i in columns_frame['指数']]
print(values)
print(names)
colors=["#d62728" if v>=0 else "#2ca02c" for v in values]
fig,ax=plt.subplots(figsize=(8,3.5))
bars=ax.barh(names,values,color=colors,height=0.5)
ax.axvline(x=0,color='black',linewidth=0.8)
ax.set_xlabel('当日涨跌幅（%）')
ax.bar_label(bars,fmt='%.2f',padding=3)
lo=min(min(values),0)
hi=max(max(values),0)
pad=(hi-lo)*0.12
ax.set_xlim(lo-pad,hi+pad)
ax.set_title("当日涨跌幅（2026-11-13）")
fig.tight_layout()
fig.savefig('docs/img/bar.png',dpi=300)