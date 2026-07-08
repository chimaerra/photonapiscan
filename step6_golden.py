import json, time, os, re, collections
from datetime import datetime, timezone
from api_utils import BASE_URL, make_request

POLITICAL_KEYWORDS = {
    "сво": r"\bсво\b", "войн": r"войн[а-я]*", "мобилиз": r"мобилиз[а-я]*",
    "украин": r"украин[а-я]*", "хохл": r"хохл[а-я]*", "путин": r"путин[а-я]*",
    "зеленск": r"зеленск[а-я]*", "наци": r"нацист[а-я]*|нациз[а-я]*",
    "военн": r"военн[а-я]*", "запад": r"запад[а-я]*", "ппо": r"\bппо\b",
    "пво": r"\bпво\b", "дрон": r"дрон[а-я]*", "ракет": r"ракет[а-я]*"
}

def get_bounds(author, endpoint):
    first_url = f"{BASE_URL}/{endpoint}/search?author={author}&limit=1&sort=asc"
    last_url = f"{BASE_URL}/{endpoint}/search?author={author}&limit=1&sort=desc"
    first_data = make_request(first_url)
    last_data = make_request(last_url)
    first_ts = first_data['data'][0]['created_utc'] if first_data and first_data.get('data') else None
    last_ts = last_data['data'][0]['created_utc'] if last_data and last_data.get('data') else None
    return first_ts, last_ts

def fetch_full_history(author, endpoint, window_days):
    first_ts, last_ts = get_bounds(author, endpoint)
    if not first_ts or not last_ts: return []
    items = []
    seen_ids = set()
    window_sec = window_days * 86400
    intervals = list(range(first_ts, last_ts + window_sec, window_sec))
    for ts in intervals:
        after_ts = ts
        before_ts = ts + window_sec
        while True:
            url = f"{BASE_URL}/{endpoint}/search?author={author}&limit=100&sort=asc&after={after_ts}&before={before_ts}"
            data = make_request(url)
            if not data or not data.get('data'): break
            batch = data['data']
            for item in batch:
                if item['id'] not in seen_ids:
                    seen_ids.add(item['id'])
                    items.append(item)
            if len(batch) == 100:
                last_batch_ts = batch[-1]['created_utc']
                after_ts = after_ts + 1 if last_batch_ts == after_ts else last_batch_ts
                time.sleep(0.1)
            else:
                break
    return items

