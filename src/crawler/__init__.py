from crawler.logger import configure_logging
from crawler.start import start_as_cli


def main() -> None:
    configure_logging()
    start_as_cli()


if __name__ == "__main__":
    main()
