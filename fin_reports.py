import requests
import pandas as pd
import numpy as np
import pymysql
from sqlalchemy import create_engine

def financial_statement(co_id, year, quarter, report):
    """
    透過公開資訊觀測站，抓取個股的季度報表
    co_id: 股票代碼
    year: 報告的西元年度 YYYY
    quarter: 報告的季度 (1,2,3,4)
    report: 報告的名稱 (bs-資產負債表, pl-損益表, cf-現金流量表)
    """
    
    if year >= 1000:
        year -= 1911
    
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
    res.encoding = "utf8"
    df = pd.read_html(res.text)[1]
    df = df.iloc[:, 0:2]
    df.iloc[:,1] = df.iloc[:,1] * 1000
    year += 1911
    period = str(year)+"Q"+str(quarter)
    df.columns = ["account", period]
    tmp = pd.DataFrame({"account": ["co_id","year","quarter"], period: [co_id, year, quarter]})
    df = pd.concat([tmp, df])
    return df
    

def merge_statements(co_id, start_yr, end_yr, report):
    """
    合併連續期間的季度報表
    co_id: 股票代碼
    start_yr: 合併期間的起始年度 YYYY
    start_yr: 合併期間的結束年度 YYYY
    report: 報告的名稱 (bs-資產負債表, pl-損益表, cf-現金流量表)
    """
    df = pd.DataFrame({"account":[]})
    for year in range(start_yr, end_yr+1):
        for quarter in range(1,5):
            tmp_df = financial_statement(co_id, year, quarter, report)
            df = pd.merge(df, tmp_df, on="account", how="outer")
            df = df.drop_duplicates(subset="account", keep="last")
    
    if report == "pl": # Q4 is full-year amount in Income Statement rather than quarter amount
        try:    
            for i in range(end_yr - start_yr +1):
                df.iloc[3:, 4*i+4] = df.iloc[3:, 4*i+4] - df.iloc[3:, 4*i+1] - df.iloc[3:, 4*i+2] - df.iloc[3:, 4*i+3]
        except KeyError:
            for i in range(end_yr - start_yr):
                df.iloc[3:, 4*i+4] = df.iloc[3:, 4*i+4] - df.iloc[3:, 4*i+1] - df.iloc[3:, 4*i+2] - df.iloc[3:, 4*i+3]

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
    df = df.astype(object).replace(np.nan, 0.0)
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
    pl = merge_statements(3231, 2017, 2021, "pl")
    bs = merge_statements(3231, 2017, 2021, "bs")
    cf = merge_statements(3231, 2017, 2021, "cf")
    pl = df_transpose(pl)
    bs = df_transpose(bs)
    cf = df_transpose(cf)
    conn = connection_mysql("localhost", "user1", "Password2022?", "fin_report")
    to_mysql(conn, "balance_sheet", bs)
    to_mysql(conn, "income_statement", pl)
    to_mysql(conn, "cash_flow", cf)
    connection_dispose(conn)
    to_csv(bs, "balance_sheet")
    to_csv(pl, "income_statement")
    to_csv(cf, "cash_flow")


