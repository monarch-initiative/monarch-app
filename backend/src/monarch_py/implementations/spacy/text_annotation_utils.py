"""
Utility functions for annotating text with SPACY.
"""

import re
import json
import requests


def search_monarch_api(query):
    try:
        url = f"https://127.0.0.1:8000/v3/api/search?q={query}&limit=20&offset=0" #alternate DEV or PROD/v3 urls
        response = requests.get(url)
        response.raise_for_status()

        return response.json()
    except requests.RequestException as e:
        print(f"Error in Monarch Initiative API request: {e}")
        raise
    except Exception as e:
        print(f"Error processing Monarch Initiative API response: {e}")
        raise


def get_monarch_equivalent(doc, entities):
    for entity in doc.ents:
        res_j = search_monarch_api(entity)
        for t in range(len(res_j['items'])):
            item_name = str.lower(res_j['items'][t]['name'])
            entity_lower = str.lower(str(entity))

            conditions = [
                item_name == entity_lower + " (hpo)",
                item_name == entity_lower,
                item_name == entity_lower + " (mpo)"
            ]

            if any(conditions):
                element = [entity.start_char, entity.end_char, res_j['items'][t]['name'] + "," + res_j['items'][t]['id']]
                entities.append(element)
    return entities


def get_monarch_top_three(doc, entities):
    for entity in doc.ents:
        for sublist in entities:
            if str(entity).lower() not in sublist[2].lower():
                res_j = search_monarch_api(entity)
                if len(res_j['items']) > 3:
                    for t in range(3):
                        element = [entity.start_char, entity.end_char,
                                   res_j['items'][t]['name'] + "," + res_j['items'][t]['id']]
                        entities.append(element)
                break
    return entities


def concatenate_same_entities(lst):
    result = {}
    for elem in lst:
        key = (elem[0], elem[1])
        if key in result:
            result[key] += "|" + elem[2]
        else:
            result[key] = elem[2]
    concatenated_list = [[key[0], key[1], value] for key, value in result.items()]
    return concatenated_list


def replace_entities(text, entities):
    replaced_text = text
    # Sort the entities in descending order of start character indices
    entities = sorted(entities, key=lambda x: x[0], reverse=True)
    for entity in entities:
        # start, end = entity[0] - 1, entity[1] #for OAK
        start, end = entity[0], entity[1]
        # entity_value = entity[2]
        entity_value = f'<span class="sciCrunchAnnotation" data-sciGraph="{entity[2]}">{text[start:end]}</span>'
        replaced_text = replaced_text[:start] + entity_value + replaced_text[end:]
    return replaced_text


def convert_to_json(text):
    result = []
    span_pattern = re.compile(r'<span class="sciCrunchAnnotation" data-sciGraph="([^"]+)">([^<]+)</span>')

    start_index = 0
    for match in span_pattern.finditer(text):
        span_data = match.group(1)
        span_text = match.group(2)

        if start_index < match.start():
            non_span_text = text[start_index: match.start()]
            result.append({"text": non_span_text})

        tokens = []
        for token_data in span_data.split("|"):
            token_parts = token_data.split(",")
            tokens.append({"id": token_parts[1], "name": token_parts[0]})

        result.append({"text": span_text, "tokens": tokens})
        start_index = match.end()

    if start_index < len(text):
        non_span_text = text[start_index:]
        result.append({"text": non_span_text})

    result.append({"text": "\n"})

    api_response = json.dumps(result)
    # Load the JSON
    data = json.loads(api_response)

    return data
