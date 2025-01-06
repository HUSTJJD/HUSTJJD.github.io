import os
import re

EMPTY_MD = 'Empty.md'
REFERENCE_MD = 'Z Reference Link.md'
SCAN_DEPTH = 4
DEFAULT_TITLE = 'Misc'

def check_and_create_empty_md(directory):
    items = os.listdir(directory)
    for item in items:
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) and not '.' in item:
            sub_items = os.listdir(item_path)
            if len(sub_items) == 0:
                empty_md_path = os.path.join(item_path, EMPTY_MD)
                with open(empty_md_path, 'w') as f:
                    f.write('')
                print(f"create {empty_md_path}")
            else:
                check_and_create_empty_md(item_path)

def scan_directory_structure(root_dir):
    structure = []
    for root, dirs, files in os.walk(root_dir):
        relative_path = os.path.relpath(root, root_dir)
        if relative_path == '.':
            continue
        levels = relative_path.count(os.sep) + 1
        title = os.path.basename(root)
        if levels > 0 and levels < SCAN_DEPTH:
            structure.append((levels, title))
    return structure

def generate_new_md_content(old_headings : list, new_headings : list):
    new_content = []
    for level, title in new_headings:
        lack = True
        for old_level, old_title, old_content in old_headings:
            if old_level == level and old_title == title:   
                lack = False
        if lack:
            old_headings.append((level, title, ['\n']))
    for old_level, old_title, old_content in old_headings:
        new_content.append(f"{'#' * old_level} {old_title}\n")
        new_content.extend(old_content)
    return new_content

def parse_md_headings(md_content : list):
    if md_content[-1] != '\n':
        md_content.append('\n')
    custom_content = []
    headings = [(1, DEFAULT_TITLE, [])]
    def flush_buffer():
        headings[len(headings) - 1][2].extend(custom_content)
        custom_content.clear()
    for line in md_content:
        match = re.match(r'^(#+)\s+(.*)$', line)
        if match:
            flush_buffer()
            level = len(match.group(1))
            title = match.group(2)
            if level != 1 or title != DEFAULT_TITLE:
                headings.append((level, title, []))
        else:
            custom_content.append(line)
    flush_buffer()
    return headings

def check_and_update_reference(directory):
    items = os.listdir(directory)
    for item in items:
        item_path = os.path.join(directory, item)
        if '.git' in item:
            continue
        if os.path.isdir(item_path) and not '.' in item:
            reference_md_path = os.path.join(item_path, REFERENCE_MD)
            with open(reference_md_path, "r+", encoding="utf-8") as f:
                content = f.readlines()
                old_headings = parse_md_headings(content)
                new_structure = scan_directory_structure(item_path)
                new_content = generate_new_md_content(old_headings, new_structure)
                f.seek(0)
                f.writelines(new_content)
                print(f"update {reference_md_path}")

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.abspath(__file__))
    check_and_create_empty_md(root_dir)
    check_and_update_reference(root_dir)