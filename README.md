# prompt



# v2 (sub scan)
You had to build a scanning subprotocol for the KafkaFPS subreddit with the API that you're currently using (Arctic Photon). 

What it needs to do in steps of separate scripts:

1. Pull all posts within the last week or month, open all those posts by their respective ID, scan through all the comments on that post, exclude users "AskGrok", "[deleted]", "AutoModetator", "kafka-imperium" before any further actions. Write all nicknames except the excluded ones for an additional later check (active users check file). 
2. Get post ids from script 1
3. Scan each. Then if post has less than 5 comments (excluding those I specified to be ignored already in script 1 rules) then this post gets ignored and isn't proceeded with. Then if post is unpopular, by that I mean low amount of comments less than 10 and "likes" or "downs" parameter on most comments is "likes": null (means no upvote on the comment) and "downs": 0 (means no downvotes on the comment), which would mean the post gained no traction and commenters didn't get any feedback then this post is also ignored and isn't proceeded with.
4. Get post ids from previous script. Based on filtered (valid) posts, there needs to be a check on the amount of comments as sometimes the post can have more than 100. According to previous rules, find top 5 most upvoted and top 5 most downvoted comments usernames in the post and write these usernames into a "whitelist", do not append the same nickname multiple times and keep unique hits if it just so happens to be in other post according to the criteria of top upvotes/downvotes. 
5. Pull (active users check file) and nicknames that occur in comments of posts more than 30% of the time on all posts(even filtered out invalid posts), should also go in whitelist even if they didn't meet the criteria on top5 upvotes or top5 downvotes.
6. Then after done scanning the subreddit posts and appending all correct username cases (top5 upvotes, top5 downcotes on filtered valid posts + top 30% most frequent comments usernames including filtered out invalid posts), then schedule the same golden standard background check which will give them a respective markdown file analysis.
