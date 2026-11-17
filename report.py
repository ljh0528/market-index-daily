import pandas as pd
import os
data1=pd.read_csv('data/raw/上证指数_sh000001.csv')
data2=pd.read_csv('data/raw/创业板指_sz399006.csv')
data3=pd.read_csv('data/raw/沪深300_sh000300.csv')
#打印基础信息
def print_desc(df):
    print(df.shape)
    print(df.dtypes)
#去除缺失值
def drop_empty(df):
    df.dropna(how='all',inplace=True)
#去重
def drop_repeat(df):
    df.drop_duplicates(inplace=True)
#统一日期格式
def clean_date(df):
    df['date']= pd.to_datetime(df['date'], errors='coerce')
    return df.sort_values(by=['date']).reset_index(drop=True)
def ptc_change1(df):
    r1=df['close'].pct_change().iloc[-1]*100
    return round(r1,2)
def ptc_change2(df):
    r2=(df['close'].iloc[-1]/df['close'].iloc[-21]-1)*100
    return round(r2,2)
def ptc_change3(df):
    year=df['date'].iloc[-1].year
    base=df[df['date'].dt.year==year]['close'].iloc[0]
    r3= (df['close'].iloc[-1]/base-1)*100
    return round(r3,2)
def fun1(df):
    f1= df['volume'].iloc[-1]/df['volume'].tail(20).mean()
    return round(f1,2)
if __name__ == '__main__':
    drop_empty(data1)
    drop_empty(data2)
    drop_empty(data3)
    drop_repeat(data1)
    drop_repeat(data2)
    drop_repeat(data3)
    data1=clean_date(data1)
    data2=clean_date(data2)
    data3=clean_date(data3)
    print_desc(data1)
    list1 = [data1, data2, data3]
    columns={'日期':[data1['date'].iloc[-1],data2['date'].iloc[-1],data3['date'].iloc[-1]],'指数':['上证指数','创业板指','沪深300'],'收盘':[data1['close'].iloc[-1],data2['close'].iloc[-1],data3['close'].iloc[-1]],'当日%':[],'近20日%':[],'年初至今%':[],'量比':[]}
    for i in list1:
        columns['当日%'].append(ptc_change1(i))
        columns['近20日%'].append(ptc_change2(i))
        columns['年初至今%'].append(ptc_change3(i))
        columns['量比'].append(fun1(i))
    columns_frame=pd.DataFrame(columns)
    os.makedirs('output', exist_ok=True)
    columns_frame.to_csv('output/metrics.csv',index=False,float_format='%.2f')



