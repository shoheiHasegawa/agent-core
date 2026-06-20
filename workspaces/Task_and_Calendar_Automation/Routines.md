# Routines & Fixed Schedules

本ドキュメントは、COO Agentが自動的に読み込んでGoogle Calendar（`hs.app1ifeaut0@gmail.com`）に時間枠を確保するための、定例業務（ルーティン）、固定の会社予定、およびライフサイクル（習慣・家事・趣味）を定義する「唯一の真実のソース（SSOT）」です。

---

## 📅 定例・固定予定一覧

### 1. 🏢 会社関連・講師・研修
| 予定名 | 発生周期・日付 | 時間 | 分類 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| **帰社日** | 毎月第3金曜日 | 18:00 ~ 20:00 | 会社定例 | 旧名: BOLDAY。この日は出社日となる |
| **帰社日 懇親会** | 毎月第3金曜日 | 20:00 ~ 22:00 | 会社定例 | |
| **勤怠入力完了と勤務表の提出** | 毎月末日 | 終日 | 事務手続き | MUSTタスク |
| **毎月の目標エビデンス・進捗提出** | 毎月最終土日 | 任意のMUST枠 | 事務手続き | 土日のタスクとして実行 |
| **勉強会(サブ講師)** | 毎月第3火曜日 | 20:00 ~ 22:00 | 講師業務 | 旧名: Oracle基礎勉強会。サブ講師として参加（学習ではない） |
| **リーダ育成研修** | 毎月第4木曜日 | 20:00 ~ 22:00 | 研修 | 1月〜6月限定（2026年6月が最終回） |
| **教える力育成勉強会** | 2026-06-10, 2026-07-01, 2026-07-15 | 20:00 ~ 22:00 | 研修・育成 | 全8回開催、7/15が最終回 |

### 2. ☀️ 朝・夜のルーティン & 平日ライフサイクル

#### 💻 月曜日・金曜日（在宅勤務モデル）
* ※ **注意**: 毎月第3金曜日（帰社日）のみ、在宅ではなく**「出社勤務モデル」**となります。
* **05:00 ~ 05:15**: 朝の起動ジャーナリング（起動・タスク確認）
* **05:15 ~ 07:00**: **フォーカス時間**（学習、Second Brain開発など頭を使うインプット・作業）
* **07:00 ~ 09:00**: **筋トレ ＋ 朝食・準備時間**（運動で頭をリフレッシュし、9時始業へ完璧につなげる）
* **09:00**: 在宅勤務開始

#### 🚶 火曜日・水曜日・木曜日 ＆ 帰社日の金曜日（出社勤務モデル）
* **05:00 ~ 05:15**: 朝の起動ジャーナリング（起動・タスク確認）
* **05:15 ~ 07:00**: **フォーカス時間**（学習、Second Brain開発など。※週の真ん中の水曜などは筋トレでも可）
* **07:00 ~ 08:00**: 出社準備・移動（この通勤時間がリフレッシュタイムに）
* **08:00 ~ 09:00**: **朝の読書インプット**（会社デスクで集中して読書）
* **09:00**: 勤務開始

| 予定名 | 発生周期・日付 | 時間 | 分類 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| **朝の起動ジャーナリング** | 毎日 | 05:00 ~ 05:15 | ルーティン | 起床後すぐに実施。前夜振り返り未実施ならここで吸収 |
| **朝のフォーカス時間** | 平日（月〜金） | 05:15 ~ 07:00 | フォーカス | 開発、Second Brain構築、資格学習などの知的作業 |
| **在宅リフレッシュ（筋トレ＋朝食準備）** | 毎週月・金 | 07:00 ~ 09:00 | 運動・準備 | 在宅勤務日のみ。※第3金曜日は除く |
| **朝の読書インプット** | 平日（火〜木）＆ 第3金曜日 | 08:00 ~ 09:00 | インプット | 出社日限定。通勤でのリフレッシュ後、集中して読書 |
| **夜の振り返りジャーナリング**| 毎日 | 22:30 ~ 22:45 | ルーティン | 睡眠前のリセット。スキップ時は翌朝実施 |

### 3. 🏌️ 週末アクティビティ & 週末リセット（家事）
* **土日の家事・買い出し**:
  * カレンダーで時間をガチガチに固定せず、**「土日リセット枠（タスクプール）」**として管理。雨などの天候や体調に合わせて柔軟に消化する。
* **低頻度の家事（4〜5週に1回）**:
  * トイレ掃除, 風呂掃除, 排水溝掃除などをCOO Agentが「良きタイミング」で土日のタスクリストに自動注入する。

