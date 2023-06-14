import sys

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

CURRENT_PROTOCOL_VERSION: Final = 2.0
