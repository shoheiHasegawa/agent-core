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
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.appendRow(["Title", "Edit URL", "Published URL"]);
  
  // Pythonスクリプトによって埋め込まれたJSONデータ
  const sessionsData = {JSON_DATA_PLACEHOLDER};
  
  // テスト用フォームの生成
  sessionsData.forEach(session => {
    Logger.log("Creating form for: " + session.sessionTitle);
    const form = FormApp.create("【AI活用勉強会 テスト】" + session.sessionTitle);
    form.setIsQuiz(true); 
    form.setAllowResponseEdits(false);
    
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
    
    // Add URLs to sheet
    sheet.appendRow([session.sessionTitle + " テスト", form.getEditUrl(), form.getPublishedUrl()]);
  });
  
  // --- ここからアンケートフォームの生成 ---
  Logger.log("Creating survey form...");
  const surveyForm = FormApp.create("【AI活用勉強会 基礎編】講座評価アンケート");
  surveyForm.setDescription("全6回の勉強会お疲れ様でした。今後の改善のため、率直なご意見をお聞かせください。");
  
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
