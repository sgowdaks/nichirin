import json
import re
import os
import csv
import sys
import yaml
import emoji
import random
import argparse
import xmltodict
import subprocess
from pathlib import Path

csv.field_size_limit(sys.maxsize)
FLAGS = re.MULTILINE | re.DOTALL

html_tags = [
    "a",
    "abbr",
    "acronym",
    "address",
    "applet",
    "area",
    "article",
    "aside",
    "audio",
    "b",
    "base",
    "basefont",
    "bdi",
    "bdo",
    "big",
    "blockquote",
    "body",
    "br",
    "button",
    "canvas",
    "caption",
    "center",
    "cite",
    "code",
    "col",
    "colgroup",
    "datalist",
    "dd",
    "del",
    "details",
    "dfn",
    "dialog",
    "dir",
    "div",
    "dl",
    "dt",
    "em",
    "embed",
    "fieldset",
    "figcaption",
    "figure",
    "font",
    "footer",
    "form",
    "frame",
    "frameset",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hr",
    "html",
    "i",
    "iframe",
    "img",
    "input",
    "ins",
    "kbd",
    "label",
    "legend",
    "li",
    "link",
    "main",
    "map",
    "mark",
    "meta",
    "meter",
    "nav",
    "noframes",
    "noscript",
    "object",
    "ol",
    "optgroup",
    "option",
    "output",
    "p",
    "param",
    "picture",
    "pre",
    "progress",
    "q",
    "rp",
    "rt",
    "ruby",
    "s",
    "samp",
    "script",
    "section",
    "select",
    "small",
    "source",
    "span",
    "strike",
    "strong",
    "style",
    "sub",
    "summary",
    "sup",
    "svg",
    "table",
    "tbody",
    "td",
    "template",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "time",
    "title",
    "tr",
    "track",
    "tt",
    "u",
    "ul",
    "var",
    "video",
    "wbr",
]


def re_sub(pattern, repl, text):
    return re.sub(pattern, repl, text, flags=FLAGS)


def parse_tsv(file):
    with open(file, "r") as data:
        # for line in f:
        for line in data:
            # print(line.split("\t"))
            if len(line.split("\t")) < 3 or len(line.split("\t")[1]) < 10:
                continue
            title, text, url = line.split("\t")
            yield title, text, url


# wiki_data
def parse_jsonl(file):
    with open(file, "r") as docs:
        for doc in docs:
            doc = json.loads(doc)
            if len(doc["text"].split()) < 10:
                continue
            title = process_text(doc["title"])
            text = process_text(doc["text"])
            url = doc["url"]
            yield title, text, url


def generate_examples(n=9, file="data/sample_questions.json"):
    # Read json file
    with open(file, "r") as f:
        data = json.load(f)
    all_questions = [item for sublist in data.values() for item in sublist]
    return random.sample(all_questions, n)


# xml parser
def xml_parser(input_file_path, output_file_path):
    pattern = r"<!--.*?-->"

    with open(input_file_path, "r") as file:
        with open(output_file_path, "w") as file2:
            for line in file:
                for tag in html_tags:
                    line = re.sub(f"<{tag} [^>]*>", "", line)
                    line = re.sub(f"<{tag}>", "", line)
                    line = re.sub(f"</{tag}>", "", line)

                line = line.replace("&nbsp;", "")
                line = line.replace("&", "")
                line = re.sub(pattern, "", line, flags=re.DOTALL)

                file2.write(line)


# xml to json converter
def xml_to_json(input_file_path=None, output_file_path=None):
    with open(input_file_path, "r") as file:
        xml_data = file.read()

    data_dict = xmltodict.parse(xml_data)
    json_data = json.dumps(data_dict)

    with open(output_file_path, "w") as file:
        file.write(json_data)


def preprocess_query(query, logger=None):
    clean_query = (
        query.replace('"', "")
        .replace("'", "")
        .replace("?", "")
        .replace("!", "")
        .replace(".", "")
        .replace(",", "")
    )
    if logger:
        logger.info(f"Cleaned query: {clean_query}")
    return clean_query


