def build_association_query(args: dict) -> str:
    query = "?"
    filter_params = ['subject', 'object', 'predicate', 'entity', 'category', 'between']

    query += f"q={args['q']}"

    if 'limit' in args and args['limit'] is not None:
        query += f"&rows={args['limit']}"

    if 'offset' in args and args['offset'] is not None:
        query += f"&start={args['offset']}"

    for i in filter_params:
        if args[i] == None:
            pass
        elif i == 'entity':
            query += f'&fq=(subject:"{i}" OR object:"{i}")'
        elif i == 'between':
            between = args[i].split(",")
            query += f'fq=(subject:"{between[0]}" AND object:"{between[1]}") OR (subject:"{between[1]}" AND object:"{between[0]}")'
        else:
            query += f'fq={i}:"{args[i]}"'

    return query
