from constants.parts import PARTS

def label(part: str) -> str:
    if part not in PARTS or PARTS[part] is None or len(PARTS[part]) < 3:
        raise Exception(f"invalid part found : {part}")
    return PARTS[part][0]


def category(part: str) -> str:
    if part not in PARTS or PARTS[part] is None or len(PARTS[part]) < 3:
        raise Exception(f"invalid part found : {part}")
    return PARTS[part][1]


def prompt_list() -> str:
    groups = {}
    for key, (name, _, place) in PARTS.items():
        groups.setdefault(place, []).append(f"{key} ({name})")
    return "\n".join(f"  {place}: " + ", ".join(items) for place, items in groups.items())
