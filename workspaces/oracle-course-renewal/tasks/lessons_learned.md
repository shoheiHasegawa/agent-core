# Lessons Learned: Oracle Course Renewal

## 🧠 学びと反省（Failure Patterns & Insights）
- **前任者資料の監査知見**: 単なる資格試験の丸暗記講義ではなく、実務に生きる普遍的な「RDBMS基礎体力（インフラ視点＋開発視点）」をインストールする講義設計とSOLID問題設計が受講者のエンゲージメントを高める。
- **NotebookLM分割投入規格**: 長大なMarkdownを一括投入するとハルシネーションを起こすため、フレーム、チャプター別、プロンプトの3分割で投入するサンドイッチ方式が極めて安定する。
- **GAS自動生成**: Google Formsの手作業作成を排除し、MarkdownからPythonスクリプトでGASを生成・流し込むことで、問題修正時の手戻りコストが激減した。
