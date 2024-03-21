import csv
import hashlib
import nltk
import json

from pathlib import Path

nltk.download("punkt")


def parse_jsonl(file):
    with open(file, "r") as data:
        for line in data:
            line = json.loads(line)
            key = hashlib.sha256(str(line).encode()).hexdigest()
            yield line, key


def split_paragraph(paragraph):
    # sentences = re.split(r'(?<=[.!?])\s+', paragraph)
    result = []
    start = 0
    par = len(paragraph.split())

    if par < 750:
        result.append(paragraph)
        return result

    paragraph = paragraph.split()

    while start < par:
        if start + 750 > par:
            result.append(" ".join(paragraph[start:par]))
            return result
        result.append(" ".join(paragraph[start : start + 750]))  # 1st type
        start += 700

    result.append(" ".join(paragraph[start - par : par]))
    return result


def join_sentences(sentences, n):
    # Join n sentences at a time
    joined_sentences = [
        " ".join(sentences[i : i + n]) for i in range(0, len(sentences), n)
    ]
    return joined_sentences


def split_data(files_path):
    path = Path(files_path)
    clean_files = [f for f in path.glob("*.jsonl")]
    all_the_files = [d for d in path.iterdir()]

    for clean_file in clean_files:
        if Path(str(clean_file) + ".split") not in all_the_files:
            with open(str(clean_file) + ".split", "w") as output_file:
                for row, key in parse_jsonl(clean_file):
                    try:
                        row.get("url") and row.update(
                            {"url": row["url"].replace("\n", "")}
                        )
                        row["key"] = key

                        result = split_paragraph(row["text"])

                        for i, sen in enumerate(result):
                            sen = row["title"] + ":" + sen.replace("\n", "")
                            row["text"] = sen
                            output_file.write(
                                json.dumps(row, ensure_ascii=False) + "\n"
                            )

                    except:
                        print(f"skipping the line {list(row)}")
