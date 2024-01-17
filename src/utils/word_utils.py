def filter_by_word_length(input_word, min_length=3, max_length=9):
    """
    Filter a word based on the number of words (space-separated).

    Args:
        input_word (str or list): Word or list of words to be filtered.
        min_length (int): Minimum number of words allowed.
        max_length (int): Maximum number of words allowed.

    Returns:
        str or list or None: If input_word is a string and the number of words is within
                             the specified range, return the input_word. If input_word is a list,
                             return a list containing only words with word counts within the
                             specified range. If input_word is not a valid string or list, return None.
    """
    # Check if input_word is a string
    if isinstance(input_word, str):
        # Split the string into words
        words = input_word.split()

        # Check if the number of words is within the specified range
        if min_length <= len(words) <= max_length:
            return input_word
        else:
            return None
    # Check if input_word is a list
    elif isinstance(input_word, list):
        # Filter words in the list based on word count
        filtered_words = [
            word for word in input_word if min_length <= len(word.split()) <= max_length
        ]
        return filtered_words
    else:
        return None
