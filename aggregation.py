import pandas as pd
from datetime import datetime, timedelta

# データの読み込み（適宜ファイルパスを指定）
file_path_2024 = "./data/dataset_v2.csv"
file_path_2025 = "./data/simulation.csv"
df = pd.read_csv(file_path_2024)
df_2025 = pd.read_csv(file_path_2025)

# 2024年の新規購入データの前処理
df['date'] = pd.to_datetime(df['date'], format='%m/%d')  # 月日を日付型に変換（年は後で補完）
df['date'] = df['date'].apply(lambda x: x.replace(year=2024))  # 2024年を適用

# 2025年の新規購入データを日別に分配
df_2025['date'] = pd.to_datetime(df_2025['date'], format='%Y-%m')  # 月単位の日付型に変換

df_2025_daily = []
for index, row in df_2025.iterrows():
    date = row['date']
    monthly_new_cv = row['new_cv']
    days_in_month = (date + pd.DateOffset(months=1) - timedelta(days=1)).day
    daily_new_cv = monthly_new_cv // days_in_month  # 日別の新規獲得数
    
    for day in range(days_in_month):
        df_2025_daily.append({"date": date + timedelta(days=day), "new_cv": daily_new_cv})

df_2025_daily = pd.DataFrame(df_2025_daily)

# 2024年と2025年の新規購入データを統合（修正後）
df_all = pd.concat([df, df_2025_daily], ignore_index=True)

# 継続率と購入スケジュールの設定
continuation_rates = [0.65, 0.55, 0.57, 0.62]  # 5回目以降は0.62を適用
repeat_intervals = [20] + [60] * 10  # 初回から20日後、以降60日ごと

# 各月の売上を計算
sales_by_month = {}

for index, row in df_all.iterrows():
    purchase_date = row['date']
    num_purchases = row['new_cv']
    
    # 初回購入の売上
    month_year = purchase_date.strftime("%Y-%m")
    sales_by_month[month_year] = sales_by_month.get(month_year, 0) + num_purchases * 980
    
    # 継続購入のシミュレーション
    remaining_users = num_purchases
    for i, interval in enumerate(repeat_intervals):
        if i >= len(continuation_rates):
            rate = continuation_rates[-1]  # 5回目以降は0.62を適用
        else:
            rate = continuation_rates[i]
        
        remaining_users = int(remaining_users * rate)  # 継続率を適用
        if remaining_users == 0:
            break
        
        next_purchase_date = purchase_date + timedelta(days=interval)
        next_month_year = next_purchase_date.strftime("%Y-%m")
        
        if next_month_year in sales_by_month:
            sales_by_month[next_month_year] += remaining_users * 10800
        else:
            sales_by_month[next_month_year] = remaining_users * 10800

# データフレームに整理
sales_df = pd.DataFrame(list(sales_by_month.items()), columns=["month", "sales"])
sales_df = sales_df.sort_values(by="month")

# 結果を表示
print(sales_df)

