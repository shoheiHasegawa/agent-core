#!/usr/bin/env python3
"""
tools/authenticate_google.py

Google Tasks API & Calendar API のための OAuth 2.0 認可ワンショットスクリプト。
社長のブラウザを開いて認可フローを実行し、token.json を保存します。
"""

import sys
from pathlib import Path


def authenticate(
    client_secrets_path: Path = Path("config/client_secret.json"),
    token_path: Path = Path("config/token.json"),
) -> None:
    scopes = [
        "https://www.googleapis.com/auth/tasks",
        "https://www.googleapis.com/auth/calendar.events.readonly",
    ]

    if not client_secrets_path.exists():
        print(f"❌ Error: Client secret file not found at: {client_secrets_path.resolve()}")
        print("💡 Please follow 'docs/02_oauth_setup_guide.md' to download the OAuth client JSON")
        print("   and place it at 'config/client_secret.json'.")
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow

        flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_path), scopes)
        print("🌐 Opening browser for Google OAuth authorization...")
        creds = flow.run_local_server(port=0)

        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

        print(f"✅ Authorization successful! Token saved to: {token_path.resolve()}")
        print("🎉 You can now use Google Tasks & Calendar synchronization seamlessly.")
    except Exception as e:
        print(f"❌ Authorization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    authenticate()
