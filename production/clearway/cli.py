import logging
import sys

from gpio import stateMachinePanel

# TODO Macro for GPIO or not

__LOG_FORMAT = "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s"


def __configure_logging() -> None:
    """Configure the app's logger.

    The log file is stored in `ClearWay.log` and every time the program
    restart, the file is cleared.
    Is format is:
        `Date Time FileName:FunctionName Level >> Message`
        example:
            `2021-10-28 18:20:19,018 foo.py:10 [INFO] >> Foo`

    There is two mode:
        - Release mode, where the log are only print in the file, the minimum level of the lof is `INFO`.
        - Debug mode, where the log are print in the file and displayed in the console, The minimum level of the
        lof is `DEBUG`.
    """
    # TODO Update the README
    if __debug__:
        logging.basicConfig(
            level=logging.DEBUG,
            format=__LOG_FORMAT,
            handlers=[
                logging.FileHandler("ClearWay.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format=__LOG_FORMAT,
            filename="ClearWay.log",
         )


def main():
    __configure_logging()

    stateMachinePanel.new(5)
    stateMachinePanel.start(5)
    stateMachinePanel.signal(5)

    stateMachinePanel.end_signal(5)
    stateMachinePanel.stop(5)
    stateMachinePanel.free(5)


if __name__ == "__main__":
    main()
