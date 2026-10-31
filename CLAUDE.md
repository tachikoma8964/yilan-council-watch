# 宜蘭縣議會觀測

給一般縣民看的宜蘭縣議會公開資料站。靜態網站,資料來自宜蘭縣議會官網(www.ilcc.gov.tw)。

## 原則

- 只呈現可驗證的量化資訊(件數、日期、原文連結)。不做政治評價,不做排名。
- 不用政黨色。黨籍只以文字標示。強調色不用藍色或綠色。
- 每個數字都要能追到官網原文,頁面要標示資料來源與擷取日期。
- 範例或假資料必須明確標示「範例」。
- Avoid unnecessary secondary labels and descriptions. Let the layout do the explaining.

## 技術

- 靜態 HTML/CSS/JS,不使用 Node 建置。這台機器沒有 Node。
- 資料抓取用 Python 3,腳本放 `scripts/`,原始檔放 `data/raw/`,整理後的 JSON 放 `data/processed/`。
- 官網是 Big5 編碼的舊式 ASP 網站,抓取時要用 Big5 解碼。

## 前端

- 手機優先,同時支援 iOS Safari 與 Android Chrome。可點目標至少 44px,考慮 `env(safe-area-inset-*)`。
- CSS 使用 `:root` 設計 token,不寫死色碼。不用行內樣式(僅允許用來傳遞資料的 CSS 自訂屬性)。
- 通過 WCAG 2.2 AA:文字對比 4.5:1、鍵盤可操作、`prefers-reduced-motion`。
- 字體用系統字體疊,不為內文載入網路字體。

## 設計規範

- 已選定視覺方向:**地籍圖**。把縣分成編號的選區地塊,點選地塊看議員與議案。完整合約在 `.impeccable/` 的 surface brief(`impeccable surface-brief read site/index.html`)。
- 白底、黑色細線兩種粗細、紅色地號(#c1272d)是唯一強調色、選取地塊用淡色填色。沒有漸層、陰影、卡片、數字面板、標題上方小標籤、編號 01/02/03。
- 選區邊界在取得官方資料前一律標示「示意」。
- `site/style-sample/` 是被淘汰的 A、B 兩版與決策過程的樣板,保留作參考,不要沿用其版面。
- 同時遵守 `taste-accessibility`、`taste-typography`、`taste-color`、`taste-code-craft`、`taste-web-performance`。
- 控制項(下拉選單、按鈕)的邊框對比至少 3:1,用 `--control-border`,不要用 `--line-strong`。
- 網路字體只在需要時載入(B 的宋體只在 B 風格載入)。

## 檢查工具

- Node 24 裝在 `~/.local/node`,使用前先 `export PATH="$HOME/.local/node/bin:$PATH"`。
- 設計檢查:`npx impeccable detect http://127.0.0.1:8791/<頁面>`,對比與字級規則只在掃描網址時才會執行。
- 效能與無障礙:`CHROME_PATH` 指向 Edge 後執行 `npx lighthouse <網址>`。
- 其他協作者需自行執行 `npx impeccable install --providers=claude --scope=project`。
- 本機預覽:在 `site/` 內執行 `python3 -m http.server 8791`。

## 工作方式

- 用最省 token 的方式:回覆簡短、批次執行指令、只讀需要的檔案片段、只在做設計決定時才看圖。
- 政府提案不納入主要資料,只在網站備註說明。議員黨籍官網空白者不顯示黨籍,待核對後補。
- 回報錯誤信箱、單位名稱先留「待填」。GitHub 帳號之後提供。

## 資料範圍

第 19、20 屆。先抓議員名單、議案資料庫、議事日程。表決紀錄與質詢內文是否可得尚待確認。
