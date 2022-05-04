# fin_analysis_public_company
公開發行公司_財報分析

## 公開發行公司連續期間季報表爬蟲程式: fin_reports.py
1. 抓取公開資訊觀測站內，特定公司與競爭對手的季度損益表、資產負債表與現金流量表
2. 依三大表，合併個別公司連續期間的季報資料
3. 依三大表，合併所有公司資料
4. 資料儲存:(1) 載入至MySQL資料庫(使用SQLAlchemy) (2) 儲存至csv檔案

## Data
1. 2017~2021年5年度合併損益表、資產負債表與現金流量表 (爬蟲程式)
2. 2017~2020年的年報附註: 手動蒐集年報附註揭露之有用資訊

## Power BI dashbord
1. 營收與獲利
![image](https://github.com/SidneyChou/fin_analysis_public_company/blob/master/img/sales_profit.gif)

2. 現金流量與財務結構
![image](https://github.com/SidneyChou/fin_analysis_public_company/blob/master/img/cf_bs.gif)

3. 年報資訊
![image](https://github.com/SidneyChou/fin_analysis_public_company/blob/master/img/annual_report_info.gif)

4. 同業比較 - 營收與獲利
![image](https://github.com/SidneyChou/fin_analysis_public_company/blob/master/img/competitor_sales_profit.gif)

5. 同業比較 - 現金流量與財務結構
![image](https://github.com/SidneyChou/fin_analysis_public_company/blob/master/img/competitor_cf_bs.gif)

6. 同業比較 - CCC days
![image](https://github.com/SidneyChou/fin_analysis_public_company/blob/master/img/competitor_ccc_days.gif)


## Power BI 分析結論與追蹤事項
1. 結論
   - 在提升產品附加價值的商業模式下，比起營收，需更注意產品別毛利的改善狀況。
   - 獲利雖穩定成長，但存貨天數已來到新高60天。長料的進貨建議趨向保守，避免未來產品出貨減緩時，造成存貨跌價損失。
   - 公司的財務槓桿與FCF margin皆弱於同業，建議在未來總體經濟下行風險提升下，加速營業現金流入，且研發支出與資本支出趨向保守。
2. 追蹤事項
   - 存貨去化
     - 特別關注NB相關原料
     - 長料要考慮減少進貨
     - 客戶別專屬原料追蹤
   - 降低應收帳款
     - 追蹤逾期收款
     - 檢視帳齡表
   - 銷貨
     - 高附加價值產品之銷貨成長目標達成率
     - 新客戶銷貨
   - 毛利率
     - 各產品別是否也逐年改善
   - 資本支出與研發費用
     - 效益追蹤

