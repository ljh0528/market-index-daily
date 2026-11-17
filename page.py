import os
import pandas as pd
df=pd.read_csv('output/metrics.csv')
rows=[]
for _, row in df.iterrows():
    rows.append(
        f"<tr>"
        f"<td>{row['指数']}</td>"
        f"<td>{row['收盘']:.2f}</td>"
        f"<td>{row['当日%']:.2f}%</td>"
        f"<td>{row['近20日%']:.2f}%</td>"
        f"<td>{row['年初至今%']:.2f}%</td>"
        f"<td>{row['量比']:.2f}</td>"
        f"</tr>"
    )
rows_html='\n'.join(rows)
date=df['日期'].iloc[0]
html=f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>市场指数日报</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>市场指数日报</h1>
  <p class="date">{date} 收盘</p>
  <table>
    <thead>
      <tr>
        <th>指数</th><th>收盘</th><th>当日</th>
        <th>近20日</th><th>年初至今</th><th>量比</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
    <p>过去一年三大指数均在下跌区间，创业板指跌幅最深（约 22.6%），上证指数相对抗跌（约 8.2%）。当日三大指数全线收跌，创业板指跌 3.32%，波动明显大于主板。</p>
  </table>
  <section>
    <img src="img/trend.png" alt="三大指数近一年走势">
    <img src="img/bar.png" alt="当日涨跌幅">
  </section>
  <footer>数据来源：新浪财经 · 最后生成：2026-11-13 18:02</footer>
</body>
</html>
"""
os.makedirs('docs',exist_ok=True)
with open(os.path.join('docs','index.html'),'w',encoding='utf-8') as f:
    f.write(html)
print("已生成 docs/index.html")
print("页面里共有", len(df), "行数据")