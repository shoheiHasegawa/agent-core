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
