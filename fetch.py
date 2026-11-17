# -*- coding: utf-8 -*-
"""
Day 1：拉取三个指数的日线数据，存成本地 CSV。

设计原则（重要，别改）：
  1. 只负责"取数据 + 存文件"，不做任何计算和图。
  2. 成功后之后所有代码只读 data/raw/*.csv，不再联网。
  3. 主接口挂了会依次尝试备用接口；全挂就打印手动下载指引，不抛裸异常。

运行：
    python fetch_data.py
"""

import os
import time
import traceback

import pandas as pd

# ---- 要的指数：名字 -> 新浪代码 ----
SYMBOLS = {
    "上证指数": "sh000001",
    "沪深300": "sh000300",
    "创业板指": "sz399006",
}

RAW_DIR = os.path.join("data", "raw")
COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def fetch_primary(symbol: str) -> pd.DataFrame:
    """主接口：新浪源，走 ak.stock_zh_index_daily。"""
    import akshare as ak

    df = ak.stock_zh_index_daily(symbol=symbol)
    if df is None or df.empty:
        raise ValueError("返回空表")
    return df


def fetch_backup(symbol: str) -> pd.DataFrame:
    """备用接口：东财源。注意东财可能限流，正常不要主动调它。"""
    import akshare as ak

    # 东财要纯数字代码，去掉 sh/sz 前缀
    code = symbol[2:] if symbol[:2] in ("sh", "sz") else symbol
    df = ak.index_zh_a_hist(
        symbol=code,
        period="daily",
        start_date="20150101",
        end_date="20991231",
    )
    if df is None or df.empty:
        raise ValueError("返回空表")
    # 东财中文列名映射成统一英文
    rename = {
        "日期": "date", "开盘": "open", "最高": "high",
        "最低": "low", "收盘": "close", "成交量": "volume",
    }
    return df.rename(columns=rename)


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """统一成 date/open/high/low/close/volume 六列，日期升序。"""
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"缺列 {missing}，实际列：{list(df.columns)}")

    out = df[COLUMNS].copy()
    out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    for c in ["open", "high", "low", "close", "volume"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["close"]).drop_duplicates(subset=["date"])
    out = out.sort_values("date").reset_index(drop=True)
    return out


def main() -> int:
    os.makedirs(RAW_DIR, exist_ok=True)
    ok, failed = [], []

    for name, symbol in SYMBOLS.items():
        df = None
        for label, fn in (("主接口(新浪)", fetch_primary), ("备用接口(东财)", fetch_backup)):
            try:
                df = normalize(fn(symbol))
                print(f"[OK] {name}({symbol}) 走 {label}：{len(df)} 行")
                break
            except Exception as e:
                print(f"[失败] {name} {label}: {type(e).__name__}: {e}")

        if df is None:
            failed.append((name, symbol))
            continue

        path = os.path.join(RAW_DIR, f"{name}_{symbol}.csv")
        # utf-8-sig：用 Excel 直接双击打开中文不乱码
        df.to_csv(path, index=False, encoding="utf-8-sig")
        last = df.iloc[-1]
        print(f"     -> {path}  最新 {last['date']}  收盘 {last['close']}")
        ok.append(name)

        time.sleep(1.5)  # 别把对端打急眼

    print("-" * 50)
    print(f"成功 {len(ok)}/{len(SYMBOLS)}：{', '.join(ok) if ok else '无'}")

    if failed:
        print("\n以下指数没取到，用兜底方案：")
        for name, symbol in failed:
            print(f"  - {name}({symbol})")
        print(
            "\n兜底两步：\n"
            "  1) 等 20 分钟再跑一次本脚本（限流会恢复）。\n"
            "  2) 还不行就去 https://finance.sina.com.cn/realstock/company/"
            + SYMBOLS.get("上证指数", "") + "/hisdata/qiandata.shtml\n"
            "     手动下载 CSV，改名为 上证指数_sh000001.csv 放进 data/raw/。\n"
            "     后面所有代码只读这个文件夹，所以照样能往下做。"
        )
        return 1

    print("\nDay 1 完成。接下来所有代码只读 data/raw/，不要再联网。")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)