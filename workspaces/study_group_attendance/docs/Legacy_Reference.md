# Legacy Study Group Attendance Code
## test_script.js
```
// Fake environment to simulate the crash
const { execSync } = require('child_process');
// We cannot run GAS locally directly. But we can build a mini GAS claps project to test it.
```

## System_Specification.md
```
# Study Group DX - システム仕様書

## 1. システム構成・アーキテクチャ
本システムは「マスタースプレッドシート（ジェネレーター）」と、それによって生成される「期別・勉強会別スプレッドシート（子）」および「Googleフォーム」で構成されます。

### 1.1 ジェネレーターの役割
- UIは「対象とする期」と「名称」の入力のみに極限まで削ぎ落とされています。
- 設定（Settingsシート）のカスタムメニューを実行すると、あらかじめシステムコード（`system_builder.js`）内にハードコードされたテンプレートID（ひな形スプレッドシート）を複製し、新しい独立した出欠管理システムを全自動で構築します。

### 1.2 設定情報（時間・遅刻許容）の責務
- システム内の「基本開始時刻」「遅刻許容時間」といった全てのスケジューリングロジックは、生成されたスプレッドシート内の `Schedule_DB` シートに**完全に集約（一本化）**されています。
- 管理者は `Schedule_DB` で「通常回ごとの時間」「補講回のみの特別時間（遅刻禁止）」などを超柔軟に設定でき、関数がそれを直接参照してリアルタイムで遅刻判定を下します。

## 2. コア機能：ハッシュ認証と自動防衛

### 2.1 不正打刻のブロック（自己防衛アーキテクチャ）
当システムの最大の特徴は、Googleフォームを通じた「代返」や「URLの使い回し」を完全に防衛する**ハッシュ認証ロジック**です。
- 管理者のみが発行できる「リアル打刻用URL」と「リモート打刻用URL」には、その日の日付とシークレットキーで計算された**不可逆なハッシュ値**（例：`29480273119`）が事前入力（Prefilled）されています。
- 生徒には「氏名（社員番号）」のみを打刻させ、システム側で受信したハッシュ値を検算し、一致した場合のみ出席（リアル/リモート）として受理します。
- **改ざん検知**: 受信したハッシュが無効・または空欄の場合、即座に背景が真っ赤に染まり `❌ 不正・無効` としてブロックされ、集計側（Progress_Master）への波及を完全に遮断します。

### 2.2 特権管理者による手動承認（バックドア・リカバリ）
万が一、生徒が打刻できずに管理者が直接ログ（`Log_Attendance`）に手入力で救済追加を行う場合への備えです。
- 管理者がシステムの `G列（手動区分）` に「リアル」または「リモート」をプルダウンで選択した瞬間に、ハッシュ認証のブロックを貫通し、強制的に `手動承認(リアル)` / `手動承認(リモート)` として正規の出席扱いへとオーバーライド（上書き）されます。
- **フォールバック**: プルダウン以外の文字（例: 「OK」や「救済」など）が入力された場合も、一律 `手動承認(リアル)` として受理されます。メモを残す場合はH列（メモ）を使用してください。

## 3. シート構成とカラーユニバーサルデザイン
各シートの列（ヘッダ）は、管理者にとって直感的に「触っていい場所か」が分かるように厳密な色分けルールが適用されています。

**ヘッダー共通デザイン**: 全シートのヘッダー行は `#434343`（ダークグレー）背景 / 白文字 / 太字で統一します。

**セルの役割別配色ルール:**

- 🟣 **紫色（自動適用）**: Googleフォームが自動生成する生の回答データ領域。（絶対保護）
- 🔵 **薄い青色 (`#cfe2f3`)**: システム参照・計算領域。触る必要はありません。（絶対保護）
- 🟠 **薄いオレンジ (`#fce5cd`)**: 不正検知・判定状況を示すウォッチ領域。
- 🟡 **薄い黄色 (`#fff2cc`)**: **唯一、管理者が手入力で編集してよい領域。（管理者備考など）**
- ⬜ **薄いグレー (`#f3f3f3`)**: 自動計算保護エリア。値が未確定（将来の日付など）であっても、数式が展開されているエリアです。**手入力禁止。**
- 🔴 **赤色ヘッダー（アラート列）**: 各ログシートの右端に配置される「⚠️ システムMSG」列のヘッダー。エラーを言葉で通知します。

### 3.1 Progress_Master の列構成（スキーマ）

集計の要となる `Progress_Master` は以下の10列で構成されます：

1. **社員番号**: `Member_DB` A列からの一意な抽出。
2. **氏名**: `Member_DB` からの VLOOKUP 参照。
3. **拠点**: `Member_DB` からの VLOOKUP 参照。
4. **出席回数**: 全開催日のうち「出席」扱い（リアル/リモート/届出有）の合計。
5. **リアル回数**: 出席のうち「リアル」のみの合計。
6. **リアル参加率**: リアル回数 / 出席回数。
7. **アンケート提出数**: `Log_ExternalSurvey` への回答回数。
8. **課題提出物**: （手入力用）課題の提出状況。
9. **最終試験合否**: （手入力用）試験結果。
10. **資格取得**: （手入力用）関連資格の取得有無。

> [!NOTE]
> K列以降は `Schedule_DB` に基づき、日付ごとの出欠詳細が動的に展開されます。

## 4. 動的数式プロビジョニング（自己修復・オートフィルアーキテクチャ）
Google Forms連携時に行が挿入されて配列展開が寸断される問題（ARRAYFORMULAの構造的限界）や、最新のGoogle Sheets「Table機能」との競合、条件付き書式の剥奪を防ぐため、本システムは数式の展開プロセスをGASのイベントトリガーに完全委譲しています。

- **フォーム送信連携 (`fillFormulasOnSubmit`)**: フォームから新しい回答が送信・挿入された瞬間に、該当行にのみ必要なシステム判定数式を物理的に書き込むことで、Google Sheetsの仕様変更に左右されない計算精度を保証します。
- **手動編集連携 (`fillFormulasOnEdit`/`onEditRouter`)**: 管理者が手動で行を追加したり、不具合データを直接修正・上書きした場合にも、欠落している数式を検知して瞬時に自動補完します。
- **条件付き書式の自己修復 (`healLogConditionalFormats`)**: Table化の影響で、エラー検知時の赤色ハイライト（条件付き書式）が破壊・削除された場合でも、同期実行時に自動的に書式設定を復元しUIの安全性を担保します。
- **数式の自己修復 (`healLogFormulas`)**: フォーム連携による数式消去が発生した場合、ヘッダー行・データ行の数式を全行にわたって再展開し、H列（システムMSG）の警告数式も合わせて復旧します。

## 5. 社員番号の型安全設計

Googleフォームや手動入力・一括貼り付けなど、社員番号（数字列）の入力経路が複数あるため、保存時のデータ型（文字列 `"12345"` または数値 `12345`）は経路によって異なります。これがVLOOKUPの照合失敗を引き起こす根本原因となります。

### 5.1 採用方針: 「検索キー側の `TEXT(VALUE(),"0")` 正規化」

VLOOKUP の **検索キー側** を `TEXT(VALUE(B2),"0")` で文字列に変換してから照合します。`Member_DB` A列は `@`（テキスト）書式で管理されるため、検索キーを文字列化することで **B2の元の型（数値・文字列どちら）に関わらず** 常にマッチします。

```
// 型正規化パターン（Log_Att/Log_Notice のF列 全照合箇所で統一）
IFERROR(VLOOKUP(TEXT(VALUE(B2),"0"), Member_DB!$A:$B, 2, FALSE), "#N/A")
//              ↑ 検索キーを常に文字列"12345"へ正規化
//                                   ↑ Member_DB A列は @書式で "12345" テキスト保持
```

| 入力経路 | B列に保存される型 | TEXT(VALUE(B2),"0") | Member_DB A | 照合 |
|:---|:---|:---|:---|:---|
| フォーム送信（テキスト設問） | 文字列 `"12345"` | `"12345"` | `"12345"` | ✅ |
| 手動入力（`@`書式列） | 文字列 `"12345"` | `"12345"` | `"12345"` | ✅ |
| 一括貼り付け（書式崩れで数値） | 数値 `12345` | `"12345"` | `"12345"` | ✅ |

> [!NOTE]
> 過去に試みた「IFERRORダブル試行」パターン（B2をそのまま照合→VALUE(B2)でフォールバック）は、B2が数値かつMember_DBがテキストのケースで **両試行とも失敗する**ことが実運用で判明し廃止。

> [!NOTE]
> `ARRAYFORMULA` を使う `Progress_Master` B/C列は `IFERROR(VLOOKUP(A2:A,...), IFERROR(VLOOKUP(VALUE(A2:A),...)))` のIFERRORダブル試行を継続使用（ARRAYFORMULAコンテキストでは `TEXT(VALUE(A2:A),"0")` のkey正規化も検討可）。
> K2 の判定ロジック（MAKEARRAY+LET内）では `TEXT(VALUE(emp_id),"0")` での正規化を継続使用。

### 5.2 二重の安全機構

- **照合側（数式）**: `TEXT(VALUE(B2),"0")` で検索キーを文字列に正規化し、型に依存しない照合を保証。
- **入力側（onEdit）**: `Member_DB` A列が編集・貼り付けされた際、`onEditRouter` が即座に `@`（テキスト）書式を強制適用し、参照される側を常にテキストで維持します。

### 5.3 対象列の全量整理

| シート | 列 | 対応内容 |
|:---|:---|:---|
| `Log_Attendance` | B列（社員番号）→ F列 VLOOKUP | 検索キー `TEXT(VALUE(B2),"0")` で正規化 |
| `Log_Notice` | C列（社員番号）→ F列 VLOOKUP | 検索キー `TEXT(VALUE(C2),"0")` で正規化 |
| `Member_DB` | A列（社員番号） | `@`書式 ＋ onEdit による書式自動修復（参照される側をテキストで維持） |
| `Progress_Master` | B/C列 VLOOKUP | IFERRORダブル試行（ARRAYFORMULA内） |
| `Progress_Master` | G列 COUNTIF | `TEXT(VALUE(),"0")` で正規化（ARRAYFORMULAコンテキスト） |
| `Progress_Master` | K2 判定ロジック（MAKEARRAY+LET内） | `TEXT(VALUE(emp_id),"0")` で正規化 |
| `Log_ExternalSurvey` | A列（社員番号） | `@`書式 ＋ G列 COUNTIF で `TEXT(VALUE())` 正規化 |

## 6. Dashboard アラートサマリーの設計

### 6.1 Table機能によるクロスシート参照変換への対応

Google SheetsのTable機能は、他シートからテーブル列を参照する数式（例: `Log_Attendance!H2:H`）を自動的にテーブルのデータ開始行基準の参照（例: `H6:H`）へ変換する場合があります。これにより、`H2:H` と書いた数式が実際のデータ行を参照しなくなる問題が発生しました。

### 6.2 採用する集計方式

Google Sheets の「Table機能」化によって、他シートからテーブル列を参照する数式（例: `Log_Attendance!H2:H`）が、テーブルのデータ開始行基準（例: `H6:H`）へ自動変換され、集計範囲が壊れる問題が発生します。

これを回避するため、`H:H` 全列参照から、ヘッダーセル「⚠️ システムMSG」の1件を明示的に差し引くことで、行番号の変動に依存しない堅牢な集計を実現します。

```
// Dashboard A5 アラートサマリー数式パターン
COUNTIF(Log_Attendance!I:I,"⚠️*") - COUNTIF(Log_Attendance!I:I,"⚠️ システムMSG")
//  ↑ H列の全⚠️パターン              ↑ ヘッダー行「⚠️ システムMSG」の1件を除外
```

| シート | ヘッダー値（除外対象） | データ値（集計対象） |
|:---|:---|:---|
| `Log_Attendance` I列 | `"⚠️ システムMSG"` | `"⚠️マスタ未登録（社員番号）"` 等 |
| `Log_Notice` H列 | `"⚠️ システムMSG"` | `"⚠️マスタ未登録（社員番号）"` 等 |

