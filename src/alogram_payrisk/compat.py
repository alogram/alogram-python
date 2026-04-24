# Copyright (c) 2025 Alogram Inc.
# Compatibility utility to bootstrap the SDK namespace.

import sys

# 🚀 Dynamic namespace registration
try:
    from ._generated import payrisk_v1

    # 🛡️ SECURITY & STABILITY: Register payrisk_v1 in the global module path.
    # This ensures that machine-generated models and pydantic validators can resolve
    # absolute imports (e.g. from payrisk_v1.models...) even when vendored deep in the SDK.
    if "payrisk_v1" not in sys.modules:
        sys.modules["payrisk_v1"] = payrisk_v1
except ImportError:
    # Fallback for local development if _generated is not yet built
    pass
