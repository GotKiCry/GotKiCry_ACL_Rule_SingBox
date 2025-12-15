import yaml
import requests
import os
import sys

def update_rules(config_path):
    print(f"Reading config from {config_path}...")
    
    # Check if config_path is a URL
    if config_path.startswith('http://') or config_path.startswith('https://'):
        try:
            print(f"Downloading config from {config_path}...")
            response = requests.get(config_path, timeout=30)
            response.raise_for_status()
            config = yaml.safe_load(response.text)
            
            # Save strictly for reference/caching, but we work from memory/response usually.
            # However, generate_json.py reads a local file. So we MUST save it locally.
            local_filename = "ACL4SSR_Online_Full_WithIcon.yaml"
            with open(local_filename, 'wb') as f:
                f.write(response.content)
            print(f"Saved config to {local_filename}")
            
        except Exception as e:
             print(f"Error downloading config: {e}")
             sys.exit(1)
    else:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"Error reading config file: {e}")
            sys.exit(1)

    if 'rule-providers' not in config:
        print("No rule-providers found in config.")
        return

    providers = config['rule-providers']
    
    # Ensure the root directory for relative paths is the repo root
    # Assuming script is run from repo root or we adjust paths
    # The config paths are like ./ruleset/xxx.list
    
    for name, details in providers.items():
        # Get source URL (upstream) if available, otherwise fallback to url
        url = details.get('source') or details.get('url')
        path = details.get('path')
        
        if not url or not path:
            print(f"Skipping {name}: Missing url or path")
            continue
            
        print(f"Updating {name} from {url}...")
        
        try:
            # Create directory if it doesn't exist
            dir_name = os.path.dirname(path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
                
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Write content to file
            with open(path, 'wb') as f:
                f.write(response.content)
                
            print(f"Successfully updated {name} to {path}")
            
        except Exception as e:
            print(f"Failed to update {name}: {e}")

if __name__ == "__main__":
    # Assuming config is in the root directory relative to where script is run
    # If script is in scripts/ and run from root, config is ./ACL4SSR_Online_Full_WithIcon.yaml
    CONFIG_FILE = "https://raw.githubusercontent.com/GotKiCry/GotKiCry_ACL_Rule/master/ACL4SSR_Online_Full_WithIcon.yaml"
    
    # Logic to handle local vs remote check
    if not CONFIG_FILE.startswith('http') and not os.path.exists(CONFIG_FILE):
        print(f"Config file {CONFIG_FILE} not found!")
        sys.exit(1)
        
    update_rules(CONFIG_FILE)
