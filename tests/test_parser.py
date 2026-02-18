import pytest
from compiler.lexer import TokenType, lex_file_data
from compiler.parser import (
    NonTerminal,
    expect_tktype,
    expect_string,
    match_list,
    match_tuple,
    apply_production,
)

TEST_FILE_1 = {
    "name": "test.rkt",
    "lines": [
        "(x y (z 1))",
        "(: x [X Y] (X Y -> Integer))",
        "(define (x) (lambda (x y) (+ x y)))",
    ],
}

TEST_TOKENS_1 = lex_file_data(TEST_FILE_1)


def test_expect_tktype():
    assert expect_tktype(TokenType.KEYWORD, TEST_TOKENS_1) == {
        "ast": TEST_TOKENS_1[0],
        "error": {
            "file": TEST_FILE_1,
            "line": 1,
            "col": 1,
            "expected": "<KEYWORD>",
            "found": "(",
        },
        "tokens": TEST_TOKENS_1[1:],
    }

    assert expect_tktype(TokenType.SEPARATOR, TEST_TOKENS_1) == {
        "ast": TEST_TOKENS_1[0],
        "error": None,
        "tokens": TEST_TOKENS_1[1:],
    }


def test_expect_string():
    assert expect_string("(x", TEST_TOKENS_1) == {
        "ast": TEST_TOKENS_1[0],
        "error": {
            "file": TEST_FILE_1,
            "line": 1,
            "col": 1,
            "expected": '"(x"',
            "found": "(",
        },
        "tokens": TEST_TOKENS_1[1:],
    }
    assert expect_string("y", TEST_TOKENS_1[3:]) == {
        "ast": TEST_TOKENS_1[3],
        "error": None,
        "tokens": TEST_TOKENS_1[4:],
    }


def test_match_list():
    assert match_list(
        [(None, "("), ("name", TokenType.IDENTIFIER)], TEST_TOKENS_1[1:]
    ) == {
        "ast": {},
        "error": {
            "file": TEST_FILE_1,
            "line": 1,
            "col": 2,
            "expected": '"("',
            "found": "x",
        },
        "tokens": TEST_TOKENS_1[2:],
    }
    assert match_list([(None, "("), ("name", TokenType.IDENTIFIER)], TEST_TOKENS_1) == {
        "ast": {"name": TEST_TOKENS_1[1]},
        "error": None,
        "tokens": TEST_TOKENS_1[2:],
    }


def test_match_tuple():
    assert match_tuple(("name", TokenType.IDENTIFIER), TEST_TOKENS_1[1:]) == {
        "ast": {"name": TEST_TOKENS_1[1]},
        "error": None,
        "tokens": TEST_TOKENS_1[2:],
    }

    assert match_tuple((None, TokenType.IDENTIFIER), TEST_TOKENS_1[1:]) == {
        "ast": {},
        "error": None,
        "tokens": TEST_TOKENS_1[2:],
    }

    assert match_tuple(("+", TokenType.IDENTIFIER), TEST_TOKENS_1) == {
        "ast": [TEST_TOKENS_1[0]],
        "error": {
            "file": TEST_FILE_1,
            "line": 1,
            "col": 1,
            "expected": "<IDENTIFIER>",
            "found": "(",
        },
        "tokens": TEST_TOKENS_1[1:],
    }
