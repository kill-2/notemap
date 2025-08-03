import argparse
import analyzer
from book import Book
import os
from pathlib import Path


def process_notebook(path):
    book = Book(path)
    snippets = book.code_snippets()
    result = analyzer.parse(snippets)
    print(f"{path}: {result}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(        "path", help="Path to .ipynb file or dir containing notebooks"    )
    args = parser.parse_args()

    path = Path(args.path)
    if path.is_file() and path.suffix == ".ipynb":
        process_notebook(str(path))
    elif path.is_dir():
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.endswith(".ipynb"):
                    notebook_path = os.path.join(root, file)
                    process_notebook(notebook_path)
    else:
        print(f"Error: {args.path} is not a valid .ipynb file or directory")


if __name__ == "__main__":
    main()
