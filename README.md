# Taiwan Company Network Research Skill

這是一個供 AGENT 使用的台灣公司關聯研究的 Skill，主要解決的是業務查找潛客之機會。輸入公司名稱、8 碼統一編號或上市櫃／興櫃股票代號後，可依公開資料整理公司的母子公司、轉投資、被投資公司、投資損益、資本額、公開市場狀態，以及代表人／董監事延伸公司。

## 研究內容

- 法定母公司、合併子公司及孫公司
- 權益法投資、合資與非控制性轉投資
- 持股比例、帳面金額及認列投資損益
- 公司登記資本額、實收資本額、代表人及登記狀態
- 上市、上櫃、興櫃、公發未上市櫃或未見於公開市場名單
- 代表人及董監事的其他公司職務
- IPO 與 SPO／籌資潛力的初步承銷篩選欄位
- 可篩選並保留來源軌跡的 Excel 研究文件

Skill 會把有股權或控制證據的關係，與僅因代表人／董監事重疊形成的關聯分開，避免將人脈關聯誤列為母子公司。

## 安裝

在 AGENT 中輸入：

```text
請從以下 GitHub 網址安裝這個 Skill：
https://github.com/aa1807848522-glitch/taiwan-company-network-skill/tree/main/skills/research-taiwan-company-network
```

或使用 Skill Installer：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo aa1807848522-glitch/taiwan-company-network-skill \
  --path skills/research-taiwan-company-network
```

安裝完成後，下一個對話回合即可使用。

## 使用範例

```text
請用 $research-taiwan-company-network 研究 3707，整理完整公司關聯並輸出 Excel。
```

```text
請用 $research-taiwan-company-network 研究統編 12138114，並篩選可能的 IPO 或 SPO 潛在客戶。
```

## 主要資料來源

- 經濟部商工行政資料開放平臺與 FindBiz
- 公開資訊觀測站及 TWSE／TPEx 公開資料
- 年報、財務報表附註及重大訊息
- 全國公司登記董監事資料集

使用時需要網路存取權限。部分私人公司股權、境外公司資料或未公開投資損益可能沒有完整公開資訊；Skill 會以 `未公開揭露`、`待核實` 或信心等級標示，不會將空白推定為零。

## 免責聲明

本 Skill 提供公開資料整理、研究與初步承銷潛客篩選，不構成法律、會計、投資或承銷建議。中文姓名可能存在同名情形，重要的董監事關聯仍應以官方登記及其他第一手資料交叉核實。

## License

MIT License
