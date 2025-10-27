import random

def shuffle_inner_letters(word: str) -> str:
    """
    Randomly shuffles the inner letters of a word while keeping the first and last letters in place.
    If the shuffled middle part happens to be identical to the original, it will be reversed instead.
    Words shorter than or equal to three characters, or consisting only of whitespace, are returned unchanged.

    Args:
        word (str): The input word to shuffle.

    Returns:
        str: The word with its inner letters shuffled, or reversed if shuffling
        does not change the middle part. Returns the original word if it is too short
        or contains identical middle letters only.
    """
    if not word or len(word) <= 3 or word.isspace():
        return word

    first, middle, last = word[0], word[1:-1], word[-1]


    if middle.count(middle[0]) == len(middle):
        return word

    middle_list = list(middle)
    random.shuffle(middle_list)
    shuffled = ''.join(middle_list)

    # if shuffle didn't change the middle, reverse it
    if shuffled == middle:
        shuffled = middle[::-1]

    return first + shuffled + last




def shuffle_text_line(line: str) -> str:
    """
    Processes a line of text by shuffling the inner letters of each word.
    Each word in the input line is passed to the `shuffle_inner_letters` function.

    Args:
        line (str): A line of text to process.

    Returns:
        str: A new line where each word has its inner letters shuffled,
        maintaining the original word order and spacing between words.
    """
    return ' '.join(shuffle_inner_letters(word) for word in line.split())




from typing import Iterable, Callable, Generator

def line_generator(
    infile: Iterable[str],
    line_processor: Callable[[str], str]
) -> Generator[str, None, None]:
    """
    A generator that processes lines from an input source using a given line processor function.

    This function iterates over each line in the provided iterable (e.g., a file object or list of strings),
    applies the `line_processor` function to transform it, and yields the processed line with a newline
    character appended at the end.

    Args:
        infile (Iterable[str]): An iterable source of text lines (for example, a file object or list of strings).
        line_processor (Callable[[str], str]): A function that takes a single line of text as input
            and returns a processed version of that line.

    Yields:
        str: Each processed line, terminated with a newline character (`'\n'`).

    Notes:
        - The input lines have their trailing newline (`'\\n'`) removed before processing.
        - Each yielded line includes a newline at the end for easy writing to files.
    """
    for line in infile:
        yield line_processor(line.rstrip('\n')) + '\n'