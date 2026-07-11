from snaptex.core import DragBox, normalize_latex


def test_normalize_latex_removes_display_math_wrapper() -> None:
    assert normalize_latex(r"  $$ x^2   + y^2 = z^2 $$  ") == r"x^2 + y^2 = z^2"


def test_normalize_latex_removes_bracket_wrapper() -> None:
    assert normalize_latex(r"\[\frac{a}{b}\]") == r"\frac{a}{b}"


def test_normalize_latex_leaves_internal_dollars() -> None:
    assert normalize_latex(r"x + \text{cost is $5}") == r"x + \text{cost is $5}"


def test_drag_box_normalizes_reverse_drag() -> None:
    assert DragBox(90, 70, 10, 20).bounds == (10, 20, 90, 70)


def test_drag_box_rejects_accidental_click() -> None:
    assert not DragBox(10, 10, 14, 13).is_large_enough
