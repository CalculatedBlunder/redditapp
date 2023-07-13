import datetime
import time
import praw
import json


reddit = praw.Reddit(
  client_id='csFOWHojS-aoR-OPK7ND3Q',
  client_secret='sg-wMYc6mst8C2Sy-FOvHxze0EAWLg',
  user_agent='myApp:scrapper:v1.0 (by /u/echo162)'
)

subreddit = reddit.subreddit('wallstreetbets+stocks+investing')
search_query = 'TSLA OR Tesla'

def handle_comment(comment, parent_id=None, comment_dict=None, parent_dict=None):
    if comment_dict is None or parent_dict is None:
        return
    comment_dict[comment.id] = {
        "body": comment.body,
        "score": comment.score,
        "num_replies": len(comment.replies)
    }
    parent_dict[comment.id] = parent_id
    for reply in comment.replies:
        handle_comment(reply, comment.id, comment_dict, parent_dict)


def save_to_file(comments, parents, submission):
    with open("reddit_comments.json", "a", encoding='utf-8') as f:
        for comment_id, parent_id in parents.items():
            comment_obj = {
                "parent_title": submission.title,
                "comment": comments[comment_id]["body"],
                "score": comments[comment_id]["score"],
                "num_replies": comments[comment_id]["num_replies"],
                "created_utc": comment.created_utc
            }

            if parent_id is not None:
                parent_comment = comments.get(parent_id, "")
                comment_obj["parent_comment"] = parent_comment["body"]
            else:
                comment_obj["parent_comment"] = ""

            json.dump(comment_obj, f)
            f.write("\n")


for submission in subreddit.search(search_query, limit=2000, time_filter='year'):
    start_time = time.time()
    if submission.num_comments <= 10:
        continue

    submission.comments.replace_more(limit=10)
    comment_dict = {}
    parent_dict = {}

    info = reddit.auth.limits
    print(f"Remaining: {info['remaining']}")
    print(f"Reset time: {datetime.datetime.fromtimestamp(info['reset_timestamp'])}")
    print(f"Used: {info['used']}")
    for comment in submission.comments:
        handle_comment(comment, None, comment_dict, parent_dict)

    save_to_file(comment_dict, parent_dict, submission)

    print(f"Time taken: {time.time() - start_time} seconds")