> [!IMPORTANT]
> ヘッダー「⚠️ システムMSG」はスペースが含まれる（`"⚠️ "`）のに対し、エラーメッセージは `"⚠️マ..."` とスペースなしで始まります。将来的には `"⚠️ *"` と `"⚠️[! ]*"` のパターン分けも可能ですが、現状は EXACT 文字列差分方式を採用しています。
```

## Installation_Guide.md
```
# 導入マニュアル (Installation Guide)

本システム「Study Group DX」を利用開始するための、初回セットアップ手順です。

## Step 1: ジェネレーター（マザー）の準備
1. 管理者は、マスターとなる「ジェネレータースプレッドシート」を開きます。
2. 拡張機能 ＞ Apps Script を開き、本リポジトリ内の `src/AttendanceGenerator/system_builder.js` のコードをコピペして保存します。
   - *(※ コード内に「テンプレートのスプレッドシートID」がハードコードされているため、特別な設定は不要です。)*
3. スプレッドシート側の「Settings（設定）」シートに、以下の必須事項のみを入力します。
   - **対象とする期** (例: `26上期`)
   - **勉強会名称** (例: `Oracle勉強会`)

## Step 2: システム一式の自動生成
1. スプレッドシート上部のカスタムメニュー **「▶️ システム生成」** から **「システムを構築する」** をクリックします。
2. 内部で先ほどのハードコードされたIDのテンプレートがコピーされ、自動的に「当期専用の出欠管理スプレッドシート」と「打刻用・事前連絡用の2つのGoogleフォーム」が錬成されます。
3. 完了ダイアログが表示されれば、生成成功です。生成されたスプレッドシートのURLを開いてください。

## Step 3: 各期ごとの運用初期設定（子スプレッドシート側）
1. **マスタの登録**:
   - `Member_DB` シートに、参加するメンバーの氏名と社員番号を登録します。
   - `Schedule_DB` シートに、全日程を登録します。**（※ここが非常に重要です）**
   - 必ず D列の「開始時刻（例: 20:00）」と E列の「遅刻許容時間（例: 30）」を入力してください。これを元にこの期の遅刻判定が厳格に処理されます。
2. **深夜バッチとフォームの同期**:
   - シート上部のカスタムメニュー **「▶️ 管理メニュー」** から **「⚙️ 初期セットアップ（フォーム同期とタイマー起動）」** を実行します。
   - これにより、毎日のハッシュ防衛機能（シークレットキーの更新とフォームの開閉）が自動で稼働し始めます。

## 【重要】 過去のログを移行・コピペする際の設定
以前使っていたスプレッドシートから `Log_Attendance` や `Log_Notice` に生のログデータをコピペ移行する場合は、以下の仕様にご注意ください。
1. 必ず **フォームからの回答データ列（Timestamp〜フォームの最終設問）だけ** をコピペしてください。右端の「⚠️ システムMSG」列や、D列以降のシステム計算列（システム判定・計算キー・氏名参照）は**貼り付け範囲に含めないでください**。
2. コピペや手動で行を追加した瞬間に、システムの `onEdit` トリガーが発動し、システム計算列（数式）は**自動的に各行へ補完・展開**されます。
3. 万が一数式の自動補完が失敗したり、表のUIデザインが崩れた場合は、カスタムメニューの **『🛠️ 破損した数式の修復（リセット）』** を実行すれば、全行の数式と異常時の色付け（条件付き書式）が強制的に再構築されます。

## 【重要】 書式（データ型）の修復について
`Member_DB` 等へ一括貼り付け（通常のCtrl+V）を行うと、社員番号が「数値」として貼り付けられ、ログ側との照合に失敗することがあります（氏名が `#N/A` になる）。
その場合も、カスタムメニューの **『🛠️ 破損した数式の修復（リセット）』** を実行すると、以下の書式が自動で正しい状態に修復されます：
- `Member_DB` A列・各ログシートの社員番号列 → テキスト形式に修復
- `Schedule_DB` B列（開催日）・D列（開始時刻） → 日時形式に修復
```

## README.md
```
# 出欠・進捗統合管理システム (Study Group Attendance System)

社内勉強会における出欠管理や進捗を一元管理するためのスプレッドシート・Google Forms連携システムおよびその自動生成ツール群です。

## プロジェクト概要
従来のExcelベースの出欠管理プロセス（目視での確認、手動での色分けと集計）や、アンケート等の他のツールとの連携の悪さを解消するため、Google Workspaceの標準機能を活用した完全自動・連携可能な出欠管理システムを構築・自動生成します。

## 開発思想（Docs as Code）
本プロジェクトでは「機能凝集」と「中央集権」のハイブリッド構成を採用し、各機能やドキュメントを責任範囲ごとに分離しています。

---

## 📚 ドキュメント構成一覧 (Map of Content)

### 📊 1. 機能・技術層 (`docs/`)
システムの基本設計、および導入に関するドキュメント群です。エンジニアリングおよびシステム管理者向けの資料です。

* **[システム設計仕様書 (System Specification)](docs/System_Specification.md)**
  * シート構成のDBスキーマ、フォームの役割、コアとなるステータス自動判定ロジック定義。特定の運用（勉強会等）に依存しないシステムの基本挙動を記述。
* **[導入・セットアップ手順書 (Installation Guide)](docs/Installation_Guide.md)**
  * 自社環境へ本システム（ジェネレーター）をデプロイするための技術手順書。初期テンプレートの準備やGASの設定方法を記載。

### ⚙️ 2. 実装・開発層 (`src/`)
システムのソースコードおよびその技術仕様群です。

* **[AttendanceGenerator/](src/AttendanceGenerator/)**
  * システムを一瞬で構築するためのGASベースのプロビジョニングツール一式。
  * **[機能概要・構成 (README)](src/AttendanceGenerator/README.md)**: ジェネレーターの責務とアーキテクチャの解説。
  * **[技術仕様定義 (spec_generator)](src/AttendanceGenerator/spec_generator.md)**: GASが自動生成する内容の定義、パラメータ定義、内部処理フロー。

---

## 💡 運用マニュアルについて
特定の勉強会運営に関する「本番運用時の実務マニュアル」は、本リポジトリではなく別リポジトリ（`second-brain` 内の知見アセット）に管理を委譲しています。
開発環境へのパスを含まない、外部共有可能な形式で維持されています。
```

## template_bound_script.js
```
/**
 * 出欠管理システム - テンプレート内蔵スクリプト (Template Bound Script)
 * 
 * 役割:
 * このスクリプトは、ジェネレーターから生成された「個別の勉強会用スプレッドシート」
 * に内蔵され、日々の自動化タスク（フォームのプルダウン同期）や、
 * シートが壊れた際の「数式リセット（自己修復）」機能を提供します。
 */

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('▶️ 管理メニュー')
    .addItem('⚙️ 初期セットアップ（フォーム同期とタイマー起動）', 'setupTriggersAndSync')
    .addItem('🔄 最新の予定をフォームに手動同期する', 'syncFormManually')
    .addItem('🛠️ 破損した数式の修復（リセット）', 'resetFormulas')
    .addToUi();
}

/**
 * 管理者が手動で最新の予定・ハッシュパラメータをフォームに同期する機能
 */
function syncFormManually() {
  dailySync();
  SpreadsheetApp.getUi().alert("同期完了", "当日の開催予定とシステム認証パラメータをフォームに同期しました。", SpreadsheetApp.getUi().ButtonSet.OK);
}

/**
 * 毎日深夜に実行されるトリガーの中身
 */
function dailySync() {
  syncFormDropdowns();
  syncAuthForm();
  healLogFormulas(SpreadsheetApp.getActiveSpreadsheet());
  healLogConditionalFormats(SpreadsheetApp.getActiveSpreadsheet());
}

/**
 * フォーム回答シート（Log_Attendance, Log_Notice）のヘッダ数式が
 * Googleフォームの非同期連携によって自動消去されてしまう現象を防ぐための自己修復機能
 */
function healLogFormulas(ss) {
  const attSheet = ss.getSheetByName("Log_Attendance");
  if (attSheet) {
    if (attSheet.getLastRow() > 1) {
      const numRows = attSheet.getLastRow() - 1;
      attSheet.getRange(2, 4, numRows, 3).clearContent(); // D, E, F列をクリア
      attSheet.getRange(2, 9, numRows, 1).clearContent(); // I列をクリア
    }
    attSheet.getRange(1, 4).setValue("システム判定（区分）").setBackground("#fce5cd").setFontColor("#000000").setFontWeight("bold");
    attSheet.getRange(1, 5).setValue("計算キー").setBackground("#434343").setFontColor("#ffffff").setFontWeight("bold");
    attSheet.getRange(1, 6).setValue("氏名参照").setBackground("#434343").setFontColor("#ffffff").setFontWeight("bold");
    attSheet.getRange(1, 7).setValue("手動区分").setBackground("#fff2cc").setFontColor("#000000").setFontWeight("bold");
    attSheet.getRange(1, 8).setValue("メモ").setBackground("#e69138").setFontColor("#ffffff").setFontWeight("bold");
    attSheet.getRange(1, 9).setValue("⚠️ システムMSG").setBackground("#cc0000").setFontColor("#ffffff").setFontWeight("bold");

    const lastRow = attSheet.getLastRow();
    if (lastRow > 1) {
      const numRows = lastRow - 1;
      attSheet.getRange(2, 4, numRows).setFormula('=IF(A2="", "", IF(G2="リモート", "手動承認(リモート)", IF(G2="リアル", "手動承認(リアル)", IF(G2<>"", "手動承認(リアル)", IF(C2="", "", IF(IFERROR(VALUE(C2), 0) = (INT(A2) * VALUE(Dashboard!$Z$2)) + 11, "リアル", IF(IFERROR(VALUE(C2), 0) = (INT(A2) * VALUE(Dashboard!$Z$2)) + 22, "リモート", "❌ 不正・無効")))))))');
      attSheet.getRange(2, 5, numRows).setFormula('=IF(D2="❌ 不正・無効", "", IF(A2="", "", INT(A2) & "_" & TEXT(VALUE(B2),"0")))');
      attSheet.getRange(2, 6, numRows).setFormula('=IF(B2="", "", IFERROR(VLOOKUP(TEXT(VALUE(B2),"0"), Member_DB!$A:$B, 2, FALSE), "#N/A"))');
      attSheet.getRange(2, 9, numRows).setFormula('=IF(A2="", "", IF(F2="#N/A", "⚠️マスタ未登録（社員番号）", IF(D2="❌ 不正・無効", "⚠️不正・改ざん疑い", IF(AND(E2<>"", COUNTIF(E:E, E2)>1), "⚠️重複打刻（最新のみ有効）", ""))))');
    }
  }

  const notSheet = ss.getSheetByName("Log_Notice");
  if (notSheet) {
    if (notSheet.getLastRow() > 1) {
      const numRowsN = notSheet.getLastRow() - 1;
      notSheet.getRange(2, 6, numRowsN, 1).clearContent(); // F列をクリア
      notSheet.getRange(2, 8, numRowsN, 1).clearContent(); // H列をクリア
    }
    notSheet.getRange(1, 6).setValue("氏名参照").setBackground("#434343").setFontColor("#ffffff").setFontWeight("bold");
    notSheet.getRange(1, 7).setValue("メモ").setBackground("#e69138").setFontColor("#ffffff").setFontWeight("bold");
    notSheet.getRange(1, 8).setValue("⚠️ システムMSG").setBackground("#cc0000").setFontColor("#ffffff").setFontWeight("bold");

    const lastRow = notSheet.getLastRow();
    if (lastRow > 1) {
      const numRowsN = lastRow - 1;
      notSheet.getRange(2, 6, numRowsN).setFormula('=IF(C2="", "", IFERROR(VLOOKUP(TEXT(VALUE(C2),"0"), Member_DB!$A:$B, 2, FALSE), "#N/A"))');
      notSheet.getRange(2, 8, numRowsN).setFormula('=IF(A2="", "", IF(F2="#N/A", "⚠️マスタ未登録（社員番号）", IF(AND(B2<>"", ISNA(MATCH(IFERROR(INT(B2),B2), INDIRECT("Schedule_DB!B:B"), 0))), "⚠️開催予定外の日付", "")))');
    }
  }
}


