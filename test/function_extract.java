package com.example;

import java.util.List;
import java.util.function.Consumer;

/**
 * This class contains various edge cases to test the function extractor.
 */
public class TrickyCases {

    // Case 1: A constructor (should be ignored by the current script)
    public TrickyCases(int value) {
        System.out.println("Constructor with value: " + value);
    }

    // Case 2: Method with a string containing braces
    // The brace counting logic might fail here.
    public void methodWithStringBraces() {
        String json = "{\"key\": \"value\"}";
        System.out.println(json);
    }

    // Case 3: Method with a block comment containing braces
    public void methodWithBlockCommentBraces() {
        /*
         * This is a comment. { brace in comment }
         */
        int x = 10; // another comment }
    }

    // Case 4: Nested static class with a method
    public static class NestedStaticClass {
        public void nestedMethod() {
            System.out.println("I am in a nested static class.");
        }
    }

    // Case 5: Method with an anonymous inner class
    public void methodWithAnonymousInnerClass() {
        Runnable r = new Runnable() {
            @Override
            public void run() {
                System.out.println("Hello from an anonymous inner class.");
            }
        };
        r.run();
    }

    // Case 6: Method in a single line
    public void singleLineMethod() { System.out.println("This method is in a single line."); }

    // A simple method to mark the end of the complex cases
    public void finalMethod() {
        System.out.println("This is the final method.");
    }
}

