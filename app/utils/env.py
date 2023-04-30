import os


def env(var_name: str) -> str | bool:
    value = os.getenv(var_name)
    match value:
        case "yes" | "true" | "1":
            return True

        case "no" | "false" | "0":
            return False

        case _:
            return value
