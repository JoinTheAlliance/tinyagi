from pathlib import Path
import tiktoken
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

default_text_model = os.getenv("DEFAULT_TEXT_MODEL")

encoding = tiktoken.encoding_for_model(default_text_model)

log_file_path = Path('logs/code.log')
log_file_path.parent.mkdir(parents=True, exist_ok=True)

def count_tokens(text):
    return len(encoding.encode(text))

total_lines = 0
total_tokens = 0

ignore_dirs = [
    ".chroma",
    ".git",
    ".vscode",
    "logs",
    "__pycache__",
    "skills_to_implement",
    "scripts"
]

ignore_files = [
    "requirements.txt",
    "README.md",
    ".env",
    "LICENSE"
]

with open(log_file_path, 'w') as log_file:
    # Write the file structure to the log
    log_file.write("Filetree:\n")
    for root, dirs, files in os.walk("."):
        if any(ignore_dir in root for ignore_dir in ignore_dirs):
            continue
        level = root.replace(".", "").count(os.sep)
        indent = ' ' * 4 * (level)
        log_file.write('{}{}/\n'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f in ignore_files:
                continue
            log_file.write('{}{}\n'.format(subindent, f))

    log_file.write("\nTEXT FILES:\n")
    # Find and write .txt files to the log
    for root, dirs, files in os.walk("."):
        if any(ignore_dir in root for ignore_dir in ignore_dirs):
            continue
        for file in files:
            if file in ignore_files:
                continue
            if file.endswith(".txt"):
                log_file.write(f"\nFile: {os.path.join(root, file)}\n")
                with open(os.path.join(root, file), 'r') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    for line in lines:
                        total_tokens += count_tokens(line)
                        log_file.write(line)

    log_file.write("\nSOURCE CODE:\n")
    # Find and write .py files to the log
    for root, dirs, files in os.walk("."):
        # if the path contains an ignored directory, skip it
        if any(ignore_dir in root for ignore_dir in ignore_dirs):
            continue
        for file in files:
            if file in ignore_files:
                continue
            if file.endswith(".py"):
                log_file.write(f"\nFile: {os.path.join(root, file)}\n")
                with open(os.path.join(root, file), 'r') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    for line in lines:
                        total_tokens += count_tokens(line)
                        log_file.write(line)

    log_file.write(f"\nSTATISTICS:\nTotal lines: {total_lines}\n")
    log_file.write(f"Total tokens: {total_tokens}\n")
