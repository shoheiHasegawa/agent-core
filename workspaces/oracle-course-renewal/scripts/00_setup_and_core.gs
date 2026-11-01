/**
 * ================================================================================
 * 25上期 Oracle基礎勉強会：マスタスプレッドシート 共通セットアップ ＆ フォーム生成コアエンジン
 * ファイル名：00_setup_and_core.gs
 * ================================================================================
 *
 * 【このファイルの役割（最初に1回だけApps Scriptに登録する共通エンジン）】
 * ・各回のスクリプト（`generate_session04_forms.gs`, `generate_session05_forms.gs` 等）から共通で呼び出される
 *   フォーム自動生成処理および「社員番号KEY」一元管理 Dashboard の自動構築ロジックを提供します。
 *
 * 【使い方（初回のみ）】
 * 1. 新規の Google スプレッドシート（全回共通マスタ用）を作成します。
 * 2. メニュー「拡張機能」＞「Apps Script」を開きます。
 * 3. デフォルトの `コード.gs` の中身を消して、この `00_setup_and_core.gs` の内容を貼り付けます。
 *    （※任意：先に空のLinksシート・Dashboardシートだけ作っておきたい場合は `setupMasterSpreadsheet` を実行できます）
 * 4. 続けて、左側の「ファイル」横の「＋」＞「スクリプト」から各回用のファイル（例：`session04`）を追加し、
 *    `generate_session04_forms.gs` を貼り付けて `generateSession4Forms` を実行してください。
 * ================================================================================
 */

/**
 * マスタスプレッドシートの初期セットアップ関数（単体実行も可能）
 * 空のスプレッドシートに `Links` シートと `Dashboard` シート（ヘッダー枠）を作成し、不要な空白シートを整理します。
 */
function setupMasterSpreadsheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  ensureLinksSheet_(ss);
  rebuildDashboard(ss);
  cleanupDefaultBlankSheet_(ss);
  Logger.log("マスタスプレッドシートの初期セットアップ（Linksシート・Dashboardシート作成）が完了しました。");
}

/**
 * 各回の設定オブジェクト（sessionConfig）を受け取り、3つのGoogle Formを生成して
 * スプレッドシートへの紐付け・Links追記・Dashboard再構築までを一括実行する共通コアエンジン
 *
 * @param {Object} sessionConfig - 各回のフォーム定義・設問データを含む設定オブジェクト
 */
