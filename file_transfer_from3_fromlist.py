import os
import csv
from pathlib import Path

import boto3


def read_isbns(isbn_file):
    """
    Reads ISBNs from a txt or csv file.
    One ISBN per line or first column of CSV.
    """
    isbns = set()

    if isbn_file.lower().endswith(".csv"):
        with open(isbn_file, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip():
                    isbns.add(row[0].strip())
    else:
        with open(isbn_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    isbns.add(line.strip())

    return isbns


def list_s3_objects(bucket, prefix):
    """
    Recursively list all files under prefix.
    """
    s3 = boto3.client("s3")

    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            yield obj["Key"]


def find_matching_files(bucket, prefix, isbns):
    """
    Look for ISBN.xml or ISBN.pdf
    """
    matches = {}

    for key in list_s3_objects(bucket, prefix):

        filename = os.path.basename(key)

        if "." not in filename:
            continue

        stem, ext = os.path.splitext(filename)

        ext = ext.lower()

        if ext not in [".xml", ".pdf"]:
            continue

        if stem in isbns:
            matches.setdefault(stem, []).append(key)

    return matches


def download_files(bucket, matches, output_dir):
    """
    Download matching files.
    """
    s3 = boto3.client("s3")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    total_downloaded = 0

    for isbn, keys in matches.items():

        for key in keys:

            filename = os.path.basename(key)
            local_path = os.path.join(output_dir, filename)

            print(f"Downloading s3://{bucket}/{key}")
            s3.download_file(bucket, key, local_path)

            total_downloaded += 1

    print(f"\nDownloaded {total_downloaded} files")


def main():

    # INPUTS
    bucket = "ol-research-data-prod"
    prefix = "German/"  # search recursively under this folder

    isbn_file = r"C:\Users\agarwais\Downloads\JiraTasks\Transfer_files_froms3_sample\isbnfile.csv"
    output_dir = r"C:\Users\agarwais\Downloads\JiraTasks\Transfer_files_froms3_sample\German"

    isbns = read_isbns(isbn_file)

    print(f"Loaded {len(isbns)} ISBNs")

    matches = find_matching_files(bucket, prefix, isbns)

    found = len(matches)
    missing = len(isbns) - found

    print(f"Found: {found}")
    print(f"Missing: {missing}")

    download_files(bucket, matches, output_dir)

    if missing:
        missing_isbns = sorted(isbns - set(matches.keys()))

        with open(
            os.path.join(output_dir, "missing_isbns.txt"),
            "w",
            encoding="utf-8"
        ) as f:
            f.write("\n".join(missing_isbns))

        print(
            f"Missing ISBN list written to "
            f"{os.path.join(output_dir, 'missing_isbns.txt')}"
        )


if __name__ == "__main__":
    main()