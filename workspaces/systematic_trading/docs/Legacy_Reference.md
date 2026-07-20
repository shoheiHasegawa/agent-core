# Legacy Trading Automation Code
## deploy.sh
```
#!/bin/bash

# --- 設定 ---
# iCloud上のObsidianのパス
ICLOUD_VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Mobile_Vault"
DEST_DIR="$ICLOUD_VAULT/99_System/Scripts"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

# デプロイ対象
FILES=("generate_trade_log.py" "trade_log_template.md")

echo "Starting deploy to iCloud..."

# デプロイ先ディレクトリの作成
DIRS=(
    "$ICLOUD_VAULT/00_Inbox"
    "$ICLOUD_VAULT/99_System/Scripts"
    "$ICLOUD_VAULT/99_System/Attachments"
    "$ICLOUD_VAULT/99_System/Templates"
)

echo "Preparing directory structure in iCloud..."
for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "Creating directory: $dir"
        mkdir -p "$dir"
    fi
done

# ファイルのコピー
# 1. Pythonスクリプト
if [ -f "$SRC_DIR/generate_trade_log.py" ]; then
    cp "$SRC_DIR/generate_trade_log.py" "$ICLOUD_VAULT/99_System/Scripts/"
    echo "Deployed: generate_trade_log.py -> Scripts/"
fi

# 2. テンプレート
if [ -f "$SRC_DIR/trade_log_template.md" ]; then
    cp "$SRC_DIR/trade_log_template.md" "$ICLOUD_VAULT/99_System/Templates/"
    echo "Deployed: trade_log_template.md -> Templates/"
fi

echo "Deploy complete. a-Shell on iPhone can now run the script from vault/99_System/Scripts/"
```

## generate_trade_log.py
```
import os
import shutil
from datetime import datetime
import json

# --- 設定 ---
# プログラムの場所から自動でルートを特定する
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

DEFAULT_CONFIG = {
    "INBOX_DIR": os.path.join(VAULT_ROOT, "00_Inbox"),
    "VAULT_ROOT": VAULT_ROOT,
    "ATTACHMENTS_PATH": "99_System/Attachments",
    "OUTBOX_PATH": os.path.join(VAULT_ROOT, "00_Inbox"),
    "TEMPLATE_FILE": os.path.join(VAULT_ROOT, "99_System/Templates/trade_log_template.md")
}

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG

def main():
    config = load_config()
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    display_time = now.strftime("%Y-%m-%d %H:%M")

    # 1. 画像の取得
    inbox = config["INBOX_DIR"]
    
    # ディレクトリがなければ作成する（親切設計）
    if not os.path.exists(inbox):
        print(f"Directory not found. Creating: {inbox}")
        os.makedirs(inbox, exist_ok=True)
        print("Please put your screenshots in the folder and run again.")
        return

    # 最新3枚を取得
    files = [f for f in os.listdir(inbox) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if len(files) < 3:
        print(f"Error: Need at least 3 images in inbox. Found: {len(files)}")
        return

    # 修正日時順にソート (古い順)
    # ユーザーの運用ルール: 週足(1番目) -> 日足(2番目) -> 30分足(3番目) に撮影
    files.sort(key=lambda x: os.path.getmtime(os.path.join(inbox, x)))
    target_files = files[-3:] # 最新の3枚を、撮影した順番（古い順）で取得

    labels = ["3_weekly", "2_daily", "1_30m"]
    img_links = {}

    attachments_dir = os.path.join(config["VAULT_ROOT"], config["ATTACHMENTS_PATH"])
    os.makedirs(attachments_dir, exist_ok=True)

    for img, label in zip(target_files, labels):
        ext = os.path.splitext(img)[1]
        new_name = f"{timestamp}_{label}{ext}"
        src_path = os.path.join(inbox, img)
        dst_path = os.path.join(attachments_dir, new_name)
        
        # 移動
        shutil.move(src_path, dst_path)
        img_links[label] = new_name
        print(f"Moved: {img} -> {new_name}")

    # 2. Markdown生成
    template_path = os.path.join(os.path.dirname(__file__), config["TEMPLATE_FILE"])
    if not os.path.exists(template_path):
        print(f"Error: Template file not found: {template_path}")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 置換 (パスを含める)
    attachments_prefix = config["ATTACHMENTS_PATH"] + "/"
    content = content.replace("{{DATETIME}}", display_time)
    content = content.replace("{{IMAGE_WEEKLY}}", attachments_prefix + img_links["3_weekly"])
    content = content.replace("{{IMAGE_DAILY}}", attachments_prefix + img_links["2_daily"])
    content = content.replace("{{IMAGE_30M}}", attachments_prefix + img_links["1_30m"])

    # 3. 保存
    md_filename = f"{timestamp}_Trade.md"
    outbox_dir = os.path.join(config["VAULT_ROOT"], config["OUTBOX_PATH"])
    os.makedirs(outbox_dir, exist_ok=True)
    
    md_path = os.path.join(outbox_dir, md_filename)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Success: Generated {md_path}")

if __name__ == "__main__":
    main()
```

