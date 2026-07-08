import json

def main():
    print("[*] STEP 3: Filtering Posts based on popularity and comment volume")
    with open('raw_data.json', 'r') as f:
        data = json.load(f)
        
    with open('post_ids_step1.json', 'r') as f:
        pids = json.load(f)
        
    valid_pids = []
    
    for pid in pids:
        comments = data['comments'].get(pid, [])
        
        # Rule 1: Less than 5 comments (excluding ignored) -> ignore
        if len(comments) < 5:
            continue
            
        # Rule 2: Unpopular -> Less than 10 comments AND most comments have no upvotes/downvotes
        if len(comments) < 10:
            scores = [c.get('score', 1) for c in comments]
            # If strictly more than 50% have score <= 1 (meaning no upvotes besides self-upvote)
            no_feedback_count = sum(1 for s in scores if s <= 1)
            if no_feedback_count > len(scores) / 2:
                continue
                
        valid_pids.append(pid)
        
    with open('valid_posts_step3.json', 'w') as f:
        json.dump(valid_pids, f)
        
    print(f"[*] STEP 3 COMPLETE. Valid Posts: {len(valid_pids)} out of {len(pids)}")

if __name__ == "__main__":
    main()
