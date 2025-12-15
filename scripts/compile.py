import os
import json
import subprocess
import glob

def parse_list_file(file_path):
    rules = {
        "domain": [],
        "domain_suffix": [],
        "domain_keyword": [],
        "ip_cidr": [],
        "process_name": []
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(',')
            if len(parts) < 2:
                continue
                
            rule_type = parts[0].strip().upper()
            value = parts[1].strip()
            
            if rule_type == 'DOMAIN-SUFFIX':
                rules['domain_suffix'].append(value)
            elif rule_type == 'DOMAIN-KEYWORD':
                rules['domain_keyword'].append(value)
            elif rule_type == 'DOMAIN':
                rules['domain'].append(value)
            elif rule_type == 'IP-CIDR' or rule_type == 'IP-CIDR6':
                rules['ip_cidr'].append(value)
            elif rule_type == 'PROCESS-NAME':
                rules['process_name'].append(value)
                
    return rules

def create_singbox_json(rules):
    srs_rules = []
    
    # We create a single rule entry containing all criteria
    # Sing-box rule-set structure allows combining fields
    rule_entry = {}
    
    if rules['domain']:
        rule_entry['domain'] = rules['domain']
    if rules['domain_suffix']:
        rule_entry['domain_suffix'] = rules['domain_suffix']
    if rules['domain_keyword']:
        rule_entry['domain_keyword'] = rules['domain_keyword']
    if rules['ip_cidr']:
        rule_entry['ip_cidr'] = rules['ip_cidr']
    if rules['process_name']:
        rule_entry['process_name'] = rules['process_name']
        
    if rule_entry:
        srs_rules.append(rule_entry)
        
    return {
        "version": 1,
        "rules": srs_rules
    }

def compile_rules(rule_dir):
    if not os.path.exists(rule_dir):
        print(f"Rule directory {rule_dir} does not exist.")
        return

    list_files = glob.glob(os.path.join(rule_dir, '*.list'))
    print(f"Found {len(list_files)} list files in {rule_dir}")

    for list_file in list_files:
        filename = os.path.basename(list_file)
        name_without_ext = os.path.splitext(filename)[0]
        json_file = os.path.join(rule_dir, f"{name_without_ext}.json")
        srs_file = os.path.join(rule_dir, f"{name_without_ext}.srs")
        
        print(f"Processing {filename}...")
        
        try:
            rules_content = parse_list_file(list_file)
            singbox_json = create_singbox_json(rules_content)
            
            # Skip if no valid rules found
            if not singbox_json['rules']:
                print(f"  No valid rules found in {filename}, skipping.")
                continue

            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(singbox_json, f, indent=2, ensure_ascii=False)
            
            # Compile using sing-box
            # Assuming 'sing-box' is in PATH. 
            # If verify fails locally (no binary), it's fine, the Action will run it.
            cmd = ['sing-box', 'rule-set', 'compile', json_file, '-o', srs_file]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"  Compiled to {name_without_ext}.srs")
            
            # Clean up JSON file
            os.remove(json_file)
            
        except subprocess.CalledProcessError as e:
            print(f"  Compilation failed for {filename}: {e.stderr.decode()}")
        except Exception as e:
            print(f"  Error processing {filename}: {e}")

if __name__ == "__main__":
    compile_rules('./ruleset')
