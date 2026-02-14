import pytest
from compiler.lexer import Token, TokenType, lex_file_data, lex_next_token

TEST_FILE_1 = {
    "name": "test.txt",
    "lines": [
        "ü  \t; jk",
        "(not89_+-/*s<>=? #t) -12",
        "",
        "",
        "(hello) 35235 -+ABC",
        "",
    ],
}


@pytest.mark.parametrize(
    "input, expected",
    [
        ((TEST_FILE_1, 0, 0), (Token(TokenType.UNKOWN, "ü", TEST_FILE_1, 1, 1), 0, 1)),
        (
            (TEST_FILE_1, 0, 1),
            (Token(TokenType.IGNORE, "  \t", TEST_FILE_1, 1, 2), 0, 4),
        ),
        (
            (TEST_FILE_1, 0, 4),
            (Token(TokenType.IGNORE, "; jk", TEST_FILE_1, 1, 5), 1, 0),
        ),
        (
            (TEST_FILE_1, 1, 0),
            (Token(TokenType.SEPARATOR, "(", TEST_FILE_1, 2, 1), 1, 1),
        ),
        (
            (TEST_FILE_1, 1, 1),
            (Token(TokenType.IDENTIFIER, "not89_+-/*s<>=?", TEST_FILE_1, 2, 2), 1, 16),
        ),
        (
            (TEST_FILE_1, 1, 17),
            (Token(TokenType.BOOLEAN, "#t", TEST_FILE_1, 2, 18), 1, 19),
        ),
        (
            (TEST_FILE_1, 1, 21),
            (Token(TokenType.INTEGER, "-12", TEST_FILE_1, 2, 22), 4, 0),
        ),
    ],
)
def test_lex_next_token(input, expected):
    assert lex_next_token(*input) == expected


def test_lex_file_data():
    assert lex_file_data(TEST_FILE_1) == [
        Token(TokenType.UNKOWN, "ü", TEST_FILE_1, 1, 1),
        Token(TokenType.IGNORE, "  \t", TEST_FILE_1, 1, 2),
        Token(TokenType.IGNORE, "; jk", TEST_FILE_1, 1, 5),
        Token(TokenType.SEPARATOR, "(", TEST_FILE_1, 2, 1),
        Token(TokenType.IDENTIFIER, "not89_+-/*s<>=?", TEST_FILE_1, 2, 2),
        Token(TokenType.IGNORE, " ", TEST_FILE_1, 2, 17),
        Token(TokenType.BOOLEAN, "#t", TEST_FILE_1, 2, 18),
        Token(TokenType.SEPARATOR, ")", TEST_FILE_1, 2, 20),
        Token(TokenType.IGNORE, " ", TEST_FILE_1, 2, 21),
        Token(TokenType.INTEGER, "-12", TEST_FILE_1, 2, 22),
        Token(TokenType.SEPARATOR, "(", TEST_FILE_1, 5, 1),
        Token(TokenType.IDENTIFIER, "hello", TEST_FILE_1, 5, 2),
        Token(TokenType.SEPARATOR, ")", TEST_FILE_1, 5, 7),
        Token(TokenType.IGNORE, " ", TEST_FILE_1, 5, 8),
        Token(TokenType.INTEGER, "35235", TEST_FILE_1, 5, 9),
        Token(TokenType.IGNORE, " ", TEST_FILE_1, 5, 14),
        Token(TokenType.UNKOWN, "-", TEST_FILE_1, 5, 15),
        Token(TokenType.IDENTIFIER, "+ABC", TEST_FILE_1, 5, 16),
    ]
