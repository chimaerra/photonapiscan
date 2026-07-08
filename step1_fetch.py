import json, time, os
from api_utils import BASE_URL, make_request, IGNORED_AUTHORS

def main():
    end_ts = int(time.time())
    start_ts = end_ts - 86400  # 24 hours
    subreddit = "KafkaFPS"
    
    print(f"[*] STEP 1: Fetching posts and comments for r/{subreddit} (last 24 hours)")
    
    posts = []
    after_ts = start_ts
    while True:
        url = f"{BASE_URL}/posts/search?subreddit={subreddit}&limit=100&sort=asc&after={after_ts}&before={end_ts}"
        data = make_request(url)
        if not data or not data.get('data'): break
        batch = data['data']
        posts.extend(batch)
        if len(batch) == 100:
            last_ts = batch[-1]['created_utc']
            after_ts = after_ts + 1 if last_ts == after_ts else last_ts
        else:
            break

    print(f"[*] Found {len(posts)} posts. Fetching comments...")

    all_data = {"posts": posts, "comments": {}}
    active_users = {} # user -> list of post IDs they commented on
    
    for i, p in enumerate(posts):
        pid = p['id']
        comments = []
        c_after_ts = 0
        while True:
            # FIX: Use link_id={pid} without 't3_' which fixes the HTTP 400/422 error
            url = f"{BASE_URL}/comments/search?link_id={pid}&limit=100&sort=asc"
            if c_after_ts > 0:
                url += f"&after={c_after_ts}"
                
            data = make_request(url)
            if not data or not data.get('data'): break
            batch = data['data']
            comments.extend(batch)
            if len(batch) == 100:
                last_ts = batch[-1]['created_utc']
                c_after_ts = c_after_ts + 1 if last_ts == c_after_ts else last_ts
            else:
                break
                
        # Filter IGNORED users
        valid_comments = [c for c in comments if c.get('author') and c['author'] not in IGNORED_AUTHORS]
        all_data["comments"][pid] = valid_comments
        
        # Track presence on ALL posts
        for c in valid_comments:
            author = c['author']
            if author not in active_users:
                active_users[author] = set()
            active_users[author].add(pid)
            
        if (i+1) % 10 == 0:
            print(f"    Fetched comments for {i+1} posts...")
            
    # Save data
    with open('raw_data.json', 'w') as f:
        json.dump(all_data, f)
        
    # Convert sets to lists for JSON
    for k in active_users:
        active_users[k] = list(active_users[k])
        
    with open('active_users.json', 'w') as f:
        json.dump(active_users, f)

    print(f"[*] STEP 1 COMPLETE. Total valid users tracked: {len(active_users)}")

if __name__ == "__main__":
    main()
