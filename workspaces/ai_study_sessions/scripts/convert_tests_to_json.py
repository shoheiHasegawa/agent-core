import os
import re
import json
import glob

def parse_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract session title
    title_match = re.search(r'# AI活用勉強会 テスト問題: (Session \d+)', content)
    session_title = title_match.group(1) if title_match else os.path.basename(filepath).replace('_Test.md', '')

    questions = []
    
    # Split content by question headers
    q_blocks = re.split(r'\*\*(Q\d+\..*?)\*\*', content)
    
    for i in range(1, len(q_blocks), 2):
        q_header = q_blocks[i].strip()
        q_body = q_blocks[i+1].strip()
        
        # Extract ID and type
        id_match = re.match(r'(Q\d+)', q_header)
        q_id = id_match.group(1) if id_match else f"Q{i}"
        
        q_type = "CHECKBOX" if "複数選択" in q_header else "RADIO"
        
        # Parse question text and options
        lines = [line.strip() for line in q_body.split('\n') if line.strip()]
        
        question_text_lines = []
        options = []
        
        for line in lines:
            if line.startswith('- [x] '):
                options.append({"text": line[6:].strip(), "isCorrect": True})
            elif line.startswith('- [ ] '):
                options.append({"text": line[6:].strip(), "isCorrect": False})
            else:
                question_text_lines.append(line)
        
        question_text = "\n".join(question_text_lines).strip()
        
        questions.append({
            "id": q_id,
            "type": q_type,
            "questionText": f"{q_id}\n{question_text}",
            "points": 1,
            "options": options
        })
        
    return {
        "sessionTitle": session_title,
        "questions": questions
    }

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tests_dir = os.path.join(base_dir, 'docs', 'tests')
    json_dir = os.path.join(tests_dir, 'json')
    
    md_files = glob.glob(os.path.join(tests_dir, 'Session*_Test.md'))
    
    for md_file in md_files:
        filename = os.path.basename(md_file)
        print(f"Processing {filename}...")
        parsed_data = parse_markdown(md_file)
        
        json_filename = filename.replace('.md', '.json')
        json_path = os.path.join(json_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            
        print(f"Saved to {json_filename}")

if __name__ == "__main__":
    main()
