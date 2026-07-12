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

  // --- IF_Legacy_Export シートの数式もリセット ---
  const ifSheet = ss.getSheetByName("IF_Legacy_Export");
  if (ifSheet) {
    ifSheet.getRange("C1").setFormula("=ARRAY_CONSTRAIN(Progress_Master!K1:ZZ1, 1, 12)");
    ifSheet.getRange("A2").setFormula('=ARRAYFORMULA(IF(Member_DB!A2:A="", "", Member_DB!A2:B))');
    
    const mappingLogic = [
        `=ARRAY_CONSTRAIN(ARRAYFORMULA(IF($A2:$A="", "", `,
        `  IFS(`,
        `    Progress_Master!K2:ZZ="", "",`,
        `    REGEXMATCH(Progress_Master!K2:ZZ, "出席\\(.*\\)・届出有"), "○",`,
        `    REGEXMATCH(Progress_Master!K2:ZZ, "出席\\(.*\\)・遅刻・届出有"), "△",`,
        `    REGEXMATCH(Progress_Master!K2:ZZ, "出席\\(.*\\)・遅刻"), "▲",`,
        `    Progress_Master!K2:ZZ="欠席・届出有", "-",`,
        `    Progress_Master!K2:ZZ="無断欠席", "×",`,
        `    Progress_Master!K2:ZZ="無断欠席(遅刻届のみ)", "×",`,
        `    Progress_Master!K2:ZZ="欠席(遅刻30分超)", "×",`,
        `    Progress_Master!K2:ZZ="対象外", "",`,
        `    REGEXMATCH(Progress_Master!K2:ZZ, "出席"), "○",`,
        `    TRUE, ""`,
        `  )`,
        `)), 1000, 12)`
    ].join("");
    ifSheet.getRange("C2").setFormula(mappingLogic);
    
    ifSheet.getRange("O2").setFormula('=ARRAYFORMULA(IF($A2:$A="", "", Progress_Master!D2:D))');
    ifSheet.getRange("P2").setFormula('=ARRAYFORMULA(IF($A2:$A="", "", Progress_Master!G2:G))');
    ifSheet.getRange("Q2").setFormula('=ARRAYFORMULA(IF($A2:$A="", "", Progress_Master!H2:H))');
    ifSheet.getRange("R2").setFormula('=ARRAYFORMULA(IF($A2:$A="", "", Progress_Master!E2:E))');
    ifSheet.getRange("S2").setFormula('=ARRAYFORMULA(IF($A2:$A="", "", Progress_Master!I2:I))');
    ifSheet.getRange("T2").setFormula('=ARRAYFORMULA(IF($A2:$A="", "", Progress_Master!J2:J))');
  }

  // --- 簡易版 Idea-17: 各シートのデータ型を正しい状態に強制修復 ---
  const ss2 = SpreadsheetApp.getActiveSpreadsheet();
  const memberDb = ss2.getSheetByName("Member_DB");
  const logAtt = ss2.getSheetByName("Log_Attendance");
  const logNot = ss2.getSheetByName("Log_Notice");
  const logExt = ss2.getSheetByName("Log_ExternalSurvey");
  const prog = ss2.getSheetByName("Progress_Master");
  const sched = ss2.getSheetByName("Schedule_DB");
  const ifLegacy = ss2.getSheetByName("IF_Legacy_Export");

  if (memberDb) memberDb.getRange("A:A").setNumberFormat("@");
  if (logAtt) logAtt.getRange("B:B").setNumberFormat("@");
  if (logNot) logNot.getRange("C:C").setNumberFormat("@");
  if (logExt) logExt.getRange("A:A").setNumberFormat("@");
  if (prog) prog.getRange("A:A").setNumberFormat("@");
  if (ifLegacy) ifLegacy.getRange("A:B").setNumberFormat("@");
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
