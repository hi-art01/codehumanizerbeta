import unittest
import sys
import os

# Add the parent directory to the path to import the humanizer module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from humanizer import humanize_code

class TestHumanizer(unittest.TestCase):

    def test_add_comments(self):
        code = """def my_func(a, b):
    return a + b"""
        options = {'add_comments': True}
        expected_code = '''def my_func(a, b):
    """This function, `my_func`, takes the following arguments: a, b and returns a result."""
    return a + b'''
        self.assertEqual(humanize_code(code, options).strip(), expected_code.strip())

    def test_snake_case_conversion(self):
        code = """def myFunction(myVar):
    return myVar"""
        options = {'naming_convention': 'snake_case', 'add_comments': False}
        expected_code = """def my_function(my_var):
    return my_var"""
        self.assertEqual(humanize_code(code, options).strip(), expected_code.strip())

    def test_camel_case_conversion(self):
        code = """def my_function(my_var):
    return my_var"""
        options = {'naming_convention': 'camelCase', 'add_comments': False}
        expected_code = """def myFunction(myVar):
    return myVar"""
        self.assertEqual(humanize_code(code, options).strip(), expected_code.strip())

    def test_for_loop_to_list_comprehension(self):
        code = """def my_function():
    my_list = []
    for i in range(5):
        my_list.append(i)
    return my_list"""
        options = {'convert_loops': True, 'add_comments': False}
        expected_code = """def my_function():
    my_list = [i for i in range(5)]
    return my_list"""
        self.assertEqual(humanize_code(code, options).strip(), expected_code.strip())

    def test_for_loop_with_if_to_list_comprehension(self):
        code = """def my_function():
    my_list = []
    for i in range(10):
        if i % 2 == 0:
            my_list.append(i)
    return my_list"""
        options = {'convert_loops': True, 'add_comments': False}
        expected_code = """def my_function():
    my_list = [i for i in range(10) if i % 2 == 0]
    return my_list"""
        self.assertEqual(humanize_code(code, options).strip(), expected_code.strip())

    def test_for_else_loop_is_not_transformed(self):
        code = """def my_function():
    my_list = []
    for i in range(5):
        my_list.append(i)
    else:
        print("Loop finished")
    return my_list"""
        options = {'convert_loops': True, 'add_comments': False}
        self.assertEqual(humanize_code(code, options).strip(), code.strip())

    def test_for_loop_with_complex_body_is_not_transformed(self):
        code = """def my_function():
    my_list = []
    for i in range(5):
        print(i)
        my_list.append(i)
    return my_list"""
        options = {'convert_loops': True, 'add_comments': False}
        self.assertEqual(humanize_code(code, options).strip(), code.strip())

if __name__ == '__main__':
    unittest.main()
