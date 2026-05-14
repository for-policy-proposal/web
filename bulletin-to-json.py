import os
import json
import time
import google.genai as genai
from pathlib import Path
import fitz
from dotenv import load_dotenv 
import concurrent.futures
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import threading
from tenacity import retry, stop_after_attempt, wait_fixed
from htmldate import find_date
from datetime import datetime

# 環境変数の読み込み (APIキー)
load_dotenv()
key = os.environ.get('GEMINI_API')
client = genai.Client(api_key= key)

# ファイルパスの設定
INPUT_DIR = "output/manifesto/"
OUTPUT_DIR = "data/"
POLICIES_FILE = os.path.join(OUTPUT_DIR, "policies.json")

def load_json(filepath):
    """JSONファイルを読み込む"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(filepath, data):
    """JSONファイルを保存する"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_policy_id(client, new_policy_title, master_policies):
    """
    Geminiを使って、新しい公約がマスタデータのどれに該当するか判定する
    """
    # マスタデータが空の場合は、比較せずにNEWを返す
    if not master_policies:
        return "NEW"

    # マスタデータをAIに渡しやすい文字列に変換
    master_text = "\n".join([f"ID: {pid} | タイトル: {info['title']}" for pid, info in master_policies.items()])

    prompt = f"""
    あなたは厳密な政治公約の分類アシスタントです。
    以下の【既存の公約マスタ】の中に、【新しい公約】と「意味・対象範囲が完全に一致する」ものがあるか判定してください。

    【厳密なルール】
    - ゆらぎは許容しません。「食料品消費税0％」と「消費税0％」は対象範囲が異なるため、別物として扱ってください。
    - 単なる言い回しの違い（例：「食品消費税のゼロ化」と「食料品の消費税をゼロにする」）であれば、同じとみなしてください。

    【既存の公約マスタ】
    {master_text}

    【新しい公約】
    {new_policy_title}

    【出力形式】
    完全に一致するものがあれば、その「ID（例: policy_001）」のみを出力してください。
    一致するものがなければ、「NEW」とだけ出力してください。
    説明や言い訳は一切不要です。
    """

    try:
        response = client.models.generate_content(
            model='gemma-4-31b-it', 
            contents=prompt,
        )
        result = response.text.strip()
        
        # 出力がIDの形式か、NEWかをチェック
        if result == "NEW" or re.match(r"^policy_\d+$", result):
            return result
        else:
            print(f"警告: AIの予期せぬ返答: {result}")
            return "NEW"
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return "NEW"
import os
import json
import re

# --- 設定（パスを実際の構造に合わせて調整してください） ---
SOURCE_DIR = "output/manifesto/"      # 抽出済みデータがある場所
TARGET_BASE_DIR = "data/2026/shu/tokyo/"  # 最終的な1.jsonなどがある場所
POLICIES_FILE = "data/policies.json"  # マスタデータ

def merge_and_process(filename, master_policies):
    # 1. 公約マスタの読み込み
    master_policies = load_json(POLICIES_FILE)
    
    # 2. 抽出済みファイル（tokyo-01.json など）をループ
    for filename in os.listdir(SOURCE_DIR):
        if not filename.endswith(".json"):
            continue
            
        source_path = os.path.join(SOURCE_DIR, filename)
        source_data = load_json(source_path) # tokyo-01.jsonの中身
        
        # ファイル名からターゲットのファイル名を特定 (例: tokyo-01.json -> 1.json)
        # ※ファイル名の命名規則に合わせて調整してください
        target_filename = re.sub(r'^[a-z]+-0?', '', filename) # "tokyo-01.json" -> "1.json"
        target_path = os.path.join(TARGET_BASE_DIR, target_filename)
        
        if not os.path.exists(target_path):
            print(f"警告: ターゲットファイルが見つかりません: {target_path}")
            continue
            
        target_data = load_json(target_path) # 1.jsonの中身

        print(f"--- {filename} を {target_filename} に統合中 ---")

        # 3. データのコピー（ここが重要）
        # tokyo-01.json の "manifesto" を 1.json の candidates[0]["bulletin"]["manifesto"] に入れる
        if "manifesto" in source_data:
            # 1.jsonの最初の候補者のbulletin.manifestoを更新
            target_data["candidates"][0]["bulletin"]["manifesto"] = source_data["manifesto"]
            
            # 4. コピーしたデータに対してID付与処理を行う
            for manifesto in target_data["candidates"][0]["bulletin"]["manifesto"]:
                title = manifesto["title"]
                matched_id = get_policy_id(client, title, master_policies)
                
                if matched_id == "NEW":
                    new_id = f"policy_{len(master_policies) + 1:03}"
                    master_policies[new_id] = {"title": title, "status": "未確認"}
                    manifesto["policy_id"] = new_id
                    print(f"  [新規] {title} -> {new_id}")
                else:
                    manifesto["policy_id"] = matched_id
                    print(f"  [一致] {title} -> {matched_id}")

        # 5. 統合後のデータを保存
        save_json(target_path, target_data)
        print(f"保存完了: {target_path}")

    # 最終的なマスタを保存
    save_json(POLICIES_FILE, master_policies)

# ※ get_policy_id, load_json, save_json 等の関数は既存のものをそのまま使用してください
if __name__ == "__main__":
    # 出力先フォルダがなければ作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # マスタデータを読み込む
    master_policies = load_json(POLICIES_FILE)
    
    # input_dataフォルダ内のJSONファイルを順番に処理
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".json"):
            master_policies = merge_and_process(filename, master_policies)
    
    # 最終的なマスタデータを保存
    save_json(POLICIES_FILE, master_policies)
    print("すべての処理が完了し、マスタデータを更新しました！")