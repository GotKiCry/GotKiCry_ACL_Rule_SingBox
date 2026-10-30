import yaml
import json
import os

# User provided template (stripped of dynamic parts)
# 可配合 ShellCrash 等第三方客户端的本地 DNS (如 MosDNS/AdGuardHome) 使用
# 格式示例: {"type": "udp", "server": "127.0.0.1", "server_port": 1053}
# 如果设置了此项，内置的 Google/Ali/FakeIP 分流将被禁用，所有 DNS 流量指向此服务器
CUSTOM_DNS_SERVER = None 

TEMPLATE = {
  "log": {
    "level": "info",
    "timestamp": True
  },
  "ntp": {
    "enabled": True,
    "server": "time.apple.com",
    "server_port": 123,
    "interval": "30m0s"
  },
  "experimental": {
    "cache_file": {
      "enabled": True,
      "store_fakeip": True,
      "store_rdrc": True
    },
    "clash_api": {
      "external_controller": "127.0.0.1:9090",
      "access_control_allow_origin": [
        "http://127.0.0.1",
        "https://yacd.metacubex.one",
        "https://metacubex.github.io",
        "https://metacubexd.pages.dev",
        "https://board.zash.run.place"
      ]
    }
  },
  "dns": {
    "independent_cache": True,
    "strategy": "prefer_ipv4",
    "servers": [
      {
        "tag": "google",
        "type": "https",
        "server": "8.8.8.8"
      },
      {
        "tag": "ali",
        "type": "https",
        "server": "223.5.5.5"
      },
      {
        "tag": "fakeip",
        "type": "fakeip",
        "inet4_range": "198.18.0.0/15",
        "inet6_range": "fc00::/18"
      }
    ],
    "rules": [
      {
        "rule_set": "ProxyDNS",
        "server": "google"
      },
      {
        "rule_set": [
          "ChinaDomain",
          "CNDNS",
          "geoip-cn"
        ],
        "server": "ali"
      },
      {
        "query_type": [
          "A",
          "AAAA"
        ],
        "server": "fakeip"
      },
      {
        "server": "google"
      }
    ]
  },
  "inbounds": [
    {
      "type": "tun",
      "tag": "tun-in",
      "interface_name": "tun0",
      "address": [
        "172.19.0.1/30",
        "fdfe:dcba:9876::1/126"
      ],
      "mtu": 9000,
      "auto_route": True,
      "strict_route": True,
      "stack": "mixed",
      "endpoint_independent_nat": True,
    },
    {
      "type": "mixed",
      "tag": "mixed-in",
      "listen": "::",
      "listen_port": 7890,
      "set_system_proxy": False
    }
  ],
  "outbounds": [], # To be populated
  "route": {
    "default_domain_resolver": {
      "server": "ali"
    },
    "auto_detect_interface": True,
    "rules": [],    # To be populated
    "rule_set": []  # To be populated
  }
}

YAML_FILE = 'ACL4SSR_Online_Full_WithIcon.yaml'
# This base URL points to the raw files in the repo we are pushing to
REPO_BASE_URL = "https://raw.githubusercontent.com/GotKiCry/GotKiCry_ACL_Rule_SingBox/master/ruleset/"