// フォーム回答シート（Table）が条件付き書式を破壊・剥奪する問題への自己修復
function healLogConditionalFormats(ss) {
  const attSheet = ss.getSheetByName("Log_Attendance");
  if (attSheet) {
    const ruleFraud = SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied('=$D2="❌ 不正・無効"')
      .setBackground("#ea4335").setFontColor("#ffffff")
      .setRanges([attSheet.getRange("A2:I")])
      .build();
    const ruleInvalidEmpAtt = SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied("=ISNA($F2)")
      .setBackground("#fce8e6").setFontColor("#cc0000")
      .setRanges([attSheet.getRange("A2:I")])
      .build();
    // BUG-1修正: ruleDuplicateAtt を定義して追加
    const ruleDuplicateAtt = SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied('=AND($E2<>"", COUNTIF($E:$E, $E2) > 1)')
      .setBackground("#fff2cc").setFontColor("#b45f06")
      .setRanges([attSheet.getRange("A2:I")])
      .build();
    const ruleMsgAtt = SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied('=$I2<>""')
      .setBackground("#fce8e6").setFontColor("#cc0000")
      .setRanges([attSheet.getRange("A2:I")])
      .build();
    attSheet.setConditionalFormatRules([ruleFraud, ruleInvalidEmpAtt, ruleDuplicateAtt, ruleMsgAtt]);
  }

  const notSheet = ss.getSheetByName("Log_Notice");
  if (notSheet) {
    const ruleInvalidDate = SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied('=AND($B2<>"", ISNA(MATCH(IFERROR(INT($B2),$B2), INDIRECT("Schedule_DB!B:B"), 0)))')
      .setBackground("#fce8e6").setFontColor("#cc0000")
      .setRanges([notSheet.getRange("A2:H")])
      .build();
    const rulePastDate = SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied('=AND($B2<>"", INT($A2)>$B2)')
      .setBackground("#fef0d9").setFontColor("#e69138")
      .setRanges([notSheet.getRange("A2:H")])
      .build();
    const ruleMsgNotice = SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied('=$H2<>""')
      .setBackground("#fce8e6").setFontColor("#cc0000")
      .setRanges([notSheet.getRange("A2:H")])
      .build();
    // BUG-2修正: 未定義の ruleInvalidEmpNotice を削除
    notSheet.setConditionalFormatRules([ruleInvalidDate, rulePastDate, ruleMsgNotice]);
  }
}

/**
 * フォームのプルダウン（対象日）を最新の Schedule_DB と同期する。
 * 過去日は自動的に除外する。
 */
function syncFormDropdowns() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const scheduleSheet = ss.getSheetByName("Schedule_DB");
  
  if (!scheduleSheet) return;

  // B列から開催予定日を取得（インデックス1からのデータ）
  const dates = scheduleSheet.getRange("B2:B").getValues().flat().filter(d => d instanceof Date || d !== "");
  
  const today = new Date();
  today.setHours(0, 0, 0, 0); // 今日の0時0分0秒

  const validDates = [];
  dates.forEach(d => {
    let dt = new Date(d);
    dt.setHours(0, 0, 0, 0);
    // 今日以降の日付のみを抽出（過去日は除外）
    if (dt >= today) {
      validDates.push(Utilities.formatDate(dt, Session.getScriptTimeZone(), "yyyy/MM/dd"));
    }
  });

  // Unique処理
  const uniqueDates = [...new Set(validDates)].sort();

  // DashboardからForm B（事前連絡用）のIDを取得
  // ジェネレーター側で、システム生成時に一時的にZ1等へFormIDを吐き出させるか、
  // あるいはシートに紐づくFormを取得する
  const dashSheet = ss.getSheetByName("Dashboard");
  const formBId = dashSheet.getRange("Z1").getValue(); // 隠しセルに保存されたID

  if (!formBId) {
    Logger.log("Form B IDが見つかりません");
    return;
  }

  try {
    const formB = FormApp.openById(formBId);
    const items = formB.getItems(FormApp.ItemType.LIST); // ドロップダウン（LIST）を使用するよう変更
    if (items.length > 0) {
      const dateItem = items[0].asListItem(); // 最初の項目のプルダウンを想定
      if (uniqueDates.length > 0) {
        dateItem.setChoiceValues(uniqueDates);
      } else {
        dateItem.setChoiceValues(["(予定されている開催日はありません)"]);
      }
    }
  } catch (e) {
    Logger.log("フォームの同期に失敗しました: " + e.message);
  }
}

/**
 * フォームA（当日打刻）のフェーズ管理（受付開始/停止）および、当日のハッシュ認証URLの生成を行う。
 */
function syncAuthForm() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const scheduleSheet = ss.getSheetByName("Schedule_DB");
  const dashSheet = ss.getSheetByName("Dashboard");
  
  if (!scheduleSheet || !dashSheet) return;

  const formAId = dashSheet.getRange("Z4").getValue();
  if (!formAId) return;

  // 今日の日付シリアル値を確定
  dashSheet.getRange("Z3").setFormula("=INT(TODAY())");
  SpreadsheetApp.flush();
  const todaySerial = dashSheet.getRange("Z3").getValue();
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  let isTodaySession = false;
  let sessionNumber = "";
  
  const scheduleData = scheduleSheet.getRange("A2:B").getValues();
  for (let i = 0; i < scheduleData.length; i++) {
    if (scheduleData[i][1] instanceof Date) {
      let d = new Date(scheduleData[i][1]);
      d.setHours(0, 0, 0, 0);
      if (d.getTime() === today.getTime()) {
        isTodaySession = true;
        sessionNumber = scheduleData[i][0];
        break;
      }
    }
  }

  try {
    const formA = FormApp.openById(formAId);
    
    if (isTodaySession) {
      formA.setTitle(`第${sessionNumber}回 当日打刻フォーム`);
      formA.setAcceptingResponses(true);
      
      const secretKey = dashSheet.getRange("Z2").getValue();
      const realHash = (todaySerial * secretKey) + 11;
      const remoteHash = (todaySerial * secretKey) + 22;
      
      const authItem = formA.getItems(FormApp.ItemType.TEXT)[1].asTextItem(); // 2番目の設問
      
      const realUrl = formA.createResponse().withItemResponse(authItem.createResponse(String(realHash))).toPrefilledUrl();
      const remoteUrl = formA.createResponse().withItemResponse(authItem.createResponse(String(remoteHash))).toPrefilledUrl();
      
      dashSheet.getRange("B3").setValue(remoteUrl);
      dashSheet.getRange("B4").setValue(realUrl);
      
    } else {
      formA.setTitle(`現在受付停止中`);
      formA.setAcceptingResponses(false);
    }
  } catch (e) {
    Logger.log("フォームAの同期に失敗しました: " + e.message);
  }
}

/**
 * 初回セットアップ：深夜タイマーを登録し、初回同期を実行する
 */
function setupTriggersAndSync() {
  const ui = SpreadsheetApp.getUi();
  
  // 既存のトリガーを全削除
  const triggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < triggers.length; i++) {
    ScriptApp.deleteTrigger(triggers[i]);
  }
  
  // 毎日深夜2〜3時頃に dailySync を実行
  ScriptApp.newTrigger("dailySync")
    .timeBased()
    .everyDays(1)
    .atHour(2)
    .create();

  // 各種手動編集イベントを捌くルーター関数をonEditトリガーに登録（マスタ反映や、手動行追加時の数式即時展開など）
  ScriptApp.newTrigger("onEditRouter")
    .forSpreadsheet(SpreadsheetApp.getActiveSpreadsheet())
    .onEdit()
    .create();

  // Form回答時にリアルタイムで数式を復元展開する（ARRAYFORMULAの弱点を補う最強のトリガー）
  ScriptApp.newTrigger("fillFormulasOnSubmit")
    .forSpreadsheet(SpreadsheetApp.getActiveSpreadsheet())
    .onFormSubmit()
    .create();

  // 手動で1回目を実行（全フォームの同期）
  dailySync();

  ui.alert("セットアップ完了", "フォームの同期と自動更新タイマーの設定が完了しました。", ui.ButtonSet.OK);
}

/**
 * 数式の破損を検知した際に、管理者が手動で正規の数式を再セットするための機能
 */
