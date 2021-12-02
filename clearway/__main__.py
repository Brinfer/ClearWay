"""Module allowing for `python -m clearway ...`."""

import sys

sys.path.append(".")

from clearway.cli import main  # noqa: E402 module level import not at top of file

sys.exit(main())
