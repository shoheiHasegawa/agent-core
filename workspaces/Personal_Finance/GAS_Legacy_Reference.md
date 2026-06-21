# Legacy GAS Scripts
## GAS-zaimu-into-rakutenpay-payment-history.md
```
GAS編集前
```javascript
function importRakutenPayEmailsMonthly() {
  var labelName = "RakutenPay"; // 対象ラベル
  var folderId = "18ixI0zlv30o_fNPXS-Ba3o8dZkvreEDJ"; // CSV出力先フォルダID
  var processedSheetName = "ProcessedIDs"; // メールID管理用シート
  
  var label = GmailApp.getUserLabelByName(labelName);
  if (!label) {
    Logger.log("ラベルが存在しません: " + labelName);
    return;
  }

  // 実行日を基準に前月の1日〜末日
  var today = new Date();
  var year = today.getFullYear();
  var month = today.getMonth(); // 0=1月
  var firstDayPrevMonth = new Date(year, month - 1, 1);
  var lastDayPrevMonth = new Date(year, month, 0);

  var afterStr = Utilities.formatDate(firstDayPrevMonth, "JST", "yyyy/MM/dd");
  var beforeStr = Utilities.formatDate(new Date(lastDayPrevMonth.getTime() + 24*60*60*1000), "JST", "yyyy/MM/dd");

  // Gmail検索クエリ
  var query = 'label:' + labelName + ' after:' + afterStr + ' before:' + beforeStr;
  Logger.log("検索クエリ: " + query);
  var threads = GmailApp.search(query);
  Logger.log("取得スレッド数: " + threads.length);

  var sheet = SpreadsheetApp.getActiveSpreadsheet();

  // メールID管理用シート作成 or 取得
  var processedSheet = sheet.getSheetByName(processedSheetName);
  if (!processedSheet) {
    processedSheet = sheet.insertSheet(processedSheetName);
    processedSheet.appendRow(["MessageID"]);
  }
  var lastRow = processedSheet.getLastRow();
  var processedIds = [];
  if (lastRow > 1) {
    processedIds = processedSheet.getRange(2, 1, lastRow - 1, 1).getValues().flat();
  }

  // CSV用データ
  var csvData = [["日付","カテゴリ","内訳","内容","金額","支払元","メモ"]];
  var newMailCount = 0;

  threads.forEach(function(thread){
    var messages = thread.getMessages();
    messages.forEach(function(msg){
      var msgId = msg.getId();
      if (processedIds.includes(msgId)) return; // 重複メールはスキップ

      var body = msg.getPlainBody();
      var dateMatch = body.match(/ご利用日時\s*([\d]{4}\/[\d]{2}\/[\d]{2})/);
      var amountMatch = body.match(/決済総額\s*¥?([\d,]+)/);
      var storeMatch = body.match(/ご利用店舗\s*(.*)/);

      if (dateMatch && amountMatch && storeMatch) {
        csvData.push([
          dateMatch[1],
          "",
          "",
          "楽天Pay: " + storeMatch[1],
          parseInt(amountMatch[1].replace(/,/g, "")),
          "楽天Pay",
          ""
        ]);
        newMailCount++;
      }

      // メールIDを記録して重複防止
      processedSheet.appendRow([msgId]);
    });
  });

  // CSV出力
  if (csvData.length > 1) {
    var folder = DriveApp.getFolderById(folderId);
    var timestamp = Utilities.formatDate(new Date(), "JST", "yyyyMMdd_HHmm");
    var fileName = "RakutenPay_" + timestamp + ".csv";
    var csvContent = csvData.map(e => e.join(",")).join("\n");
    folder.createFile(fileName, csvContent, MimeType.CSV);
    Logger.log("CSVを作成しました: " + fileName);
  } else {
    Logger.log("新規メールがありませんでした。CSVは作成されません。");
  }

  // 実行ログ
  Logger.log("実行日: " + Utilities.formatDate(new Date(), "JST", "yyyy/MM/dd HH:mm"));
  Logger.log("新規取得メール件数: " + newMailCount);
}
```

修正後
```
function importRakutenPayEmailsMonthly() {
  var labelName = "RakutenPay"; // 対象ラベル
  var folderId = "18ixI0zlv30o_fNPXS-Ba3o8dZkvreEDJ"; // CSV出力先フォルダID
  var processedSheetName = "ProcessedIDs"; // メールID管理用シート

  var label = GmailApp.getUserLabelByName(labelName);
  if (!label) {
    Logger.log("ラベルが存在しません: " + labelName);
    return;
  }

  // 実行日を基準に前月の1日〜末日
  var today = new Date();
  var year = today.getFullYear();
  var month = today.getMonth(); // 0=1月
  var firstDayPrevMonth = new Date(year, month - 1, 1);
  var lastDayPrevMonth = new Date(year, month, 0);

  var afterStr = Utilities.formatDate(firstDayPrevMonth, "JST", "yyyy/MM/dd");
  var beforeStr = Utilities.formatDate(
    new Date(lastDayPrevMonth.getTime() + 24 * 60 * 60 * 1000),
    "JST",
    "yyyy/MM/dd"
  );

  // Gmail検索クエリ
  var query = 'label:' + labelName + ' after:' + afterStr + ' before:' + beforeStr;
  Logger.log("検索クエリ: " + query);

  var threads = GmailApp.search(query);
  Logger.log("取得スレッド数: " + threads.length);

  var sheet = SpreadsheetApp.getActiveSpreadsheet();

  // メールID管理用シート作成 or 取得
  var processedSheet = sheet.getSheetByName(processedSheetName);
  if (!processedSheet) {
    processedSheet = sheet.insertSheet(processedSheetName);
    processedSheet.appendRow(["MessageID"]);
  }

  var lastRow = processedSheet.getLastRow();
  var processedIds = [];
  if (lastRow > 1) {
    processedIds = processedSheet
      .getRange(2, 1, lastRow - 1, 1)
      .getValues()
      .flat();
  }

  // CSV用データ
  var csvData = [["日付","カテゴリ","内訳","内容","金額","支払元","メモ"]];
  var newMailCount = 0;

  threads.forEach(function(thread) {
    var messages = thread.getMessages();

    messages.forEach(function(msg) {
      var msgId = msg.getId();
      if (processedIds.includes(msgId)) return; // 重複メールはスキップ

      var body = msg.getPlainBody();

      // ===== ログ出力（調査用・今後の保守用）=====
      Logger.log("======================================");
      Logger.log("MessageID: " + msgId);
      Logger.log("Subject  : " + msg.getSubject());
      Logger.log("Body (plain):\n" + body);
      Logger.log("======================================");
      // ============================================

      // 正規表現（耐性強化済み）
      var dateMatch = body.match(/ご利用日時\s*([\d]{4}\/[\d]{2}\/[\d]{2})/);
      var amountMatch = body.match(/決済総額\s*([\d,]+)円/);
      var storeMatch = body.match(/ご利用店舗\s*([\s\S]*?)\s*-{10,}/);

      if (dateMatch && amountMatch && storeMatch) {
        // 店舗名を整形（電話番号行などを除外）
        var storeName = storeMatch[1]
          .split(/\r?\n/)
          .map(s => s.trim())
          .filter(s => s && !s.startsWith("電話番号"))[0];

        csvData.push([
          dateMatch[1],
          "",
          "",
          "楽天Pay: " + storeName,
          parseInt(amountMatch[1].replace(/,/g, "")),
          "楽天Pay",
          ""
        ]);

        newMailCount++;
      } else {
        Logger.log("⚠ 抽出失敗 MessageID: " + msgId);
      }

      // メールIDを記録して重複防止
      processedSheet.appendRow([msgId]);
    });
  });

  // CSV出力
  if (csvData.length > 1) {
    var folder = DriveApp.getFolderById(folderId);
    var timestamp = Utilities.formatDate(new Date(), "JST", "yyyyMMdd_HHmm");
    var fileName = "RakutenPay_" + timestamp + ".csv";
    var csvContent = csvData.map(e => e.join(",")).join("\n");
    folder.createFile(fileName, csvContent, MimeType.CSV);
    Logger.log("CSVを作成しました: " + fileName);
  } else {
    Logger.log("新規メールがありませんでした。CSVは作成されません。");
  }

  // 実行ログ
  Logger.log("実行日: " + Utilities.formatDate(new Date(), "JST", "yyyy/MM/dd HH:mm"));
  Logger.log("新規取得メール件数: " + newMailCount);
}
``````