function resetFormulas() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.alert("数式リセットの確認", "Progress_Master の数式（灰色のセル）をすべて出荷状態にリセットします。\n※手入力したデータ（備考など）は消えません。\n\nよろしいですか？", ui.ButtonSet.YES_NO);
  if (response == ui.Button.NO) return;

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const progressSheet = ss.getSheetByName("Progress_Master");
  
  if (!progressSheet) {
    ui.alert("エラー", "Progress_Master シートが見つかりません。", ui.ButtonSet.OK);
    return;
  }

  // --- ヘッダー日付展開数式 (K1) ---
  const dateHeaderFormula = `=IFERROR(TRANSPOSE(SORT(UNIQUE(Schedule_DB!$B$2:$B), 1, TRUE)), "")`;
  progressSheet.getRange("K1").setFormula(dateHeaderFormula);

  // --- 状態判定マトリクス展開数式 (K2) ---
  // system_builder.js と同一の LET+INDIRECT 版（Table機能の参照変換を回避、型正規化付き）
  const logicFormula = [
      // ── 外側LET: INDIRECT変数（Table変換を受けない）────────────────
      `=LET(`,
      `  att_A,  INDIRECT("Log_Attendance!A2:A"),`,
      `  att_B,  INDIRECT("Log_Attendance!B2:B"),`,
      `  att_D,  INDIRECT("Log_Attendance!D2:D"),`,
      `  att_AD, INDIRECT("Log_Attendance!A2:D"),`,
      `  not_B,  INDIRECT("Log_Notice!B2:B"),`,
      `  not_C,  INDIRECT("Log_Notice!C2:C"),`,
      `  not_D,  INDIRECT("Log_Notice!D2:D"),`,
      // ── MAKEARRAY: 全emp × 全日付 の出欠マトリクス ─────────────────
      `  MAKEARRAY(COUNTA($A$2:$A), COUNTA($K$1:$1), LAMBDA(r, c, LET(`,
      `    emp_id,     INDEX($A$2:$A, r),`,
      `    target_date, INDEX($K$1:$1, 1, c),`,
      `    sched_info,  XLOOKUP(target_date, Schedule_DB!$B:$B, Schedule_DB!$C:$E, {"", "", ""}),`,
      `    session_type, INDEX(sched_info, 1, 1),`,
      `    start_time,  INDEX(sched_info, 1, 2),`,
      `    grace_mins,  INDEX(sched_info, 1, 3),`,
      `    threshold_time, start_time + TIME(0, grace_mins, 0),`,
      `    orig_date, IF(session_type="補講", XLOOKUP(INDEX(XLOOKUP(target_date, Schedule_DB!$B:$B, Schedule_DB!$A:$A, ""), 1, 1) & "通常", ARRAYFORMULA(Schedule_DB!$A:$A & Schedule_DB!$C:$C), Schedule_DB!$B:$B, ""), ""),`,
      `    orig_key, IF(orig_date<>"", TEXT(orig_date, "yyyy/MM/dd") & emp_id, ""),`,
      `    orig_has_att, IF(orig_key<>"", XLOOKUP(orig_key, ARRAYFORMULA(TEXT(att_A, "yyyy/MM/dd") & TEXT(VALUE(att_B),"0")), att_A, "", 0, -1) <> "", FALSE),`,
      `    key_str, TEXT(target_date, "yyyy/MM/dd") & TEXT(VALUE(emp_id),"0"),`,
      `    max_ts, IFERROR(MAX(FILTER(att_A, (INT(att_A)=target_date) * (TEXT(VALUE(att_B),"0")=TEXT(VALUE(emp_id),"0")) * (att_D<>"❌ 不正・無効"))), 0),`,
      `    has_att, max_ts > 0,`,
      `    att_rec, IF(has_att, XLOOKUP(max_ts, att_A, att_AD, {"","","",""}), {"","","",""}),`,
      `    att_time, IF(has_att, MOD(INDEX(att_rec, 1, 1), 1), 0),`,
      `    att_type, IF(has_att, INDEX(att_rec, 1, 4), ""),`,
      `    att_short, IF(REGEXMATCH(att_type, "リアル"), "リアル", IF(REGEXMATCH(att_type, "リモート"), "リモート", att_type)),`,
      `    notice_type, XLOOKUP(key_str, ARRAYFORMULA(TEXT(not_B, "yyyy/MM/dd") & TEXT(VALUE(not_C),"0")), not_D, "", 0, -1),`,
      `    has_notice, notice_type <> "",`,
      `    IF(emp_id="", "",`,
      `      IFS(`,
      `        target_date > TODAY(), "",`,
      `        has_att, IF(att_time > threshold_time, "欠席(遅刻30分超)",`,
      `                   IF(att_time > start_time,`,
      `                     IF(has_notice, "出席(" & att_short & ")・遅刻・届出有", "出席(" & att_short & ")・遅刻"),`,
      `                     IF(has_notice, "出席(" & att_short & ")・届出有", "出席(" & att_short & ")"))),`,
      `        has_notice, IF(notice_type="欠席", "欠席・届出有", "無断欠席(遅刻届のみ)"),`,
      `        AND(session_type="補講", orig_has_att), "対象外",`,
      `        TRUE, "無断欠席"`,
      `      )`,
      `    )`,
      `  )))`,
      `)`
  ].join("");

  progressSheet.getRange("K2").setFormula(logicFormula);

  // A〜G列の固定カラムの数式もリセット
  // BUG-3修正: B2/C2 に IFERROR 双試行パターンを適用（system_builder.js と統一）
  progressSheet.getRange("A2").setFormula('=UNIQUE(FILTER(Member_DB!A2:A, Member_DB!A2:A<>""))');
  progressSheet.getRange("B2").setFormula('=ARRAYFORMULA(IF(A2:A="","", IFERROR(VLOOKUP(A2:A, Member_DB!$A:$D, 2, FALSE), IFERROR(VLOOKUP(VALUE(A2:A), Member_DB!$A:$D, 2, FALSE), ""))))');
  progressSheet.getRange("C2").setFormula('=ARRAYFORMULA(IF(A2:A="","", IFERROR(VLOOKUP(A2:A, Member_DB!$A:$D, 3, FALSE), IFERROR(VLOOKUP(VALUE(A2:A), Member_DB!$A:$D, 3, FALSE), ""))))');
  progressSheet.getRange("D2").setFormula('=ARRAYFORMULA(IF(A2:A="","", BYROW(K2:ZZ, LAMBDA(r, COUNTIF(r, "*出席*")))))');
  progressSheet.getRange("E2").setFormula('=ARRAYFORMULA(IF(A2:A="","", BYROW(K2:ZZ, LAMBDA(r, COUNTIF(r, "*リアル*")))))');
  progressSheet.getRange("F2").setFormula('=ARRAYFORMULA(IF(D2:D="","", IF(D2:D=0, 0, E2:E / D2:D)))');
  // BUG-3b修正: G2 に TEXT(VALUE(),"0") 型正規化を適用（system_builder.js と統一）
  progressSheet.getRange("G2").setFormula('=ARRAYFORMULA(IF(A2:A="","", COUNTIF(ARRAYFORMULA(TEXT(VALUE(Log_ExternalSurvey!$A:$A),"0")), TEXT(VALUE(A2:A),"0"))))');

  // --- Log_Attendance と Log_Notice の数式列もリセットし、干渉するゴミデータを削除する ---
  healLogFormulas(ss);
  healLogConditionalFormats(ss);

  // --- 簡易版 Idea-17: 各シートのデータ型を正しい状態に強制修復 ---
  const ss2 = SpreadsheetApp.getActiveSpreadsheet();
  const memberDb = ss2.getSheetByName("Member_DB");
  const logAtt = ss2.getSheetByName("Log_Attendance");
  const logNot = ss2.getSheetByName("Log_Notice");
  const logExt = ss2.getSheetByName("Log_ExternalSurvey");
  const prog = ss2.getSheetByName("Progress_Master");
  const sched = ss2.getSheetByName("Schedule_DB");

  if (memberDb) memberDb.getRange("A:A").setNumberFormat("@");
  if (logAtt) logAtt.getRange("B:B").setNumberFormat("@");
  if (logNot) logNot.getRange("C:C").setNumberFormat("@");
  if (logExt) logExt.getRange("A:A").setNumberFormat("@");
  if (prog) prog.getRange("A:A").setNumberFormat("@");
  if (sched) {
    sched.getRange("B2:B").setNumberFormat("yyyy/MM/dd");
    sched.getRange("D2:D").setNumberFormat("HH:mm");
  }

  ui.alert("修復完了", "数式システムを正常な状態にリセットし、エラー原因となるデータおよびデータ型の不整合を修正しました。", ui.ButtonSet.OK);
}

/**
 * フォームから新しい行が追加された瞬間に、自動で対象行へ数式を刻み込む機能
 * これによりGoogle Forms特有の行挿入ズレやARRAYFORMULAの機能不全を完璧に防ぐ
 */
function fillFormulasOnSubmit(e) {
  if (!e || !e.range) return;
  const sheet = e.range.getSheet();
  const row = e.range.getRow();
  
  if (sheet.getName() === "Log_Attendance") {
    sheet.getRange(row, 4).setFormula(`=IF(A${row}="", "", IF(G${row}="リモート", "手動承認(リモート)", IF(G${row}="リアル", "手動承認(リアル)", IF(G${row}<>"", "手動承認(リアル)", IF(C${row}="", "", IF(IFERROR(VALUE(C${row}), 0) = (INT(A${row}) * VALUE(Dashboard!$Z$2)) + 11, "リアル", IF(IFERROR(VALUE(C${row}), 0) = (INT(A${row}) * VALUE(Dashboard!$Z$2)) + 22, "リモート", "❌ 不正・無効")))))))`);
    sheet.getRange(row, 5).setFormula(`=IF(D${row}="❌ 不正・無効", "", IF(A${row}="", "", INT(A${row}) & "_" & TEXT(VALUE(B${row}),"0")))`);
    sheet.getRange(row, 6).setFormula(`=IF(B${row}="", "", IFERROR(VLOOKUP(TEXT(VALUE(B${row}),"0"), Member_DB!$A:$B, 2, FALSE), "#N/A"))`);
    sheet.getRange(row, 9).setFormula(`=IF(A${row}="", "", IF(F${row}="#N/A", "⚠️マスタ未登録（社員番号）", IF(D${row}="❌ 不正・無効", "⚠️不正・改ざん疑い", IF(AND(E${row}<>"", COUNTIF(E:E, E${row})>1), "⚠️重複打刻（最新のみ有効）", ""))))`);
  } else if (sheet.getName() === "Log_Notice") {
    sheet.getRange(row, 6).setFormula(`=IF(C${row}="", "", IFERROR(VLOOKUP(TEXT(VALUE(C${row}),"0"), Member_DB!$A:$B, 2, FALSE), "#N/A"))`);
    sheet.getRange(row, 8).setFormula(`=IF(A${row}="", "", IF(F${row}="#N/A", "⚠️マスタ未登録（社員番号）", IF(AND(B${row}<>"", ISNA(MATCH(IFERROR(INT(B${row}),B${row}), INDIRECT("Schedule_DB!B:B"), 0))), "⚠️開催予定外の日付", "")))`)

  }
}

/**
 * ユーザーがスプレッドシートを手動で編集した際に発火する統合ルーター
 */
function onEditRouter(e) {
  if (!e || !e.range) return;
  const sheet = e.range.getSheet();
  const sName = sheet.getName();
  
  // Schedule_DB が編集されたらフォームの対象日ドロップダウンを即座に更新する
  if (sName === "Schedule_DB") {
    syncFormDropdowns();
  }
  
  // Member_DB の A列（社員番号）が編集・貼り付けされた場合、即座にテキスト書式を強制適用
  // これにより、一括貼り付け後に手動リセットが不要になる
  if (sName === "Member_DB" && e.range.getColumn() === 1) {
    sheet.getRange(e.range.getRow(), 1, e.range.getNumRows(), 1).setNumberFormat("@");
  }
  
  // Log_* シートが手動で編集（行追加など）された際、A列等に入力があり、かつ数式列が空であれば即座に数式を展開する
  if (sName === "Log_Attendance" || sName === "Log_Notice") {
    fillFormulasOnEdit(e);
  }
}

/**
 * 手動で行を追加・編集した際にも、自動で数式を補完する機能
 * （すでに数式や手動入力値が入っている場合は上書きしない安全設計）
 */
function fillFormulasOnEdit(e) {
  const sheet = e.range.getSheet();
  const row = e.range.getRow();
  
  if (row <= 1) return;
  
  if (sheet.getName() === "Log_Attendance") {
    if (sheet.getRange(row, 4).getValue() === "") {
      sheet.getRange(row, 4).setFormula(`=IF(A${row}="", "", IF(G${row}="リモート", "手動承認(リモート)", IF(G${row}="リアル", "手動承認(リアル)", IF(G${row}<>"", "手動承認(リアル)", IF(C${row}="", "", IF(IFERROR(VALUE(C${row}), 0) = (INT(A${row}) * VALUE(Dashboard!$Z$2)) + 11, "リアル", IF(IFERROR(VALUE(C${row}), 0) = (INT(A${row}) * VALUE(Dashboard!$Z$2)) + 22, "リモート", "❌ 不正・無効")))))))`)
      sheet.getRange(row, 5).setFormula(`=IF(D${row}="❌ 不正・無効", "", IF(A${row}="", "", INT(A${row}) & "_" & TEXT(VALUE(B${row}),"0")))`);
      sheet.getRange(row, 6).setFormula(`=IF(B${row}="", "", IFERROR(VLOOKUP(TEXT(VALUE(B${row}),"0"), Member_DB!$A:$B, 2, FALSE), "#N/A"))`);
      sheet.getRange(row, 9).setFormula(`=IF(A${row}="", "", IF(F${row}="#N/A", "⚠️マスタ未登録（社員番号）", IF(D${row}="❌ 不正・無効", "⚠️不正・改ざん疑い", IF(AND(E${row}<>"", COUNTIF(E:E, E${row})>1), "⚠️重複打刻（最新のみ有効）", ""))))`);
    }
  } else if (sheet.getName() === "Log_Notice") {
    if (sheet.getRange(row, 6).getValue() === "") {
      sheet.getRange(row, 6).setFormula(`=IF(C${row}="", "", IFERROR(VLOOKUP(TEXT(VALUE(C${row}),"0"), Member_DB!$A:$B, 2, FALSE), "#N/A"))`);
      sheet.getRange(row, 8).setFormula(`=IF(A${row}="", "", IF(F${row}="#N/A", "⚠️マスタ未登録（社員番号）", IF(AND(B${row}<>"", ISNA(MATCH(IFERROR(INT(B${row}),B${row}), INDIRECT("Schedule_DB!B:B"), 0))), "⚠️開催予定外の日付", "")))`);
    }
  }
}
```

## README.md
```
# AttendanceGenerator モジュール

本モジュールは、「出欠・進捗統合管理システム」を特定のプロジェクトや期間ごとに複製・展開するための親ツール（ジェネレーター）を担うGASプロジェクトです。

## モジュール概要と責務
本ディレクトリに格納されているスクリプト群は、煩雑なスプレッドシートやフォームの作成・紐付け・数式の埋め込み作業を、GASを利用して瞬時かつ全自動で行うためのプロビジョニングツールです。
このツールは「システムの作り方」を知っている工場のような役割を持ち、生成される「システム本体」とは疎結合に保たれています。

