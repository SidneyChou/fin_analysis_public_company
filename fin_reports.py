import requests
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import time
import random

co_id_list = [3231, 2382, 2324, 2356, 4938, 2317]
co_name_list = ["緯創", "廣達", "仁寶","英業達","和碩","鴻海"]
start_yr = 2017
end_yr =2021
host = "localhost"
user =  "user1"
password = "Password2022?"
mydb = "financials"

def financial_statement(co_id, co_name, year, quarter, report):
    """
    透過公開資訊觀測站，抓取個股的季度報表
    co_id: 股票代碼
    co_name: 公司名稱
    year: 報告的西元年度 YYYY
    quarter: 報告季度 (1,2,3,4)
    report: 報告名稱 (bs-資產負債表, pl-損益表, cf-現金流量表)
    """
    if year >= 1000:
        year = year - 1911
    
    if report == "bs":
        url = "https://mops.twse.com.tw/mops/web/ajax_t164sb03"
    elif report == "pl":
        url = "https://mops.twse.com.tw/mops/web/ajax_t164sb04"
    elif report == "cf":
        url = "https://mops.twse.com.tw/mops/web/ajax_t164sb05"
    else:
        print("report name does not match\n you can choose 'bs', 'is', and 'cf'")
    
    payload = {
        "encodeURIComponent" : "1",
        "step" : "1",
        "firstin" : "1",
        "off" : "1",
        "queryName" : "co_id",
        "inpuType" : "co_id",
        "TYPEK" : "all",
        "isnew" : "false",
        "co_id" : str(co_id),
        "year": str(year),
        "season": str(quarter)
        }
    res = requests.post(url, data=payload)
    df = pd.read_html(res.text)[1].fillna(0)
    df = df.iloc[:, 0:2]
    df.iloc[:,1] = df.iloc[:,1] * 1000
    year = year + 1911
    period = str(year)+"Q"+str(quarter)+"_"+str(co_id)
    df.columns = ["account", period]
    tmp = pd.DataFrame({"account": ["co_id", "co_name", "year", "quarter"], period: [co_id, co_name, year, quarter]})
    df = pd.concat([tmp, df])
    df = df.replace(np.nan, 0.0)
    return df


def merge_year_mtd(co_id, co_name, start_yr, end_yr, report):
    """
    合併同一公司連續期間的季度報表- MTD base
    co_id: 股票代碼
    co_name: 公司名稱
    start_yr: 合併期間的起始年度 YYYY
    end_yr: 合併期間的結束年度 YYYY
    report: 報告的名稱 (bs-資產負債表, pl-損益表, cf-現金流量表)
    """
    df = pd.DataFrame({"account":[]})
    for year in range(start_yr, end_yr+1):
        for quarter in range(1,5):
            tmp_df = financial_statement(co_id, co_name, year, quarter, report)
            df = pd.merge(df, tmp_df, on="account", how="outer")
            df = df.drop_duplicates(subset="account", keep="last")
            df = df.replace(np.nan, 0.0)
            time.sleep(random.randint(3, 6))
    
    if report == "pl": # Q4 is full-year amount in Income Statement rather than quarter amount
        try:    
            for i in range(end_yr - start_yr +1):
                df.iloc[4:, 4*i+4] = df.iloc[4:, 4*i+4] - df.iloc[4:, 4*i+1] - df.iloc[4:, 4*i+2] - df.iloc[4:, 4*i+3]
        except KeyError:
            for i in range(end_yr - start_yr):
                df.iloc[4:, 4*i+4] = df.iloc[4:, 4*i+4] - df.iloc[4:, 4*i+1] - df.iloc[4:, 4*i+2] - df.iloc[4:, 4*i+3]

    else: # is accumulated amount in each quarter
        for i in range(end_yr - start_yr +1):
            df.iloc[4:, 4*i+4] = df.iloc[4:, 4*i+4] - df.iloc[4:, 4*i+3]
            df.iloc[4:, 4*i+3] = df.iloc[4:, 4*i+3] - df.iloc[4:, 4*i+2]
            df.iloc[4:, 4*i+2] = df.iloc[4:, 4*i+2] - df.iloc[4:, 4*i+1]

    return df


