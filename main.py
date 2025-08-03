import argparse
import analyzer
from book import Book
import os
from pathlib import Path


class Figure:
    def __init__(self, books: list[Book]):
        for b in books:
            self.process_notebook(b)

    def process_notebook(self, book):
        snippets = book.code_snippets()
        in_out = analyzer.parse(snippets)
        print(f"{book.file_path}: {in_out}")


def book_paths(path):
    path = Path(path)
    if path.is_file() and path.suffix == ".ipynb":
        yield str(path)
    elif path.is_dir():
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".ipynb"):
                    notebook_path = os.path.join(root, file)
                    yield notebook_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to .ipynb file or dir containing notebooks")
    args = parser.parse_args()

    fig = Figure([Book(path) for path in book_paths(args.path)])
    print(fig)


if __name__ == "__main__":
    main()
