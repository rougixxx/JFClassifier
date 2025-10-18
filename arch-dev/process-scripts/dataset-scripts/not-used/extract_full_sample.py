import os
import re

# ✅ Settings
JULIET_SRC = "/path/to/Juliet_Test_Suite_Java"
DEST_DIR = "jfinder_ready_dataset"
METHOD_TYPE = "bad"  # or "good"

# ✅ Known source/sink method patterns
KNOWN_SOURCES = ["getParameter", "readLine", "getInputStream"]
KNOWN_SINKS = ["exec", "print", "write", "println", "executeQuery"]

def get_imports(code):
    return "\n".join(re.findall(r'^\s*import\s+.*;', code, re.MULTILINE))

def get_class_fields(code):
    return "\n".join(re.findall(r'\s*(private|public|protected)?\s+\w+(\[\])?\s+\w+\s*=\s*[^;]+;', code))

def extract_method(code, name):
    lines = code.splitlines()
    in_method, brace_count = False, 0
    body = []

    for line in lines:
        if not in_method and re.match(rf'\s*public\s+void\s+{name}\s*\(', line):
            in_method = True
            brace_count += line.count('{') - line.count('}')
            body.append(line)
        elif in_method:
            body.append(line)
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                break
    return "\n".join(body)

def get_called_helpers(method_body):
    return set(re.findall(r'(\w+)\s*\(', method_body)) - {METHOD_TYPE}

def extract_helper_methods(code, called_methods):
    helper_code = []
    for method in called_methods:
        match = re.search(
            rf'(public|private|protected)?\s+\w+[\s<>\w]*\s+{method}\s*\([^)]*\)\s*\{{[\s\S]*?\n\}}',
            code,
            re.MULTILINE
        )
        if match:
            helper_code.append(match.group(0))
    return "\n\n".join(helper_code)

def wrap_sample(imports, fields, method_body, helpers, class_name):
    parts = [
        imports,
        f"public class {class_name} {{",
        fields,
        method_body,
        helpers,
        "}"
    ]
    return "\n\n".join([p for p in parts if p.strip()])

def contains_source_or_sink(method_body):
    return any(api in method_body for api in KNOWN_SOURCES + KNOWN_SINKS)

def process():
    os.makedirs(DEST_DIR, exist_ok=True)
    count = 0

    for root, _, files in os.walk(JULIET_SRC):
        for file in files:
            if not file.endswith(".java"):
                continue

            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()

                if f'void {METHOD_TYPE}(' not in code:
                    continue

                imports = get_imports(code)
                fields = get_class_fields(code)
                method_body = extract_method(code, METHOD_TYPE)
                if not contains_source_or_sink(method_body):
                    continue  # filter to keep real flow

                called_helpers = get_called_helpers(method_body)
                helpers = extract_helper_methods(code, called_helpers)
                wrapped = wrap_sample(imports, fields, method_body, helpers, os.path.splitext(file)[0])

                out_path = os.path.join(DEST_DIR, f"{METHOD_TYPE}_sample_{str(count).zfill(5)}.java")
                with open(out_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(wrapped)
                count += 1
                print(f"✅ Saved {out_path}")

            except Exception as e:
                print(f"❌ Error processing {file}: {e}")

if __name__ == "__main__":
    process()
