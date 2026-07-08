import json

def main():
    print("[*] STEP 5: Adding 30%+ frequent commenters to Whitelist")
    with open('active_users.json', 'r') as f:
        active_users = json.load(f)
        
    with open('post_ids_step1.json', 'r') as f:
        all_pids = json.load(f)
        
    whitelist = set()
    with open('whitelist_step4.txt', 'r') as f:
        for line in f:
            if line.strip():
                whitelist.add(line.strip())
                
    total_posts = len(all_pids)
    added_count = 0
    
    if total_posts > 0:
        for user, pids in active_users.items():
            if len(pids) / total_posts > 0.30:
                if user not in whitelist:
                    whitelist.add(user)
                    added_count += 1
                    
    with open('final_whitelist.txt', 'w') as f:
        for u in sorted(whitelist):
            f.write(u + '\n')
            
    print(f"[*] STEP 5 COMPLETE. Added {added_count} frequent users. Final Whitelist Size: {len(whitelist)}")

if __name__ == "__main__":
    main()
