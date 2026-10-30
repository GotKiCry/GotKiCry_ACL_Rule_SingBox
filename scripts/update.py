#!/usr/bin/env python3
"""从上游 ACL4SSR 配置同步 rule-providers 对应的 .list 规则文件。

数据源: https://github.com/GotKiCry/GotKiCry_ACL_Rule
输出:   ./ruleset/<name>.list （并按需下载 ACL4SSR_Online_Full_WithIcon.yaml 供 generate_json.py 使用）

任意一个规则文件下载失败都会以非 0 退出，避免"静默缺规则"。
"""
import os
import sys

import requests
import yaml

CONFIG_URL = "https://raw.githubusercontent.com/GotKiCry/GotKiCry_ACL_Rule/master/ACL4SSR_Online_Full_WithIcon.yaml"
LOCAL_YAML = "ACL4SSR_Online_Full_WithIcon.yaml"
TIMEOUT = 30


def fetch_config(url):
    print(f"Downloading config from {url} ...")
    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    with open(LOCAL_YAML, "wb") as f:
        f.write(resp.content)
    print(f"Saved config to {LOCAL_YAML} ({len(resp.content)} bytes)")
    return yaml.safe_load(resp.text)


def update_rules(config):
    providers = config.get("rule-providers") or {}
    if not providers:
        print("ERROR: no rule-providers found in config")
        return False

    print(f"Found {len(providers)} rule providers")
    failed = []
    for name, details in providers.items():
        url = details.get("source") or details.get("url")
        path = details.get("path")
        if not url or not path:
            print(f"  SKIP {name}: missing url/path")
            failed.append(name)
            continue
        try:
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            resp = requests.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            if not resp.content:
                raise ValueError("empty response")
            with open(path, "wb") as f:
                f.write(resp.content)
            print(f"  OK   {name} -> {path} ({len(resp.content)} bytes)")
        except Exception as exc:
            print(f"  FAIL {name}: {exc}")
            failed.append(name)

    if failed:
        print(f"ERROR: {len(failed)} rule(s) failed: {', '.join(failed)}")
        return False
    print(f"All {len(providers)} rule lists updated")
    return True


def main():
    try:
        config = fetch_config(CONFIG_URL)
    except Exception as exc:
        print(f"ERROR: failed to fetch config: {exc}")
        return 1
    return 0 if update_rules(config) else 1


if __name__ == "__main__":
    sys.exit(main())
