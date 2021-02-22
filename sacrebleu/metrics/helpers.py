from collections import Counter
from typing import List


def extract_word_ngrams(tokens: List[str], min_order: int, max_order: int) -> Counter:
    """Extracts all ngrams (min_order <= n <= max_order) from a sentence.

    :param tokens: A list of tokens
    :param min_order: Minimum n-gram length
    :param max_order: Maximum n-gram length
    :return: a count dictionary
    """

    ngrams = []

    for n in range(min_order, max_order + 1):
        for i in range(0, len(tokens) - n + 1):
            ngrams.append(tuple(tokens[i: i + n]))

    return Counter(ngrams)


def extract_char_ngrams(line: str, n: int) -> Counter:
    """Yields counts of character n-grams from a sentence.

    :param line: A segment containing a sequence of words.
    :param n: The order of the n-grams.
    :return: a dictionary containing ngrams and counts
    """
    return Counter([line[i:i + n] for i in range(len(line) - n + 1)])
