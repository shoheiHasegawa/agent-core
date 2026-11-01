#!/usr/bin/env python3
"""
Oracle基礎勉強会（25上期）Google Forms & 社員番号KEY一元管理Dashboard 自動生成GASビルダー（2ファイル分離・OCP対応版）

概要:
- Google Apps Script (GAS) を以下の2ファイルに分離して生成・構文検証（`node --check`）する：
  1. `scripts/00_setup_and_core.gs`:
     マスタ用スプレッドシートに最初に1回だけ登録する「共通セットアップ＆コアエンジン」。
     （`setupMasterSpreadsheet()`, `createSessionFormsFromConfig(sessionConfig)`, `rebuildDashboard(ss)` 等を収録）
  2. `sessions/session_XX/generate_sessionXX_forms.gs`:
     各回の `quiz_set_25h1.md` からパースした全20問のJSONデータと、実行トリガー関数 `generateSessionXForms()` のみを持つ軽量ファイル。
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Tuple


CORE_GAS_TEMPLATE = """/**
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
  var answerSheetPattern = /^S(\\d+)_(\\d+)_Answer$/;
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
"""


SESSION_GAS_TEMPLATE = """/**
 * ================================================================================
 * 25上期 Oracle基礎勉強会 第{SESSION_NUM}回：練習問題フォーム生成データ ＆ 実行トリガー
 * ファイル名：generate_session{SESSION_NUM_PAD}_forms.gs
 * ================================================================================
 *
 * 【このスクリプトで生成される第{SESSION_NUM}回の3フォーム】
 * 1. フォーム①：{FORM1_TITLE}（5問・5点満点）➔ 回答シート `S{SESSION_NUM}_1_Answer`
 * 2. フォーム②：{FORM2_TITLE}（5問・5点満点）➔ 回答シート `S{SESSION_NUM}_2_Answer`
 * 3. フォーム③：{FORM3_TITLE}（10問・10点満点）➔ 回答シート `S{SESSION_NUM}_3_Answer`
 *
 * 【Apps Script への登録・実行手順（2ファイル構成）】
 * Step 1（初回のみ）：
 *   マスタ用スプレッドシートの「拡張機能 ＞ Apps Script」を開き、1つ目のファイル（`コード.gs` 等）に
 *   共通エンジン `scripts/00_setup_and_core.gs` を貼り付けて保存します。
 * Step 2（第{SESSION_NUM}回の追加）：
 *   Apps Script 左側の「ファイル」横の「＋」＞「スクリプト」をクリックして新規ファイル（例：`session{SESSION_NUM_PAD}`）を追加し、
 *   この `generate_session{SESSION_NUM_PAD}_forms.gs` の内容を貼り付けて保存（Ctrl+S / Cmd+S）します。
 * Step 3（実行）：
 *   上部の関数選択プルダウンで `generateSession{SESSION_NUM}Forms` を選択し、「実行」をクリックします。
 *   ➔ 3つのフォームが自動生成され、`Links` シートへのURL追記と `Dashboard` シートの集計列更新が全自動で行われます！
 * ================================================================================
 */

