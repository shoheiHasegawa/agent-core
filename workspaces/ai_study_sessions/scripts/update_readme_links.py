import os
import glob
import re

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    course_dir = os.path.join(base_dir, 'course_content')
    
    for i in range(1, 7):
        readme_path = os.path.join(course_dir, f'session_{i}', 'README.md')
        if not os.path.exists(readme_path):
            continue
            
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 置換
        pattern = re.compile(rf'👉 \*\*\[Session {i} 振り返りフォームへ進む \(ダミーリンク\)\]\(#\)\*\*')
        replacement = f'👉 **[【Session {i} テスト】Google Formを開く]({{FORM_URL_PLACEHOLDER}})**'
        
        new_content, count = pattern.subn(replacement, content)
        
        if count > 0:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {readme_path}")
        else:
            print(f"No match found in {readme_path}")

if __name__ == "__main__":
    main()
