from calc import calc


def test_precedence():
    assert calc("1 + 2 * 3") == 7.0


def test_parens():
    assert calc("(1 + 2) * 3") == 9.0


def test_unary_minus():
    assert calc("-3 + 4") == 1.0


def test_associativity():
    assert calc("8 - 2 - 1") == 5.0
