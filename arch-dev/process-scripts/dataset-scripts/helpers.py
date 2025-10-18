import re 
import os
import javalang
import javalang.tree
import json
'''
Funttions without a comment before defintions are verified to work well

'''

def extract_class_level_fields(java_source_code):
    

        tree = javalang.parse.parse(java_source_code)
        external_fields = []
   
        classDeclaration = tree.types[0]
        # Process all top-level classes in the file
       
                
        for node in classDeclaration.body:
                if isinstance(node, javalang.tree.FieldDeclaration):
                    # Get field modifiers
                    modifiers = ' '.join(node.modifiers) if node.modifiers else ''
                    
                    # Get field type with dimensions
                    type_name = node.type.name
                    if node.type.dimensions:
                        array_dims = '[]' * len(node.type.dimensions)
                        type_name += array_dims
                        
                    # Handle generic types
                    if hasattr(node.type, 'arguments') and node.type.arguments:
                        args_list = []
                        for arg in node.type.arguments:
                            # Handle nested generics
                            if hasattr(arg, 'type') and hasattr(arg.type, 'name'):
                                if hasattr(arg.type, 'arguments') and arg.type.arguments:
                                    nested_args = []
                                    for nested_arg in arg.type.arguments:
                                        if hasattr(nested_arg, 'type') and hasattr(nested_arg.type, 'name'):
                                            nested_args.append(nested_arg.type.name)
                                    if nested_args:
                                        args_list.append(f"{arg.type.name}<{', '.join(nested_args)}>")
                                    else:
                                        args_list.append(arg.type.name)
                                else:
                                    args_list.append(arg.type.name)
                        type_name = f"{type_name}<{', '.join(args_list)}>"
                    
                    # Process each declarator in a multi-variable declaration
                    for declarator in node.declarators:
                        name = declarator.name
                        
                        # Handle array dimensions on variable name
                        if hasattr(declarator, 'dimensions') and declarator.dimensions:
                            array_dims = '[]' * len(declarator.dimensions)
                            name += array_dims
                        
                        # Handle initializers
                        initializer = ''
                        if declarator.initializer:
                            # Try to capture the full initializer from source
                            # Find line range for initializer
                            if hasattr(declarator.initializer, 'position') and declarator.initializer.position:
                                init_pos = declarator.initializer.position
                                line_start = init_pos.line - 1
                                
                                # Find the whole initializer
                                lines = java_source_code.splitlines()
                                if line_start < len(lines):
                                    line = lines[line_start]
                                    var_name_pos = line.find(name)
                                    equal_pos = line.find('=', var_name_pos) if var_name_pos != -1 else line.find('=')
                                    
                                    if equal_pos != -1:
                                        # Try to find end of initializer (semicolon)
                                        semi_pos = line.find(';', equal_pos)
                                        
                                        if semi_pos != -1:
                                            # Single line initializer
                                            initializer = f" = {line[equal_pos+1:semi_pos].strip()}"
                                        else:
                                            # Multi-line initializer - we need to search forward
                                            init_text = line[equal_pos+1:].strip()
                                            brace_count = init_text.count('{') - init_text.count('}')
                                            paren_count = init_text.count('(') - init_text.count(')')
                                            
                                            # Continue reading lines until we find the end of the initializer
                                            current_line = line_start + 1
                                            while (current_line < len(lines) and 
                                                  (brace_count > 0 or paren_count > 0 or ';' not in init_text)):
                                                next_line = lines[current_line].strip()
                                                init_text += " " + next_line
                                                brace_count += next_line.count('{') - next_line.count('}')
                                                paren_count += next_line.count('(') - next_line.count(')')
                                                
                                                if ';' in next_line and brace_count <= 0 and paren_count <= 0:
                                                    init_text = init_text[:init_text.find(';')]
                                                    break
                                                    
                                                current_line += 1
                                                
                                            initializer = f" = {init_text}"
                        
                        # Construct final field declaration
                        field_str = f"{modifiers} {type_name} {name}{initializer};".replace("  ", " ").strip()
                        external_fields.append(field_str)
                
         
        return external_fields


def remove_comments_from_code(java_code):
            java_code = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", java_code)
            java_code = re.sub(re.compile("//.*?\n"),  "", java_code)
            return java_code

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
def allman_to_knr_representation(contents):
        s, contents = [], contents.split("\n")
        line = 0
        while line < len(contents):
            if contents[line].strip() == "{":
                s[-1] = s[-1].rstrip() + " {"
            else:
                s.append(contents[line])
            line += 1
        return "\n".join(s)

