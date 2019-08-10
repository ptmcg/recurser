import unittest
from pyparsing import ParseException

from app.services.interpreter import (
    StackException,
    IterationException,
    Context,
    parse,
)

shell = """
fun() {
%s
}

fun();
"""


class InterpreterTestCase(unittest.TestCase):
    def test_string_append(self):
        context = Context()
        parse(shell % 'x = "a";\nx = x + x;').execute(context)
        self.assertEqual(context.root_frame.values["x"], "aa")

        context = Context()
        parse(shell % 'x = "a" + "b" + "c";').execute(context)
        self.assertEqual(context.root_frame.values["x"], "abc")

        with self.assertRaises(ParseException):
            context = Context()
            parse(shell % 'x = "a" + 1;').execute(context)
            self.assertEqual(context.root_frame.values["x"], "abc")

    def test_string_insert(self):
        context = Context()
        parse(shell % 'x = ""; x.insert(0, "a");').execute(context)
        self.assertEqual(context.root_frame.values["x"], "a")

        context = Context()
        parse(shell % 'x = "abc"; x.insert(1, "x");').execute(context)
        self.assertEqual(context.root_frame.values["x"], "axbc")

    def test_array_insert(self):
        context = Context()
        parse(shell % 'x = []; x.insert(0, "a");').execute(context)
        self.assertEqual(context.root_frame.values["x"], ["a"])

    def test_array_append(self):
        context = Context()
        parse(shell % 'x = []; x.append("a");').execute(context)
        self.assertEqual(context.root_frame.values["x"], ["a"])
  
    def test_string_replace(self):
        context = Context()
        parse(shell % 'x = "a"; x.replace("a", "");').execute(context)
        self.assertEqual(context.root_frame.values["x"], "")

        context = Context()
        parse(shell % 'x = "abc"; x.replace("b", "");').execute(context)
        self.assertEqual(context.root_frame.values["x"], "ac")

    def test_evaluate_numbers(self):
        context = Context()
        parse(shell % 'x = 1000; x = x * -0.1;').execute(context)
        self.assertEqual(context.root_frame.values["x"], -100.0)

    def test_comments(self):
        context = Context()
        parse(shell % 'x = 1000; x = x * -0.1; x = x + 10; x = x - 1;').execute(context)
        self.assertEqual(context.root_frame.values["x"], -91.0)

        context = Context()
        parse(shell % 'x = 1000; x = x * -0.1; /* x = x + 10; */ x = x - 1;').execute(context)
        self.assertEqual(context.root_frame.values["x"], -101.0)

        context = Context()
        parse(shell % 'x = 1000; x = x * -0.1; # x = x + 10; \n x = x - 1;').execute(context)
        self.assertEqual(context.root_frame.values["x"], -101.0)

        context = Context()
        parse(shell % 'x = 1000; x = x * -0.1; // x = x + 10; \n x = x - 1;').execute(context)
        self.assertEqual(context.root_frame.values["x"], -101.0)

    def test_if_then_else(self):
        context = Context()
        parse(shell % 'x = 1000; if (x < 10) { x = x * 100; } else { x = x / 100; }').execute(context)
        self.assertEqual(context.root_frame.values["x"], 10.0)

    def test_error_location(self):
        with self.assertRaises(Exception) as pe:
            parse(shell % 'for (i=0; i < 1000; i = i +) { a = 100; }')
        self.assertEqual(pe.exception.loc, 35)

    def test_array_add(self):
        context = Context()
        parse(shell % 'x = ["a"] + ["a"];').execute(context)
        self.assertEqual(context.root_frame.values["x"], ["a", "a"])

    def test_array_reference(self):
        context = Context()
        parse(shell % 'x = ["a"] + ["a"]; x = x[1];').execute(context)
        self.assertEqual(context.root_frame.values["x"], "a")


if __name__ == "__main__":
    unittest.main()
