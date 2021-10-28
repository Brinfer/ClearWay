import logging
from logging.handlers import RotatingFileHandler
import sys

def __configureLogger() -> None:
    """Configure the app's logger

    The log file is stored in `ClearWay.log` and every time the program
    restart, the file is cleared.
    The minimum level of the lof is `INFO`.
    Is format is:
        `Date Time FileName:FunctionName Level >> Message`
        example:
            `2021-10-28 18:20:19,018 foo.py:10 [INFO] >> Foo`
    """
    logging.basicConfig(
        level=logging.DEBUG,  # TODO On Realease change to INFO
        format="%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s",
        handlers=[
            logging.FileHandler("ClearWay.log"),
            logging.StreamHandler(sys.stdout)  # TODO On Realease remove
        ],
    )


def main():
    __configureLogger()

if __name__ == "__main__":
    main()
