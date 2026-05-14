import os
import json
import re
from pathlib import Path

# --- パスの設定 ---
# ウェブ公約のデータ (assign_ids.py で処理した後のデータ)
WEB_DATA_DIR = Path("data")  # または output/finaldata
# 選挙公報のテキストデータ
BULLETIN_DATA_DIR = Path("data/ai_output/2026/shu/tokyo")
# 統合後のJSONを保存するフォルダ (Hugoが読み込む場所)
OUTPUT_DIR = Path("data/2026/shu/tokyo")

def load_json(filepath):
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_json(filepath, data):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def format_bulletin_text(raw_text):
    """
    選挙公報のテキストを段落ごとに分け、
    header(見出し) と body(<br>区切りの本文) の辞書リストに変換する
    """
    blocks = []
    if not raw_text:
        return blocks

    paragraphs = raw_text.split("\n\n")
    for p in paragraphs:
        lines = p.strip().split("\n")
        if lines:
            header = lines[0] # 1行目を見出しとする
            body = "<br>".join(lines[1:]) if len(lines) > 1 else "" # 2行目以降を<br>でつなぐ
            blocks.append({
                "header": header,
                "body": body
            })
    return blocks

def merge_district_data(district_num):
    # ファイル名の作成 (例: tokyo-01)
    filename_base = f"tokyo-{district_num:02d}"
    
    # データ読み込み
    web_data = load_json(WEB_DATA_DIR / f"{filename_base}-final.json")
    bulletin_data = load_json(BULLETIN_DATA_DIR / f"{filename_base}.json")
    
    if not web_data or not bulletin_data:
        print(f"スキップ: {filename_base} のデータが揃っていません。")
        return

    # 統合先の枠組みを作成
    merged = {
        "district": web_data.get("district", ""),
        "district_code": f"2026-shu-tokyo-{district_num}",
        "candidates": []
    }

    # web_data の候補者をベースに処理
    for web_candidate in web_data.get("candidates", []):
        cand_name = web_candidate.get("name")
        
        # bulletin_data から同じ名前の候補者を探す
        bulletin_cand = next((c for c in bulletin_data.get("candidates", []) if c.get("name") == cand_name), {})
        
        # 選挙公報テキストの整形
        raw_text = bulletin_cand.get("full_text", "")
        formatted_blocks = format_bulletin_text(raw_text)

        # 1人の候補者のデータを組み立てる
        merged_candidate = {
            "name": cand_name,
            "party": web_candidate.get("party", ""),
            "bulletin": {
                "full_text_blocks": formatted_blocks,
                # 選挙公報からも公約を抽出している場合はここに入れる
                "manifesto": bulletin_cand.get("manifesto", []) 
            },
            "web": {
                # ウェブからの公約（policy_id付き）
                "manifesto": web_candidate.get("manifesto", []),
                # ウェブからの非公約（元のJSONに not_manifesto があれば取得）
                "not_manifesto": web_candidate.get("not_manifesto", [])
            }
        }
        merged["candidates"].append(merged_candidate)

    # 統合したデータを保存
    output_path = OUTPUT_DIR / f"{filename_base}.json"
    save_json(output_path, merged)
    print(f"保存完了: {output_path}")

if __name__ == "__main__":
    # 東京1区と2区を処理する (必要に応じて範囲を広げてください)
    for i in range(1, 3):
        merge_district_data(i)