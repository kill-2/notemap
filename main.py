import argparse
import analyzer
from book import Book


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", help="Path to .ipynb notebook file")
    args = parser.parse_args()

    book = Book(args.notebook)
    snippets = book.code_snippets()
    result = analyzer.parse(snippets)
    print(result)


if __name__ == "__main__":
    main()
