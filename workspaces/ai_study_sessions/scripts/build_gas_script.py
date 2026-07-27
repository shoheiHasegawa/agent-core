import os
import json
import glob

GAS_TEMPLATE = """
/**
 * AI Study Sessions - Google Form Generator
 * 
 * 使い方:
 * 1. 新規のGoogle Spreadsheetを作成する
 * 2. 「拡張機能」 > 「Apps Script」を開く
 * 3. このスクリプトを貼り付けて、generateForms() を実行する
 * 4. 初回実行時は権限承認が求められるので許可する
 * 5. スプレッドシートにフォームのリンクが出力される
 */

function generateForms() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  sheet.setName("Links");
  sheet.appendRow(["Title", "Edit URL", "Published URL"]);
  
  // Pythonスクリプトによって埋め込まれたJSONデータ
  const sessionsData = {JSON_DATA_PLACEHOLDER};
  
  const sheetNames = [];
  
  // テスト用フォームの生成
  sessionsData.forEach((session, index) => {
    Logger.log("Creating form for: " + session.sessionTitle);
    const form = FormApp.create("【AI活用勉強会 テスト】" + session.sessionTitle);
    form.setIsQuiz(true); 
    form.setAllowResponseEdits(false);
    form.setCollectEmail(true); // ダッシュボード集計用にメールアドレスを収集
    
    session.questions.forEach(q => {
      let item;
      if (q.type === "RADIO") {
        item = form.addMultipleChoiceItem();
      } else {
        item = form.addCheckboxItem();
      }
      
      item.setTitle(q.questionText);
      item.setPoints(q.points);
      item.setRequired(true);
      
      const choices = q.options.map(opt => {
        return item.createChoice(opt.text, opt.isCorrect);
      });
      item.setChoices(choices);
    });
    
    // スプレッドシートのシート数（ID）を記録してからDestinationを設定
    const beforeIds = ss.getSheets().map(s => s.getSheetId());
    form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
    SpreadsheetApp.flush();
    Utilities.sleep(3000); // シート作成完了を待つ
    
    // 新しく追加されたシートを見つけてリネーム
    const afterSheets = ss.getSheets();
    const newSheet = afterSheets.find(s => !beforeIds.includes(s.getSheetId()));
    const targetSheetName = "Session" + (index + 1) + "_Answer";
    if (newSheet) {
      newSheet.setName(targetSheetName);
      sheetNames.push(targetSheetName);
    } else {
      // フェイルセーフ（見つからない場合は手動で名前を合わせる想定）
      sheetNames.push("Session" + (index + 1) + "_Answer");
    }
    
    // Add URLs to sheet
    sheet.appendRow([session.sessionTitle + " テスト", form.getEditUrl(), form.getPublishedUrl()]);
  });
  
  // --- Dashboardの生成 ---
  Logger.log("Creating Dashboard...");
  let dashSheet = ss.getSheetByName("Dashboard");
  if (!dashSheet) {
    dashSheet = ss.insertSheet("Dashboard", 1); // 2番目のタブに
  } else {
    dashSheet.clear();
  }
  
  // Dashboard Header
  dashSheet.getRange("A1").setValue("メールアドレス");
  sheetNames.forEach((name, i) => {
    dashSheet.getRange(1, 2 + i).setValue("Session " + (i + 1) + " スコア (最新)");
  });
  
  // Dashboard Formula: Email list (UNIQUE across all answer sheets)
  if (sheetNames.length > 0) {
    const emailRanges = sheetNames.map(name => `'${name}'!B2:B`).join("; ");
    dashSheet.getRange("A2").setFormula(`=IFERROR(QUERY(UNIQUE({${emailRanges}}), "where Col1 <> ''"), "")`);
    
    // Dashboard Formula: Latest Score for each session
    sheetNames.forEach((name, i) => {
      const colLetter = String.fromCharCode(66 + i); // 66 = B, 67 = C...
      // B:B(Email), C:C(Score), A:A(Timestamp) の配列を作り、Timestampで降順ソートしてVLOOKUP
      const formula = `=ARRAYFORMULA(IF($A2:$A="","", IFERROR(VLOOKUP($A2:$A, SORT({ '${name}'!B:B, '${name}'!C:C, '${name}'!A:A }, 3, FALSE), 2, FALSE), "未回答")))`;
      dashSheet.getRange(`${colLetter}2`).setFormula(formula);
    });
  }
  
  // --- ここからアンケートフォームの生成 ---
  Logger.log("Creating survey form...");
  const surveyForm = FormApp.create("【AI活用勉強会 基礎編】講座評価アンケート");
  surveyForm.setDescription("全6回の勉強会お疲れ様でした。今後の改善のため、率直なご意見をお聞かせください。");
  surveyForm.setCollectEmail(true); // アンケートもメールアドレス収集
  
  // Q1
  surveyForm.addScaleItem()
    .setTitle("Q1. 本講座のコア概念（「1タスク1セッション」「SSOT」「ルールの外部化」など）を理解し、他人に説明できるレベルになりましたか？")
    .setBounds(1, 5)
    .setLabels("全くできない", "十分にできる")
    .setRequired(true);
    
  // Q2
  surveyForm.addParagraphTextItem()
    .setTitle("Q2. 講座を受講する前と後で、AIに対する認識（特にハルシネーションの捉え方やAIとの接し方）はどのように変わりましたか？")
    .setRequired(true);
    
  // Q3
  surveyForm.addScaleItem()
    .setTitle("Q3. 全6回のセッションの難易度や分量は適切でしたか？")
    .setBounds(1, 5)
    .setLabels("簡単すぎた", "難しすぎた")
    .setRequired(true);
    
  // Q4
  surveyForm.addScaleItem()
    .setTitle("Q4. 各セッションの構成（最初に「よくある絶望・失敗例」を提示する流れなど）は、学習意欲を高める上で効果的でしたか？")
    .setBounds(1, 5)
    .setLabels("全く効果的でなかった", "非常に効果的だった")
    .setRequired(true);
    
  // Q5
  surveyForm.addParagraphTextItem()
    .setTitle("Q5. 講座全体を通して「ここが分かりにくかった」「もっと深く知りたかった」という点があれば教えてください。")
    .setRequired(false);
    
  // Q6
  surveyForm.addParagraphTextItem()
    .setTitle("Q6. 明日からの業務やご自身のプロジェクトにおいて、学んだ「空間設計（コンテキスト・エンジニアリング）」を具体的にどのように実践しますか？（行動宣言）")
    .setRequired(true);
    
  // Q7
  surveyForm.addScaleItem()
    .setTitle("Q7. この勉強会を、あなたのチームメンバーや同僚にどの程度お勧めしたいですか？")
    .setBounds(0, 10)
    .setLabels("全く思わない", "非常にそう思う")
    .setRequired(true);
    
  // アンケートの回答先もスプレッドシートに指定
  const beforeSurveyIds = ss.getSheets().map(s => s.getSheetId());
  surveyForm.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  SpreadsheetApp.flush();
  Utilities.sleep(3000);
  
  const afterSurveySheets = ss.getSheets();
  const newSurveySheet = afterSurveySheets.find(s => !beforeSurveyIds.includes(s.getSheetId()));
  if (newSurveySheet) {
    newSurveySheet.setName("Survey_Answer");
  }
    
  sheet.appendRow(["講座評価アンケート", surveyForm.getEditUrl(), surveyForm.getPublishedUrl()]);

  Logger.log("All forms generated successfully.");
}
"""

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_dir = os.path.join(base_dir, 'docs', 'tests', 'json')
    
    json_files = glob.glob(os.path.join(json_dir, 'Session*_Test.json'))
    json_files.sort()
    
    all_sessions_data = []
    
    for j_file in json_files:
        with open(j_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_sessions_data.append(data)
            
    json_str = json.dumps(all_sessions_data, ensure_ascii=False, indent=2)
    
    gas_code = GAS_TEMPLATE.replace('{JSON_DATA_PLACEHOLDER}', json_str)
    
    gas_output_path = os.path.join(base_dir, 'scripts', 'generate_google_form.gs')
    
    with open(gas_output_path, 'w', encoding='utf-8') as f:
        f.write(gas_code.strip() + "\n")
        
    print(f"Generated GAS script at {gas_output_path}")

if __name__ == "__main__":
    main()