## ドキュメント一覧
本モジュールに関連する各種ドキュメントは以下の通り機能ごとに分離されています。

* **[内部アーキテクチャ・技術仕様 (`spec_generator.md`)](spec_generator.md)**
  * ジェネレーターが受け取るパラメータ仕様、自動生成されるフォームの設問内容、バックエンドで実行される生成フェーズの詳細。
* **[システム導入手順書 (`docs/Installation_Guide.md`)](../../docs/Installation_Guide.md)**
  * このジェネレーターを実際に使ってシステムを立ち上げる手順、および初期設定についての導入者向けマニュアル。
* **[システム設計仕様書 (`docs/System_Specification.md`)](../../docs/System_Specification.md)**
  * 本ジェネレーターによって『生成された後』のシート群のDB設計や、出欠ステータスの判定ロジックに関する仕様書。

## 格納ファイル
* `generator_mother.js`: ジェネレーター自身の初期化用スクリプト（Settingsシート等のUI生成）
* `system_builder.js`: パラメータを読み取ってシステム本体を自動生成する主処理スクリプト
* `template_bound_script.js`: 生成されるスプレッドシートに自動で埋め込まれる各種ユーティリティ関数
```

## spec_generator.md
```
# ジェネレーター技術仕様 (spec_generator)

本ドキュメントは、`AttendanceGenerator` モジュールの内部仕様・アーキテクチャ・プロビジョニング処理フローを定義します。

## 1. ジェネレーターのアーキテクチャと責務

本システムは、手動での環境構築に伴う設定漏れや不整合を完全に排除するため、**プロビジョニング・アプローチ**を採用しています。

**【コンポーネント構成】**
ジェネレーターは以下の2段構成で処理を行います。
1. **ジェネレーター・マザー (`generator_mother.js`):** ジェネレーター自体の環境を構築するための初期化スクリプト。設定用UI（Settingsシート）や実行メニューを生成します。
2. **システム・ビルダー (`system_builder.js`):** 設定UIからパラメータを読み込み、実際のシステム一式（スプレッドシート＋フォーム）を動的に自動生成するコアロジックです。

## 2. Configuration (入力パラメータ定義)

UI(`Settings` シート)から受け取るパラメータ仕様は以下の通りです。

| 項目名 | 説明・役割 |
| --- | --- |
| **対象とする期** | 生成されるファイル名の接頭辞（例：`26上期`）。 |
| **勉強会名称** | 開催される勉強会のタイトル。ファイル名の本体になります。 |
| **保存先フォルダID** | 成果物の出力先DriveフォルダのIDまたはURL。 |

## 3. 自動生成されるフォームの構成仕様

GASによって動的に生成・バインドされる2つのフォームは、以下の設問構成で初期化されます。

### [Form A] 当日参加打刻フォーム
* **タイトル:** `{イベント名} 当日出欠打刻`
* **設問1:** `社員番号（半角数字）` 【必須: 短答式】
* **設問2:** `【システム専用】認証コード（変更しないでください）` 【必須: 短答式】 ※ハッシュ認証用のプレフィル領域

### [Form B] 事前届出フォーム
* **タイトル:** `{イベント名} 欠席・遅刻 事前連絡`
* **設問1:** `対象日（いつ休み/遅刻しますか？）` 【必須: リスト選択】（Schedule_DBから同期）
* **設問2:** `社員番号（半角数字）` 【必須: 短答式】
* **設問3:** `連絡種別` 【必須: ラジオボタン】 (欠席 / 遅刻)
* **設問4:** `理由` 【必須: 段落】

## 4. プロビジョニング処理フロー

システム生成は以下のフェーズで実行されます。

* **Phase 1 (リソース確保):** 指定フォルダに新規スプレッドシートを作成。
* **Phase 2 (フォーム生成・バインド):** 2種のフォームを生成し、スプレッドシートの回答先シートとして紐付け。
* **Phase 3 (スキーマ構築):** `Member_DB`, `Schedule_DB`, `Progress_Master` 等を生成し、判定ロジック関数をセルへパッチ処理。
* **Phase 4 (配備フィードバック):** 生成された各種URL情報をSettingsシートへ書き出し。

### 運用上の保護ロジック（書式強制の対象列）

データ型の不一致（貼り付けによる数値化）によるVLOOKUPエラーを防ぐため、以下の列にシステム生成時および数式リセット時に書式が強制適用されます。

| シート | 列 | 強制書式 | 理由 |
| :--- | :--- | :--- | :--- |
| `Member_DB` | A列（社員番号） | 書式なしテキスト `@` | 全テーブルのJOINキー。数値化するとVLOOKUP全滅。 |
| `Log_Attendance` | B列（社員番号） | 書式なしテキスト `@` | フォーム送信は文字列。手動リカバリ時の型ズレ防止。 |
| `Log_Notice` | C列（社員番号） | 書式なしテキスト `@` | 同上。 |
| `Log_ExternalSurvey` | A列（社員番号） | 書式なしテキスト `@` | Progress_MasterのCOUNTIF照合に使用。 |
| `Progress_Master` | A列（社員番号） | 書式なしテキスト `@` | UNIQUE展開のキー。型混在で重複排除が壊れる。 |
| `Schedule_DB` | B列（開催日） | `yyyy/MM/dd` | ログのTimestampと日付比較するため厳格な日付型が必要。 |
| `Schedule_DB` | D列（開始時刻） | `HH:mm` | 遅刻閾値の算出に使用する時刻シリアル値として保持する。 |

### データ入力規則（バリデーション）

`Schedule_DB` C列（種別）には、データ入力規則（プルダウン）を設定します。

* **許容値:** `通常` / `補講`
* **理由:** `Progress_Master` の判定ロジック（IFS関数）は種別の完全一致で分岐するため、全角/半角の差異や誤記が判定破損を招く。プルダウンにより人的ミスを物理的に排除する。

## 5. システムMSG（アラート）列の仕様

各ログシートには、生成またはデータ登録の際に自動判定される「⚠️ システムMSG」列が右端に配置されます。

### Log_Attendance のI列（システムMSG）

| 判定条件 | 表示メッセージ | 優先順位 |
| :--- | :--- | :--- |
| 氏名参照が `#N/A`（マスタ未登録） | `⚠️マスタ未登録（社員番号）` | 1（最高） |
| 打刻判定が `❌ 不正・無効` | `⚠️不正・改ざん疑い` | 2 |
| 同日・同人物で打刻が複数存在 | `⚠️重複打刻（最新のみ有効）` | 3 |
| 上記いずれにも該当しない | 空白 | - |

### Log_Notice のH列（システムMSG）

| 判定条件 | 表示メッセージ | 優先順位 |
| :--- | :--- | :--- |
| 氏名参照が `#N/A`（マスタ未登録） | `⚠️マスタ未登録（社員番号）` | 1（最高） |
| 対象日がSchedule_DBに存在しない | `⚠️開催予定外の日付` | 2 |
| 上記いずれにも該当しない | 空白 | - |
```

## generator_mother.js
```
/**
 * 出欠管理システム - ジェネレーター初期構築用スクリプト (ジェネレーター・マザー)
 * 
 * 使い方:
 * 1. 新規のGoogleスプレッドシートを作成する。
 * 2. 拡張機能 > Apps Script を開き、このコードを貼り付ける。
 * 3. 画面上の [実行] を押し、権限を承認する。
 * 4. シートに戻ると「Settings」シートが完成しており、上部にシステム生成メニューが追加される。
 */

function setupGenerator() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // 1. 既存の「シート1」等を削除し、新しい「Settings」シートを作成
  let sheet = ss.getSheetByName("Settings");
  if (!sheet) {
    sheet = ss.insertSheet("Settings");
  }

  // 不要な初期シートがあれば削除
  const sheets = ss.getSheets();
  sheets.forEach(s => {
    if (s.getName() !== "Settings") {
      ss.deleteSheet(s);
    }
  });

  // 2. UIの枠組み構築
  sheet.clear();

  // ヘッダー行
  sheet.getRange("A1").setValue("システム生成パラメーターの設定").setFontWeight("bold").setFontSize(14).setBackground("#cfe2f3");
  sheet.getRange("A1:C1").merge();

  const headers = [
    ["項目名 (Parameter)", "設定値 (Value)", "説明・入力例 (Description)"]
  ];
  sheet.getRange("A3:C3").setValues(headers).setBackground("#4a86e8").setFontColor("white").setFontWeight("bold");

  // 入力項目定義
  const parameters = [
    ["対象とする期", "26上期", "システム生成名（Prefix）の一部となる半期や年度の指定。"],
    ["勉強会名称", "AWS勉強会", "開催される勉強会のタイトル。対象期と結合されてファイル名になります。"],
    ["保存先フォルダID", "", "生成したファイルを格納するGoogle Driveのフォルダの「ID」または「URL」を直接貼り付けてください。空欄ならこのシートと同じ場所に作成されます。"]
  ];

  const rowCount = parameters.length;
  sheet.getRange(4, 1, rowCount, 3).setValues(parameters);

  // スタイル設定（入力セル）
  const valueRange = sheet.getRange(4, 2, rowCount, 1);
  valueRange.setBackground("#fff2cc").setBorder(true, true, true, true, true, true);

  // 列幅の調整
  sheet.setColumnWidth(1, 200);
  sheet.setColumnWidth(2, 250);
  sheet.setColumnWidth(3, 450);

  // 枠線の設定
  sheet.getRange(3, 1, rowCount + 1, 3).setBorder(true, true, true, true, true, true);

  // 注釈（使い方とエラー時の連絡先）
  const instructionCell = sheet.getRange(rowCount + 5, 1);
  instructionCell.setValue("※ 上記の「設定値（黄色いセル）」を入力後、上部メニューの「▶️ システム生成」＞「システムを構築する」をクリックしてください。").setFontColor("red").setFontWeight("bold");

  const authWarningCell = sheet.getRange(rowCount + 7, 1);
  authWarningCell.setValue("【初回実行時の注意（承認画面が出た場合）】\n初めて実行する際、「このアプリはGoogleで確認されていません」という警告が出ます（GASの標準仕様です）。\n慌てずに ［詳細］ ＞ ［安全ではないページに移動］ ＞ ［許可］ の順にクリックして進めてください。").setFontColor("red").setFontWeight("bold");

  const creatorContactCell = sheet.getRange(rowCount + 9, 1);
  creatorContactCell.setValue("【管理者・作成者へのお問い合わせ】\nジェネレーターの誤作動やエラーが発生した場合は、〇〇部 〇〇（Slack: @xxxx）までご連絡ください。").setFontColor("#666666").setFontSize(10);

  Browser.msgBox("ジェネレーターのUI構築が完了しました！\\n画面上部のメニューからシステムを生成できます。");
}

/**
 * スプレッドシートを開いたときに自動的にメニューを追加する
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('▶️ システム生成')
    .addItem('システムを構築する', 'buildSystem')
    .addToUi();
}
```

## system_builder.js
```
/**
 * 出欠管理システム - メイン・システムビルダー
 *
 * アーキテクチャ:
 *   buildSystem()         ← エントリポイント（オーケストレーター）
 *   _createForms()        ← Phase 2: フォーム作成・バインド待機
 *   _buildLogSheets()     ← Phase 3a: Log_Attendance / Log_Notice 構築
 *   _buildMasterSheets()  ← Phase 3b: DB・Progress_Master・Schedule_DB 構築
 *   _buildDashboard()     ← Phase 4: Dashboard 作成・URL生成・シート整列
 */

// ============================================================
// エントリポイント
// ============================================================

