import ast
from utils.logger import logger


""" def create_anki_tags(data, tag_template, values):
    for entry in data:

    for hanja_entry, input_entry in zip(hanja_data, input_data):
        ref_idx = input_entry["reference_idx"]
        h_str = f"{{'漢字': ['{hanja_entry['rank']}', {{'暗記博士1': '{ref_idx}'}}]}}"
        result = " ".join(create_hierarchy_instance(h_str))
        hanja_entry["tags"] = result

    return hanja_data """


def create_anki_tags(data, tag_template, values):
    for entry in data:
        tag_values = []
        for value in values:
            if "{" in value and "}" in value:
                # If the value is enclosed in curly brackets, find the key in the entry
                key = value.strip("{}")
                if key not in entry:
                    raise KeyError(
                        f"Key '{key}' not found in entry: {entry}. Check the 'values' argument for valid keys: {values}"
                    )
                tag_values.append(entry[key])
            else:
                # If the value is just a string, use it as the key
                tag_values.append(value)

        h_str = tag_template.format(*tag_values)
        h_list = create_hierarchy_instance(h_str)
        entry["tags"] = " ".join(h_list)
    return data


def create_hierarchy_instance(input_string, delimiter="::"):
    """
    Converts a hierarchical input string into Anki tags.

    Args:
        input_string (str): Input string representing a hierarchical structure.
        delimiter (str, optional): Delimiter used to separate levels in the hierarchy. Default is "::".

    Returns:
        str: Anki tags derived from the hierarchical structure in the input string.
    """

    def convert_string_to_dict(string):
        """Converts a string to a dictionary."""
        try:
            return ast.literal_eval(string)
        except (SyntaxError, ValueError) as e:
            logger.warning(
                f"Error evaluating string: {e}\nProblematic string: {input_string}"
            )
            return {}

    def generate_hierarchy(node, current_path="", result=None):
        """Recursively generates a hierarchy list from a nested dictionary or list."""
        if result is None:
            result = []

        # If the current node is a dictionary, iterate through key-value pairs
        if isinstance(node, dict):
            for key, value in node.items():
                new_path = current_path + str(key)
                result.append(new_path)
                # Recursively call generate_hierarchy for the nested value
                generate_hierarchy(value, new_path + delimiter, result)
        # If the current node is a list, iterate through items
        elif isinstance(node, list):
            # Add delimiter only once before processing the list items
            for item in node:
                new_path = current_path
                # If the item is a nested dictionary or list, recursively call generate_hierarchy
                if isinstance(item, (dict, list)):
                    generate_hierarchy(item, new_path, result)
                # If the item is a string or other type, add it to the result
                else:
                    result.append(
                        new_path + (str(item) if isinstance(item, str) else str(item))
                    )
        # If the current node is a string, add it to the result
        elif isinstance(node, str):
            result.append(current_path + node)

    # Generate hierarchy from input string through dictionary
    hierarchy_list = []
    input_dict = convert_string_to_dict(input_string)
    generate_hierarchy(input_dict, "", hierarchy_list)

    # return the Anki tags a string
    return hierarchy_list
