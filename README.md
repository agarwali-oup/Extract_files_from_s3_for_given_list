# S3 ISBN File Downloader

This utility reads a list of ISBNs from a file, searches for matching files in a specified S3 location (including all subfolders), and downloads them to a local output directory.

A matching file can be:

- ISBN.xml
- ISBN.pdf

For example, if the ISBN list contains:
9780123456789 9780987654321

the script will search for:
9780123456789.xml 9780123456789.pdf 9780987654321.xml 9780987654321.pdf
