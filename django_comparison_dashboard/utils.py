def prepare_query(query):
    """Unpacks filters given as list"""

    def parse_list(value):
        if value[0] == "[" and value[-1] == "]":
            return value[1:-1].split(",")
        return value

    filters = {k: parse_list(v) for k, v in query.items() if k != "groupby"}
    groupby = parse_list(query["groupby"]) if "groupby" in query else []
    return filters, groupby
