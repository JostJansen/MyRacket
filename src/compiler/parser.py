from enum import Enum, auto
from compiler.lexer import TokenType


class NonTerminal(Enum):
    BASIC_FSIG = auto()
    COMPLEX_SIG = auto()
    CONSTANT_DEF = auto()
    DEFINITION = auto()
    EXPRESSION = auto()
    FSIG_DEC = auto()
    FUNC_CALL = auto()
    FUNC_DEF = auto()
    FUNC_SIG = auto()
    LAMBDA = auto()
    LITERAL = auto()
    PARAM_FSIG = auto()
    PROGRAM = auto()
    SIGNATURE = auto()
    SIG_DEF = auto()
    STATEMENT = auto()


GRAMMAR = {
    NonTerminal.PROGRAM: [
        [("statements", ("*", NonTerminal.STATEMENT)), (None, TokenType.EOF)],
    ],
    NonTerminal.STATEMENT: [
        NonTerminal.DEFINITION,
        NonTerminal.FSIG_DEC,
        NonTerminal.EXPRESSION,
    ],
    NonTerminal.DEFINITION: [
        NonTerminal.CONSTANT_DEF,
        NonTerminal.FUNC_DEF,
        NonTerminal.SIG_DEF,
    ],
    NonTerminal.CONSTANT_DEF: [
        [
            (None, "("),
            (None, "define"),
            ("name", TokenType.IDENTIFIER),
            ("value", NonTerminal.EXPRESSION),
            (None, ")"),
        ],
    ],
    NonTerminal.SIG_DEF: [
        [
            (None, "("),
            (None, "define"),
            ("name", TokenType.IDENTIFIER),
            ("signature", NonTerminal.SIGNATURE),
            (None, ")"),
        ],
    ],
    NonTerminal.FUNC_DEF: [
        [
            (None, "("),
            (None, "define"),
            (None, "("),
            ("name", TokenType.IDENTIFIER),
            ("params", ("*", TokenType.IDENTIFIER)),
            (None, ")"),
            ("body", NonTerminal.EXPRESSION),
            (None, ")"),
        ],
    ],
    NonTerminal.FSIG_DEC: [
        NonTerminal.BASIC_FSIG,
        NonTerminal.PARAM_FSIG,
    ],
    NonTerminal.BASIC_FSIG: [
        [
            (None, "("),
            (None, ":"),
            ("name", TokenType.IDENTIFIER),
            ("signature", NonTerminal.FUNC_SIG),
            (None, ")"),
        ],
    ],
    NonTerminal.PARAM_FSIG: [
        [
            (None, "("),
            (None, ":"),
            ("name", TokenType.IDENTIFIER),
            (None, "["),
            ("params", ("+", TokenType.IDENTIFIER)),
            (None, "]"),
            ("signature", NonTerminal.FUNC_SIG),
            (None, ")"),
        ],
    ],
    NonTerminal.SIGNATURE: [
        NonTerminal.FUNC_SIG,
        NonTerminal.COMPLEX_SIG,
        TokenType.IDENTIFIER,
    ],
    NonTerminal.FUNC_SIG: [
        [
            (None, "("),
            ("param_sigs", ("+", NonTerminal.SIGNATURE)),
            (None, "->"),
            ("ret_sig", NonTerminal.SIGNATURE),
            (None, ")"),
        ],
    ],
    NonTerminal.COMPLEX_SIG: [
        [
            (None, "("),
            ("name", TokenType.IDENTIFIER),
            ("signatures", ("+", NonTerminal.SIGNATURE)),
            (None, ")"),
        ],
    ],
    NonTerminal.EXPRESSION: [
        NonTerminal.LITERAL,
        NonTerminal.FUNC_CALL,
        TokenType.IDENTIFIER,
        NonTerminal.LAMBDA,
    ],
    NonTerminal.LITERAL: [
        TokenType.BOOLEAN,
        TokenType.INTEGER,
    ],
    NonTerminal.FUNC_CALL: [
        [
            (None, "("),
            ("function", NonTerminal.EXPRESSION),
            ("args", ("*", NonTerminal.EXPRESSION)),
            (None, ")"),
        ],
    ],
    NonTerminal.LAMBDA: [
        [
            (None, "("),
            (None, "lambda"),
            (None, "("),
            ("params", ("+", TokenType.IDENTIFIER)),
            (None, ")"),
            ("body", NonTerminal.EXPRESSION),
            (None, ")"),
        ],
    ],
}


