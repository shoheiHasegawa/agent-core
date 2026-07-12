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