# not verified if it works 
def extract_helper_methods(code, bad_body):
    helper_methods = []
    # Capture all private/public non-bad/good methods
    method_defs = re.findall(
        r'(public|private|protected)?\s+[\w<>]+\s+(\w+)\s*\([^)]*\)\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
        code,
        re.DOTALL
    )
    used_methods = re.findall(r'(\w+)\s*\(', bad_body)

    for full_match in method_defs:
        method_name = full_match[1]
        if method_name not in ["bad", "good"] and method_name in used_methods:
            full_text = re.search(
                rf'(public|private|protected)?\s+[\w<>]+\s+{method_name}\s*\([^)]*\)\s*\{{[^{{}}]*(?:\{{[^{{}}]*\}}[^{{}}]*)*\}}',
                code,
                re.DOTALL
            )
            if full_text:
                helper_methods.append(full_text.group(0))
    return "\n\n".join(helper_methods)

def extract_post_method(code):
    annotations =  False
    lines = code.splitlines()
    in_post_def = False
    brace_count = 0
    method = []
    bad_start_line = -1
    for i, line in enumerate(lines):
        # check for @override Singature
        line_stripped = line.strip()
        if not in_post_def and not annotations and line_stripped == "@Override":
            annotations = True
            method.append(line_stripped)
            continue

        if (not in_post_def and (re.match(r'\s*public\s+void\s+doPost\s*\(', line) or (annotations and re.match(r'\s*public\s+void\s+doPost\s*\(', line)))):
            in_post_def = True
            bad_start_line = i
            brace_count += line.count('{') - line.count('}')
            method.append(line.lstrip())  # Remove leading whitespace
        elif in_post_def:
            method.append(line)
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                break
        elif annotations and line_stripped and not line_stripped.startswith("//"):
            if not re.match(r'\s*public\s+void\s+doPost\s*\(', line):
                annotations = False
                method = []
    if method and in_post_def:
        return "\n".join(method)
    return None
def extract_bad_method(code):
    
    lines = code.splitlines()
    in_bad_def = False
    brace_count = 0
    method = []
    bad_start_line = -1

    # First extract the bad method
    for i, line in enumerate(lines):
        if not in_bad_def and re.match(r'\s*public\s+void\s+bad\s*\(', line):
            in_bad_def = True
            bad_start_line = i
            brace_count += line.count('{') - line.count('}')
            method.append(line.lstrip())  # Remove leading whitespace
        elif in_bad_def:
            method.append(line)
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                break

    # If we found a bad method, check if it only calls helperBad
    if method:
        bad_method_text = "\n".join(method)
        
        # Check for helperBad calls
        helper_bad_calls = re.findall(r'\bhelperBad\s*\(', bad_method_text)
        
        # Check for substantive code lines (ignoring trivial lines)
        # Count non-trivial lines that are not just helperBad calls, braces, or comments
        substantive_lines = 0
        for line in method:
            stripped = line.strip()
            # Skip empty lines, lone braces, and helper calls
            if (stripped and 
                stripped != "{" and 
                stripped != "}" and 
                not re.match(r'\s*helperBad\s*\(.*\)\s*;', stripped) and
                not re.match(r'\s*\/\/.*', stripped)):
                substantive_lines += 1
        
        # If there are helperBad calls and very little substantive code, skip this method
        if helper_bad_calls and substantive_lines < 4:  # Adjust threshold as needed
            return None
            
        return bad_method_text
    
    return None
def extract_good_methods(code):
    good_methods_patterns = [
        r'\s*private\s+void\s+goodB2G\d*\s*\(',
        r'\s*private\s+void\s+goodG2B\d*\s*\(',
        r'\s*private\s+void\s+good\d+\s*\(', 
    ] 
    
    lines = code.splitlines()
    b2g_methods, g2b_methods, good_methods = [], [], []
    helperGood_pattern = r'\bhelperGood(B2G|G2B)?\d*\s*\('
    in_good_method_def = False
    patterns_with_types = [
        # First priority: goodB2G* methods
        {
            "pattern": r'\s*private\s+void\s+goodB2G\d*\s*\(',
            "storage": b2g_methods
        },
        # Second priority: goodG2B* methods
        {
            "pattern": r'\s*private\s+void\s+goodG2B\d*\s*\(',
            "storage": g2b_methods
        },
        # Lowest priority: generic good methods
        {
            "pattern": r'\s*private\s+void\s+good\d+\s*\(',
            "storage": good_methods
        }
    ]
    for pattern_info in patterns_with_types:
        pattern = pattern_info["pattern"]
        storage = pattern_info["storage"]
        
        for i, line in enumerate(lines):
            if re.match(pattern, line):
                # Found a matching method
                in_good_method_def = True
                brace_count = line.count('{') - line.count('}')
                method = [line.lstrip()]  # Remove leading whitespace
                
                # Continue from next line
                j = i + 1
                while j < len(lines) and in_good_method_def:
                    current_line = lines[j]
                    method.append(current_line)
                    brace_count += current_line.count('{') - current_line.count('}')
                    
                    # Check if we've reached the end of the method
                    if brace_count == 0:
                        good_method_text = "\n".join(method)
                        helper_calls = re.findall(helperGood_pattern, good_method_text)
                        substantive_lines = 0
                        for line in method:
                            stripped = line.strip()
                            # Skip empty lines, lone braces, helper calls, and comments
                            if (stripped and 
                                stripped != "{" and 
                                stripped != "}" and 
                                not re.match(r'\s*helperGood(?:G2B|B2G)?\d*\s*\(.*\)\s*;', stripped) and
                                not re.match(r'\s*\/\/.*', stripped)):
                                substantive_lines += 1
                        
                        # If there are helper calls and very little substantive code, skip this method
                        if helper_calls and substantive_lines < 4:  # Same threshold as bad method
                            print(f"Skipping good method that primarily calls helper methods ({len(helper_calls)} calls)")
                        else:
                            storage.append(good_method_text)
                            
                        in_good_method_def = False
                        break
                    j += 1
    
    if good_methods:
        return good_methods
    else:
        return b2g_methods + g2b_methods
    
    """ In case you want to remove   or keep goodG2B methods
    elif len(b2g_methods) == 2:
        return b2g_methods
    elif len(b2g_methods) == 1:
        return b2g_methods + [g2b_methods[0]] 
    """

