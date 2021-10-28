import logging
from logging.handlers import RotatingFileHandler
import time
# import pilotLED


def __configureLogger() -> None:
    """Configure the app's logger

    The log file is stored in `ClearWay.log` and its maximum size is 5MB, every time the program
    restart, the file is cleared.
    The minimum level of the lof is `INFO`.
    Is format is:
        `Date Time Level FunctionName LineNumber Message`
        example:
            `2021-10-28 16:42:01,393 INFO foo(23) Test Logger`
    """

    logFormatter = logging.Formatter("%(asctime)s %(levelname)s %(funcName)s-%(lineno)d : %(message)s")
    appLog = logging.getLogger('root')
    appLog.setLevel(logging.INFO)  # TODO On Realease change to INFO


    # TODO On Realease remove
    # create console handler and set level to info
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(logFormatter)
    appLog.addHandler(consoleHandler)

    # create file handler and set level to info
    fileHandler = RotatingFileHandler(mode='w', maxBytes=5*1024*1024, encoding="utf8", filename="ClearWay.log")
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.DEBUG)  # TODO On Realease change to INFO
    appLog.addHandler(fileHandler)


def main():
    __configureLogger()

if __name__ == "__main__":
    main()
