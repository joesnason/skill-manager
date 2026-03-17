# Skill Manager

一個用於管理 Claude Code Skills 的桌面 GUI 工具，以 Python + tkinter 開發。

## 功能

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

## 執行方式

```bash
python3 skill_manager.py
```

## Skill 目錄位置

```
~/.claude/skills/
```

## 注意事項

- 刪除操作**無法復原**，請謹慎操作。
- 在 macOS 上，按鈕使用 `tk.Label` 模擬實作，以確保背景顏色正確顯示（macOS 原生 tkinter `tk.Button` 不支援自訂背景色）。