| 予定名 | 発生周期・日付 | 時間 | 分類 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| **ゴルフスクール＆練習** | 毎週日曜日 | 09:05 ~ 12:00 | 趣味・運動 | レッスン（9:05~10:05）＋居残り練習1〜2時間分をブロック |
| **週末リセット（掃除・洗濯・買出）** | 毎週土日 | 任意の時間 | 家事タスク | 土日のタスクプールとして管理し、週末にリセット実行 |
| **低頻度ローテーション家事** | 4〜5週に1回 | 任意の時間（土日）| 家事タスク | トイレ、風呂、排水溝などを週替わりで自動タスク化 |

---

## 🤖 COO Agent パース用構造化データ (YAML)

```yaml
routines:
  # 🏢 会社関連・講師・研修
  - name: "帰社日"
    type: "recurrent"
    rule:
      freq: "monthly"
      byday: "3FR"
    time:
      start: "18:00"
      end: "20:00"
    category: "company_event"

  - name: "帰社日 懇親会"
    type: "recurrent"
    rule:
      freq: "monthly"
      byday: "3FR"
    time:
      start: "20:00"
      end: "22:00"
    category: "company_event"

  - name: "勤怠入力完了と勤務表の提出"
    type: "recurrent"
    rule:
      freq: "monthly"
      bymonthday: -1
    time:
      all_day: true
    category: "administrative"

  - name: "毎月の目標エビデンス・進捗提出"
    type: "recurrent"
    rule:
      freq: "monthly"
      byday: "last_weekend"
    time:
      start: "10:00"
      end: "12:00"
    category: "administrative"

  - name: "勉強会(サブ講師)"
    type: "recurrent"
    rule:
      freq: "monthly"
      byday: "3TU"
    time:
      start: "20:00"
      end: "22:00"
    category: "instructor_duty"

  - name: "リーダ育成研修"
    type: "recurrent"
    rule:
      freq: "monthly"
      byday: "4TH"
      until: "2026-06-30"
    time:
      start: "20:00"
      end: "22:00"
    category: "training"

  - name: "教える力育成勉強会 (直近確定分)"
    type: "specific_date"
    dates:
      - "2026-06-10"
      - "2026-07-01"
      - "2026-07-15"
    time:
      start: "20:00"
      end: "22:00"
    category: "training"

  # ☀️ 朝・夜のルーティン & ライフサイクル
  - name: "朝の起動ジャーナリング"
    type: "recurrent"
    rule:
      freq: "daily"
    time:
      start: "05:00"
      end: "05:15"
    category: "routine"

  - name: "朝のフォーカス時間"
    type: "recurrent"
    rule:
      freq: "weekly"
      byday: "MO,TU,WE,TH,FR"
    time:
      start: "05:15"
      end: "07:00"
    category: "focus_work"

  - name: "在宅リフレッシュ（筋トレ＋朝食準備）"
    type: "recurrent"
    rule:
      freq: "weekly"
      byday: "MO,FR"
      exclude_on_company_events: true # 帰社日などの会社行事（出社日）と重なる日は除外するルール
    time:
      start: "07:00"
      end: "09:00"
    category: "workout"

  - name: "朝の読書インプット"
    type: "recurrent"
    rule:
      freq: "weekly"
      byday: "TU,WE,TH"
      include_on_company_event_days: ["3FR"] # 毎月第3金曜日（帰社日）も出社するため、この読書枠を適用する
    time:
      start: "08:00"
      end: "09:00"
    category: "reading"

  - name: "勤務時間 (Work Hours)"
    type: "recurrent"
    rule:
      freq: "weekly"
      byday: "MO,TU,WE,TH,FR"
      exclude_on_holidays: true
    time:
      start: "09:00"
      end: "18:00"
    category: "work"

  - name: "夜の振り返りジャーナリング"
    type: "recurrent"
    rule:
      freq: "daily"
    time:
      start: "22:30"
      end: "22:45"
    category: "routine"

  # 🏌️ 週末アクティビティ & 週末リセット
  - name: "ゴルフスクール＆練習"
    type: "recurrent"
    rule:
      freq: "weekly"
      byday: "SU"
    time:
      start: "09:05"
      end: "12:00"
    category: "hobby"

  - name: "週末リセット（掃除・洗濯・買出）"
    type: "recurrent"
    rule:
      freq: "weekly"
      byday: "SA,SU"
    time:
      flexible: true
    category: "housework"

  - name: "低頻度ローテーション家事"
    type: "recurrent"
    rule:
      freq: "monthly_rotation"
      rotation_items:
        - "風呂掃除（カビ対策・徹底洗浄）"
        - "排水溝掃除（キッチン・風呂・洗面台）"
        - "トイレ徹底掃除＆フィルター換気扇"
    time:
      flexible: true
    category: "housework"
```
