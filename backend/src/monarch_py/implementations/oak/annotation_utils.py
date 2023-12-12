"""
Utility functions for annotating text with OAK.
"""

import re
import json

def get_word_length(text, start):
    word = ""
    index = start
    while index < len(text) and text[index].isalpha():
        word += text[index]
        index += 1
    return len(word)


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


def concatenate_ngram_entities(lst):
    merged_list = []
    start, end, text = lst[0]
    for element in lst[1:]:
        if element[0] <= end:  # Check if range overlaps
            end = max(end, element[1])  # Merge the range
            text += "|" + element[2]  # Concatenate the texts
        else:
            merged_list.append([start, end, text])  # Add the merged element to the result
            start, end, text = element  # Move to the next element
    merged_list.append([start, end, text])  # Add the last merged element
    return merged_list


def replace_entities(text, entities):
    replaced_text = text
    # Sort the entities in descending order of start character indices
    entities = sorted(entities, key=lambda x: x[0], reverse=True)
    for entity in entities:
        start, end = entity[0] - 1, entity[1]
        #entity_value = entity[2]
        entity_value = f'<span class=\"sciCrunchAnnotation\" data-sciGraph=\"{entity[2]}\">{text[start:end]}</span>'
        replaced_text = replaced_text[:start] + entity_value + replaced_text[end:]
    return replaced_text

'''
### with start and end format ###
def convert_to_json(text, entities):
    json_data = {
        "content": text,
        "spans": []
    }
    for item in entities:
        start = item[0]
        end = item[1]
        entity = item[2].split(',')[0].lower()
        token_id = item[2].split(',')[1]

        json_item = {
            "start": start,
            "end": end,
            "text": entity,
            "token": [
                {
                    "id": token_id,
                    "category": [],
                    "terms": [entity.capitalize()]
                }
            ]
        }

        json_data["spans"].append(json_item)

    return json.dumps(json_data, indent=4)
'''


def convert_to_json(text):
    result = []
    span_pattern = re.compile(r'<span class="sciCrunchAnnotation" data-sciGraph="([^"]+)">([^<]+)</span>')

    start_index = 0

    for match in span_pattern.finditer(text):
        span_data = match.group(1)
        span_text = match.group(2)

        if start_index < match.start():
            non_span_text = text[start_index:match.start()]
            result.append({"text": non_span_text})

        tokens = []
        for token_data in span_data.split('|'):
            token_parts = token_data.split(',')
            tokens.append({"id": token_parts[1], "name": token_parts[0]})

        result.append({"text": span_text, "tokens": tokens})
        start_index = match.end()

    if start_index < len(text):
        non_span_text = text[start_index:]
        result.append({"text": non_span_text})

    #return json.dumps(result, indent=2)
    #return json.dumps(result)
    api_response = json.dumps(result)
    # Replace "\n" with actual line breaks
    api_response = api_response.replace("\\n", "\n")

    # Load the JSON
    data = json.loads(api_response)

    return data