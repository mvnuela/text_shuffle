import random
import io
from text_processor.utils.text_utils import shuffle_inner_letters, shuffle_text_line, line_generator


def test_shuffle_inner_letters_short_words():
    assert shuffle_inner_letters("a") == "a"
    assert shuffle_inner_letters("ab") == "ab"
    assert shuffle_inner_letters("abc") == "abc"


def test_shuffle_inner_letters_preserves_edges(monkeypatch):
    monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())

    word = "python"
    shuffled = shuffle_inner_letters(word)
    assert shuffled[0] == "p"
    assert shuffled[-1] == "n"
    assert shuffled != word
    assert len(shuffled) == len(word)

def test_shuffle_inner_letters_whitespace():
    assert shuffle_inner_letters("       ") == "       "
    assert shuffle_inner_letters("\t") == "\t"
    assert shuffle_inner_letters(" \n ") == " \n "

def test_shuffle_text_line(monkeypatch):
    monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
    line = "Python Django Test"
    result = shuffle_text_line(line)
    words = result.split()
    assert len(words) == 3
    for orig, new in zip(line.split(), words):
        assert len(orig) == len(new)
        assert orig[0] == new[0]
        assert orig[-1] == new[-1]


def test_line_generator(monkeypatch):
    monkeypatch.setattr(random, "shuffle", lambda x: x.reverse())
    input_data = io.StringIO("Hello\nWorld\n")
    output = list(line_generator(input_data, shuffle_text_line))
    assert len(output) == 2
    assert output[0].endswith("\n")
    assert output[1].endswith("\n")
