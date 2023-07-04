from collections import defaultdict
from pathlib import Path
import tiktoken
from dotenv import load_dotenv
import os
import re

load_dotenv()  # take environment variables from .env.

default_text_model = os.getenv("DEFAULT_TEXT_MODEL")
if default_text_model is None or default_text_model == "":
    default_text_model = "gpt-3.5-turbo-0613"

encoding = tiktoken.encoding_for_model(default_text_model)

log_file_path = Path('logs/code.log')
code_only_log_file_path = Path('logs/code_only.log')
log_file_path.parent.mkdir(parents=True, exist_ok=True)

code_core_log_file_path = Path('logs/code_core.log')
code_only_core_log_file_path = Path('logs/code_only_core.log')
code_core_log_file_path.parent.mkdir(parents=True, exist_ok=True)

code_actions_log_file_path = Path('logs/code_actions.log')
code_only_actions_log_file_path = Path('logs/code_only_actions.log')
code_actions_log_file_path.parent.mkdir(parents=True, exist_ok=True)

code_connectors_log_file_path = Path('logs/code_connectors.log')
code_only_connectors_log_file_path = Path('logs/code_only_connectors.log')
code_connectors_log_file_path.parent.mkdir(parents=True, exist_ok=True)

def count_tokens(text):
    return len(encoding.encode(text))

total_lines = 0
total_tokens = 0

total_code_only_lines = 0
total_code_only_tokens = 0

per_dir_stats = defaultdict(lambda: defaultdict(int))  # {dir_path: {"lines": int, "tokens": int}}
per_file_stats = defaultdict(lambda: defaultdict(int))  # {file_path: {"lines": int, "tokens": int}}

ignore_dirs = [
    ".chroma",
    ".git",
    ".vscode",
    "logs",
    "__pycache__",
    "actions_to_implement",
    "scripts"
]

ignore_files = [
    "requirements.txt",
    "README.md",
    ".env",
    "LICENSE"
]

def print_and_log(text, log_file):
    print(text.strip())
    log_file.write(text)

def strip_comments_and_literals(line):
    # Remove comments
    line = re.sub(r'#.*', '', line)
    # Remove action comments
    line = re.sub(r'""".*?"""', '', line, flags=re.DOTALL)
    return line

def process_file(file_path, log_file, code_only_log_file, code_type, root):
    global total_lines, total_tokens, total_code_only_lines, total_code_only_tokens

    log_file.write(f"\nFile: {file_path}\n")
    with open(file_path, 'r') as f:
        lines = f.readlines()
        total_lines += len(lines)
        per_file_stats[file_path]["lines"] = len(lines)
        per_dir_stats[root]["lines"] += len(lines)
        for line in lines:
            tokens = count_tokens(line)
            total_tokens += tokens
            per_file_stats[file_path]["tokens"] += tokens
            per_dir_stats[root]["tokens"] += tokens
            log_file.write(line)
            code_only_line = strip_comments_and_literals(line)
            if code_only_line.strip():  # Skip if the line is now blank
                total_code_only_lines += 1
                total_code_only_tokens += count_tokens(code_only_line)
                per_file_stats[file_path]["code_only_lines"] += 1
                per_file_stats[file_path]["code_only_tokens"] += count_tokens(code_only_line)
                per_dir_stats[root]["code_only_lines"] += 1
                per_dir_stats[root]["code_only_tokens"] += count_tokens(code_only_line)
                code_only_log_file.write(code_only_line)

                # Check if line is a test block
                if code_only_line.strip().startswith("if __name__ == '__main__'"):
                    break  # Skip the remaining lines in the file

with open(log_file_path, 'w') as log_file, \
        open(code_only_log_file_path, 'w') as code_only_log_file, \
        open(code_core_log_file_path, 'w') as code_core_log_file, \
        open(code_only_core_log_file_path, 'w') as code_only_core_log_file, \
        open(code_actions_log_file_path, 'w') as code_actions_log_file, \
        open(code_only_actions_log_file_path, 'w') as code_only_actions_log_file, \
        open(code_connectors_log_file_path, 'w') as code_connectors_log_file, \
        open(code_only_connectors_log_file_path, 'w') as code_only_connectors_log_file:
    
    log_file.write("Filetree:\n")
    for root, dirs, files in os.walk("."):
        if any(ignore_dir in root for ignore_dir in ignore_dirs):
            continue
        level = root.replace(".", "").count(os.sep)
        indent = ' ' * 4 * (level)
        print_and_log('{}{}/\n'.format(indent, os.path.basename(root)), log_file)
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f in ignore_files:
                continue
            print_and_log('{}{}\n'.format(subindent, f), log_file)

    log_file.write("\nTEXT FILES:\n")
    for root, dirs, files in os.walk("."):
        if any(ignore_dir in root for ignore_dir in ignore_dirs):
            continue
        for file in files:
            if file in ignore_files:
                continue
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                process_file(file_path, log_file, code_only_log_file, "text")

    log_file.write("\nSOURCE CODE:\n")
    for root, dirs, files in os.walk("."):
        if any(ignore_dir in root for ignore_dir in ignore_dirs):
            continue
        for file in files:
            if file in ignore_files:
                continue
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if "core" in root:
                    process_file(file_path, code_core_log_file, code_only_core_log_file, "code", root)
                elif "actions" in root:
                    process_file(file_path, code_actions_log_file, code_only_actions_log_file, "code", root)
                elif "connectors" in root:
                    process_file(file_path, code_connectors_log_file, code_only_connectors_log_file, "code", root)
                else:
                    process_file(file_path, log_file, code_only_log_file, "code", root)

    print_and_log(f"\nSTATISTICS:\nTotal lines: {total_lines}\n", log_file)
    print_and_log(f"Total tokens: {total_tokens}\n", log_file)
    print_and_log(f"Total code only lines: {total_code_only_lines}\n", log_file)
    print_and_log(f"Total code only tokens: {total_code_only_tokens}\n", log_file)

    log_file.write("\nPER-FILE STATISTICS:\n")
    for file_path, stats in per_file_stats.items():
        print_and_log(f"\nFile: {file_path}\n", log_file)
        print_and_log(f"Lines: {stats['lines']}\n", log_file)
        print_and_log(f"Tokens: {stats['tokens']}\n", log_file)
        print_and_log(f"Code only lines: {stats['code_only_lines']}\n", log_file)
        print_and_log(f"Code only tokens: {stats['code_only_tokens']}\n", log_file)

    log_file.write("\nPER-DIRECTORY STATISTICS:\n")
    for dir_path, stats in per_dir_stats.items():
        print_and_log(f"\nDirectory: {dir_path}\n", log_file)
        print_and_log(f"Lines: {stats['lines']}\n", log_file)
        print_and_log(f"Tokens: {stats['tokens']}\n", log_file)
        print_and_log(f"Code only lines: {stats['code_only_lines']}\n", log_file)
        print_and_log(f"Code only tokens: {stats['code_only_tokens']}\n", log_file)
