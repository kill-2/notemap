import argparse
import analyzer
import os
from book import Book
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


class Figure:
    def __init__(self, path: str):
        self.root = self._root(path)
        with ThreadPoolExecutor() as executor:
            results = executor.map(self.process_notebook, self._find_books(path))
            for result in results:
                print(result)

    def process_notebook(self, path):
        book = Book(path)
        snippets = book.code_snippets()
        in_out = analyzer.parse(snippets)
        return (book.file_path, in_out)

    def _root(self, path):
        path = Path(path).resolve()
        if path.is_file():
            return str(path.parent)
        return str(path)

    def _find_books(self, path):
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
    fig = Figure(args.path)
    print(fig)


if __name__ == "__main__":
    main()
