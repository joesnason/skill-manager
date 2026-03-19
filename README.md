# Skill Manager

一個用於管理 Claude Code Skills 的桌面 GUI 工具，以 Python + tkinter 開發。

## 功能

- **Install**：從本地路徑或 Git URL 安裝 skill（支援目錄、`.skill` 檔、`.md` 檔，以及 `git clone`）。安裝完成後自動刷新清單。
- **自動建立目錄**：若 `~/.claude/skills/` 不存在，安裝時會自動建立；若連 `~/.claude/` 都不存在，則顯示錯誤提示。
- **列出已安裝的 Skills**：自動掃描 `~/.claude/skills/` 目錄，顯示所有已安裝的 skill 名稱與描述。
- **Refresh**：重新掃描目錄，即時更新清單。
- **Remove**：從清單中選擇並刪除指定的 skill（刪除前會顯示確認對話框）。
- **狀態列**：顯示目前已安裝的 skill 總數。

## 支援的 Skill 格式

| 格式 | 說明 |
|------|------|
| 目錄（含 `SKILL.md`）| 標準 skill 目錄格式 |
| `.skill` 壓縮檔 | zip 封裝的 skill 套件 |
| `.md` 檔案 | 舊版單檔格式（legacy） |

Skill 名稱與描述從各格式內的 `SKILL.md` YAML frontmatter 中讀取。

## 環境需求

- Python 3.10+
- tkinter（Python 標準函式庫，通常已內建）
- git（安裝 Git URL 時需要）
- 無第三方套件依賴（詳見 `requirements.txt`）

## 執行方式

```bash
pip3 install -r requirements.txt  # 無套件需安裝，可省略
python3 skill_manager.py
```

## Skill 目錄位置

```
~/.claude/skills/
```

## 注意事項

- 刪除操作**無法復原**，請謹慎操作。
- Install 操作以背景執行緒執行，不會凍結 UI；安裝完成後自動刷新清單。
- 安裝前會檢查 `~/.claude/` 是否存在（未安裝 Claude Code 時顯示錯誤）；`~/.claude/skills/` 若不存在則自動建立。
- 在 macOS 上，按鈕使用 `tk.Label` 模擬實作，以確保背景顏色正確顯示（macOS 原生 tkinter `tk.Button` 不支援自訂背景色）。
