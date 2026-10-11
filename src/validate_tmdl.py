import os
import re
from collections import defaultdict

def validate_tmdl_semantic_model(model_dir):
    tables_dir = os.path.join(model_dir, 'definition', 'tables')
    declared_tables = defaultdict(list)
    errors = []

    if not os.path.exists(tables_dir):
        return [f"Tables directory does not exist: {tables_dir}"]

    # 1. Check all table definitions in definition/tables
    for fname in sorted(os.listdir(tables_dir)):
        if fname.endswith('.tmdl'):
            p = os.path.join(tables_dir, fname)
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
            m = re.search(r'^table\s+([^\s\r\n]+)', content, re.MULTILINE)
            if m:
                tname = m.group(1)
                declared_tables[tname].append(fname)
            else:
                errors.append(f"File {fname} does not declare any table.")

    # Check for duplicate table declarations
    for tname, files in declared_tables.items():
        if len(files) > 1:
            errors.append(f"Duplicate declaration of table '{tname}' across files: {files}")

    # 2. Check model.tmdl ref table declarations vs declared tables
    model_file = os.path.join(model_dir, 'definition', 'model.tmdl')
    if os.path.exists(model_file):
        with open(model_file, 'r', encoding='utf-8') as f:
            model_content = f.read()
        ref_tables = re.findall(r'^ref\s+table\s+([^\s\r\n]+)', model_content, re.MULTILINE)
        
        # Check that all referenced tables exist
        for ref in ref_tables:
            if ref not in declared_tables:
                errors.append(f"model.tmdl references table '{ref}', but it is not declared in any .tmdl file.")
        
        # Check that all declared tables are referenced in model.tmdl
        for tname in declared_tables:
            if tname not in ref_tables:
                errors.append(f"Table '{tname}' is declared in {declared_tables[tname]}, but not referenced in model.tmdl.")

    # 3. Check relationships.tmdl
    rel_file = os.path.join(model_dir, 'definition', 'relationships.tmdl')
    if os.path.exists(rel_file):
        with open(rel_file, 'r', encoding='utf-8') as f:
            rel_content = f.read()
        from_cols = re.findall(r'fromColumn:\s+([^.\s\r\n\']+)\.', rel_content)
        to_cols = re.findall(r'toColumn:\s+([^.\s\r\n\']+)\.', rel_content)
        for t in from_cols + to_cols:
            if t not in declared_tables and not t.startswith('LocalDateTable') and not t.startswith('DateTable'):
                errors.append(f"relationships.tmdl references unknown table '{t}'.")

    return declared_tables, errors

if __name__ == '__main__':
    mdir = 'powerbi/netflix_report/processedData.SemanticModel'
    declared, errs = validate_tmdl_semantic_model(mdir)
    print("Declared tables in semantic model:")
    for tname, files in declared.items():
        status = "OK" if len(files) == 1 else "DUPLICATE ERROR"
        print(f"  [{status}] {tname}: {files}")
    
    print("\nValidation Results:")
    if errs:
        print(f"Found {len(errs)} error(s):")
        for e in errs:
            print(f"  - {e}")
    else:
        print("0 errors found. TMDL semantic model structure is clean and valid.")