function buildSystem() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName("Settings");
    const ui = SpreadsheetApp.getUi();

    if (!sheet) {
        ui.alert("エラー", "Settingsシートが見つかりません。セットアップをやり直してください。", ui.ButtonSet.OK);
        return;
    }

    const targetTerm = sheet.getRange("B4").getValue();
    const studyName  = sheet.getRange("B5").getValue();
    const targetFolderId = sheet.getRange("B6").getValue();

    if (!targetTerm || !studyName) {
        ui.alert("入力エラー", "「対象とする期」と「勉強会名称」は必須項目です。", ui.ButtonSet.OK);
        return;
    }

    const systemName = `[${targetTerm}] ${studyName} 出欠管理システム`;
    const response = ui.alert("システム生成の開始",
        `以下の設定でシステム一式を自動生成します。\n\nシステム名: ${systemName}\n\nよろしいですか？（数分かかる場合があります）`,
        ui.ButtonSet.YES_NO);
    if (response == ui.Button.NO) return;

    sheet.getRange(13, 1).setValue("🔄 システムを生成中...しばらくお待ちください").setFontColor("orange");

    try {
        // --- Phase 1: 保存先フォルダの決定 ---
        const TEMPLATE_SS_ID = "1HCWhO6R4IHquO63YNFcy4UcMGNaF0cs9AZOS87DfpA0";
        let parentFolder;
        try {
            if (targetFolderId) {
                const folderIdStr = String(targetFolderId).match(/folders\/([^/?]+)/)
                    ? String(targetFolderId).match(/folders\/([^/?]+)/)[1] : String(targetFolderId);
                parentFolder = DriveApp.getFolderById(folderIdStr);
            } else {
                parentFolder = DriveApp.getFileById(ss.getId()).getParents().next();
            }
        } catch (e) {
            ui.alert("エラー", "指定されたフォルダIDが見つからないか、権限がありません。カレントフォルダに作成します。", ui.ButtonSet.OK);
            parentFolder = DriveApp.getFileById(ss.getId()).getParents().next();
        }

        // テンプレートをコピーして新しいスプレッドシートを作成
        const newSSFile = DriveApp.getFileById(TEMPLATE_SS_ID).makeCopy(systemName, parentFolder);
        const newSS = SpreadsheetApp.openById(newSSFile.getId());

        // --- Phase 2: フォーム作成・バインド ---
        const { formA, formB, formASheet, formBSheet } = _createForms(newSS, studyName, parentFolder);

        // --- Phase 3a: Log シートの構築 ---
        _buildLogSheets(newSS, formASheet, formBSheet);

        // --- Phase 3b: マスタ・集計シートの構築 ---
        _buildMasterSheets(newSS);

        // --- Phase 3c: 旧出欠表連携IFシートの構築 ---
        _buildIFLegacySheet(newSS);

        // --- Phase 4: Dashboard 構築・完了 ---
        _buildDashboard(newSS, formA, formB);

        // 完了通知
        sheet.getRange(13, 1).setValue("✅ システム生成完了！").setFontColor("green");
        sheet.getRange(14, 1).setValue("管理スプレッドシートURL: ");
        sheet.getRange(14, 2).setValue(newSS.getUrl());
        sheet.getRange(15, 1).setValue("当日打刻フォームURL: ");
        sheet.getRange(15, 2).setValue(formA.getPublishedUrl());
        sheet.getRange(16, 1).setValue("事前連絡フォームURL: ");
        sheet.getRange(16, 2).setValue(formB.getPublishedUrl());

        ui.alert("完了", "システム一式の自動生成が完了しました！\n生成されたスプレッドシートのURLから初期設定（Member_DBの登録等）を行ってください。", ui.ButtonSet.OK);

    } catch (e) {
        ui.alert("実行エラー", "処理中にエラーが発生しました。\n" + e.message + "\n\n詳細:\n" + e.stack, ui.ButtonSet.OK);
        sheet.getRange(13, 1).setValue("❌ エラー発生: " + e.message + " (詳細: " + e.stack + ")").setFontColor("red");
    }
}

// ============================================================
// Phase 2: フォーム作成・バインド待機
// ============================================================

/**
 * 当日打刻フォーム(A)と事前連絡フォーム(B)を作成しスプレッドシートにバインドする。
 * Googleの非同期バインド完了を最大45秒待機し、シートオブジェクトを返す。
 * @returns {{ formA, formB, formASheet, formBSheet }}
 */
function _createForms(newSS, studyName, parentFolder) {
    // Form A: 当日出欠打刻用
    const formA = FormApp.create(`${studyName} 当日出欠打刻`);
    formA.setDescription(`本日の勉強会へのご参加ありがとうございます。\n出欠を記録するため、以下の情報を入力してチェックインしてください。\n※所定の遅刻許容時間を過ぎての打刻は「欠席」としてシステムに自動判定・記録されます。\n（何か問題がある場合は「${studyName}」の運営担当までお知らせください）`);
    formA.addTextItem().setTitle('社員番号（半角数字）').setRequired(true);
    formA.addTextItem().setTitle('【システム専用】認証コード（変更しないでください）').setRequired(true);
    formA.setDestination(FormApp.DestinationType.SPREADSHEET, newSS.getId());
    const formAFile = DriveApp.getFileById(formA.getId());
    parentFolder.addFile(formAFile);
    DriveApp.getRootFolder().removeFile(formAFile);

    // Form B: 事前連絡用（列順序: B=日付, C=社員番号, D=連絡種別, E=理由）
    const formB = FormApp.create(`${studyName} 欠席・遅刻 事前連絡`);
    formB.setDescription(`やむを得ず勉強会を欠席、または遅刻される場合は、こちらから事前申請を行ってください。\n事前連絡がない場合は「無断欠席」ステータスとなり、評価に影響する場合があります。\n※個別の相談事項がある場合は、「${studyName}」にて講師宛にご連絡ください。`);
    formB.addListItem().setTitle('対象となる日付（いつ休み/遅刻しますか？）').setRequired(true);
    formB.addTextItem().setTitle('社員番号（半角数字）').setRequired(true);
    formB.addMultipleChoiceItem().setTitle('連絡種別').setChoiceValues(['欠席', '遅刻']).setRequired(true);
    formB.addParagraphTextItem().setTitle('理由').setRequired(true);
    formB.setDestination(FormApp.DestinationType.SPREADSHEET, newSS.getId());
    const formBFile = DriveApp.getFileById(formB.getId());
    parentFolder.addFile(formBFile);
    DriveApp.getRootFolder().removeFile(formBFile);

    // バインド完了を最大45秒待機
    let formASheet = null;
    let formBSheet = null;
    for (let wait = 0; wait < 15; wait++) {
        Utilities.sleep(3000);
        SpreadsheetApp.flush();
        for (let s of newSS.getSheets()) {
            const url  = s.getFormUrl();
            const name = s.getName();
            if (url && url.includes(formA.getId())) {
                formASheet = s;
            } else if (url && url.includes(formB.getId())) {
                formBSheet = s;
            } else if (name.includes("フォーム") || name.includes("Form")) {
                const lastCol = s.getLastColumn();
                if (lastCol > 0) {
                    const headerStr = s.getRange(1, 1, 1, lastCol).getValues()[0].join("");
                    if (headerStr.includes("認証コード")) formASheet = s;
                    else if (headerStr.includes("連絡種別") || headerStr.includes("遅刻")) formBSheet = s;
                }
            }
        }
        if (formASheet && formBSheet) break;
    }

    if (!formASheet && !formBSheet) {
        throw new Error("フォームのバインド処理がタイムアウトしました。(両方のフォームが見つかりません)\nGoogleのシステム遅延の可能性があります。1〜2分後にもう一度「初期セットアップ」を実行してください。");
    } else if (!formASheet || !formBSheet) {
        throw new Error("片方のフォームのバインドがタイムアウトしました。\nもう一度「初期セットアップ」を実行してください。");
    }

    return { formA, formB, formASheet, formBSheet };
}

// ============================================================
// Phase 3a: Log シート構築
// ============================================================

/**
 * Log_Attendance・Log_Notice シートのヘッダー・数式・条件付き書式を設定する。
 */
function _buildLogSheets(newSS, formASheet, formBSheet) {

    // --- Log_Attendance ---
    formASheet.setName("Log_Attendance");
    // ARRAYFORMULAはフォーム行挿入で破壊されるため、ヘッダはテキストのみとし
    // フォーム送信トリガーで行単位に数式を書き込むアーキテクチャを採用。
    const hdrDark = { bg: "#434343", fg: "#ffffff" };
    formASheet.getRange(1, 4).setValue("システム判定（区分）").setBackground("#fce5cd").setFontColor("#000000").setFontWeight("bold");
    formASheet.getRange(1, 5).setValue("計算キー").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");
    formASheet.getRange(1, 6).setValue("氏名参照").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");
    formASheet.getRange(1, 7).setValue("手動区分").setBackground("#fff2cc").setFontColor("#000000").setFontWeight("bold");
    formASheet.getRange(1, 8).setValue("メモ").setBackground("#e69138").setFontColor("#ffffff").setFontWeight("bold");
    formASheet.getRange(1, 9).setValue("⚠️ システムMSG").setBackground("#cc0000").setFontColor("#ffffff").setFontWeight("bold");
    // G列: 手動区分プルダウン（リアル/リモートのみ許容）
    formASheet.getRange("G2:G1000").setDataValidation(
        SpreadsheetApp.newDataValidation()
            .requireValueInList(["リアル", "リモート"], true)
            .setAllowInvalid(true)
            .setHelpText("手動でリアル/リモートを指定する場合のみ選択。空欄=ハッシュ認証で自動判定。")
            .build()
    );

    const lastRowA = formASheet.getLastRow();
    if (lastRowA > 1) {
        const numRows = lastRowA - 1;
        formASheet.getRange(2, 4, numRows).setFormula('=IF(A2="", "", IF(G2="リモート", "手動承認(リモート)", IF(G2="リアル", "手動承認(リアル)", IF(G2<>"", "手動承認(リアル)", IF(C2="", "", IF(IFERROR(VALUE(C2), 0) = (INT(A2) * VALUE(Dashboard!$Z$2)) + 11, "リアル", IF(IFERROR(VALUE(C2), 0) = (INT(A2) * VALUE(Dashboard!$Z$2)) + 22, "リモート", "❌ 不正・無効")))))))');
        formASheet.getRange(2, 5, numRows).setFormula('=IF(D2="❌ 不正・無効", "", IF(A2="", "", INT(A2) & "_" & TEXT(VALUE(B2),"0")))');
        formASheet.getRange(2, 6, numRows).setFormula('=IF(B2="", "", IFERROR(VLOOKUP(TEXT(VALUE(B2),"0"), Member_DB!$A:$B, 2, FALSE), "#N/A"))');
        formASheet.getRange(2, 9, numRows).setFormula('=IF(A2="", "", IF(F2="#N/A", "⚠️マスタ未登録（社員番号）", IF(D2="❌ 不正・無効", "⚠️不正・改ざん疑い", IF(AND(E2<>"", COUNTIF(E:E, E2)>1), "⚠️重複打刻（最新のみ有効）", ""))))');
    }
    formASheet.getRange("A:A").setNumberFormat("yyyy/MM/dd HH:mm:ss");
    formASheet.getRange("B:B").setNumberFormat("@");

    formASheet.setConditionalFormatRules([
        SpreadsheetApp.newConditionalFormatRule()
            .whenFormulaSatisfied('=$D2="❌ 不正・無効"').setBackground("#ea4335").setFontColor("#ffffff")
            .setRanges([formASheet.getRange("A2:I1000")]).build(),
        SpreadsheetApp.newConditionalFormatRule()
            .whenFormulaSatisfied('=AND($E2<>"", COUNTIF($E:$E, $E2) > 1)').setBackground("#fff2cc").setFontColor("#b45f06")
            .setRanges([formASheet.getRange("A2:I1000")]).build(),
        SpreadsheetApp.newConditionalFormatRule()
            .whenFormulaSatisfied('=$I2<>""').setBackground("#fce8e6").setFontColor("#cc0000")
            .setRanges([formASheet.getRange("A2:I1000")]).build(),
    ]);

    // --- Log_Notice ---
    formBSheet.setName("Log_Notice");
    formBSheet.getRange(1, 6).setValue("氏名参照").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");
    formBSheet.getRange(1, 7).setValue("メモ").setBackground("#e69138").setFontColor("#ffffff").setFontWeight("bold");
    formBSheet.getRange(1, 8).setValue("⚠️ システムMSG").setBackground("#cc0000").setFontColor("#ffffff").setFontWeight("bold");

    const lastRowB = formBSheet.getLastRow();
    if (lastRowB > 1) {
        const numRowsB = lastRowB - 1;
        formBSheet.getRange(2, 6, numRowsB).setFormula('=IF(C2="", "", IFERROR(VLOOKUP(TEXT(VALUE(C2),"0"), Member_DB!$A:$B, 2, FALSE), "#N/A"))');
        formBSheet.getRange(2, 8, numRowsB).setFormula('=IF(A2="", "", IF(F2="#N/A", "⚠️マスタ未登録（社員番号）", IF(AND(B2<>"", ISNA(MATCH(IFERROR(INT(B2),B2), INDIRECT("Schedule_DB!B:B"), 0))), "⚠️開催予定外の日付", "")))');
    }
    formBSheet.getRange("B:B").setNumberFormat("yyyy/MM/dd");
    formBSheet.getRange("C:C").setNumberFormat("@");

    formBSheet.setConditionalFormatRules([
        SpreadsheetApp.newConditionalFormatRule()
            .whenFormulaSatisfied('=AND($B2<>"", ISNA(MATCH(IFERROR(INT($B2),$B2), INDIRECT("Schedule_DB!B:B"), 0)))').setBackground("#fce8e6").setFontColor("#cc0000")
            .setRanges([formBSheet.getRange("B2:B1000")]).build(),
        SpreadsheetApp.newConditionalFormatRule()
            .whenFormulaSatisfied('=AND($B2<>"", INT($A2)>$B2)').setBackground("#fef0d9").setFontColor("#e69138")
            .setRanges([formBSheet.getRange("B2:B1000")]).build(),
        SpreadsheetApp.newConditionalFormatRule()
            .whenFormulaSatisfied('=$H2<>""').setBackground("#fce8e6").setFontColor("#cc0000")
            .setRanges([formBSheet.getRange("A2:H1000")]).build(),
    ]);

    // 初期シート（シート1）を削除
    const sheet1 = newSS.getSheetByName("シート1");
    if (sheet1) newSS.deleteSheet(sheet1);
}

