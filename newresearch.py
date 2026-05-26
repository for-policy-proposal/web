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
from tenacity import retry, stop_after_attempt, wait_fixed, wait_exponential
from htmldate import find_date
from datetime import datetime

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else None

load_dotenv()

#今後
    #読みにくい、改善
    #今後printを減らす
    #manifestoとNot manifesto両方に同じ政策が入ったケース、対策する

#googleのdeep researchに公約を抽出させていたものを、URLのみ抽出に変更
#research1は公式サイトを対象に、research2は公式サイト以外のURLを主に抽出するプロンプトになっています。
#その後URLからウェブの内容を取り、Gemmaが政策を書いているかを、政策であればGeminiが公約か否かを判定します。
#gemmaの方がAPIに余裕があるのでこの形です





headers = {
       'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0"
    }

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=3, max=50))
def safe_request_get(url):
    print(headers)
    res = requests.get(url, headers=headers, timeout=(12, 15))
    res.raise_for_status() 
    return res

from openrouter import OpenRouter


api_key_openrouter = os.environ.get('OPENROUTER')
url = os.environ.get('URL')

@retry(stop=stop_after_attempt(5), wait=wait_fixed(5))
def safe_generate_content(client, model, contents, config):
    print(api_key_openrouter)
    print(url)
    full_text = "\n\n".join(str(c) for c in contents)

    with OpenRouter(api_key=api_key_openrouter) as client:
        response = client.chat.send(
            model="~google/gemini-pro-latest",
            messages=[{"role": "user", "content": full_text}],
            response_format=config ,
            server_url=url )
        
        content = response.choices[0].message.content
        print(content)
        

        class SimpleResponse:
            def __init__(self, text):
                self.text = text
        return SimpleResponse(content)


 
@retry(stop=stop_after_attempt(5), wait=wait_fixed(5))
def openrouter_gemma(client, model, contents, config):
    print(api_key_openrouter)
    print(url)
    full_text = "\n\n".join(str(c) for c in contents)

    with OpenRouter(api_key=api_key_openrouter) as client:
        response = client.chat.send(
            model=model,
            messages=[{"role": "user", "content": full_text}],
            response_format=config ,
            server_url=url )
        
        content = response.choices[0].message.content
        print(content)
        

        class SimpleResponse:
            def __init__(self, text):
                self.text = text
        return SimpleResponse(content)

key = os.environ.get('GEMINI_API')
client = genai.Client(api_key= key)

@retry(stop=stop_after_attempt(8), wait=wait_exponential(multiplier=1, min=3, max=50))
def safe_generate_gemma(client, model, contents, config):
    print(key)
    return client.models.generate_content(model=model, contents=contents, config=config)
   


save_lock = threading.Lock()

def wait_for_research(client, interaction_id):
    while True:
        interaction = client.interactions.get(interaction_id)
        if interaction.status == "completed":
            print("research completed")
            print(interaction.steps[-1].content[0].text)
            final_result = interaction.steps[-1].content[0].text
            #final_result = interaction.outputs[-1].text
            return final_result

        elif interaction.status == "failed":
            print(f"Research failed: {interaction.error}")
            break
        time.sleep(10)

def save_append_data(out_file, district, num, winner, new_manifesto, new_not_manifesto):
    with save_lock: 
        data = {"district": f"{district}{num}区", "candidates": [{"name": winner, "party": "", "manifesto": [], "not-manifesto": []}]}
        
      
        if out_file.exists():
            with open(out_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    pass

        data["candidates"][0]["manifesto"].extend(new_manifesto)
        data["candidates"][0]["not-manifesto"].extend(new_not_manifesto)
        
    
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)





ALL_WINNERS = {
    "tokyo": {
        13: {
            "name": "土田慎",
            "official": "http://www.tsuchida-shin.jp/",
            "party": "自由民主党"
        },
    }
}


'''    

        2: {
            "name": "辻清人",
            "official": "https://k-tsuji.jp/",
            "party": "自由民主党"
        },
 3: {
            "name": "石原宏高",
            "official": "https://www.ishihara-hirotaka.com/",
            "party": "自由民主党"
        },
      4: {
            "name": "平将明",
            "official": "https://www.taira-m.jp/",
            "party": "自由民主党"
        },
        5: {
            "name": "若宮健嗣",
            "official": "https://k-wakamiya.com/",
            "party": "自由民主党"
        },
        6: {
            "name": "畦元将吾",
            "official": "https://azemoto.jp/",
            "party": "自由民主党"
        },
        7: {
            "name": "丸川珠代",
            "official": "https://t-marukawa.jp/",
            "party": "自由民主党"
        },
        8: {
            "name": "門寛子",
            "official": "https://kado-hiroko.jp/",
            "party": "自由民主党"
        },
        9: {
            "name": "菅原一秀",
            "official": "https://isshu.online/",
            "party": "自由民主党"
        },
        10: {
            "name": "鈴木隼人",
            "official": "https://www.suzukihayato.jp/",
            "party": "自由民主党"
        },
        11: {
            "name": "下村博文",
            "official": "https://www.hakubun.biz/",
            "party": "自由民主党"
        },
        12: {
            "name": "高木啓",
            "official": "https://takagi-kei.com/",
            "party": "自由民主党"
        },
        13: {
            "name": "土田慎",
            "official": "http://www.tsuchida-shin.jp/",
            "party": "自由民主党"
        },
 

        '''





