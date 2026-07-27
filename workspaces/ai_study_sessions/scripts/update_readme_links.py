import os
import glob
import re

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    course_dir = os.path.join(base_dir, 'course_content')
    
    urls = {
        1: "https://docs.google.com/forms/d/e/1FAIpQLSftUOa3MYhCIiBfLtLOpUzyTip2S7Y9z1VcFkTye_IfFSVTRg/viewform",
        2: "https://docs.google.com/forms/d/e/1FAIpQLSeNBUWzvIeQx9P-FkbFBG3v-S9m9GIZSOfGapG6H7W7SSZLyQ/viewform",
        3: "https://docs.google.com/forms/d/e/1FAIpQLScc44T-47c1bx9oikaM-6oggKqANhMZ3TZkTC-lRjk1o12iVg/viewform",
        4: "https://docs.google.com/forms/d/e/1FAIpQLSflekzxJ6XjWu6sjU17imLfwRPjKnD4jf1YAvJ6TeXYXAbKNA/viewform",
        5: "https://docs.google.com/forms/d/e/1FAIpQLSfxG0crCRXOtowlFm2gGzPK_jmahu0yLHqAwqFXJNdfdOYQ2w/viewform",
        6: "https://docs.google.com/forms/d/e/1FAIpQLScKEjT15TROobMfF_4J03XXVxke4qb5N_Yj1kdskCD4S9Wdow/viewform"
    }
    
    survey_url = "https://docs.google.com/forms/d/e/1FAIpQLSedZldwIsjzpQna9YgQBst-aOBIrXOUIIE4CUOLvO2GhSje9Q/viewform"
    
    for i in range(1, 7):
        readme_path = os.path.join(course_dir, f'session_{i}', 'README.md')
        if not os.path.exists(readme_path):
            continue
            
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 以前に置換済みのパターンにマッチさせる
        pattern = re.compile(rf'👉 \*\*\[【Session {i} テスト】Google Formを開く\]\(.*?\)\*\*')
        replacement = f'👉 **[【Session {i} テスト】Google Formを開く]({urls[i]})**'
        content, count = pattern.subn(replacement, content)
        
        # もしまだ古い形式（ダミーリンク）が残っていた場合のフォールバック
        if count == 0:
            fallback_pattern = re.compile(rf'👉 \*\*\[Session {i} 振り返りフォームへ進む \(ダミーリンク\)\]\(#\)\*\*')
            content, count = fallback_pattern.subn(replacement, content)
            
        # アンケートフォームへのリンク (Session 6のみ)
        if i == 6:
            survey_pattern = re.compile(rf'👉 \*\*\[【全日程修了】講座評価アンケートを開く\]\(.*?\)\*\*')
            survey_replacement = f'👉 **[【全日程修了】講座評価アンケートを開く]({survey_url})**'
            content, s_count = survey_pattern.subn(survey_replacement, content)
            
            if s_count == 0:
                fallback_survey = re.compile(rf'👉 \*\*\[講座評価アンケートへ進む \(ダミーリンク\)\]\(#\)\*\*')
                content, s_count = fallback_survey.subn(survey_replacement, content)
        
        if count > 0:
            print(f"Updated {readme_path}")
        else:
            print(f"No match found in {readme_path}")
            
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    main()

