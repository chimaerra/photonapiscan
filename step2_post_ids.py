import json

def main():
    print("[*] STEP 2: Extracting Post IDs")
    with open('raw_data.json', 'r') as f:
        data = json.load(f)
        
    pids = [p['id'] for p in data['posts']]
    
    with open('post_ids_step1.json', 'w') as f:
        json.dump(pids, f)
        
    print(f"[*] STEP 2 COMPLETE. Total posts: {len(pids)}")

if __name__ == "__main__":
    main()