def postprocess_answer(answer, logger=None):
    if logger:
        logger.info(f"Raw string: {answer}")

    answer = answer.strip("[")
    answer = answer.strip("]")
    answer = answer.strip("'")
    answer = answer.strip('"')
    answer = answer.strip()

    if logger:
        logger.info(f"Post-processed string:\n{answer}")
    return answer


def hashtag(text):
    text = text.group()
    hashtag_body = text[1:]
    if hashtag_body.isupper():
        result = "<hashtag> {} <allcaps>".format(hashtag_body.lower())
    else:
        result = " ".join(
            ["<hashtag>"] + re.split(r"(?=[A-Z])", hashtag_body, flags=FLAGS)
        )
    return result


def clean_data(text):
    emoji_eyes = r"[8:=;]"
    emoji_nose = r"['`\-]?"

    # Takes care of html tags
    clean = re.compile("<.*?>")
    text = re.sub(clean, "", text)
    text = re_sub(r"https?:\/\/\S+\b|www\.(\w+\.)+\S*", "<url>", text)
    text = re_sub(r"@\w+", "<user>", text)
    text = re_sub(
        r"{}{}[)dD]+|[)dD]+{}{}".format(emoji_eyes, emoji_nose, emoji_nose, emoji_eyes),
        "<smile>",
        text,
    )
    text = re_sub(r"{}{}p+".format(emoji_eyes, emoji_nose), "<lolface>", text)
    text = re_sub(
        r"{}{}\(+|\)+{}{}".format(emoji_eyes, emoji_nose, emoji_nose, emoji_eyes),
        "<sadface>",
        text,
    )
    text = re_sub(r"{}{}[\/|l*]".format(emoji_eyes, emoji_nose), "<neutralface>", text)
    text = re_sub(r"/", " / ", text)
    text = re_sub(r"<3", "<heart>", text)
    text = re_sub(r"#\w+", hashtag, text)
    text = re_sub(r"([!?.]){2,}", r"\1 <repeat>", text)
    text = re_sub(r"\b(\S*?)(.)\2{2,}\b", r"\1\2 <elong>", text)
    text = re_sub(r"([a-zA-Z<>()])([?!.:;,])", r"\1 \2", text)
    text = re_sub(r"\(([a-zA-Z<>]+)\)", r"( \1 )", text)
    text = re_sub(r"  ", r" ", text)
    return text


def process_text(text):
    text = emoji.demojize(text)
    text = clean_data(text)
    text = text.replace("\n", "").replace("\t", "").replace("\r", "")
    text = text.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
    return text


def file_to_clean(args):
    path = Path(args["input"])
    type_ = args["file_type"]

    if not os.path.exists(args["json_file_path"] + ".tsv_"):
        if type_ == ".json":
            json_file_path = args["json_file_path"]
            rows = parse_jsonl(json_file_path)
            with open(json_file_path + ".tsv_", "w") as out:
                tsv_writer = csv.writer(out, delimiter="\t")
                for title, txt, url in rows:
                    tsv_writer.writerow([title, txt, url])

            if not os.path.isdir(path):
                bash_command = (
                    "split -a 4 -d --additional-suffix=.tsv -l 1000000 "
                    + json_file_path
                    + ".tsv_ "
                    + path
                    + "/part-"
                )
                subprocess.run(bash_command, shell=True, executable="/bin/bash")


def load_yaml(path):
    with open(path, "r") as stream:
        return yaml.safe_load(stream)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        help="Give the input file path",
    )
    parser.add_argument(
        "--file_type",
        type=str,
        default=".json",
        help="Give the file type either .tsv or .json",
    )
    parser.add_argument(
        "--json_file_path",
        type=str,
        help="Give the json file path if it is .json",
    )
    args = parser.parse_args()
    return vars(args)


if __name__ == "__main__":
    args = parse_args()
    file_to_clean(args)
    # xml_to_json()
