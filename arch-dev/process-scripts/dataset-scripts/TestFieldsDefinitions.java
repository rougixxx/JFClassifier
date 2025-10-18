package com.example.test;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * This class contains various field/variable declarations to test extraction
 */
public class TestFieldsDefinitions extends BaseClass implements TestInterface {
    // Basic types with different access modifiers
    private int privateInt = 42;
    protected boolean protectedBool = false;
    public String publicString = "Hello World";
    float packageFloat = 3.14f;  // Default/package access
    
    // Static fields
    private static final long CONSTANT = 1000L;
    public static double staticDouble = 2.71828;
    
    // Array definitions (different styles)
    private int[] numberArray = {1, 2, 3, 4, 5};
    protected String arrayOfStrings[] = new String[10];
    public char[][] multiDimensionalArray;
    
    // Collection types with generics
    private List<String> stringList = new ArrayList<>();
    protected Map<Integer, String> mapping = new HashMap<Integer, String>();
    public List<Map<String, Object>> complexType;
    
    // Multiple variable declarations in one statement
    private int x = 1, y = 2, z = 3;
    
    // Uninitialized variables
    private long uninitialized;
    protected byte[] dataBuffer;
    
    // Variables with complex initializers
    private String formatted = String.format("%d items", 5);
    protected StringBuilder builder = new StringBuilder()
        .append("Multi")
        .append("line")
        .append("initializer");
    
    // Inner class with its own fields
    private class InnerClass {
        private int innerField = 100;
        protected boolean innerFlag;
    }
    
    // Enum with fields
    public enum TestEnum {
        ONE(1),
        TWO(2),
        THREE(3);
        
        private final int value;
        
        TestEnum(int value) {
            this.value = value;
        }
    }
    
    // Instance initialization block
    {
        privateInt = 50;
        stringList.add("Init block");
    }
    
    // Static initialization block
    static {
        staticDouble = Math.PI;
        System.out.println("Static initialization");
    }
    
    // Methods (should be excluded from field extraction)
    public void testMethod() {
        // Local variables (should be excluded)
        int localVar = 10;
        String localString = "Local";
    }
    
    private int calculateValue() {
        int local = 5;
        return local * 10;
    }
}

// Class with only fields, no methods
class SimpleFieldsClass {
    int a = 1;
    String b = "test";
    double c = 3.0;
}