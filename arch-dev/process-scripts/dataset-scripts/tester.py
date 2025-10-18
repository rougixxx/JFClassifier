def remove_java_comments(java_content):
    """
    Remove single-line (//) and multi-line (/* */) comments from Java source code
    while preserving comments inside string literals and character literals.
    
    Args:
        java_content (str): The Java source code as a string
        
    Returns:
        str: Java code with comments removed
    """
    result = []
    i = 0
    in_string = False
    in_char = False
    in_multiline_comment = False
    string_delimiter = None
    escaped = False
    
    while i < len(java_content):
        char = java_content[i]
        
        # Handle escape sequences
        if escaped:
            result.append(char)
            escaped = False
            i += 1
            continue
        
        # Check for escape character
        if char == '\\' and (in_string or in_char):
            escaped = True
            result.append(char)
            i += 1
            continue
        
        # Handle string and character literals
        if char in ['"', "'"] and not in_multiline_comment:
            if not in_string and not in_char:
                # Starting a string or char literal
                if char == '"':
                    in_string = True
                else:
                    in_char = True
                string_delimiter = char
                result.append(char)
            elif char == string_delimiter:
                # Ending the string or char literal
                in_string = False
                in_char = False
                string_delimiter = None
                result.append(char)
            else:
                result.append(char)
            i += 1
            continue
        
        # If we're inside a string or char literal, preserve everything
        if in_string or in_char:
            result.append(char)
            i += 1
            continue
        
        # Handle multi-line comments
        if in_multiline_comment:
            if char == '*' and i + 1 < len(java_content) and java_content[i + 1] == '/':
                in_multiline_comment = False
                i += 2  # Skip both '*' and '/'
                continue
            else:
                # Preserve newlines to maintain line structure
                if char == '\n':
                    result.append(char)
                i += 1
                continue
        
        # Check for start of multi-line comment
        if char == '/' and i + 1 < len(java_content) and java_content[i + 1] == '*':
            in_multiline_comment = True
            i += 2  # Skip both '/' and '*'
            continue
        
        # Check for single-line comment
        if char == '/' and i + 1 < len(java_content) and java_content[i + 1] == '/':
            # Skip until end of line, but preserve the newline
            while i < len(java_content) and java_content[i] != '\n':
                i += 1
            if i < len(java_content):
                result.append(java_content[i])  # Add the newline
                i += 1
            continue
        
        # Regular character
        result.append(char)
        i += 1
    
    return ''.join(result)


# Example usage and test
if __name__ == "__main__":
    # Test the function
    with open('./BenchmarkTest.java', 'r') as file:
        java_code = file.read()
    
    print("=== ORIGINAL CODE ===")
    print(java_code)
    
    print("\n=== CODE WITH COMMENTS REMOVED ===")
    cleaned_code = remove_java_comments(java_code)
    print(cleaned_code)