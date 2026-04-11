# Alias the vendored package so internal machine-generated lookups work
import sys

from . import payrisk_v1

sys.modules["payrisk_v1"] = payrisk_v1
