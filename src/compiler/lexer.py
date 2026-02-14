import re
from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    BOOLEAN = auto()
    IDENTIFIER = auto()
    IGNORE = auto()
    INTEGER = auto()
    SEPARATOR = auto()
    UNKOWN = auto()

@dataclass(frozen=True)
class Token:
    tktype: TokenType 
    tkstr: str
    file: dict  # "name": str, "lines": [str]
    line: int
    column: int

# order matters! patterns later in the list are matched later
# important for overlapping patterns
GRAMMAR = [
    (TokenType.BOOLEAN, "#t|#f"),
    (TokenType.INTEGER, "-?\\d+"),
    (TokenType.SEPARATOR, "[\\(\\)]"),
    (TokenType.IDENTIFIER, 
     "[a-zA-z_\\+\\*\\/\\<\\>\\=\\?\\!][a-zA-z_0-9\\+\\-\\*\\/\\<\\>\\=\\?\\!]*"),
    (TokenType.IGNORE, "\\;.*$"),
    (TokenType.IGNORE, "\\s+"),
    (TokenType.UNKOWN, "."),
]

def lex_file_data(file):
    tokens = []
    line = col = 0

    while line != len(file["lines"]):
        (token, line, col) = lex_next_token(file, line, col)
        tokens.append(token)

    return tokens

def lex_next_token(file, line, col):
    for (tktype, pattern) in GRAMMAR:
        match = re.match(pattern, file["lines"][line][col:])
        if match:
            is_linebreak = len(file["lines"][line]) <= col + len(match.group())
            new_col = 0 if is_linebreak else col + len(match.group())
            new_line = line + 1 if is_linebreak else line

            while new_line != len(file["lines"]) and len(file["lines"][new_line]) == 0:
                new_line += 1
            
            return (
                Token(
                    tktype,
                    match.group(),
                    file,
                    line + 1,  # 0 -> 1 indexed
                    col + 1), 
                new_line,
                new_col)
        
    raise RuntimeError("Unreachable")