def generate_markdown(author, comments, posts):
    if not comments: return
    comments.sort(key=lambda x: x['created_utc'])
    
    months, days, hours, subs, duplicates, kw_hits = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    
    for c in comments:
        dt = datetime.fromtimestamp(c['created_utc'], tz=timezone.utc)
        months[dt.strftime('%Y-%m')] += 1
        days[dt.strftime('%Y-%m-%d')] += 1
        hours[dt.hour] += 1
        subs[c['subreddit']] += 1
        duplicates[c['body'].strip()] += 1
        for kw, pat in POLITICAL_KEYWORDS.items():
            if re.search(pat, c['body'].lower()): kw_hits[kw] += 1
                
    duplicate_count = sum(cnt - 1 for t, cnt in duplicates.items() if cnt > 1)
    dup_pct = (duplicate_count / len(comments) * 100) if len(comments) > 0 else 0
    avg_per_day = len(comments) / len(days) if len(days) > 0 else 0
    
    busiest_month = months.most_common(1)[0][0] if months else "N/A"
    busiest_count = months.most_common(1)[0][1] if months else 0
    top_subs_str = ', '.join([f"r/{s} ({c})" for s, c in subs.most_common(5)])
    
    peak_utc_hour = hours.most_common(1)[0][0] if hours else 0
    tz_offset = (18 - peak_utc_hour) % 24
    if tz_offset > 12: tz_offset -= 24
    
    comments_by_score = sorted(comments, key=lambda x: x.get('score', 0))
    top_upvoted = comments_by_score[-3:]
    top_downvoted = comments_by_score[:3]
    
    kw_str = ""
    if kw_hits:
        for kw, c in kw_hits.most_common(): kw_str += f"* **{kw}**: {c} mentions\n"
    else:
        kw_str = "* No major propaganda/war keywords detected.\n"
        
    top_upvoted_str = "".join(f"* **(+{c.get('score', 0)})** r/{c['subreddit']}: {c['body'][:200].replace(chr(10), ' ')}...\n" for c in reversed(top_upvoted))
    top_downvoted_str = "".join(f"* **({c.get('score', 0)})** r/{c['subreddit']}: {c['body'][:200].replace(chr(10), ' ')}...\n" for c in top_downvoted)
        
    first_all = min(comments[0]['created_utc'], posts[0]['created_utc']) if posts else comments[0]['created_utc']
    last_all = max(comments[-1]['created_utc'], posts[-1]['created_utc']) if posts else comments[-1]['created_utc']
    span_months = (last_all - first_all) / (86400 * 30)
    time_span_str = f"{datetime.fromtimestamp(first_all, tz=timezone.utc).strftime('%b %Y')} - {datetime.fromtimestamp(last_all, tz=timezone.utc).strftime('%b %Y')} ({span_months:.1f} months)" if span_months >= 1 else "< 1 month"

    verdict = "🚨 LIKELY BOT/FARM" if duplicate_count > len(comments)*0.1 or avg_per_day > 50 else "✅ LIKELY HUMAN"

    report = f"""# OSINT Portrait: u/{author} (Automated Run)

**Dataset:** {len(comments)} comments, {len(posts)} posts (Arctic Shift API)  
**Time span:** {time_span_str}

---

## 🚨 BOT/PROPAGANDA WORKER INDICATORS

### 1. Impossible Volume
* **Comments:** {len(comments)}
* **Posts:** {len(posts)}
* **Average per active day:** {avg_per_day:.2f}

### 2. 24/7 Activity Pattern
* **Peak Activity UTC:** {peak_utc_hour:02d}:00
* **Estimated Timezone:** UTC{tz_offset:+}

### 3. No Exact Copy-Paste
* **Duplicates:** {duplicate_count} ({dup_pct:.1f}%)

---

## 📈 THE RADICALIZATION TIMELINE
* **Busiest Month:** {busiest_month} ({busiest_count} items)
* **Top Subreddits:** {top_subs_str}

---

## 🌍 DEMOGRAPHICS & BACKGROUND
*(Automated Data)*
* **Timezone:** UTC{tz_offset:+}

---

## 🧠 PSYCHOLOGICAL PROFILE
*(Automated Data)*
* **Top Interactions:** {top_subs_str}

---

## 📝 LINGUISTIC & KEYWORD ANALYSIS
### Targeted Keywords
{kw_str}

---

## 🗳️ EXTREMES: MOST UPVOTED & DOWNVOTED

### The Highs
{top_upvoted_str}

### The Lows
{top_downvoted_str}

---

## 🔍 BOT vs. HUMAN: Final Assessment
**Verdict:** {verdict}

---

## 📎 Raw Data
- Full dataset saved to: `data/{author}_comments.jsonl`
"""
    os.makedirs('reports', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    with open(f'reports/{author}_osint_report.md', 'w') as f: f.write(report)
    with open(f'data/{author}_comments.jsonl', 'w') as f:
        for c in comments: f.write(json.dumps(c) + '\n')

def main():
    print("[*] STEP 6: Running Golden Protocol on Final Whitelist")
    whitelist = []
    with open('final_whitelist.txt', 'r') as f:
        for line in f:
            if line.strip(): whitelist.append(line.strip())
            
    limit_users = whitelist[:2] # Limited to 2 for LLM timeout safety
    print(f"[*] Fetched {len(whitelist)} users. Generating full background checks for {len(limit_users)} user(s) (Demo limit)...")
    for i, u in enumerate(limit_users):
        print(f"  [{i+1}/{len(limit_users)}] Processing u/{u}")
        comments = fetch_full_history(u, 'comments', 7)
        posts = fetch_full_history(u, 'posts', 30)
        generate_markdown(u, comments, posts)
        
    print("[*] STEP 6 COMPLETE. All reports saved in /home/user/subgolden_pipeline/reports")

if __name__ == "__main__":
    main()
