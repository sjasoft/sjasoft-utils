from functools import reduce
import re

def split_string(s, split_by=None, eat_empty=True, convert=None):
    parts = [p.strip() for p in s.split(split_by)]
    if eat_empty:
        parts = [p for p in parts if len(p)]
    if convert:
        parts = [convert(p) for p in parts]

    return parts

def split_once(s, split_by):
    return [before(s, split_by), after(s, split_by)]


def after(s, sub):
    if not sub in s:
        return s
    return s[s.index(sub) + len(sub):].strip()

def before_last(s, split_f=None):
    if (split_f is None) or (split_f in s):
        last = s.split(split_f)[-1]
        return before(s, last)
    else:
        return s

def before(s, sub):
    if not sub in s:
        return s
    return s[: s.index(sub)].strip()

def paren_split(s, splitter, convert=None):
    open = s.index('(')
    close = s.index(')')
    content = s[open + 1: close]
    rest = s[close + 1:]
    parts = split_string(content, splitter, convert=convert)
    return parts, rest

def between(s, first, last, widest=True):
    if (first in s) and (last in s):
        start = s.index(first)
        end = s.rindex(last) if widest else s.index(last)
        return s[start+1: end].strip()
    return None

def bytes_to_string(val):
    return val.decode('utf-8') if isinstance(val, bytes) else val

def snake_to_camel_case(s, first_cap=False):
    parts = s.split('_')
    first = parts[0].capitalize() if first_cap else parts[0]
    rest = [p.capitalize() for p in parts[1:]]
    parts = [first] + rest
    return ''.join(parts)

def drop_word(s, break_fn):
    'drop a word from end of string where break_fn is a tests for word separators'
    index = len(s)
    while break_fn(s[index - 1]):
        index -= 1
    while not break_fn(s[index - 1]):
        index -= 1
    return s[:index]


def word_splitter(s, test):
    in_word = False
    word_start = -1
    res = []
    for i, c in enumerate(s):
        if test(c):
            if in_word:
                res.append(s[word_start: i])
            in_word = False
        else:
            if not in_word:
                in_word = True
                word_start = i
    if in_word:
        res.append(s[word_start:])
    return res


def word_indices(a_string, break_fn):
    words = word_splitter(a_string, break_fn)
    word_locations = []
    begin = 0
    for word in words:
        start = begin + a_string[begin:].index(word)
        end = start + len(word)
        word_locations.append((start, end))
        begin = end
    return word_locations


def max_word_break(a_string, max_length, break_fn):
    '''
    Returns the prefix of a_string less than max_length long preserving whole words as much as
    possible.  Words are considere separated by <space>. if no <space> in a_string return the
    truncated string
    '''

    word_locs = word_indices(a_string, break_fn)
    last = 0
    for _, end in word_locs:
        if end <= max_length:
            last = end
        else:
            break
    return a_string[:last] if last else a_string[:max_length]


def truncate_text(text, length=100, strict=False, elipses=False, quotes=False, removeurls=True, word_break=None):
    word_break = word_break or (lambda c: not c.isalnum())
    if removeurls:
        text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    add_elipses = lambda s: s + '...'
    add_quotes = lambda s: '"%s"' % s
    decorations = []
    if elipses:
        decorations.append(add_elipses)
        length -= 3
    if quotes:
        decorations.append(add_quotes)
        length -= 2

    decorated = lambda s: reduce(lambda a, d: d(a), decorations, s)

    if strict:
        return decorated(text[:length])
    else:
        return decorated(max_word_break(text, length, word_break))

