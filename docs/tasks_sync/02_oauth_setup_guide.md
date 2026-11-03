# 🔑 Google Tasks & Calendar OAuth 2.0 認証セットアップ手順書

Google Tasks API はサービスアカウント（`service_account`）での操作をサポートしていないため、**社長の個人 Google アカウントによる OAuth 2.0 認証（User Credentials）** を利用します。

---

## 1. 概要 (Architecture & Flow)

```text
[Google Cloud Console]
       │
       ▼ OAuth 2.0 クライアント作成（デスクトップ アプリ）
[agent-core/config/client_secret.json]
       │
       ▼ 初回認可スクリプト実行（ブラウザが開き「許可」）
[agent-core/config/token.json] (リフレッシュトークン内包・.gitignore対象)
       │
       ▼ 今後自動更新（完全ステートレス）
[core-service CLI] ➔ Google Tasks & Calendar API
```

---

## 2. Google Cloud Console での準備手順（初回1回のみ・所要時間3分）

1. **Google Cloud Console を開く**:
   - [Google Cloud Console](https://console.cloud.google.com/) にアクセス。
   - プロジェクトを選択（既存の You_Inc プロジェクト等）。
2. **必要な API を有効化**:
   - 「APIとサービス」➔「ライブラリ」から以下を検索して **有効化**：
     - **Google Tasks API**（必須）
     - **Google Calendar API**（有効化済みなら不要）
3. **OAuth 同意画面の設定（未設定の場合のみ）**:
   - ユーザータイプ: **「外部」**（個人Gmailの場合）
   - アプリ名: `You_Inc Secretary`
   - テストユーザー: 社長の Google アドレス（`@gmail.com` 等）を追加。
4. **OAuth 2.0 クライアント ID の作成**:
   - 「APIとサービス」➔「認証情報」➔「認証情報を作成」➔ **「OAuth クライアント ID」** を選択。
   - アプリケーションの種類: **「デスクトップ アプリ」**
   - 名前: `You_Inc Desktop Client`
   - 「作成」をクリック。
5. **JSON をダウンロード**:
   - ダウンロードした JSON ファイルを以下のパスに配置します：
     `agent-core/config/client_secret.json`
     *(※ `.gitignore` されているため Git にはコミットされません)*

---

## 3. 認可の実行（トークン取得）

JSON を配置後、初回認可コマンドを実行します：

```bash
uv run python tools/authenticate_google.py
```
- ブラウザが自動で立ち上がり、Google アカウントのログイン・権限許可画面が表示されます。
- 「許可」をクリックすると、`agent-core/config/token.json` が自動生成されます。
- 以降はリフレッシュトークンにより恒久的にバックグラウンドで自動更新されるため、再ログインは不要です。

---

## 4. 必要なスコープ (Scopes)

- `https://www.googleapis.com/auth/tasks`（Tasks の読み書き・完了）
- `https://www.googleapis.com/auth/calendar.events.readonly`（カレンダー予定の読み取り）
