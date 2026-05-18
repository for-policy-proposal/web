ALL_WINNERS = {
    "北海道": {
        1: {
            "name": "加藤貴弘",
            "official": "https://kato-takahiro.jp/",
            "party": "自由民主党"
        },
        2: {
            "name": "高橋祐介",
            "official": "https://takahashi-yusuke.jp/",
            "party": "自由民主党"
        },
        3: {
            "name": "高木宏壽",
            "official": "https://www.hirohisa-takagi.jp/",
            "party": "自由民主党"
        },
        4: {
            "name": "中村裕之",
            "official": "https://www.hiro-nakamura.jp/",
            "party": "自由民主党"
        },
        5: {
            "name": "和田義明",
            "official": "https://yoshiakiwada.com/",
            "party": "自由民主党"
        },
        6: {
            "name": "東国幹",
            "official": "https://azumakuniyoshi.com/",
            "party": "自由民主党"
        },
        7: {
            "name": "鈴木貴子",
            "official": "https://www.suzuki-takako.jp/",
            "party": "自由民主党"
        },
        8: {
            "name": "向山淳",
            "official": "https://mukaiyama-jun.com/",
            "party": "自由民主党"
        },
        9: {
            "name": "松下英樹",
            "official": "N/A",
            "party": "自由民主党"
        },
        10: {
            "name": "神谷裕",
            "official": "https://kamiyahiroshi.jp/",
            "party": "立憲民主党"
        },
        11: {
            "name": "中川紘一",
            "official": "N/A",
            "party": "自由民主党"
        },
        12: {
            "name": "武部新",
            "official": "http://takebe-arata.jp/",
            "party": "自由民主党"
        }
    },
    "青森県": {
        1: {
            "name": "津島淳",
            "official": "https://tsushimajun.com/",
            "party": "自由民主党"
        },
        2: {
            "name": "神田潤一",
            "official": "https://kandajunichi.jp/",
            "party": "自由民主党"
        },
        3: {
            "name": "木村次郎",
            "official": "https://kimurajiro.jp/",
            "party": "自由民主党"
        }
    },
    "岩手県": {
        1: {
            "name": "階猛",
            "official": "https://shina.jp/",
            "party": "立憲民主党"
        },
        2: {
            "name": "鈴木俊一",
            "official": "http://suzuki-shunichi.jp/",
            "party": "自由民主党"
        },
        3: {
            "name": "藤原崇",
            "official": "https://fujiwaratakashi.jp/",
            "party": "自由民主党"
        }
    },
    "宮城県": {
        1: {
            "name": "土井亨",
            "official": "https://doi-toru.com/",
            "party": "自由民主党"
        },
        2: {
            "name": "渡辺勝幸",
            "official": "https://watanabekatsuyuki.com/",
            "party": "自由民主党"
        },
        3: {
            "name": "西村明宏",
            "official": "https://www.nishimura-akihiro.jp/",
            "party": "自由民主党"
        },
        4: {
            "name": "森下千里",
            "official": "https://morishitachisato.com/",
            "party": "自由民主党"
        },
        5: {
            "name": "小野寺五典",
            "official": "https://www.itsunori.com/",
            "party": "自由民主党"
        }
    },
    "秋田県": {
        1: {
            "name": "冨樫博之",
            "official": "https://www.togachan.jp/",
            "party": "自由民主党"
        },
        2: {
            "name": "福原淳嗣",
            "official": "https://fukuhara-junji.jp/",
            "party": "自由民主党"
        },
        3: {
            "name": "村岡敏英",
            "official": "https://muraokatoshihide.jp/",
            "party": "自由民主党"
        }
    }
}

# Role

あなたは日本の国政選挙および政治家データに精通した調査スペシャリストです。



# Task

[対象：東京都1区山田美樹2区辻清人3区石原宏高4区平将明5区若宮健嗣6区畦元将吾7区丸川珠代8区門寛子9区菅原一秀10区鈴木隼人11区下村博文12区高木啓13区土田慎14区松島みどり15区大空幸星16区大西洋平17区平沢勝栄18区福田かおる19区松本洋平20区木原誠二21区小田原潔22区伊藤達也23区川松真一朗24区萩生田光一25区井上信治26区今岡植27区黒崎祐一28区安藤高夫29区長澤興祐30区長島昭久]について、以下の辞書形式（Python dictionary format）でデータを整理してください。それぞれの議員についてWikipediaへ行き、そこから公式サイトへのリンクを見つけるように。



# Constraints (厳守事項)

1. **URLの検証**: URLは必ずブラウザでアクセス可能な最新の公式サイト、または公式プロフィールページ（政党内ページやSNSではなく独自ドメインを優先）を特定してください。推測で生成せず、不明な場合は "N/A" と記載してください。

2. **所属政党の正確性**: 当選時点の最新情報を反映してください。

3. **フォーマット**: 提供する `ALL_WINNERS` 変数の構造を完全に維持してください。

4. **検索プロセス**:

   - まず、各選挙区の当選者氏名リストを確定させる。

   - 次に、氏名 + 「公式サイト」「事務所」「選挙区」で検索し、URLの整合性を確認する。



# Output Format

ALL_WINNERS = {

    "tokyo": {

        1: {

            "name": "氏名",

            "official": "URL",

            "party": "政党名"

        },

        ...

    }

}



# Target Data

対象地域: 東京都

選挙区: 第1区から第30区まで全て、2026年　　１−30区の全ての議員についてWikipediaを確認して。JSONの形に忠実に。name, official, partyの順番や名前を変えないように。当選者はプロンプトにある。