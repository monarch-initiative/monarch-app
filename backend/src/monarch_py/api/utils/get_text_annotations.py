from monarch_py.api.config import oak
import re

phenio_adapter = oak().phenio_adapter


def annotate_text(text):
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    result = ""
    for sentence in sentences:
        entities = []
        for ann in phenio_adapter.annotate_text(sentence):  # type: ignore
            if len(ann.object_label) >= 4:
                element = [ann.subject_start, ann.subject_end, str(ann.object_label) + "," + str(ann.object_id)]
                if (get_word_length(sentence, ann.subject_start - 1) - len(ann.object_label)) < 2:
                    entities.append(element)
        try:
            # Trying to access an element that doesn't exist in the list
            entities.sort()
            entities = concatenate_same_entities(entities)
            entities = concatenate_ngram_entities(entities)
            replaced_text = replace_entities(sentence, entities)
            result += replaced_text + " "
        except IndexError as error:
            # Handling the list index out of range error
            result += sentence + " "
            print("Error occurred:", error)
    return result


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
        # entity_value = entity[2]
        entity_value = f'<span class="sciCrunchAnnotation" data-sciGraph="{entity[2]}">{text[start:end]}</span>'
        replaced_text = replaced_text[:start] + entity_value + replaced_text[end:]
    return replaced_text