def main():
    # 0. Apply Custom DNS if configured
    default_resolver = "ali"
    if CUSTOM_DNS_SERVER:
        default_resolver = "local"
        print(f"Using Custom Local DNS: {CUSTOM_DNS_SERVER}")
        TEMPLATE['dns']['servers'] = [
            {
                "tag": "local",
                "type": CUSTOM_DNS_SERVER.get('type', 'udp'),
                "server": CUSTOM_DNS_SERVER['server'],
                "server_port": CUSTOM_DNS_SERVER.get('server_port', 53)
            }
        ]
        TEMPLATE['dns']['rules'] = [
            {
                "server": "local"
            }
        ]
        TEMPLATE['route']['default_domain_resolver']['server'] = 'local'
    else:
        # For the non-custom case, ensure references in rules match the tag
        # Actually it's already "ali" in the TEMPLATE definition.
        pass

    print(f"Reading {YAML_FILE}...")
    with open(YAML_FILE, 'r', encoding='utf-8') as f:
        y = yaml.safe_load(f)

    # 1. Generate Outbounds from proxy-groups
    outbounds = []
    # Always add a base Direct/Block
    outbounds.append({"tag": "直连", "type": "direct"})
    outbounds.append({"tag": "REJECT", "type": "block"})
    
    # Name mapping for Sub-Store script compatibility
    MAPPING = {
        # Existing
        "节点选择": "🚀 节点选择",
        "手动选择": "👉 手动选择",
        "手动切换": "👉 手动选择",
        "漏网之鱼": "🐟 漏网之鱼",
        "自动选择": "♻️ 自动选择",
        "GLOBAL": "GLOBAL",
        
        # New
        "电报消息": "📲 电报消息",
        "OpenAi": "🤖 OpenAi",
        "油管视频": "📹 油管视频",
        "奈飞视频": "🎥 奈飞视频",
        "巴哈姆特": "🎮 巴哈姆特",
        "哔哩哔哩": "📺 哔哩哔哩",
        "国外媒体": "🌍 国外媒体",
        "国内媒体": "🌏 国内媒体",
        "谷歌FCM": "📢 谷歌FCM",
        "微软Bing": "🔍 微软Bing",
        "微软云盘": "☁️ 微软云盘",
        "微软服务": "Ⓜ️ 微软服务",
        "苹果服务": "🍎 苹果服务",
        "Steam下载": "⬇️ Steam下载",
        "游戏平台": "🎮 游戏平台",
        "网易音乐": "🎵 网易音乐",
        "全球直连": "🎯 全球直连",
        "广告拦截": "🛑 广告拦截",
        "应用净化": "🛡️ 应用净化",
        "香港节点": "🇭🇰 香港节点",
        "日本节点": "🇯🇵 日本节点",
        "美国节点": "🇺🇸 美国节点",
        "台湾节点": "🇹🇼 台湾节点",
        "狮城节点": "🇸🇬 狮城节点",
        "韩国节点": "🇰🇷 韩国节点",
        "奈飞节点": "🎥 奈飞节点"
    }
    
    # Define groups to ignore (Regions + Netflix Node which is usually a sub-group)
    IGNORED_GROUPS = [
        "香港节点", "日本节点", "美国节点", "台湾节点", 
        "狮城节点", "韩国节点", "奈飞节点"
    ]

    if 'proxy-groups' in y:
        for pg in y['proxy-groups']:
            name = pg['name']
            pg_type = pg['type']
            proxies = pg.get('proxies', [])
            
            # Skip ignored groups
            if name in IGNORED_GROUPS:
                continue

            # Map name
            mapped_name = MAPPING.get(name, name)
            
            # Map types
            sb_type = 'selector'
            if pg_type == 'url-test':
                sb_type = 'urltest'
            elif pg_type == 'select':
                sb_type = 'selector'
            else:
                sb_type = 'selector' # Fallback
            
            # Map proxies list
            sb_outbounds = []
            for p in proxies:
                # Skip references to ignored groups
                if p in IGNORED_GROUPS:
                    continue

                if p == 'DIRECT':
                    sb_outbounds.append('直连')
                elif p == 'REJECT':
                    sb_outbounds.append('REJECT')
                else:
                    # Map references too
                    sb_outbounds.append(MAPPING.get(p, p))
            
            outbound_entry = {
                "tag": mapped_name,
                "type": sb_type,
                "outbounds": sb_outbounds
            }
            
            # Add Sub-Store hint
            # User wants "🚀 节点选择" to exclude individual nodes.
            # "手动选择", "漏网之鱼", "自动选择" and "GLOBAL" should include all.
            # UPDATE: User removed regions, so "🚀 节点选择" MUST now use all providers to see nodes.
            if mapped_name in ["👉 手动选择", "🐟 漏网之鱼", "♻️ 自动选择", "GLOBAL", "🚀 节点选择"]:
                if os.environ.get("SUBSTORE_HINT", "0") == "1":
                    outbound_entry["use_all_providers"] = True
            
            if pg_type == 'url-test':
                # Add interval/tolerance if present, with defaults
                outbound_entry['interval'] = str(pg.get('interval', 300)) + 's'
                outbound_entry['tolerance'] = pg.get('tolerance', 50)
            
            # Ensure not empty to avoid SingBox "missing tags" error
            if not sb_outbounds and not outbound_entry.get("use_all_providers"):
                sb_outbounds.append('直连')
                
            outbounds.append(outbound_entry)
            
    TEMPLATE['outbounds'] = outbounds

    # 2. Generate Rule Sets from rule-providers
    rule_sets = []
    # Add anti-ad manually or from config? 
    # The user manual example has anti-ad. We'll stick to YAML providers.
    
    if 'rule-providers' in y:
        for name, info in y['rule-providers'].items():
            # Construct remote URL
            # We assume all are synchronized to our repo's Rule/ directory as .srs
            # The name in `rules` references this provider key
            
            # Note: We use the KEY as the tag
            rs = {
                "tag": name,
                "type": "remote",
                "format": "binary",
                "url": f"{REPO_BASE_URL}{name}.srs",
                "download_detour": "直连" 
            }
            rule_sets.append(rs)

    # Add default GeoIP CN rule set
    rule_sets.append({
        "tag": "geoip-cn",
        "type": "remote",
        "format": "binary",
        "url": "https://cdn.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geoip/cn.srs",
        "download_detour": "直连"
    })
            
    TEMPLATE['route']['rule_set'] = rule_sets

    # 3. Generate Route Rules from rules
    route_rules = []
    
    # Add some default rules from the user example (sniff, hijack, private ip, anti-ad)
    # We can add them at the BEGINNING
    route_rules.extend([
      {"action": "sniff"},
      {"protocol": "dns", "action": "hijack-dns"},
      {"ip_is_private": True, "outbound": "直连"},
      {"clash_mode": "Direct", "outbound": "直连"},
      {"clash_mode": "Global", "outbound": "🚀 节点选择"} # Assuming '🚀 节点选择' is the main group
    ])

    if 'rules' in y:
        for rule_line in y['rules']:
            # Format: TYPE,VALUE,TARGET
            # Example: RULE-SET,LocalAreaNetwork,全球直连
            parts = rule_line.split(',')
            if len(parts) >= 3:
                r_type = parts[0].strip()
                r_val = parts[1].strip()
                r_target = parts[2].strip()
                
                # Setup target outbound
                if r_target == 'DIRECT':
                    target = '直连'
                elif r_target == 'REJECT':
                    target = 'REJECT'
                elif r_target in IGNORED_GROUPS:
                    # Redirect removed regions to main selector
                    target = '🚀 节点选择'
                else:
                    target = MAPPING.get(r_target, r_target)
                
                entry = {"outbound": target}
                
                if r_type == 'RULE-SET':
                    entry['rule_set'] = r_val
                elif r_type == 'DOMAIN-SUFFIX':
                    entry['domain_suffix'] = [r_val]
                elif r_type == 'DOMAIN-KEYWORD':
                    entry['domain_keyword'] = [r_val]
                elif r_type == 'IP-CIDR' or r_type == 'IP-CIDR6':
                    entry['ip_cidr'] = [r_val]
                if r_type == 'GEOIP':
                    # SingBox 1.8.0+ deprecated 'geoip' rules in favor of rule sets
                    if r_val == 'CN':
                        entry['rule_set'] = 'geoip-cn'
                    else:
                        # Fallback for other countries (might need specific rule sets)
                        # Currently we only support CN. Skip to avoid creating a "match-all" rule.
                        print(f"Warning: Skipping unsupported GEOIP rule: {rule_line}")
                        continue
                        
                elif r_type == 'MATCH':
                     # Explicit match rule
                     pass
                
                # ... support other types if needed
                
                route_rules.append(entry)
                
    TEMPLATE['route']['rules'] = route_rules
    TEMPLATE['route']['final'] = '🚀 节点选择'
    # Write config.json
    print("Writing config.json...")
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(TEMPLATE, f, indent=2, ensure_ascii=False)
    print("Done.")

if __name__ == '__main__':
    main()
