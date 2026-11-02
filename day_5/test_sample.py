# content of test_class.py
class TestClass:
    # Check that the sample text contains the letter h.
    def test_one(self):
        x = "this"
        assert "h" in x

    # Check that the sample string has a check attribute.
    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")