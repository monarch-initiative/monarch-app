def build_association_query(args: dict) -> str:
    query = "?"
    query_params = ['q', 'offset', 'limit']
    filter_params = ['subject', 'object', 'predicate', 'entity', 'category', 'between']
    for i in query_params:
        if args[i] == None:
            pass
        elif i in query_params:
            query += f'{i}={args[i]}&'
    query += "fq="
    for i in filter_params:
        if args[i] == None:
            pass
        elif i == 'entity':
            query += f'subject:"{i}" OR object:"{i}"&'
        elif i == 'between':
            between = args[i].split(",")
            query += f'(subject:"{between[0]}" AND object:"{between[1]}") OR (subject:"{between[1]}" AND object:"{between[0]}")&'
        else:
            query += f'{i}:"{args[i]}"&'
    return query