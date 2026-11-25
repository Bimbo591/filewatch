# FileWatch: File Integrity Monitor

A Python tool that calculates SHA-256 hashes for files, so any change to a file can be detected.

## Legal and Ethical Note

Scanning or attacking systems you do not own or have written permission to test is illegal. This tool only monitors my own test folder.

## How It Works

A cryptographic hash turns a file's contents into a fixed-length fingerprint. The same content always gives the same hash. Changing even one character gives a completely different hash. This is the foundation of file integrity checking.

## Setup

1. Install Python 3.
2. Create a folder called `test_folder` next to `filewatch.py` and add a few small text files.

## Usage

    python filewatch.py

The script prints the SHA-256 hash of every file in `test_folder`. Files are read in 4096-byte chunks, so it also works for large files. Missing or unreadable files are reported without crashing the script.

## Demo

Changing one character in `a.txt` changes its hash completely, while the other files stay the same. See the screenshots in this repo.
## Week 2: Baseline and Change Detection

FileWatch can save a baseline of file hashes and later check whether files were added, modified or deleted.

### Usage

Create a baseline of the folder:
python filewatch.py baseline test_folder

Check the folder against the baseline:
python filewatch.py check test_folder

### Run the tests
python -m pytest

### How it works
- The baseline is saved in baseline.json as relative file paths and SHA-256 hashes.
- Subfolders are included.
- Added and deleted files are found by comparing the file paths.
- Modified files are found by comparing the hashes.