// ============================================================
// Phase 3b: マスタ・集計シート構築
// ============================================================

/**
 * Member_DB / Log_ExternalSurvey / Progress_Master / Schedule_DB を構築する。
 */
function _buildMasterSheets(newSS) {

    // --- Member_DB ---
    const dbSheet = newSS.insertSheet("Member_DB");
    dbSheet.getRange("A1:D1").setValues([["社員番号", "氏名", "拠点", "役割"]])
        .setBackground("#434343").setFontColor("#ffffff").setFontWeight("bold");
    dbSheet.getRange("A:A").setNumberFormat("@");
    dbSheet.setConditionalFormatRules([
        SpreadsheetApp.newConditionalFormatRule().whenFormulaSatisfied('=$D2="講師"').setBackground("#fff2cc").setRanges([dbSheet.getRange("A2:D1000")]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenFormulaSatisfied('=$D2="サブ講師"').setBackground("#cfe2f3").setRanges([dbSheet.getRange("A2:D1000")]).build(),
    ]);

    // --- Log_ExternalSurvey ---
    const extSheet = newSS.insertSheet("Log_ExternalSurvey");
    extSheet.getRange("A1").setValue("社員番号").setBackground("#cfe2f3").setFontWeight("bold");
    extSheet.getRange("A:A").setNumberFormat("@");

    // --- Progress_Master ---
    const progressSheet = newSS.insertSheet("Progress_Master");
    progressSheet.getRange("A1:J1").setValues([["社員番号", "氏名", "拠点", "出席回数", "リアル回数", "リアル参加率", "アンケート提出数", "課題提出物", "最終試験合否", "資格取得"]])
        .setBackground("#434343").setFontColor("#ffffff").setFontWeight("bold");

    // A列: Member_DB から社員番号を自動展開
    progressSheet.getRange("A2").setFormula('=UNIQUE(FILTER(Member_DB!A2:A, Member_DB!A2:A<>""))');

    // B/C列: マスタ引き当て（IFERRORダブル試行: 文字列→数値）
    progressSheet.getRange("B2").setFormula('=ARRAYFORMULA(IF(A2:A="","", IFERROR(VLOOKUP(A2:A, Member_DB!$A:$D, 2, FALSE), IFERROR(VLOOKUP(VALUE(A2:A), Member_DB!$A:$D, 2, FALSE), ""))))');
    progressSheet.getRange("C2").setFormula('=ARRAYFORMULA(IF(A2:A="","", IFERROR(VLOOKUP(A2:A, Member_DB!$A:$D, 3, FALSE), IFERROR(VLOOKUP(VALUE(A2:A), Member_DB!$A:$D, 3, FALSE), ""))))');

    // D-G列: 統合集計ロジック
    progressSheet.getRange("D2").setFormula('=ARRAYFORMULA(IF(A2:A="","", BYROW(K2:ZZ, LAMBDA(r, COUNTIF(r, "*出席*")))))');
    progressSheet.getRange("E2").setFormula('=ARRAYFORMULA(IF(A2:A="","", BYROW(K2:ZZ, LAMBDA(r, COUNTIF(r, "*リアル*")))))');
    progressSheet.getRange("F2").setFormula('=ARRAYFORMULA(IF(D2:D="","", IF(D2:D=0, 0, E2:E / D2:D)))');
    progressSheet.getRange("F2:F").setNumberFormat("0%");
    progressSheet.getRange("G2").setFormula('=ARRAYFORMULA(IF(A2:A="","", COUNTIF(ARRAYFORMULA(TEXT(VALUE(Log_ExternalSurvey!$A:$A),"0")), TEXT(VALUE(A2:A),"0"))))');

    // K1: 日付ヘッダー（Schedule_DB から横展開）
    progressSheet.getRange("K1").setFormula('=IFERROR(TRANSPOSE(SORT(UNIQUE(Schedule_DB!$B$2:$B), 1, TRUE)), "")').setBackground("#ffe599");
    progressSheet.getRange("K1:Z1").setNumberFormat("yyyy/MM/dd");

    // K2: 出欠判定ロジック
    // Table機能が Log_Attendance/Log_Notice への直接参照（$A$2:$A等）を
    // データ開始行基準（$A$7:$A等）に自動変換する問題を回避するため、
    // 外側LET で INDIRECT() 変数を定義し、Table変換を受けない参照を確立する。
    const logicFormula = [
        // ── 外側LET: INDIRECT変数（Table変換を受けない）────────────────
        `=LET(`,
        `  att_A,  INDIRECT("Log_Attendance!A2:A"),`,
        `  att_B,  INDIRECT("Log_Attendance!B2:B"),`,
        `  att_D,  INDIRECT("Log_Attendance!D2:D"),`,
        `  att_AD, INDIRECT("Log_Attendance!A2:D"),`,
        `  not_B,  INDIRECT("Log_Notice!B2:B"),`,
        `  not_C,  INDIRECT("Log_Notice!C2:C"),`,
        `  not_D,  INDIRECT("Log_Notice!D2:D"),`,
        // ── MAKEARRAY: 全emp × 全日付 の出欠マトリクス ─────────────────
        `  MAKEARRAY(COUNTA($A$2:$A), COUNTA($K$1:$1), LAMBDA(r, c, LET(`,
        `    emp_id,     INDEX($A$2:$A, r),`,
        `    target_date, INDEX($K$1:$1, 1, c),`,
        `    sched_info,  XLOOKUP(target_date, Schedule_DB!$B:$B, Schedule_DB!$C:$E, {"", "", ""}),`,
        `    session_type, INDEX(sched_info, 1, 1),`,
        `    start_time,  INDEX(sched_info, 1, 2),`,
        `    grace_mins,  INDEX(sched_info, 1, 3),`,
        `    threshold_time, start_time + TIME(0, grace_mins, 0),`,
        `    orig_date, IF(session_type="補講", XLOOKUP(INDEX(XLOOKUP(target_date, Schedule_DB!$B:$B, Schedule_DB!$A:$A, ""), 1, 1) & "通常", ARRAYFORMULA(Schedule_DB!$A:$A & Schedule_DB!$C:$C), Schedule_DB!$B:$B, ""), ""),`,
        `    orig_key, IF(orig_date<>"", TEXT(orig_date, "yyyy/MM/dd") & emp_id, ""),`,
        `    orig_has_att, IF(orig_key<>"", XLOOKUP(orig_key, ARRAYFORMULA(TEXT(att_A, "yyyy/MM/dd") & TEXT(VALUE(att_B),"0")), att_A, "", 0, -1) <> "", FALSE),`,
        `    key_str, TEXT(target_date, "yyyy/MM/dd") & TEXT(VALUE(emp_id),"0"),`,
        `    max_ts, IFERROR(MAX(FILTER(att_A, (INT(att_A)=target_date) * (TEXT(VALUE(att_B),"0")=TEXT(VALUE(emp_id),"0")) * (att_D<>"❌ 不正・無効"))), 0),`,
        `    has_att, max_ts > 0,`,
        `    att_rec, IF(has_att, XLOOKUP(max_ts, att_A, att_AD, {"","","",""}), {"","","",""}),`,
        `    att_time, IF(has_att, MOD(INDEX(att_rec, 1, 1), 1), 0),`,
        `    att_type, IF(has_att, INDEX(att_rec, 1, 4), ""),`,
        `    att_short, IF(REGEXMATCH(att_type, "リアル"), "リアル", IF(REGEXMATCH(att_type, "リモート"), "リモート", att_type)),`,
        `    notice_type, XLOOKUP(key_str, ARRAYFORMULA(TEXT(not_B, "yyyy/MM/dd") & TEXT(VALUE(not_C),"0")), not_D, "", 0, -1),`,
        `    has_notice, notice_type <> "",`,
        `    IF(emp_id="", "",`,
        `      IFS(`,
        `        target_date > TODAY(), "",`,
        `        has_att, IF(att_time > threshold_time, "欠席(遅刻30分超)",`,
        `                   IF(att_time > start_time,`,
        `                     IF(has_notice, "出席(" & att_short & ")・遅刻・届出有", "出席(" & att_short & ")・遅刻"),`,
        `                     IF(has_notice, "出席(" & att_short & ")・届出有", "出席(" & att_short & ")"))),`,
        `        has_notice, IF(notice_type="欠席", "欠席・届出有", "無断欠席(遅刻届のみ)"),`,
        `        AND(session_type="補講", orig_has_att), "対象外",`,
        `        TRUE, "無断欠席"`,
        `      )`,
        `    )`,
        `  )))`,
        `)`
    ].join("");
    progressSheet.getRange("K2").setFormula(logicFormula);

    // 条件付き書式: Progress_Master
    const roleRuleRange = progressSheet.getRange("A2:J1000");
    const ruleRange     = progressSheet.getRange("K2:ZZ1000");
    progressSheet.setConditionalFormatRules([
        // 役割色分け（CF は別シート直接参照不可のため INDIRECT 経由）
        SpreadsheetApp.newConditionalFormatRule().whenFormulaSatisfied('=IFERROR(VLOOKUP($A2, INDIRECT("Member_DB!A:D"), 4, FALSE), "")="講師"').setBackground("#fff2cc").setRanges([roleRuleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenFormulaSatisfied('=IFERROR(VLOOKUP($A2, INDIRECT("Member_DB!A:D"), 4, FALSE), "")="サブ講師"').setBackground("#cfe2f3").setRanges([roleRuleRange]).build(),
        // 出欠ステータス色分け（強い条件を優先）
        SpreadsheetApp.newConditionalFormatRule().whenTextContains("無断欠席").setBackground("#ea4335").setFontColor("#ffffff").setRanges([ruleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenTextContains("欠席(遅刻30分超)").setBackground("#f4cccc").setFontColor("#cc0000").setRanges([ruleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenTextContains("出席(リアル)").setBackground("#d9ead3").setFontColor("#274e13").setRanges([ruleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenTextContains("出席(リモート)").setBackground("#d9ead3").setFontColor("#38761d").setRanges([ruleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenTextContains("・届出有").setBackground("#cfe2f3").setFontColor("#1155cc").setRanges([ruleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("欠席・届出有").setBackground("#cfe2f3").setFontColor("#1155cc").setRanges([ruleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("対象外").setBackground("#f3f3f3").setFontColor("#b7b7b7").setRanges([ruleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenFormulaSatisfied('=$A2<>""').setBackground("#f3f3f3").setRanges([ruleRange]).build(),
    ]);

    // --- Schedule_DB ---
    const schedSheet = newSS.insertSheet("Schedule_DB", 0);
    schedSheet.getRange("A1:E1").setValues([["対象回", "📅 開催予定日", "種別（通常/補講）", "開始時刻", "遅刻許容時間(分)"]])
        .setBackground("#434343").setFontColor("#ffffff").setFontWeight("bold");
    // B列の書式を先に設定してから値をセット（書式設定後にsetValuesすると文字列→日付シリアル変換が保証される）
    schedSheet.getRange("B2:B").setNumberFormat("yyyy/MM/dd");
    schedSheet.getRange("D2:D").setNumberFormat("HH:mm");
    // サンプルデータ: 日付はDateオブジェクト、時刻はTIMEVALUE相当の小数でセット
    schedSheet.getRange("A2:E2").setValues([[1, new Date(2026, 3, 10), "通常",  new Date(1899, 11, 30, 20, 0, 0), 30]]);
    schedSheet.getRange("A3:E3").setValues([[2, new Date(2026, 4, 10), "通常",  new Date(1899, 11, 30, 20, 0, 0), 30]]);
    schedSheet.getRange("A4:E4").setValues([["",  new Date(2026, 4, 24), "補講", new Date(1899, 11, 30, 13, 0, 0),  0]]);
    // 種別列: プルダウンで「通常/補講」の2択のみ許容
    schedSheet.getRange("C2:C1000").setDataValidation(
        SpreadsheetApp.newDataValidation()
            .requireValueInList(["通常", "補講"], true)
            .setAllowInvalid(false)
            .setHelpText("「通常」または「補講」のみ入力可能です。それ以外の値は判定ロジックを破損させます。")
            .build()
    );
    schedSheet.setColumnWidth(2, 120);
    schedSheet.setColumnWidth(3, 110);
    schedSheet.setColumnWidth(4, 100);
    schedSheet.setColumnWidth(5, 120);
}

// ============================================================
// Phase 4: Dashboard 構築・シート整列
// ============================================================

/**
 * Dashboard シートを作成し、QRコード・アラートサマリー・打刻URLを設定する。
 * 最後にシート順を利用頻度の高い順に整列する。
 */
function _buildDashboard(newSS, formA, formB) {
    const dashSheet = newSS.insertSheet("Dashboard", 0);

    // 秘匿データ（白文字で非表示）
    dashSheet.getRange("Z1").setValue(formB.getId()).setFontColor("#ffffff");
    const secretKey = Math.floor(Math.random() * 900000) + 100000;
    dashSheet.getRange("Z2").setValue(secretKey).setFontColor("#ffffff");
    dashSheet.getRange("Z3").setFormula("=INT(TODAY())").setFontColor("#ffffff");
    dashSheet.getRange("Z4").setValue(formA.getId()).setFontColor("#ffffff");

    SpreadsheetApp.flush(); // Z3 の日付シリアル値を確定してから読み取る
    const todaySerial = dashSheet.getRange("Z3").getValue();
    const realHash   = (todaySerial * secretKey) + 11;
    const remoteHash = (todaySerial * secretKey) + 22;

    // 打刻用プリフィルURL の生成
    const authItem  = formA.getItems(FormApp.ItemType.TEXT)[1].asTextItem();
    const realUrl   = formA.createResponse().withItemResponse(authItem.createResponse(String(realHash))).toPrefilledUrl();
    const remoteUrl = formA.createResponse().withItemResponse(authItem.createResponse(String(remoteHash))).toPrefilledUrl();

    // 案内用リンク
    dashSheet.getRange("A1:C1").setValues([["【受講者・案内用データ】コピペ用", "", ""]])
        .setBackground("#434343").setFontColor("#ffffff").setFontWeight("bold");
    dashSheet.getRange("A2:B2").setValues([["事前連絡フォームURL", formB.getPublishedUrl()]]);
    dashSheet.getRange("A3:B3").setValues([["リモート打刻用URL", remoteUrl]]);
    dashSheet.getRange("A4:B4").setValues([["リアル打刻用URL", realUrl]]);

    // アラートサマリー
    // Table機能がクロスシート参照をデータ範囲に変換するため H2:H は壊れる場合がある。
    // H:H 全列参照から「⚠️ システムMSG」ヘッダー行(各1件)を減算して正確に集計する。
    const attErrFormula = `COUNTIF(Log_Attendance!I:I,"⚠️*")-COUNTIF(Log_Attendance!I:I,"⚠️ システムMSG")`;
    const notErrFormula = `COUNTIF(Log_Notice!H:H,"⚠️*")-COUNTIF(Log_Notice!H:H,"⚠️ システムMSG")`;
    dashSheet.getRange("A5").setFormula(
        `=IF((${attErrFormula})+(${notErrFormula})=0,` +
        `"✅ 現在、システムエラーはありません",` +
        `"⚠️ " & TEXT((${attErrFormula})+(${notErrFormula}),"0") & " 件のエラーがログに存在します。各ログシートの⚠️列を確認してください")`
    ).setBackground("#fff2cc").setFontWeight("bold");

    // QRコード
    const qrApiUrl = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=";
    dashSheet.getRange("A7").setValue("会場用QRコード").setFontWeight("bold");
    dashSheet.getRange("B8").setFormula(`=IMAGE("${qrApiUrl}" & ENCODEURL(B4))`);
    dashSheet.setColumnWidth(1, 280);
    dashSheet.setColumnWidth(2, 450);
    dashSheet.setRowHeights(8, 1, 250);

    // シート順を利用頻度の高い順に整列
    const moveSheet = (sName, pos) => {
        const tgt = newSS.getSheetByName(sName);
        if (tgt) { newSS.setActiveSheet(tgt); newSS.moveActiveSheet(pos); }
    };
    moveSheet("Dashboard",        1);
    moveSheet("Progress_Master",  2);
    moveSheet("Log_Attendance",   3);
    moveSheet("Log_Notice",       4);
    moveSheet("Schedule_DB",      5);
    moveSheet("Member_DB",        6);
    moveSheet("Log_ExternalSurvey", 7);
}

// ============================================================
// Phase 3c: IF_Legacy_Export シート構築
// ============================================================

/**
 * 旧出欠表にコピペするためのインターフェースシートを作成する。
 * Member_DB と Progress_Master からデータを参照し、旧記号にマッピングする。
 */
function _buildIFLegacySheet(newSS) {
    const ifSheet = newSS.insertSheet("IF_Legacy_Export");
    const hdrDark = { bg: "#434343", fg: "#ffffff" };
    
    // ヘッダー行
    ifSheet.getRange("A1").setValue("社員番号").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");
    ifSheet.getRange("B1").setValue("氏名").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");
    
    // C1〜N1: 各回（Progress_Masterのヘッダを参照。最大12回に制限して#REF!エラーを防止）
    ifSheet.getRange("C1").setFormula("=ARRAY_CONSTRAIN(Progress_Master!K1:ZZ1, 1, 12)").setBackground("#d9ead3").setFontColor("#000000").setFontWeight("bold");
    
    // 右側のサマリー項目 (O1〜U1)
    ifSheet.getRange("O1").setValue("出席回数").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");
    ifSheet.getRange("P1").setValue("参加者アンケート").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");
    ifSheet.getRange("Q1").setValue("課題提出物").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");
    ifSheet.getRange("R1").setValue("リアル参加").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");
    ifSheet.getRange("S1").setValue("最終試験ローカル試験").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");
    ifSheet.getRange("T1").setValue("資格取得").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");
    ifSheet.getRange("U1").setValue("備考欄").setBackground(hdrDark.bg).setFontColor(hdrDark.fg).setFontWeight("bold");

    // データ展開用の数式 (行2)
    // A列、B列: Member_DB をそのまま参照
    ifSheet.getRange("A2").setFormula("=ARRAYFORMULA(IF(Member_DB!A2:A=\"\", \"\", Member_DB!A2:B))");
    
    // C列: マッピング処理 (最大12回分に制限してスプレッドシートの崩壊を防ぐ)
    const mappingLogic = [
        `=ARRAY_CONSTRAIN(ARRAYFORMULA(IF($A2:$A=\"\", \"\", `,
        `  IFS(`,
        `    Progress_Master!K2:ZZ=\"\", \"\",`,
        `    REGEXMATCH(Progress_Master!K2:ZZ, \"出席\\\\(.*\\\\)・届出有\"), \"○\",`,
        `    REGEXMATCH(Progress_Master!K2:ZZ, \"出席\\\\(.*\\\\)・遅刻・届出有\"), \"△\",`,
        `    REGEXMATCH(Progress_Master!K2:ZZ, \"出席\\\\(.*\\\\)・遅刻\"), \"▲\",`,
        `    Progress_Master!K2:ZZ=\"欠席・届出有\", \"-\",`,
        `    Progress_Master!K2:ZZ=\"無断欠席\", \"×\",`,
        `    Progress_Master!K2:ZZ=\"無断欠席(遅刻届のみ)\", \"×\",`,
        `    Progress_Master!K2:ZZ=\"欠席(遅刻30分超)\", \"×\",`,
        `    Progress_Master!K2:ZZ=\"対象外\", \"\",`,
        `    REGEXMATCH(Progress_Master!K2:ZZ, \"出席\"), \"○\",`,
        `    TRUE, \"\"`,
        `  )`,
        `)), 1000, 12)`
    ].join("");
    ifSheet.getRange("C2").setFormula(mappingLogic);

    // サマリー項目のデータ参照 (Progress_Masterから)
    ifSheet.getRange("O2").setFormula("=ARRAYFORMULA(IF($A2:$A=\"\", \"\", Progress_Master!D2:D))");
    ifSheet.getRange("P2").setFormula("=ARRAYFORMULA(IF($A2:$A=\"\", \"\", Progress_Master!G2:G))");
    ifSheet.getRange("Q2").setFormula("=ARRAYFORMULA(IF($A2:$A=\"\", \"\", Progress_Master!H2:H))");
    ifSheet.getRange("R2").setFormula("=ARRAYFORMULA(IF($A2:$A=\"\", \"\", Progress_Master!E2:E))");
    ifSheet.getRange("S2").setFormula("=ARRAYFORMULA(IF($A2:$A=\"\", \"\", Progress_Master!I2:I))");
    ifSheet.getRange("T2").setFormula("=ARRAYFORMULA(IF($A2:$A=\"\", \"\", Progress_Master!J2:J))");

    // 列幅の調整
    ifSheet.setColumnWidth(1, 100);
    ifSheet.setColumnWidth(2, 120);
    for(let i=3; i<=14; i++) {
        ifSheet.setColumnWidth(i, 50); // C〜N列
    }
    
    // 条件付き書式
    const ruleRange = ifSheet.getRange("C2:N1000");
    ifSheet.setConditionalFormatRules([
        SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("○").setFontColor("#274e13").setRanges([ruleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("△").setFontColor("#b45f06").setRanges([ruleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("▲").setFontColor("#b45f06").setRanges([ruleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("-").setFontColor("#1155cc").setRanges([ruleRange]).build(),
        SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo("×").setFontColor("#cc0000").setRanges([ruleRange]).build(),
    ]);
}
```

