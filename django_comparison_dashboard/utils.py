def prepare_filters(filters):
    """Unpacks filters given as list"""

    def parse_list(value):
        if value[0] == "[" and value[-1] == "]":
            return value[1:-1].split(",")
        return value

    return {k: parse_list(v) for k, v in filters.items()}