def expect_tktype(type, tokens):
    err = None
    if tokens[0].tktype != type:
        err = {
            "file": tokens[0].file,
            "line": tokens[0].line,
            "col": tokens[0].column,
            "expected": "<" + str(type) + ">",
            "found": tokens[0].tkstr,
        }

    return {"ast": tokens[0], "error": err, "tokens": tokens[1:]}


def expect_string(str, tokens):
    err = None
    if tokens[0].tkstr != str:
        err = {
            "file": tokens[0].file,
            "line": tokens[0].line,
            "col": tokens[0].column,
            "expected": '"' + str + '"',
            "found": tokens[0].tkstr,
        }

    return {"ast": tokens[0], "error": err, "tokens": tokens[1:]}


def match_list(lst, tokens):
    r = {"ast": {}, "error": None, "tokens": tokens}
    for symbol in lst:
        subr = match_symbol(symbol, r["tokens"])
        r["ast"] |= subr["ast"]
        r["error"] = subr["error"]
        r["tokens"] = subr["tokens"]
        if r["error"]:
            break
    return r


def match_tuple(tpl, tokens):
    r = {"ast": [], "error": None, "tokens": tokens}
    if tpl[0] == "+":
        subr = match_symbol(tpl[1], tokens)
        r["ast"].append(subr["ast"])
        r["error"] = subr["error"]
        r["tokens"] = subr["tokens"]

    if tpl[0] == "+" or tpl[0] == "*":
        while r["error"] is None:
            subr = match_symbol(tpl[1], r["tokens"])
            if subr["error"]:
                break
            r["ast"].append(subr["ast"])
            r["tokens"] = subr["tokens"]

    elif tpl[0] is None:
        r = match_symbol(tpl[1], tokens)
        r["ast"] = {}

    else:
        r = match_symbol(tpl[1], tokens)
        r["ast"] = {tpl[0]: r["ast"]}

    return r


def match_symbol(symbol, tokens):
    match symbol:
        case NonTerminal():
            r = apply_production(symbol, tokens)
        case TokenType():
            r = expect_tktype(symbol, tokens)
        case str():
            r = expect_string(symbol, tokens)
        case list():
            r = match_list(symbol, tokens)
        case tuple():
            r = match_tuple(symbol, tokens)

        case _:
            raise RuntimeError("Unreachable")

    return r


def apply_production(rule, tokens):
    # to ensure that the error with the longest match gets returned,
    # "tokens_left" saves how many tokens of the program were left,
    # when an error was discovered
    curr_err = None
    tokens_left = float("inf")
    for symbol in GRAMMAR[rule]:
        r = match_symbol(symbol, tokens)
        r["ast"] = (rule, r["ast"])
        if r["error"] is None:
            return r

        if tokens_left > len(r["tokens"]):
            curr_err = r["error"]
            tokens_left = len(r["tokens"])
        else:
            r["error"] = curr_err
    return r


def raise_syntax_error(err):
    print(f'In file "{err["file"]["name"]}" - {err["line"]}:{err["col"]}')
    print(">>  " + err["file"]["lines"][err["line"] - 1])
    print("    " + (err["col"] - 1) * " " + "^")
    print(f'SyntaxError: Expected {err["expected"]}; Found "{err["found"]}"')
    exit(-1)


def parse_tokens(tokens):
    tokens = [tk for tk in tokens if tk.tktype != TokenType.IGNORE]
    prog = apply_production(NonTerminal.PROGRAM, tokens)
    if prog["error"]:
        raise_syntax_error(prog["error"])
    return prog["ast"]
