import logging
import pilotLED
import sys
import time


def __configureLogger() -> None:
    """Configure the app's logger

    The log file is stored in `ClearWay.log` and every time the program
    restart, the file is cleared.
    Is format is:
        `Date Time FileName:FunctionName Level >> Message`
        example:
            `2021-10-28 18:20:19,018 foo.py:10 [INFO] >> Foo`

    There is two mode:
        - Release mode, where the log are only print in the file, the minimum level of the lof is `INFO`.
        - Debug mode, where the log are print in the file and displayed in the console, The minimum level of the lof is `DEBUG`.
    """

    if __debug__:
    logging.basicConfig(
            level=logging.DEBUG,
        format="%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s",
        handlers=[
            logging.FileHandler("ClearWay.log"),
                logging.StreamHandler(sys.stdout)
        ],
    )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s",
            filename="ClearWay.log"
        )


def main():
    __configureLogger()

if __name__ == "__main__":
    main()
