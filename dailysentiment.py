import json
from datetime import datetime
from collections import defaultdict

def load_comments(file_path):
    with open(file_path, "r", encoding='utf-8') as f:
        return json.load(f)

def calculate_weighted_scores(comments):
    scores_by_date = defaultdict(list)
    for comment in comments:
        label_score = get_label_score(comment)
        weighted_score = label_score * comment["confidence"] * comment["score"] * (comment["num_replies"] + 1)
        date = datetime.utcfromtimestamp(comment["created_utc"]).date().isoformat()
        scores_by_date[date].append(weighted_score)
    return scores_by_date


def get_label_score(comment):
    if comment["label"] == "POSITIVE":
        return 1
    elif comment["label"] == "NEGATIVE":
        return -1
    else:
        return 0

def calculate_daily_scores(scores_by_date):
    daily_scores = {}
    for date, scores in scores_by_date.items():
        daily_scores[date] = sum(scores) / len(scores) if scores else 0
    return daily_scores

def normalize_scores(daily_scores):
    min_score = min(daily_scores.values()) if daily_scores else 0
    max_score = max(daily_scores.values()) if daily_scores else 1
    range_score = max_score - min_score if max_score != min_score else 1

    for date in daily_scores:
        daily_scores[date] = (daily_scores[date] - min_score) / range_score * 2 - 1
    return daily_scores

def write_scores_to_file(daily_scores, file_path):
    # Convert the dictionary to a list of tuples and sort by date
    sorted_scores = sorted(daily_scores.items(), key=lambda x: x[0])

    with open(file_path, "w", encoding='utf-8') as f:
        # Write the sorted list of tuples to the file as JSON
        json.dump(sorted_scores, f, ensure_ascii=False, indent=4)

def main():
    comments = load_comments("sentiment_results.json")
    scores_by_date = calculate_weighted_scores(comments)
    daily_scores = calculate_daily_scores(scores_by_date)
    normalized_scores = normalize_scores(daily_scores)
    write_scores_to_file(normalized_scores, "daily_scores.json")

if __name__ == "__main__":
    main()