def merge_year_ytd(co_id, co_name, start_yr, end_yr, report):
    """
    合併同一公司連續期間的季度報表 - YTD base
    co_id: 股票代碼
    co_name: 公司名稱
    start_yr: 合併期間的起始年度 YYYY
    end_yr: 合併期間的結束年度 YYYY
    report: 報告的名稱 (bs-資產負債表, pl-損益表, cf-現金流量表)
    """
    df = pd.DataFrame({"account":[]})
    for year in range(start_yr, end_yr+1):
        for quarter in range(1,5):
            tmp_df = financial_statement(co_id, co_name, year, quarter, report)
            df = pd.merge(df, tmp_df, on="account", how="outer")
            df = df.drop_duplicates(subset="account", keep="last")
            df = df.replace(np.nan, 0.0)
            time.sleep(random.randint(3, 6))
    
    if report == "pl": # Q4 is full-year amount in Income Statement rather than quarter amount
        for i in range(end_yr - start_yr +1):
            df.iloc[4:, 4*i+2] = df.iloc[4:, 4*i+1] + df.iloc[4:, 4*i+2]
            df.iloc[4:, 4*i+3] = df.iloc[4:, 4*i+2] + df.iloc[4:, 4*i+3]        
    return df


def merge_co(co_id_list, start_yr, end_yr, report, period):
    """
    合併不同公司的季度報表
    co_id: 股票代碼
    co_name: 公司名稱
    start_yr: 合併期間的起始年度 YYYY
    end_yr: 合併期間的結束年度 YYYY
    report: 報告的名稱 (bs-資產負債表, pl-損益表, cf-現金流量表)
    period: 期間類型 (mtd, ytd)
    """
    df = pd.DataFrame({"account":[]})
    for i, co_id in enumerate(co_id_list):
        co_name = co_name_list[i]
        if period == "mtd":
            tmp_df = merge_year_mtd(co_id, co_name, start_yr, end_yr, report)
            df = pd.merge(df, tmp_df, on="account", how="outer")
        elif period == "ytd":
            tmp_df = merge_year_ytd(co_id, co_name, start_yr, end_yr, report)
            df = pd.merge(df, tmp_df, on="account", how="outer")
    df = df.replace(np.nan, 0.0)
    return df
    
def df_transpose(df):
    """
    轉置 dataframe，並將會計科目設為 index
    df: dataframe
    """
    df = df.set_index('account')
    df = df.T
    df = df.reset_index(drop=True)
    return df


def connection_mysql(ip_addr, username, password, dbname):
    """"
    連線到MySQL
    ip_addr: ip address
    username: your username in MySQL
    password: your password
    dbname: database name
    """
    conn = create_engine(f"mysql+pymysql://{username}:{password}@{ip_addr}:3306/{dbname}", encoding="utf8")
    return  conn

def to_mysql(connection, table, df):
    """
    將資料寫入MySQL
    connection: 連線變數名稱
    table: MySQL的 table名稱
    df: 報表的變數名稱    
    """
    df['co_id'] = df['co_id'].astype(int)
    df['year'] = df['year'].astype(int)
    df['quarter'] = df['quarter'].astype(int)
    pd.io.sql.to_sql(df, table, connection, if_exists="append", index=False)


def connection_dispose(connection):    
    """結束 MySQL的連線- sqlalchemy"""
    connection.dispose()

def to_csv(df, table_name):
    """存取csv檔案"""
    df.to_csv(f"{table_name}.csv",index=False)

if __name__ == "__main__":
    pl_mtd = merge_co(co_id_list, start_yr, end_yr, "pl", "mtd")
    bs_mtd = merge_co(co_id_list, start_yr, end_yr, "bs", "mtd")
    cf_mtd = merge_co(co_id_list, start_yr, end_yr, "cf", "mtd")
    pl_mtd = df_transpose(pl_mtd)
    bs_mtd = df_transpose(bs_mtd)
    cf_mtd = df_transpose(cf_mtd)
    pl_ytd = merge_co(co_id_list, start_yr, end_yr, "pl", "ytd")
    bs_ytd = merge_co(co_id_list, start_yr, end_yr, "bs", "ytd")
    cf_ytd = merge_co(co_id_list, start_yr, end_yr, "cf", "ytd")
    pl_ytd = df_transpose(pl_ytd)
    bs_ytd = df_transpose(bs_ytd)
    cf_ytd = df_transpose(cf_ytd)
    conn = connection_mysql(host, user, password, mydb)
    to_mysql(conn, "balance_sheet_variance", bs_mtd)
    to_mysql(conn, "income_statement_mtd", pl_mtd)
    to_mysql(conn, "cash_flow_mtd", cf_mtd)
    to_mysql(conn, "balance_sheet_ytd", bs_ytd)
    to_mysql(conn, "income_statement_ytd", pl_ytd)
    to_mysql(conn, "cash_flow_ytd", cf_ytd)
    connection_dispose(conn)