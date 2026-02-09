# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from alogram_payrisk._generated.payrisk_v1.api.payrisk_api import PayriskApi

else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from alogram_payrisk._generated.payrisk_v1.api.payrisk_api import PayriskApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