def extract_imports(java_source_code):

 """  
 tree = javalang.parse.parse(java_source_code)
    for item in tree.imports:
        if hasattr(item, 'path')  and "java." in item.path:
            imports.append(f"import {item.path};")
    return imports if imports else None
      """
 imports = []
 for line in java_source_code.splitlines():
        line = line.strip()
        if line.startswith("import java"):
            imports.append(line)
 return "\n".join(imports) if imports else None

def create_class_code(class_name, method):      
    class_parts = [
            f"public class {class_name} {{",
            f"{method}",
            "}"
        ]


    return "\n\t".join(class_parts)
    #return "\n".join(parts)
    #return method_text
""" def create_class_code(class_name, method):

    # Check if method starts with annotations (like @Override)
    lines = method.strip().split('\n')
    annotations = []
    
    # Extract any annotations that precede the method
    while lines and lines[0].strip().startswith("@"):
        annotations.append(lines[0].strip())
        lines.pop(0)
    
    # Indent the method body correctly
    indented_method_lines = []
    
    # Add back annotations
    for annotation in annotations:
        indented_method_lines.append(f"        {annotation}")
    
    # Add remaining method lines with proper indentation
    for i, line in enumerate(lines):
        indented_method_lines.append(f"    {line}")
    
    # Combine into the final class
    parts = [
        f"public class {class_name} {{",
        "\n".join(indented_method_lines),
        "}"
    ]
    
    return "\n".join(parts) """

def construct_cwe_folder_name(name):
    return name.replace(" ", "_").replace(":", "")
# Add a Helper Function that find the java file with big numner in name of an incremental counter 
def construct_java_file(counter):
    return {
        "filename": f"Sample_{counter}.java",
        "function_name": f"func_{counter}",
    }
def rename_method(method_code, new_method_name):
# Check if this is a 'bad' method
    if re.match(r'\s*public\s+void\s+bad\s*\(', method_code):
        renamed_method = re.sub(
            r'(public\s+void\s+)bad(\s*\()',
            f'\\1{new_method_name}\\2',
            method_code
        )
    # Check if this is a 'good' method (goodG2B* or goodB2G*)
    elif re.match(r'\s*private\s+void\s+good(?:G2B|B2G)\d*\s*\(', method_code):
        # Change 'private' to 'public' and rename the method
        renamed_method = re.sub(
            r'(private\s+void\s+)good(?:G2B|B2G)\d*(\s*\()',
            f'public void {new_method_name}\\2',
            method_code
        )
    # Default case - just attempt to rename whatever method name is found
    else:
        renamed_method = re.sub(
            r'((public|private|protected)\s+)([\w<>[\].,\s]+?)(\s+\w+)(\s*\()',
            f'\\1\\3 {new_method_name}\\5',
            method_code
        )
    
    return renamed_method
def append_func_toJson(json_file_path, function_code, target, cwe_id):
    json_entry = {
        "function": function_code,
        "target": target,
        "cwe": cwe_id,
    }
    with open(json_file_path, 'a', encoding='utf-8') as jsonl_file:
        jsonl_file.write(json.dumps(json_entry) + '\n')
def find_last_counter(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        lines = json_file.readlines()
        return len(lines)

    

if __name__ == "__main__":
    #print(find_last_counter("../vul-llm-finetuning/llm_finetuning.jsonl"))
    with open("/home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/data/BenchmarkJava/src/main/java/org/owasp/benchmark/testcode/BenchmarkTest02379.java", "r", encoding="utf-8") as f:
        code = f.read()
        new_code = remove_comments_from_code(code)
        print(new_code)

