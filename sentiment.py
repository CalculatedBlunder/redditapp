import json
import time
from transformers import pipeline, AutoTokenizer

nlp = pipeline('sentiment-analysis')
tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')

def analyze_sentiment(titles, parent_comments, comments, weight=2):
    # Assume that all inputs are lists of the same length
    assert len(titles) == len(parent_comments) == len(comments)

    texts = []
    for title, parent_comment, comment in zip(titles, parent_comments, comments):
        tokens_comment = tokenizer.encode(f"[COMMENT] " + f"{comment}" * weight, truncation=False)
        
        if len(tokens_comment) > 510:
            tokens_comment = tokens_comment[:510]
            text = tokenizer.decode(tokens_comment)
        else:
            tokens_title_parent = tokenizer.encode(f"[TITLE] {title} [PARENT_COMMENT] {parent_comment}", truncation=False)

            total_tokens = len(tokens_comment) + len(tokens_title_parent)
            if total_tokens > 510:
                tokens_title_parent = tokens_title_parent[:510 - len(tokens_comment)]
            
            tokens = tokens_title_parent + tokens_comment
            text = tokenizer.decode(tokens)

        texts.append(text)

    results = nlp(texts)

    return [(result['label'], result['score']) for result in results]




def load_comments():
    comments = []
    with open("reddit_comments.json", "r") as f:
        for line in f:
            comment_obj = json.loads(line)
            comments.append(comment_obj)
    return comments

def main():
    batch_size = 100  # Or whatever batch size you want

    comments = load_comments()
    results = []

    with open("sentiment_results.json", "w", encoding='utf-8') as f:
        f.write("[")  # Start of JSON list

        for i in range(0, len(comments), batch_size):
            start_time = time.time()
            batch = comments[i:i+batch_size]
            parent_titles = [comment_obj['parent_title'] for comment_obj in batch]
            parent_comments = [comment_obj['parent_comment'] for comment_obj in batch]
            comments_texts = [comment_obj['comment'] for comment_obj in batch]
            
            sentiments = analyze_sentiment(parent_titles, parent_comments, comments_texts)

            for comment_obj, (label, confidence) in zip(batch, sentiments):
                result = {
                    "parent_title": comment_obj['parent_title'],
                    "parent_comment": comment_obj['parent_comment'],
                    "comment": comment_obj['comment'],
                    "num_replies": comment_obj['num_replies'],
                    "score": comment_obj['score'],
                    "label": label,
                    "confidence": confidence,
                    "created_utc": comment_obj['created_utc']
                }

                f.write(json.dumps(result, ensure_ascii=False) + ",\n")  # Write each result followed by a comma and newline
            print(f"Time taken for this batch: {time.time() - start_time} seconds")
        f.seek(f.tell() - 2)  # Move the file pointer 2 characters back to overwrite the last comma
        f.write("\n]")  # End of JSON list



if __name__ == "__main__":
    main()
