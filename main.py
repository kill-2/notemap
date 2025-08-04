import argparse

from figure import Figure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to .ipynb file or dir containing notebooks")
    args = parser.parse_args()
    fig = Figure(args.path)
    print(fig)


if __name__ == "__main__":
    main()
