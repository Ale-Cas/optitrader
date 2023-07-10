"""Test general utils."""
from optifolio.utils import clean_string, remove_punctuation


def test_remove_punctuation():
    """Test remove_punctuation function."""
    # Test case with punctuation marks
    assert remove_punctuation("Hello, world!") == "Hello world"

    # Test case without punctuation marks
    assert remove_punctuation("Hello world") == "Hello world"

    # Test case with multiple punctuation marks
    assert remove_punctuation("Hello!!!") == "Hello"


def test_clean_string():
    """Test clean_string function."""
    # Test case with underscore and hyphen
    assert clean_string("clean_up_string") == "clean up string"

    # Test case without underscore and hyphen
    assert clean_string("Hello world") == "Hello world"

    # Test case with only underscore
    assert clean_string("_clean_string_") == " clean string "

    # Test case with only hyphen
    assert clean_string("-clean-string-") == " clean string "

    # Test case with both underscore and hyphen
    assert clean_string("clean_string-here") == "clean string here"