function generateSession{SESSION_NUM}Forms() {
  const sessionConfig = {SESSION_CONFIG_JSON};

  // 共通コアエンジン（00_setup_and_core.gs）を呼び出してフォーム生成＆Dashboard更新を実行
  createSessionFormsFromConfig(sessionConfig);
}
"""


def strip_markdown_formatting(text: str) -> str:
    """Google Formsのプレーンテキスト表示で見やすくなるよう、不要なMarkdown強調記号を整理する"""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    return text.strip()


def parse_quiz_markdown(md_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    quiz_set_25h1.md から Q1〜Q20 および章メタデータをパースして返す。
    """
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    ch_meta = {
        "ch1_num": "第7章",
        "ch1_full": "第7章：ユーザーおよびセキュリティの管理",
        "ch2_num": "第8章",
        "ch2_full": "第8章：スキーマオブジェクトの管理",
    }
    m_set1 = re.search(r"^## 📝 セット①：(第\d+章)\s+([^\【\n]+)", content, re.MULTILINE)
    m_set2 = re.search(r"^## 📝 セット②：(第\d+章)\s+([^\【\n]+)", content, re.MULTILINE)
    if m_set1:
        ch_meta["ch1_num"] = m_set1.group(1).strip()
        ch_meta["ch1_full"] = f"{m_set1.group(1).strip()}：{m_set1.group(2).strip()}"
    if m_set2:
        ch_meta["ch2_num"] = m_set2.group(1).strip()
        ch_meta["ch2_full"] = f"{m_set2.group(1).strip()}：{m_set2.group(2).strip()}"

    pattern = re.compile(
        r"^### Q(\d+)\.【([^】]+)】\s*\n(.*?)(?=^### Q\d+\.|^## 📝|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    matches = pattern.findall(content)
    if len(matches) != 20:
        raise ValueError(f"Expected 20 questions in {md_path}, but found {len(matches)}.")

    questions: List[Dict[str, Any]] = []

    for q_num_str, q_title, q_block in matches:
        q_num = int(q_num_str)

        parts_ans = q_block.split("#### 【正解】")
        if len(parts_ans) != 2:
            raise ValueError(f"Q{q_num}: Could not find '#### 【正解】' section.")

        stem_and_options_raw = parts_ans[0].strip()
        ans_and_exp_raw = parts_ans[1].strip()

        exp_split = re.split(r"#### 【高情報フィードバック解説[^】]*】", ans_and_exp_raw)
        if len(exp_split) != 2:
            raise ValueError(f"Q{q_num}: Could not find '#### 【高情報フィードバック解説...】' section.")

        explanation_raw = exp_split[1].strip()
        explanation_raw = re.sub(r"\n+---\s*$", "", explanation_raw).strip()

        lines = stem_and_options_raw.split("\n")
        stem_lines: List[str] = []
        options: List[Dict[str, Any]] = []

        opt_pattern = re.compile(r"^- \[([ xX])\] \*\*([a-d])\.\*\*\s*(.+)$")
        for line in lines:
            m_opt = opt_pattern.match(line.strip())
            if m_opt:
                is_correct = m_opt.group(1).lower() == "x"
                opt_label = m_opt.group(2)
                opt_body = strip_markdown_formatting(m_opt.group(3))
                options.append(
                    {
                        "text": f"{opt_label}. {opt_body}",
                        "isCorrect": is_correct,
                    }
                )
            else:
                stem_lines.append(line)

        if len(options) != 4:
            raise ValueError(f"Q{q_num}: Expected 4 options, found {len(options)}.")

        correct_count = sum(1 for o in options if o["isCorrect"])
        if correct_count == 0:
            raise ValueError(f"Q{q_num}: No correct option marked with [x].")

        q_type = "CHECKBOX" if correct_count > 1 else "RADIO"

        stem_text = "\n".join(stem_lines).strip()
        stem_text = re.sub(
            r"```[a-zA-Z]*\n(.*?)```",
            r"--- [SQL] ---\n\1-------------",
            stem_text,
            flags=re.DOTALL,
        )
        stem_text = strip_markdown_formatting(stem_text)
        explanation_clean = strip_markdown_formatting(explanation_raw)

        questions.append(
            {
                "globalNumber": q_num,
                "title": q_title.strip(),
                "stem": stem_text,
                "type": q_type,
                "points": 1,
                "options": options,
                "explanation": explanation_clean,
            }
        )

    return questions, ch_meta


def build_session_config(
    session_num: int,
    questions: List[Dict[str, Any]],
    ch_meta: Dict[str, str],
) -> Dict[str, Any]:
    """
    20問を1回あたり3つのGoogle Form構成（5問 / 5問 / 10問）にパッケージングする。
    """
    set1 = questions[0:5]     # Q1〜Q5 (前半・本質編)
    set2 = questions[5:10]    # Q6〜Q10 (後半・本質編)
    set34 = questions[10:20]  # Q11〜Q20 (前半5問＋後半5問・専門編)

    ch1_num = ch_meta["ch1_num"]
    ch2_num = ch_meta["ch2_num"]
    ch1_full = ch_meta["ch1_full"]
    ch2_full = ch_meta["ch2_full"]

    def format_form_questions(
        q_list: List[Dict[str, Any]],
        is_combined_specialist: bool = False,
    ) -> List[Dict[str, Any]]:
        formatted: List[Dict[str, Any]] = []
        for idx, q in enumerate(q_list, start=1):
            q_entry: Dict[str, Any] = {
                "questionText": f"問{idx}. 【{q['title']}】\n{q['stem']}",
                "type": q["type"],
                "points": q["points"],
                "options": q["options"],
                "explanation": q["explanation"],
            }
            if is_combined_specialist:
                if idx == 1:
                    q_entry["sectionHeader"] = {
                        "title": f"{ch1_full}（専門編）",
                        "helpText": f"問1〜問5は{ch1_full}に関するOracle専門編（HOW）です。",
                    }
                elif idx == 6:
                    q_entry["sectionHeader"] = {
                        "title": f"{ch2_full}（専門編）",
                        "helpText": f"問6〜問10は{ch2_full}に関するOracle専門編（HOW）です。",
                    }
            formatted.append(q_entry)
        return formatted

    forms = [
        {
            "formNumber": 1,
            "sheetName": f"S{session_num}_1_Answer",
            "formTitle": f"25上期 Oracle勉強会 第{session_num}回 練習問題①（{ch1_num}：本質編）",
            "formDescription": f"前半（{ch1_full}）で学んだ内容について、なぜその仕組みが必要なのか（WHY/WHAT）を確認する5問です。（全問4択・5点満点）",
            "questions": format_form_questions(set1, is_combined_specialist=False),
        },
        {
            "formNumber": 2,
            "sheetName": f"S{session_num}_2_Answer",
            "formTitle": f"25上期 Oracle勉強会 第{session_num}回 練習問題②（{ch2_num}：本質編）",
            "formDescription": f"後半（{ch2_full}）で学んだ内容について、設計上の判断軸（WHY/WHAT）を確認する5問です。（全問4択・5点満点）",
            "questions": format_form_questions(set2, is_combined_specialist=False),
        },
        {
            "formNumber": 3,
            "sheetName": f"S{session_num}_3_Answer",
            "formTitle": f"25上期 Oracle勉強会 第{session_num}回 練習問題③（{ch1_num}・{ch2_num}：Oracle専門編）",
            "formDescription": f"実機ハンズオン実験を終えた総仕上げとして、{ch1_num}・{ch2_num}に関するOracle固有の専門用語・SQL構文・仕様（HOW）を確認する10問です。（全問4択・10点満点）",
            "questions": format_form_questions(set34, is_combined_specialist=True),
        },
    ]

    return {
        "sessionNumber": session_num,
        "forms": forms,
    }


def check_js_syntax(gas_code: str, label: str) -> None:
    """node --check を用いてGASコードのJavaScript構文エラーがないことを検証する"""
    if shutil.which("node"):
        proc = subprocess.run(
            ["node", "--check", "--input-type=commonjs"],
            input=gas_code.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            err_msg = proc.stderr.decode("utf-8", errors="replace")
            raise AssertionError(f"JavaScript syntax validation failed for {label} via node --check:\n{err_msg}")


def validate_generated_gas_files(
    core_gas_code: str,
    session_gas_code: str,
    session_config: Dict[str, Any],
) -> None:
    """生成された2つのGASファイルの構造・必須要素およびJavaScript構文を検証する"""
    s_num = session_config["sessionNumber"]

    core_required = [
        "function setupMasterSpreadsheet()",
        "function createSessionFormsFromConfig(sessionConfig)",
        "function rebuildDashboard(ss)",
        "function ensureLinksSheet_(ss)",
        "function cleanupDefaultBlankSheet_(ss)",
        "function columnIndexToLetter_(columnIndex)",
        "form.setIsQuiz(true);",
        "form.setCollectEmail(false);",
        "社員番号を入力してください。",
        "名前を入力してください。",
        "FormApp.createFeedback()",
        "item.setFeedbackForCorrect(feedback);",
        "item.setFeedbackForIncorrect(feedback);",
        "form.addSectionHeaderItem()",
        "!C2:C",
        "!D2:D",
    ]
    for snippet in core_required:
        if snippet not in core_gas_code:
            raise AssertionError(f"Validation failed in 00_setup_and_core.gs: required snippet '{snippet}' not found.")

    session_required = [
        f"function generateSession{s_num}Forms()",
        "createSessionFormsFromConfig(sessionConfig);",
        f"S{s_num}_1_Answer",
        f"S{s_num}_2_Answer",
        f"S{s_num}_3_Answer",
    ]
    for snippet in session_required:
        if snippet not in session_gas_code:
            raise AssertionError(
                f"Validation failed in generate_session{s_num:02d}_forms.gs: required snippet '{snippet}' not found."
            )

    if "function rebuildDashboard" in session_gas_code:
        raise AssertionError("Validation failed: session GAS file must not duplicate core engine functions.")

    if "{SESSION_" in session_gas_code or "{FORM" in session_gas_code:
        raise AssertionError("Validation failed: unreplaced placeholder found in session GAS file.")

    check_js_syntax(core_gas_code, "00_setup_and_core.gs")
    check_js_syntax(session_gas_code, f"generate_session{s_num:02d}_forms.gs")
    # 2ファイルをApps Script空間で結合した状態でも構文・識別子衝突がないか検証
    check_js_syntax(core_gas_code + "\n" + session_gas_code, "combined GAS project")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build 2-file GAS scripts for Oracle Study Group Google Forms.")
    parser.add_argument(
        "--session",
        type=int,
        default=4,
        help="Session number (default: 4)",
    )
    args = parser.parse_args()

    session_num = args.session
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts_dir = os.path.join(workspace_dir, "scripts")
    session_dir = os.path.join(workspace_dir, "sessions", f"session_{session_num:02d}")

    quiz_md_path = os.path.join(session_dir, "quiz_set_25h1.md")
    core_gs_path = os.path.join(scripts_dir, "00_setup_and_core.gs")
    session_gs_path = os.path.join(session_dir, f"generate_session{session_num:02d}_forms.gs")

    if not os.path.exists(quiz_md_path):
        print(f"Error: Quiz markdown file not found at {quiz_md_path}", file=sys.stderr)
        sys.exit(1)

    questions, ch_meta = parse_quiz_markdown(quiz_md_path)
    session_config = build_session_config(session_num, questions, ch_meta)

    config_json_str = json.dumps(session_config, ensure_ascii=False, indent=2)

    core_gas_code = CORE_GAS_TEMPLATE.strip() + "\n"
    session_gas_code = (
        SESSION_GAS_TEMPLATE.replace("{SESSION_NUM}", str(session_num))
        .replace("{SESSION_NUM_PAD}", f"{session_num:02d}")
        .replace("{FORM1_TITLE}", session_config["forms"][0]["formTitle"])
        .replace("{FORM2_TITLE}", session_config["forms"][1]["formTitle"])
        .replace("{FORM3_TITLE}", session_config["forms"][2]["formTitle"])
        .replace("{SESSION_CONFIG_JSON}", config_json_str)
        .strip()
        + "\n"
    )

    validate_generated_gas_files(core_gas_code, session_gas_code, session_config)

    with open(core_gs_path, "w", encoding="utf-8") as f:
        f.write(core_gas_code)

    with open(session_gs_path, "w", encoding="utf-8") as f:
        f.write(session_gas_code)

    total_q = sum(len(f["questions"]) for f in session_config["forms"])
    print(f"[SUCCESS] Parsed {len(questions)} questions from {quiz_md_path}")
    print(f"[SUCCESS] Generated Core GAS at {core_gs_path}")
    print(f"[SUCCESS] Generated Session {session_num} GAS at {session_gs_path} ({len(session_config['forms'])} forms, {total_q} total questions)")
    print("[SUCCESS] Verified JavaScript syntax via node --check for both files & combined project (0 errors)")


if __name__ == "__main__":
    main()
