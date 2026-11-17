import os
from datetime import datetime

import pandas as pd

df = pd.read_csv('output/metrics.csv')


def color(v):
    """涨红跌绿，返回对应的 class 名"""
    return "up" if v >= 0 else "down"


def pct(v):
    """带正负号的百分比，例如 +1.23% / -0.59%"""
    return f"{v:+.2f}%"


# ---------- 顶部三张指标卡 ----------
cards = []
for _, r in df.iterrows():
    cards.append(
        f'<div class="card">'
        f'<div class="name">{r["指数"]}</div>'
        f'<div class="value {color(r["当日%"])}">{pct(r["当日%"])}</div>'
        f'<div class="sub">收盘 {r["收盘"]:.2f}</div>'
        f'</div>'
    )
cards_html = "\n".join(cards)

# ---------- 表格 ----------
rows = []
for _, r in df.iterrows():
    rows.append(
        f"<tr>"
        f"<td>{r['指数']}</td>"
        f"<td>{r['收盘']:.2f}</td>"
        f'<td class="{color(r["当日%"])}">{pct(r["当日%"])}</td>'
        f'<td class="{color(r["近20日%"])}">{pct(r["近20日%"])}</td>'
        f'<td class="{color(r["年初至今%"])}">{pct(r["年初至今%"])}</td>'
        f"<td>{r['量比']:.2f}</td>"
        f"</tr>"
    )
rows_html = "\n".join(rows)

# ---------- 结论：从数据算出来，不写死 ----------
# 写死的数字会在自动更新后变成错的，所以这里每次重新生成。
down = int((df["当日%"] < 0).sum())
worst_today = df.loc[df["当日%"].idxmin()]
worst_ytd = df.loc[df["年初至今%"].idxmin()]

if down == len(df):
    head = "全线收跌"
elif down == 0:
    head = "全线收涨"
else:
    head = f"{down} 跌 {len(df) - down} 涨"

summary = (
    f"当日三大指数{head}，跌幅最大的是{worst_today['指数']}"
    f"（{worst_today['当日%']:.2f}%）。"
    f"年初至今{worst_ytd['指数']}累计回落 {abs(worst_ytd['年初至今%']):.2f}%，幅度最深。"
)

date = df['日期'].iloc[0]

# 生成时间用北京时间（GitHub Actions 的机器跑在 UTC）
try:
    from zoneinfo import ZoneInfo
    generated = datetime.now(ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M')
except Exception:
    generated = datetime.now().strftime('%Y-%m-%d %H:%M')

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="上证指数、沪深300、创业板指的每交易日行情汇总">
  <title>市场指数日报 · {date}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>市场指数日报</h1>
  <p class="date">{date} 收盘</p>

  <p class="summary">{summary}</p>

  <div class="cards">
    {cards_html}
  </div>

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
  </table>

  <figure>
    <img src="img/trend.png" alt="三大指数近一年走势">
    <figcaption>近 250 个交易日走势，起点归一化为 100</figcaption>
  </figure>

  <figure>
    <img src="img/bar.png" alt="当日涨跌幅">
    <figcaption>{date} 当日涨跌幅，红涨绿跌</figcaption>
  </figure>

  <footer>
    数据来源：新浪财经 · 最后生成：{generated}
  </footer>
</body>
</html>
"""

os.makedirs('docs', exist_ok=True)
with open(os.path.join('docs', 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html)
print("已生成 docs/index.html")
print("页面里共有", len(df), "行数据")