## spec.md
```
# Specification: generate_trade_log.py

## 1. 概要
このスクリプトは、トレードのスクリーンショット（週足・日足・30分足）から、タイムスタンプ付きの画像ファイル名へのリネーム、移動、およびObsidian形式のトレード日誌（Markdown）を自動生成する。

## 2. ターゲット環境と技術的制約
*   **実行環境**: iOS アプリ「a-Shell」上の Python 3。
*   **ファイルシステム**: iCloud Drive上の Obsidian Vault 内で動作。
*   **トリガー**: iOSショートカット経由での実行。
*   **制約**: 
    *   外部ライブラリへの依存を最小限に抑える（標準ライブラリ `os`, `shutil`, `datetime`, `json` を使用）。
    *   パス解決は、スクリプトの配置場所 (`99_System/Scripts`) からの相対パス、または設定ファイルに基づき動的に行う。

## 3. デプロイ・運用フロー
1.  **開発**: PC（Mac）上の `daily-tools/trading-automation/` でコードを修正。
2.  **同期**: `deploy.sh` を実行し、iCloud上の `Mobile_Vault/99_System/Scripts/` へファイルをコピー。
3.  **実行**: iPhoneのアクションボタンからiOSショートカットを起動し、a-Shell経由で `python3 generate_trade_log.py` が呼び出される。

## 4. 入出力仕様
### 4.1 入力
*   **ディレクトリ**: `00_Inbox`
*   **対象ファイル**: 直近に手動保存された最新3枚の画像ファイル (`.png`, `.jpg`, `.jpeg`)。
*   **前提**: 画像の作成日時（古い順）が、週足 -> 日足 -> 30分足の順であること。

### 4.2 出力
*   **画像**: `99_System/Attachments/` へ移動。
*   **Markdown**: `00_Inbox/` に生成。

## 5. 処理ロジック (コア仕様)
### 5.1 タイムスタンプ
ファイル名に使用するタイムスタンプ書式は `YYYYMMDD_HHMMSS` とする。

### 5.2 画像命名規則とソート制御
iOSショートカット側でクリップボードにコピーする際の順序を「週足 -> 日足 -> 30分足」で固定するため、以下のプレフィックスを付与する。
*   **週足**: `{timestamp}_3_weekly.ext`
*   **日足**: `{timestamp}_2_daily.ext`
*   **30分足**: `{timestamp}_1_30m.ext`
※ショートカット側で「名前」を「ZからA（降順）」でソートすることで、常に 3 -> 2 -> 1 の順で処理されることを保証する。

### 5.3 Markdown生成
`trade_log_template.md` を読み込み、以下のプレースホルダーを置換する。
*   `{{DATETIME}}`: `YYYY-MM-DD HH:MM`
*   `{{IMAGE_WEEKLY}}`: `99_System/Attachments/{timestamp}_3_weekly.ext`
*   `{{IMAGE_DAILY}}`: `99_System/Attachments/{timestamp}_2_daily.ext`
*   `{{IMAGE_30M}}`: `99_System/Attachments/{timestamp}_1_30m.ext`

## 6. エラーハンドリング
*   `00_Inbox` 内の画像が3枚未満の場合はエラーメッセージを出力して終了。
*   テンプレートファイルが存在しない場合は警告を表示。
*   重複ファイルが存在する場合は、安全のため上書きせずスキップ、またはタイムスタンプによるユニーク性を確保。
```

## trade_log_template.md
```
# トレード日誌：{{DATETIME}}

## 1. 環境認識（週足）
![[{{IMAGE_WEEKLY}}]]

## 2. トレンド把握（日足）
![[{{IMAGE_DAILY}}]]

## 3. エントリートリガー（30分足）
![[{{IMAGE_30M}}]]

---
## Gemini AI分析フィードバック
(ここにGeminiの分析結果を貼り付ける)
```

