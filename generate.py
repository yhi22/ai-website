import anthropic
import json
import re
from datetime import datetime

client = anthropic.Anthropic()
today = datetime.now().strftime('%Y年%m月%d日')

print("Claude APIでニュースを生成中...")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=5000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[
        {
            "role": "user",
            "content": f"""今日（{today}）の以下3領域に関する最新ニュースをWeb検索で調べて、JSON形式で返してください。
JSONのみ返し、マークダウンのコードブロックや余分なテキストは一切含めないでください。

領域：
- stablecoin: ステーブルコイン（規制・市場・企業動向など）
- wallet: ウォレット（セキュリティ・新機能・規制など）
- blockchain: ブロックチェーン・技術（インフラ・DeFi・セキュリティインシデントなど）

{{
  "date": "{today}",
  "summary": "3領域を横断した今日の全体まとめ（200文字程度）",
  "action_points": ["今日やるべきこと・注目すべきこと1", "同2", "同3"],
  "news": [
    {{
      "title": "ニュースタイトル",
      "body": "ニュースの詳細（150文字程度）",
      "source": "情報源名",
      "domain": "stablecoin or wallet or blockchain",
      "subtag": "規制 or 市場 or セキュリティ or 技術 or 企業 or その他"
    }}
  ],
  "analysis": "市場全体への影響・考察（200文字程度）"
}}

各領域から2〜3件ずつ、合計6〜8件程度。最新情報を優先してください。"""
        }
    ]
)

# レスポンスからJSON抽出
news_json = None
for block in response.content:
    if block.type == "text":
        text = block.text.strip()
        if text.startswith("{"):
            news_json = json.loads(text)
        else:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                news_json = json.loads(match.group())

if not news_json:
    raise Exception("ニュースデータの生成に失敗しました")

print(f"ニュース {len(news_json['news'])} 件を取得しました")

# ドメイン設定
domain_map = {
    "stablecoin": {"label": "ステーブルコイン", "cls": "sc"},
    "wallet":     {"label": "ウォレット",       "cls": "wa"},
    "blockchain": {"label": "ブロックチェーン", "cls": "bc"},
}

# ニュースアイテムHTML生成
news_items_html = ""
for item in news_json["news"]:
    d = domain_map.get(item.get("domain", "stablecoin"), domain_map["stablecoin"])
    subtag = item.get("subtag", "")
    news_items_html += f"""
      <div class="news-item" data-cat="{d['cls']}">
        <div class="news-stripe stripe-{d['cls']}"></div>
        <div>
          <div class="news-meta">
            <span class="news-domain domain-{d['cls']}">{d['label']}</span>
            <span class="news-subtag">{subtag}</span>
          </div>
          <div class="news-title">{item['title']}</div>
          <div class="news-body">{item['body']}</div>
          <span class="news-source">{item.get('source', '')}</span>
        </div>
      </div>"""

