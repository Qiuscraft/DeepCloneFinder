import os
import sys

# Ensure project root is on sys.path so imports work when running tests from any cwd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.java_code.function_validator import is_java_function


def test_method_with_body_is_function():
    snippet = """
    public void foo() {
        System.out.println("hi");
    }
    """
    assert is_java_function(snippet)


def test_abstract_method_is_function():
    snippet = "public abstract int foo(String name);"
    assert is_java_function(snippet)


def test_multiple_members_is_not_function():
    snippet = """
    public void foo() {}
    public void bar() {}
    """
    assert not is_java_function(snippet)


def test_non_method_snippet_is_not_function():
    snippet = "int value = 0;"
    assert not is_java_function(snippet)


def test_blank_input_is_not_function():
    assert not is_java_function("   ")


def test_constructor_is_function():
    snippet = """
    public Foo() {
        this.value = 42;
    }
    """
    assert is_java_function(snippet)


def test_class_declaration_is_not_function():
    snippet = """
    public class Foo {
        private int value;
    }
    """
    assert not is_java_function(snippet)


def test_method_with_nested_initializer_is_function():
    snippet = """
    public void foo() {
        Runnable r = new Runnable() {
            @Override
            public void run() {}
        };
        r.run();
    }
    """
    assert is_java_function(snippet)