function createSessionFormsFromConfig(sessionConfig) {
  if (!sessionConfig || !sessionConfig.forms) {
    throw new Error("sessionConfig が指定されていないか、不正な形式です。generateSessionXForms() から実行してください。");
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // 1. Linksシートの準備（既存があれば維持して末尾追記、なければ新規作成）
  const linksSheet = ensureLinksSheet_(ss);

  // 2. 各フォーム（練習問題①・②・③）を順次生成してスプレッドシートに紐付け
  sessionConfig.forms.forEach(function(formDef) {
    Logger.log("Creating Form: " + formDef.formTitle);
    const form = FormApp.create(formDef.formTitle);
    form.setDescription(formDef.formDescription);
    form.setIsQuiz(true);
    form.setCollectEmail(false); // メールアドレス収集なし（「社員番号」「名前」で管理）
    form.setAllowResponseEdits(false);

    // --- 冒頭必須フィールド（配点0点）：社員番号 ➔ 名前 ---
    // ※setIsQuiz(true) かつ setCollectEmail(false) の場合、回答シートの列配置は必ず以下の通りになります：
    //   A列: タイムスタンプ | B列: スコア | C列: 社員番号を入力してください。 | D列: 名前を入力してください。 | E列以降: 各設問
    form.addTextItem()
      .setTitle("社員番号を入力してください。")
      .setHelpText("※集計キーとして使用します。半角数字で正確に入力してください。")
      .setRequired(true);

    form.addTextItem()
      .setTitle("名前を入力してください。")
      .setHelpText("例：山田 太郎")
      .setRequired(true);

    // --- 各設問（および専門編の章セクション見出し）の追加 ---
    formDef.questions.forEach(function(q) {
      if (q.sectionHeader) {
        form.addSectionHeaderItem()
          .setTitle(q.sectionHeader.title)
          .setHelpText(q.sectionHeader.helpText || "");
      }

      var item;
      if (q.type === "CHECKBOX") {
        item = form.addCheckboxItem();
      } else {
        item = form.addMultipleChoiceItem();
      }

      item.setTitle(q.questionText);
      if (q.helpText) {
        item.setHelpText(q.helpText);
      }
      item.setPoints(q.points);
      item.setRequired(true);

      var choices = q.options.map(function(opt) {
        return item.createChoice(opt.text, opt.isCorrect);
      });
      item.setChoices(choices);

      // 高情報フィードバック解説（正解時・不正解時ともに同じ詳細解説を表示）
      if (q.explanation) {
        var feedback = FormApp.createFeedback()
          .setText(q.explanation)
          .build();
        item.setFeedbackForCorrect(feedback);
        item.setFeedbackForIncorrect(feedback);
      }
    });

    // --- 回答先をこのスプレッドシートに設定し、生成されたシートを S{N}_{M}_Answer にリネーム ---
    var beforeIds = ss.getSheets().map(function(s) { return s.getSheetId(); });
    form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
    SpreadsheetApp.flush();
    Utilities.sleep(3000);

    var afterSheets = ss.getSheets();
    var newSheet = null;
    for (var i = 0; i < afterSheets.length; i++) {
      if (beforeIds.indexOf(afterSheets[i].getSheetId()) === -1) {
        newSheet = afterSheets[i];
        break;
      }
    }

    var targetSheetName = formDef.sheetName;
    if (newSheet) {
      // もし同名の古いシートが既に存在する場合はバックアップ名へ退避してからリネーム
      var existing = ss.getSheetByName(targetSheetName);
      if (existing && existing.getSheetId() !== newSheet.getSheetId()) {
        var timestampSuffix = Utilities.formatDate(new Date(), "Asia/Tokyo", "yyyyMMdd_HHmmss");
        existing.setName(targetSheetName + "_bk_" + timestampSuffix);
      }
      newSheet.setName(targetSheetName);
    }

    // LinksシートへURLを追記
    linksSheet.appendRow([
      formDef.formTitle,
      targetSheetName,
      form.getEditUrl(),
      form.getPublishedUrl()
    ]);
  });

  // 3. 不要な初期空白シート（Sheet1 / シート1）があれば整理
  cleanupDefaultBlankSheet_(ss);

  // 4. 全回横断 Dashboard シートを再構築（社員番号KEY）
  rebuildDashboard(ss);

  Logger.log("第" + sessionConfig.sessionNumber + "回の全フォームおよびDashboardの生成が完了しました！");
}

/**
 * Linksシートを取得または初期作成するヘルパー関数
 */
function ensureLinksSheet_(ss) {
  var linksSheet = ss.getSheetByName("Links");
  if (!linksSheet) {
    var firstSheet = ss.getSheets()[0];
    var isFirstSheetBlank = (firstSheet.getLastRow() === 0 && (firstSheet.getName() === "シート1" || firstSheet.getName() === "Sheet1"));
    if (isFirstSheetBlank) {
      linksSheet = firstSheet;
      linksSheet.setName("Links");
    } else {
      linksSheet = ss.insertSheet("Links", 0);
    }
    linksSheet.appendRow(["回・フォーム名", "シート名", "編集用URL (Edit URL)", "配布用URL (Published URL)"]);
    linksSheet.getRange("A1:D1").setFontWeight("bold").setBackground("#d9ead3");
    linksSheet.setFrozenRows(1);
  }
  return linksSheet;
}

/**
 * 初期状態の空の「シート1」「Sheet1」が残っていれば削除するヘルパー関数
 */
function cleanupDefaultBlankSheet_(ss) {
  var sheets = ss.getSheets();
  if (sheets.length <= 1) return;
  sheets.forEach(function(s) {
    var name = s.getName();
    if ((name === "シート1" || name === "Sheet1") && s.getLastRow() === 0) {
      ss.deleteSheet(s);
    }
  });
}

/**
 * スプレッドシート内の全 `S{回}_{番号}_Answer` シートを自動検出し、
 * 「社員番号（C列）」をKEYにした全回横断 Dashboard シートを動的に構築・更新する関数。
 * （※単体実行も可能。第5回・第6回のフォームを追加生成した際も自動で全回分を集計列に追加します）
 */
function rebuildDashboard(ss) {
  if (!ss) {
    ss = SpreadsheetApp.getActiveSpreadsheet();
  }

  // `S4_1_Answer`, `S4_2_Answer`, `S4_3_Answer`, `S5_1_Answer` ... にマッチするシートを抽出
  var answerSheetPattern = /^S(\d+)_(\d+)_Answer$/;
  var answerSheets = [];

  ss.getSheets().forEach(function(sheet) {
    var name = sheet.getName();
    var m = name.match(answerSheetPattern);
    if (m) {
      var sNum = parseInt(m[1], 10);
      var fNum = parseInt(m[2], 10);
      var maxPoints = (fNum === 3) ? 10 : 5;
      var shortLabel = "S" + sNum + "_" + fNum + " (" + maxPoints + "点)";
      answerSheets.push({
        sheetName: name,
        sessionNum: sNum,
        formNum: fNum,
        maxPoints: maxPoints,
        headerLabel: shortLabel
      });
    }
  });

  // 回番号・フォーム番号の昇順でソート
  answerSheets.sort(function(a, b) {
    if (a.sessionNum !== b.sessionNum) return a.sessionNum - b.sessionNum;
    return a.formNum - b.formNum;
  });

  var dashSheet = ss.getSheetByName("Dashboard");
  if (!dashSheet) {
    dashSheet = ss.insertSheet("Dashboard", 1);
  } else {
    dashSheet.clear();
  }

  // 基本ヘッダー（A列：社員番号、B列：名前）
  var headers = ["社員番号", "名前"];

  if (answerSheets.length === 0) {
    dashSheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    dashSheet.getRange(1, 1, 1, headers.length)
      .setFontWeight("bold")
      .setBackground("#cfe2f3");
    dashSheet.setFrozenRows(1);
    return;
  }

  // 回（Session）ごとにグルーピングして列構成を決定
  var sessionGroups = {};
  var sessionOrder = [];
  answerSheets.forEach(function(item) {
    if (!sessionGroups[item.sessionNum]) {
      sessionGroups[item.sessionNum] = [];
      sessionOrder.push(item.sessionNum);
    }
    sessionGroups[item.sessionNum].push(item);
  });

  // C列以降の列定義リストを作成（各フォームのスコア列 ＋ 回ごとの合計列）
  var columnDefs = [];
  sessionOrder.forEach(function(sNum) {
    var group = sessionGroups[sNum];
    var formColLetters = [];
    var totalMaxPoints = 0;

    group.forEach(function(item) {
      var colIndex1Based = 3 + columnDefs.length; // A=1, B=2, C=3...
      var colLetter = columnIndexToLetter_(colIndex1Based);
      formColLetters.push(colLetter);
      totalMaxPoints += item.maxPoints;

      headers.push(item.headerLabel);
      columnDefs.push({
        type: "SCORE",
        colIndex: colIndex1Based,
        colLetter: colLetter,
        sheetName: item.sheetName
      });
    });

    // 回別合計列を追加
    var sumColIndex = 3 + columnDefs.length;
    var sumColLetter = columnIndexToLetter_(sumColIndex);
    headers.push("第" + sNum + "回 合計 (" + totalMaxPoints + "点)");
    columnDefs.push({
      type: "SESSION_TOTAL",
      colIndex: sumColIndex,
      colLetter: sumColLetter,
      sourceCols: formColLetters
    });
  });

  // ヘッダー行の書き込みと装飾
  dashSheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  dashSheet.getRange(1, 1, 1, headers.length)
    .setFontWeight("bold")
    .setBackground("#cfe2f3");
  dashSheet.setFrozenRows(1);

  // --- A2セル数式：全 *_Answer シートの C2:C（社員番号）から空欄を除いて UNIQUE 抽出＆昇順ソート ---
  var empIdRanges = answerSheets.map(function(item) {
    return "'" + item.sheetName + "'!C2:C";
  }).join("; ");
  var empIdStack = "{ " + empIdRanges + " }";
  var colAFormula = '=IFERROR(SORT(UNIQUE(FILTER(' + empIdStack + ', ' + empIdStack + ' <> "")), 1, TRUE), "")';
  dashSheet.getRange("A2").setFormula(colAFormula);

  // --- B2セル数式：A列の社員番号をキーに、全回答シートの最新回答から「名前（D列）」を取得 ---
  var nameLookupTriplets = answerSheets.map(function(item) {
    var s = "'" + item.sheetName + "'";
    return s + "!C2:C, " + s + "!D2:D, " + s + "!A2:A";
  }).join("; ");
  var colBFormula = '=ARRAYFORMULA(IF($A2:$A="", "", IFERROR(VLOOKUP($A2:$A, SORT({ ' + nameLookupTriplets + ' }, 3, FALSE), 2, FALSE), "")))';
  dashSheet.getRange("B2").setFormula(colBFormula);

  // --- C列以降の数式：各フォームの最新スコア（B列）取得 ＆ 回別合計（MAP + LAMBDA） ---
  columnDefs.forEach(function(colDef) {
    var targetCell = colDef.colLetter + "2";
    if (colDef.type === "SCORE") {
      var s = "'" + colDef.sheetName + "'";
      // C:C(社員番号), B:B(スコア), A:A(タイムスタンプ) をタイムスタンプ降順ソートして最新スコアをVLOOKUP
      var scoreFormula = '=ARRAYFORMULA(IF($A2:$A="", "", IFERROR(VLOOKUP($A2:$A, SORT({ ' + s + '!C:C, ' + s + '!B:B, ' + s + '!A:A }, 3, FALSE), 2, FALSE), "未回答")))';
      dashSheet.getRange(targetCell).setFormula(scoreFormula);
    } else if (colDef.type === "SESSION_TOTAL") {
      var ranges = colDef.sourceCols.map(function(c) { return c + "2:" + c; });
      var vars = colDef.sourceCols.map(function(_, idx) { return String.fromCharCode(97 + idx); }); // a, b, c...
      var sumExpr = vars.map(function(v) { return "N(" + v + ")"; }).join("+");
      var totalFormula = '=MAP(' + ranges.join(", ") + ', LAMBDA(' + vars.join(", ") + ', IF(COUNTA(' + vars.join(", ") + ')=0, "", ' + sumExpr + ')))';
      dashSheet.getRange(targetCell).setFormula(totalFormula);
      dashSheet.getRange(1, colDef.colIndex).setBackground("#fff2cc");
    }
  });

  dashSheet.autoResizeColumns(1, headers.length);
}

/**
 * 1始まりの列番号をA, B, C... AA, AB... の列文字に変換するヘルパー関数
 */
function columnIndexToLetter_(columnIndex) {
  var temp;
  var letter = "";
  while (columnIndex > 0) {
    temp = (columnIndex - 1) % 26;
    letter = String.fromCharCode(temp + 65) + letter;
    columnIndex = (columnIndex - temp - 1) / 26;
  }
  return letter;
}