# アクションポイントHTML生成
action_html = ""
for i, pt in enumerate(news_json.get("action_points", []), 1):
    action_html += f'<li><span class="action-num">{i}</span>{pt}</li>\n'

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Stablecoin Brief</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;600&family=Noto+Sans+JP:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg:     #ffffff;
      --bg2:    #f6f6f6;
      --ink:    #0a0a0a;
      --ink2:   #2a2a2a;
      --ink3:   #777777;
      --rule:   #e2e2e2;
      --accent: #0055ff;
      --sc:     #0055cc;
      --wa:     #b45309;
      --bc:     #0e7490;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--ink);
      font-family: 'Noto Sans JP', sans-serif;
      font-weight: 300;
      line-height: 1.7;
    }}
    header {{
      border-bottom: 2px solid var(--ink);
      padding: 1.8rem 2.5rem 1.4rem;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }}
    .brand {{
      font-family: 'Noto Serif JP', serif;
      font-size: 1.55rem;
      font-weight: 600;
      color: var(--ink);
    }}
    .brand-dot {{ color: var(--accent); }}
    .header-right {{ text-align: right; }}
    .header-date {{
      font-size: 0.72rem;
      color: var(--ink3);
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }}
    .header-edition {{
      font-size: 0.68rem;
      color: var(--accent);
      letter-spacing: 0.08em;
      margin-top: 0.15rem;
    }}
    main {{
      max-width: 800px;
      margin: 0 auto;
      padding: 0 2.5rem 5rem;
    }}
    section {{
      padding: 2rem 0;
      border-bottom: 1px solid var(--rule);
    }}
    section:last-child {{ border-bottom: none; }}
    .section-label {{
      font-size: 0.62rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: var(--ink3);
      font-weight: 500;
      margin-bottom: 1.2rem;
    }}
    .summary-text {{
      font-size: 0.96rem;
      line-height: 1.9;
      color: var(--ink2);
    }}
    .action-list {{ list-style: none; display: flex; flex-direction: column; gap: 0.7rem; }}
    .action-list li {{
      display: flex;
      align-items: baseline;
      gap: 0.9rem;
      font-size: 0.87rem;
      color: var(--ink);
    }}
    .action-num {{
      font-family: 'Noto Serif JP', serif;
      font-weight: 600;
      color: var(--accent);
      min-width: 1rem;
      flex-shrink: 0;
    }}
    .filter-bar {{
      display: flex;
      gap: 0;
      margin-bottom: 1.6rem;
      border: 1.5px solid var(--ink);
      border-radius: 3px;
      overflow: hidden;
      width: fit-content;
    }}
    .filter-btn {{
      font-family: 'Noto Sans JP', sans-serif;
      font-size: 0.72rem;
      font-weight: 500;
      letter-spacing: 0.06em;
      padding: 0.45rem 1.2rem;
      border: none;
      border-right: 1.5px solid var(--ink);
      background: var(--bg);
      color: var(--ink3);
      cursor: pointer;
      transition: all 0.15s;
    }}
    .filter-btn:last-child {{ border-right: none; }}
    .filter-btn:hover {{ background: var(--bg2); color: var(--ink); }}
    .filter-btn.active {{ background: var(--ink); color: #fff; }}
    .filter-btn[data-cat="all"].active {{ background: var(--accent); }}
    .filter-btn[data-cat="sc"].active  {{ background: var(--sc); border-color: var(--sc); }}
    .filter-btn[data-cat="wa"].active  {{ background: var(--wa); border-color: var(--wa); }}
    .filter-btn[data-cat="bc"].active  {{ background: var(--bc); border-color: var(--bc); }}
    .news-list {{ display: flex; flex-direction: column; }}
    .news-item {{
      display: grid;
      grid-template-columns: 6px 1fr;
      gap: 0 1.4rem;
      padding: 1.3rem 0;
      border-bottom: 1px solid var(--rule);
      align-items: stretch;
    }}
    .news-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
    .news-item.hidden {{ display: none; }}
    .news-stripe {{ width: 3px; border-radius: 2px; align-self: stretch; }}
    .stripe-sc {{ background: var(--sc); }}
    .stripe-wa {{ background: var(--wa); }}
    .stripe-bc {{ background: var(--bc); }}
    .news-meta {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      margin-bottom: 0.35rem;
    }}
    .news-domain {{
      font-size: 0.6rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      font-weight: 500;
      color: #fff;
      padding: 0.18rem 0.5rem;
      border-radius: 2px;
    }}
    .domain-sc {{ background: var(--sc); }}
    .domain-wa {{ background: var(--wa); }}
    .domain-bc {{ background: var(--bc); }}
    .news-subtag {{ font-size: 0.62rem; color: var(--ink3); }}
    .news-title {{
      font-size: 0.92rem;
      font-weight: 500;
      color: var(--ink);
      margin-bottom: 0.4rem;
      line-height: 1.5;
    }}
    .news-body {{
      font-size: 0.82rem;
      color: var(--ink2);
      line-height: 1.75;
      margin-bottom: 0.4rem;
    }}
    .news-source {{ font-size: 0.67rem; color: var(--ink3); }}
    .empty-state {{
      display: none;
      padding: 2rem 0;
      font-size: 0.84rem;
      color: var(--ink3);
      text-align: center;
    }}
    .analysis-box {{
      background: var(--bg2);
      border-left: 3px solid var(--ink);
      padding: 1.3rem 1.6rem;
    }}
    .analysis-text {{
      font-size: 0.87rem;
      color: var(--ink2);
      line-height: 1.95;
    }}
    footer {{
      border-top: 1px solid var(--rule);
      padding: 1.3rem 2.5rem;
      display: flex;
      justify-content: space-between;
      font-size: 0.67rem;
      color: var(--ink3);
    }}
    @media (max-width: 560px) {{
      header {{ padding: 1.4rem 1.2rem; flex-direction: column; align-items: flex-start; gap: 0.5rem; }}
      .header-right {{ text-align: left; }}
      main {{ padding: 0 1.2rem 3rem; }}
      footer {{ flex-direction: column; gap: 0.4rem; padding: 1.2rem; }}
      .filter-bar {{ width: 100%; }}
      .filter-btn {{ flex: 1; padding: 0.45rem 0.3rem; text-align: center; font-size: 0.62rem; }}
    }}
  </style>
</head>
<body>
<header>
  <div class="brand">Stablecoin<span class="brand-dot">.</span>Brief</div>
  <div class="header-right">
    <div class="header-date">{today}</div>
    <div class="header-edition">Morning Edition</div>
  </div>
</header>

<main>
  <section>
    <div class="section-label">Executive Summary</div>
    <p class="summary-text">{news_json['summary']}</p>
  </section>

  <section>
    <div class="section-label">今日おさえるべきポイント</div>
    <ul class="action-list">{action_html}</ul>
  </section>

  <section>
    <div class="section-label">ニュース</div>
    <div class="filter-bar">
      <button class="filter-btn active" data-cat="all">すべて</button>
      <button class="filter-btn" data-cat="sc">ステーブルコイン</button>
      <button class="filter-btn" data-cat="wa">ウォレット</button>
      <button class="filter-btn" data-cat="bc">ブロックチェーン</button>
    </div>
    <div class="news-list" id="newsList">
      {news_items_html}
    </div>
    <div class="empty-state" id="emptyState">該当するニュースがありません</div>
  </section>

  <section>
    <div class="section-label">市場への影響・考察</div>
    <div class="analysis-box">
      <p class="analysis-text">{news_json['analysis']}</p>
    </div>
  </section>
</main>

<footer>
  <span>Stablecoin Brief — Claude AIが毎朝6時に自動生成</span>
  <span>本情報は参考目的のみ。投資判断の根拠としないこと。</span>
</footer>

<script>
  const btns = document.querySelectorAll('.filter-btn');
  const items = document.querySelectorAll('.news-item');
  const emptyState = document.getElementById('emptyState');
  btns.forEach(btn => {{
    btn.addEventListener('click', () => {{
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cat = btn.dataset.cat;
      let visible = 0;
      items.forEach(item => {{
        if (cat === 'all' || item.dataset.cat === cat) {{
          item.classList.remove('hidden');
          visible++;
        }} else {{
          item.classList.add('hidden');
        }}
      }});
      emptyState.style.display = visible === 0 ? 'block' : 'none';
    }});
  }});
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html を生成しました")
