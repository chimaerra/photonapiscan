import json

def main():
    print("[*] STEP 4: Extracting Top/Bottom 5 Users from Valid Posts")
    with open('raw_data.json', 'r') as f:
        data = json.load(f)
        
    with open('valid_posts_step3.json', 'r') as f:
        valid_pids = json.load(f)
        
    whitelist = set()
    
    for pid in valid_pids:
        comments = data['comments'].get(pid, [])
        if not comments: continue
        
        # Sort by score
        comments.sort(key=lambda x: x.get('score', 0))
        
        # Extract Top 5 and Bottom 5 (keeping unique usernames)
        target_comments = comments[:5] + comments[-5:] if len(comments) >= 10 else comments
        for c in target_comments:
            whitelist.add(c['author'])
            
    with open('whitelist_step4.txt', 'w') as f:
        for u in sorted(whitelist):
            f.write(u + '\n')
            
    print(f"[*] STEP 4 COMPLETE. Whitelist Size: {len(whitelist)}")

if __name__ == "__main__":
    main()
