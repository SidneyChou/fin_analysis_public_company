# fin_analysis_public_company
公開發行公司_財報分析

## 公開發行公司連續期間季報表爬蟲程式: fin_reports.py
1. 抓取特定公司的季度損益表、資產負債表與現金流量表
2. 合併連續期間的三大表
3. 資料儲存:(1) 載入至MySQL資料庫(使用SQLAlchemy) (2) 儲存至csv檔案

## Data
1. 損益表、資產負債表與現金流量表 (爬蟲程式)
2. 年報附註: 手動蒐集年報附註揭露之有用資訊

## Power BI 分析
1. 營收與獲利能力
![image](https://github.com/SidneyChou/fin_analysis_public_company/blob/master/powerBI_image/sales_profit.gif)