def clean_json_text(text):
    text = text.strip()
    text = re.sub(r'^```(json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text


def research1(district,winner,num,official):
    print("research1 started")
    #official="https://miki-yamada.com/"
    PROMPT = f"""
    1. 応答の開始から終了まで、一切の説明文、挨拶、レポート、Markdown装飾（```json等）を禁止します。
    2. 出力は、以下のJSONフォーマットに従った純粋なデータ構造のみとしてください。
    3. もしレポートや文章が含まれた場合、システムエラーとして処理されます。
    

    # Role
    あなたは政治学とデータ分析に精通した、極めて執念深いJSONデータ抽出エンジンです。
    指定された政治家の政策を含んだページのURLを最低20個抽出してください。
    後で選別するため、少しでも「具体的」と感じるものはすべて含めてください。質より量を求めています。
    「実現可能性」や「重要度」をあなたが判断して**切り捨てることを厳禁**します。
    具体的であれば、たとえ小さな項目であっても全てリストアップしてください。複数ページのURLを取り出すだけで、満足しないでください。最低でも30個のリンクを期待します。しつこく執念深く検索を続けてください。
   
   「政策ページ」とは以下を全て含む：
        明示的な政策・公約ページ
        活動報告・ブログ・お知らせ内で具体的施策に言及しているページ
        記者会見・演説・インタビュー記事
        政策資料・提言書
        予算・法案・制度に関する具体的記述があるページ
    政策と明記されていないページでも、具体的施策・数値・制度・予算・法案への言及があれば必ず含めること

    # Task
    公式サイト{official}のみを対象にクロールを行う。
    1. Google Search Groundingを使用し、{official}内で、政策や公約が記載されている可能性のあるページを**全て**クロールしてください。

    「公約」とのページ以外にも、ブログの欄などに政策がある可能性もあるため、公式ウェブサイトのリンクから政策がある可能性があるページをクロールしてください。公式ウェブサイトに関してはサイトマップを執念深く確認してください。
    
    2. 以下のクエリを一つずつGoogle search groundingを使用し検索すること。その上で、見つけたページに政策が含まれている場合はURLを保存すること。

    経済・税制・物価高 after:2025-03-30 site:{official}
    外交・安保・憲法 after:2025-03-30 site:{official}
    教育・子育て・デジタル after:2025-03-30 site:{official}
    厚生労働・医療・地域課題 after:2025-03-30 site:{official}
    - "{winner} 政策 after:2025-03-30 site:{official}"
    - "{winner} 公約 after:2025-03-30 site:{official}"
    - "{winner} マニフェスト site:{official}"
    - "site:{official} 政策"
    - "site:{official} 公約"

    3.以上のクエリ検索終了後、独自に site:{official} を含めた検索クエリを作ってください。一つずつGoogle search groundingを使用し検索すること。
    その上で、見つけたページに政策が含まれている場合はURLを保存すること。
    

    

    4. 抽出したURLを、必ず以下のJSONフォーマットの形式でリスト化してください。発見したURLは全てJsonにまとめてください。
    5. 今回の選挙・選挙区の考察や挨拶などは不要のため、プロンプトに対しJsonのみで返答してください。レポートを求めていません。あくまでURLの抽出が目的です。
    6. 「似たような内容だから」という理由でURLを統合することを厳禁します。URLが異なれば、それは別のソースとして全て出力してください。

   
    
# Target
    対象議員：{winner}
    対象期間：2026年2月の衆議院選挙に際して、{winner}が{official}に発表したもののリンクを検索してください。
    




※重要：３つ以上ある際は全てjsonで乗せてください。
※重要：キー名に日本語や具体的な公約内容を入れず、必ず上記の見本と同じキー名（urls）を使用してください。
見つかった全てのURLを、上記のJSONと同じ構造でリスト内に追加してください。
JSONとして正しい形で返してください。

    """

    '''２０のクエリ消した。最低でも20個のURLを返してください。'''

    interaction = client.interactions.create(
        input=PROMPT,
        agent='deep-research-preview-04-2026',
        background=True,
        response_format={
            "type": "OBJECT",
            "mime_type": "application/json",
            "properties": {
                "urls": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                }
            },
            "required": ["urls"]
        }
    
    )

    print(f"started researching {winner} in {district} {num} district")
    interaction_id = interaction.id
    final_result = wait_for_research(client,interaction_id)


            

    try:
        new_data = json.loads(clean_json_text(final_result))
        new_urls = new_data.get("urls", [])
    except Exception as e:
        print(f"JSON parse error: {e}")
        new_urls = []

    OUT_DIR = Path("output/draftresearch/")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / f"{district}-{num:02d}-final.json"


    with save_lock:
        existing_urls = []
        if out_file.exists():
            with open(out_file, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                    existing_urls = existing_data.get("urls", [])
                except Exception as e:
                    print(f"File load error: {e}")
                    existing_urls = []

       
        combined_urls = list(set(existing_urls + new_urls))

 
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({"urls": combined_urls}, f, ensure_ascii=False, indent=2)

    print(f"New URLs found: {len(new_urls)}")
    print("research 1 finished")

     



def research2(district,winner,num):
    print("research 2 started")
    PROMPT = f"""
    1. 応答の開始から終了まで、一切の説明文、挨拶、レポート、Markdown装飾（```json等）を禁止します。
    2. 出力は、以下のJSONフォーマットに従った純粋なデータ構造のみとしてください。
    3. もしレポートや文章が含まれた場合、システムエラーとして処理されます。
    
    # Role
    あなたは政治学とデータ分析に精通した、極めて執念深いJSONデータ抽出エンジンです。
    指定された政治家の政策を含んだページのURLを抽出してください。
    後で選別するため、少しでも「具体的」と感じるものはすべて含めてください。
    「実現可能性」や「重要度」をあなたが判断して**切り捨てることを厳禁**します。
    具体的であれば、たとえ小さな項目であっても全てリストアップしてください。複数ページのURLを取り出すだけで、満足しないでください。しつこく執念深く検索を続けてください。
   
    # Task
    1. Google Search Groundingを使用し、対象者の政策や公約が記載されている可能性のあるページを**全て**クロールしてください。
    なお、{winner}のNote.comをafter:2025-03-30で検索した際に、対象者のNoteアカウントが見つかった場合は、Note.comも同様に分析してください。
    また、{winner}のブログをafter:2025-03-30で検索した際に、対象者のブログが見つかった場合は、ブログも同様に分析してください。

    対象者の公式ウェブサイトは確認しないでください。
    
    2. 検索クエリを20個以上作ってください。その際、以下のクエリを必ず含めること。

    経済・税制・物価高 after:2025-03-30
    外交・安保・憲法 after:2025-03-30
    教育・子育て・デジタル after:2025-03-30
    厚生労働・医療・地域課題 after:2025-03-30
    - "{winner} 政策 after:2025-03-30"
    - "{winner} 公約 after:2025-03-30"
    - "{winner} マニフェスト"
    - "{winner} ブログ 政策"
    - "{winner} note 政策"
    - "{winner} インタビュー 政策"
    - "{winner} NHK アンケート"
    - "{winner} 新聞 候補者アンケート"

    3. 抽出したURLを、必ず以下のJSONフォーマットの形式でリスト化してください。発見したURLは全てJsonにまとめてください。
    4. 今回の選挙・選挙区の考察や挨拶などは不要のため、プロンプトに対しJsonのみで返答してください。レポートを求めていません。あくまでURLの抽出が目的です。
    5. 「似たような内容だから」という理由でURLを統合することを厳禁します。URLが異なれば、それは別のソースとして全て出力してください。

    - JSON以外の説明文、挨拶、Markdownの装飾は一切含めず、純粋なJSON文字列のみを返してください。
    - プロフィールや挨拶などは省いてください。



    
# Target
    対象議員：{winner}
    対象期間：2026年2月の衆議院選挙に際して、{winner}が発表した政策内容をソースとしてください。
    





※重要：３つ以上ある際は全てjsonで乗せてください。
※重要：キー名に日本語や具体的な公約内容を入れず、必ず上記の見本と同じキー名（urls）を使用してください。
見つかった全てのURLを、上記のJSONと同じ構造でリスト内に追加してください。
JSONとして正しい形で返してください。
    """



    interaction = client.interactions.create(
        input=PROMPT,
        agent='deep-research-preview-04-2026',
        background=True,
        response_format={
            "type": "OBJECT",
            "mime_type": "application/json",
            "properties": {
                "urls": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                }
            },
            "required": ["urls"]
        }
    )

    print(f"started researching {winner} in {district} {num} district")

    interaction_id = interaction.id
    final_result= wait_for_research(client,interaction_id)

    OUT_DIR = Path("output/draftresearch/")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / f"{district}-{num:02d}-final.json"
            
    try:
        new_data = json.loads(clean_json_text(final_result))
        new_urls = new_data.get("urls", [])
    except Exception as e:
        new_urls = []


    if out_file.exists():
        with open(out_file, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
                existing_urls = existing_data.get("urls", [])
            except Exception as e:
                existing_urls = []
    else:
        existing_urls = []

    combined_urls = list(set(existing_urls + new_urls))


    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"urls": combined_urls}, f, ensure_ascii=False, indent=2)

    print(f"New URLs found: {len(new_urls)}")
    print("research 2 finished")




def process(district,winner,num,official,party):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future1 = executor.submit(research1, district, winner, num, official)
        future2 = executor.submit(research2, district, winner, num)
        concurrent.futures.wait([future1, future2])
        print(f"{district, num} research finished")





if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures=[]
        for district, winners in ALL_WINNERS.items():
            for num, info in winners.items():
                name = info["name"]
                official = info["official"]
                party= info["party"]
                futures.append(executor.submit(process, district, name, num, official,party))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"スレッド実行中にエラーが発生しました: {exc}")