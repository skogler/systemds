# This script downloads and prepares the 20 newsgroups dataset.
# It also samples a specified subset of the dataset in order to keep the repository size small.
#
# It is provided for reproducibility and for running larger samples.
# A small prepared and sampled dataset is already provided.

import argparse
import csv
import json
import tarfile
from collections import defaultdict
from contextlib import ExitStack
from email.message import Message
from io import BytesIO
from email.parser import Parser
from math import ceil
from pathlib import Path
from random import sample
from typing import List, Dict, Tuple

import requests

SOURCE_URL = "http://qwone.com/~jason/20Newsgroups/20news-bydate.tar.gz"


def parse_message_body(message_str: str) -> str:
    """
    Returns the body of the given message, removing all headers and email stuff.
    :param message_str: The raw message.
    :return: The body of the message as string.
    """
    message: Message = Parser().parsestr(message_str)
    if message.is_multipart():
        return message.get_payload(0)
    else:
        return message.get_payload()


def extract_set_and_class(file_path: str) -> Tuple[str, str]:
    toplevel, subfolder, _ = file_path.split('/')
    return toplevel[len('20news-bydate-'):], subfolder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sample-percentage', default=20, type=int)
    parser.add_argument('output_directory', type=str)

    args = parser.parse_args()
    sample_percentage = args.sample_percentage
    output_dir = Path(args.output_directory).absolute()
    if not output_dir.is_dir():
        output_dir.mkdir(exist_ok=True, parents=True)

    set_to_class_to_entries: Dict[str, Dict[str, List[tarfile.TarInfo]]] = defaultdict(lambda: defaultdict(list))
    with requests.get(SOURCE_URL) as req, \
            tarfile.open(fileobj=BytesIO(req.content), mode='r:gz') as zf:
        for entry in zf:
            if entry.isdir():
                continue
            set_name, class_name = extract_set_and_class(entry.name)
            set_to_class_to_entries[set_name][class_name].append(entry)

        with ExitStack() as stack:
            set_csv_writers = {}
            set_file_paths = {}
            set_size = {}
            for set_name in set_to_class_to_entries.keys():
                set_size[set_name] = 0
                set_file_path = output_dir / f'20news_sample_{round(sample_percentage)}perc_{set_name}.csv'
                set_file_paths[set_name] = set_file_path
                set_file = set_file_path.open('w', newline='')
                stack.enter_context(set_file)
                set_csv_writer = csv.writer(set_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                set_csv_writer.writerow(['class', 'id', 'text'])
                set_csv_writers[set_name] = set_csv_writer

            for set_name, news_classes in set_to_class_to_entries.items():
                for class_name, message_entries in news_classes.items():
                    n = len(message_entries)
                    k = ceil(n * (sample_percentage / 100))
                    print(set_name, class_name, n, k)
                    for entry in sample(message_entries, k):
                        message = parse_message_body(zf.extractfile(entry).read().decode('latin-1'))
                        set_csv_writers[set_name].writerow([class_name, entry.name, ' '.join(message.splitlines())])
                        set_size[set_name] += 1

            for set_name, set_file_path in set_file_paths.items():
                meta_file_path = set_file_path.with_suffix('.csv.mtd')
                with meta_file_path.open('w') as meta_file:
                    meta_data = {
                        "data_type": "frame",
                        "format": "csv",
                        "header": True,
                        "schema": "STRING,STRING,STRING",
                        "cols": 3,
                        "rows": set_size[set_name],
                    }
                    json.dump(meta_data, meta_file, indent=4)


if __name__ == '__main__':
    main()
