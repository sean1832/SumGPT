def extract_values(dicts, key, parent_key=None):
    """
    Extracts values from a list of dictionaries based on a specified key.
    If the key is nested, a parent key can be specified.

    :param dicts: List of dictionaries to query
    :param key: The key for which values are to be extracted
    :param parent_key: Optional parent key if the key is nested within another dictionary
    :return: List of values corresponding to the specified key
    """
    values = []
    for dict in dicts:
        if parent_key:
            # Access the nested dictionary and then the key if parent_key is specified
            if parent_key in dict and key in dict[parent_key]:
                values.append(dict[parent_key][key])
        else:
            # Access the key directly if there is no parent_key
            if key in dict:
                values.append(dict[key])
    return values

def extract_dict_index(dicts, key, value):
    """
    Extracts the index of a dictionary in a list of dictionaries based on a specified key-value pair.

    :param dicts: List of dictionaries to query
    :param key: The key to search for
    :param value: The value to search for
    :return: Index of the dictionary containing the specified key-value pair
    """
    for i, dict in enumerate(dicts):
        if key in dict and dict[key] == value:
            return i
    return None