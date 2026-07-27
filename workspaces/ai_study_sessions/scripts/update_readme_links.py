import os
import glob
import re

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    course_dir = os.path.join(base_dir, 'course_content')
    
    urls = {
        1: "https://docs.google.com/forms/d/e/1FAIpQLScdnA4_dSpc7KIhBTLcW8zXREACGKl06YIr59ZNsfGu1XfRKA/viewform",
        2: "https://docs.google.com/forms/d/e/1FAIpQLSds-un3KnQuWtFGkMmln7HkEPkv5u0YSsdLQdJIos9Ui5PeYg/viewform",
        3: "https://docs.google.com/forms/d/e/1FAIpQLSeGH8342CUXsasJyflAXUJgPsYauhG3UYmD_yG9ZVijnd0RLA/viewform",
        4: "https://docs.google.com/forms/d/e/1FAIpQLSfik0HPxxB6Z109aE5mjTtsNUtUyG_RIsQErRk8nuuBTE9dEA/viewform",
        5: "https://docs.google.com/forms/d/e/1FAIpQLSc81l3qzhcqDqseDeUSKLJ_ejcgPW9v0VIr0vm2n_AEn24ISQ/viewform",
        6: "https://docs.google.com/forms/d/e/1FAIpQLSdFL0ySw7uiuCCt5tv-v9lHGnZ2phQiv2N1BPZ3gkJHSivvkA/viewform"
    }
    
    survey_url = "https://docs.google.com/forms/d/e/1FAIpQLScqEuqznmeK_LT-FKJZmEpMoti2cUcfXMOd_TDCbH9QReqOGw/viewform"
    
    for i in range(1, 7):
        readme_path = os.path.join(course_dir, f'session_{i}', 'README.md')
        if not os.path.exists(readme_path):
            continue
            
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # テスト用URLの置換
        # すでに置き換え済みの場合は、別のパターンでマッチするか確認
        if "{FORM_URL_PLACEHOLDER}" in content:
            content = content.replace("{FORM_URL_PLACEHOLDER}", urls[i])
            print(f"Updated (placeholder) {readme_path}")
        else:
            # 元のパターンの場合
            pattern = re.compile(rf'👉 \*\*\[Session {i} 振り返りフォームへ進む \(ダミーリンク\)\]\(#\)\*\*')
            replacement = f'👉 **[【Session {i} テスト】Google Formを開く]({urls[i]})**'
            content, count = pattern.subn(replacement, content)
            
            # アンケートフォームへのリンク (Session 6のみ)
            if i == 6:
                survey_pattern = re.compile(rf'👉 \*\*\[講座評価アンケートへ進む \(ダミーリンク\)\]\(#\)\*\*')
                survey_replacement = f'👉 **[【AI活用勉強会】講座評価アンケートを開く]({survey_url})**'
                content, s_count = survey_pattern.subn(survey_replacement, content)
            
            if count > 0:
                print(f"Updated {readme_path}")
            else:
                print(f"No match found in {readme_path}")
                
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    main()

