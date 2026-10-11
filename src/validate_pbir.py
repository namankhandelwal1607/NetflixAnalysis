import json
import os
import re
import sys
import urllib.request
from jsonschema import Draft7Validator
from referencing import Registry, Resource

# Cached schemas
_cache = {}

def get_json(uri: str):
    if uri not in _cache:
        req = urllib.request.Request(uri, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            _cache[uri] = json.loads(resp.read().decode('utf-8'))
    return _cache[uri]

def retrieve(uri: str):
    return Resource.from_contents(get_json(uri))

registry = Registry(retrieve=retrieve)

VISUAL_SCHEMA_URL = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json'
PAGE_SCHEMA_URL = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json'
REPORT_SCHEMA_URL = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json'
PAGES_META_SCHEMA_URL = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json'

visual_validator = Draft7Validator(get_json(VISUAL_SCHEMA_URL), registry=registry)
page_validator = Draft7Validator(get_json(PAGE_SCHEMA_URL), registry=registry)
report_validator = Draft7Validator(get_json(REPORT_SCHEMA_URL), registry=registry)
pages_meta_validator = Draft7Validator(get_json(PAGES_META_SCHEMA_URL), registry=registry)

def load_model(semantic_model_dir):
    tables_dir = os.path.join(semantic_model_dir, 'definition', 'tables')
    model = {}
    for fname in os.listdir(tables_dir):
        if not fname.endswith('.tmdl') or fname.startswith('LocalDateTable') or fname.startswith('DateTable'):
            continue
        tname = fname[:-5]
        with open(os.path.join(tables_dir, fname), 'r', encoding='utf-8') as f:
            content = f.read()
        cols = re.findall(r'^\tcolumn\s+(?:(?:\'([^\']+)\')|([^\s\r\n]+))', content, re.MULTILINE)
        measures = re.findall(r'^\tmeasure\s+(?:(?:\'([^\']+)\')|([^\s\r\n]+))', content, re.MULTILINE)
        
        col_list = [c[0] or c[1] for c in cols]
        meas_list = [m[0] or m[1] for m in measures]
        model[tname] = {'columns': set(col_list), 'measures': set(meas_list)}
    return model

def extract_fields(obj, fields_found):
    if isinstance(obj, dict):
        if 'field' in obj and isinstance(obj['field'], dict):
            f = obj['field']
            if 'Column' in f:
                c = f['Column']
                entity = c.get('Expression', {}).get('SourceRef', {}).get('Entity')
                prop = c.get('Property')
                if entity and prop:
                    fields_found.append(('Column', entity, prop))
            elif 'Measure' in f:
                m = f['Measure']
                entity = m.get('Expression', {}).get('SourceRef', {}).get('Entity')
                prop = m.get('Property')
                if entity and prop:
                    fields_found.append(('Measure', entity, prop))
        for v in obj.values():
            extract_fields(v, fields_found)
    elif isinstance(obj, list):
        for item in obj:
            extract_fields(item, fields_found)

def validate_all(report_dir, model_dir):
    all_errors = []
    model = load_model(model_dir)
    
    # Validate report.json
    report_file = os.path.join(report_dir, 'definition', 'report.json')
    if os.path.exists(report_file):
        with open(report_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for err in report_validator.iter_errors(data):
            all_errors.append(f"report.json: {err.message} at path {list(err.path)}")
            
    # Validate pages.json
    pages_meta_file = os.path.join(report_dir, 'definition', 'pages', 'pages.json')
    if os.path.exists(pages_meta_file):
        with open(pages_meta_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for err in pages_meta_validator.iter_errors(data):
            all_errors.append(f"pages.json: {err.message} at path {list(err.path)}")
            
    # Validate each page
    pages_dir = os.path.join(report_dir, 'definition', 'pages')
    if os.path.exists(pages_dir):
        for page_name in os.listdir(pages_dir):
            pdir = os.path.join(pages_dir, page_name)
            if not os.path.isdir(pdir):
                continue
            page_file = os.path.join(pdir, 'page.json')
            if os.path.exists(page_file):
                with open(page_file, 'r', encoding='utf-8') as f:
                    pdata = json.load(f)
                for err in page_validator.iter_errors(pdata):
                    all_errors.append(f"page.json ({page_name}): {err.message} at path {list(err.path)}")
            
            # Validate visuals
            vdir = os.path.join(pdir, 'visuals')
            if os.path.exists(vdir):
                for vname in os.listdir(vdir):
                    v_file = os.path.join(vdir, vname, 'visual.json')
                    if os.path.exists(v_file):
                        with open(v_file, 'r', encoding='utf-8') as f:
                            vdata = json.load(f)
                        for err in visual_validator.iter_errors(vdata):
                            all_errors.append(f"visual.json ({page_name}/{vname}): {err.message} at path {list(err.path)}")
                        
                        # Validate fields exist in model
                        fields = []
                        extract_fields(vdata, fields)
                        for ftype, entity, prop in fields:
                            if entity not in model:
                                all_errors.append(f"Field error in {page_name}/{vname}: Entity '{entity}' not found in model.")
                            elif ftype == 'Column' and prop not in model[entity]['columns']:
                                all_errors.append(f"Field error in {page_name}/{vname}: Column '{prop}' not found in table '{entity}'.")
                            elif ftype == 'Measure' and prop not in model[entity]['measures']:
                                all_errors.append(f"Field error in {page_name}/{vname}: Measure '{prop}' not found in table '{entity}'.")
                            
    return all_errors

if __name__ == '__main__':
    rdir = sys.argv[1] if len(sys.argv) > 1 else 'powerbi/netflix_report/processedData.Report'
    mdir = sys.argv[2] if len(sys.argv) > 2 else 'powerbi/netflix_report/processedData.SemanticModel'
    errors = validate_all(rdir, mdir)
    if errors:
        print(f"Validation failed with {len(errors)} errors:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    else:
        print("All PBIR files and field references validated successfully! 0 errors.")
