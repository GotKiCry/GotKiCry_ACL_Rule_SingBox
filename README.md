# GotKiCry ACL Rule for SingBox

把 [GotKiCry/GotKiCry_ACL_Rule](https://github.com/GotKiCry/GotKiCry_ACL_Rule) 的 Clash 规则**全自动**编译成 sing-box 原生 `.srs` 规则集，并生成一份可直接使用的 `config.json`。

## 自动同步机制

| 项 | 值 |
| :--- | :--- |
| 触发时间 | 每天 **UTC 03:00**（北京时间 11:00） |
| 上游更新 | GotKiCry_ACL_Rule 每天 UTC 02:00 同步 ACL4SSR，本仓库 1 小时后跟进 |
| 手动触发 | Actions 页面 → *Sync & Compile Rules* → *Run workflow* |
| 编译版本 | sing-box **1.13.21** |

## 流水线

1. **Fetch** — 读取上游 `ACL4SSR_Online_Full_WithIcon.yaml` 的 `rule-providers`，逐个下载 36 个 `.list` 到 `ruleset/`
2. **Verify** — 数量必须为 36、且没有空文件，否则整个任务失败（避免静默缺规则）
3. **Compile** — 用 sing-box 把每个 `.list` 编译成 `.srs` 二进制
4. **Generate** — 按上游的 `proxy-groups` / `rules` 生成 `config.json`
5. **Validate** — `sing-box check -c config.json` 必须通过
6. **Commit** — 有变化才提交，无变化不产生空提交

## 使用方式

### 规则集（推荐）

在任意 sing-box 配置里按 tag 引用：

```json
{
  "type": "remote",
  "tag": "Telegram",
  "format": "binary",
  "url": "https://raw.githubusercontent.com/GotKiCry/GotKiCry_ACL_Rule_SingBox/master/ruleset/Telegram.srs",
  "download_detour": "direct"
}
```

可用 tag 与 `ruleset/*.srs` 文件名一致（共 36 个）。

### 完整配置

```
https://raw.githubusercontent.com/GotKiCry/GotKiCry_ACL_Rule_SingBox/master/config.json
```

直接下载后 `sing-box check -c config.json` 可通过，节点部分需要自行注入（或在 SubStore 里用脚本操作注入）。

## 版本要求

- `.srs` 由 **sing-box 1.13.x** 编译，客户端需 **≥ 1.13**
- `config.json` 使用 1.11+ 的 `route.rules` 动作语法，需要 **≥ 1.11**
- 若客户端是 1.14+，会出现 `independent_cache` / `store_rdrc` 的弃用警告（不影响运行，1.16 起才移除）

## 目录结构

| 路径 | 说明 |
| :--- | :--- |
| `ruleset/*.srs` | 编译后的二进制规则集（构建产物，已提交） |
| `config.json` | 生成的完整 sing-box 配置（构建产物，已提交） |
| `scripts/update.py` | 拉取上游 `.list`，任一失败即非 0 退出 |
| `scripts/compile.py` | `.list` → sing-box JSON（version 3）→ `.srs` |
| `scripts/generate_json.py` | 按上游 YAML 生成 `config.json` |
| `.github/workflows/update_rules.yml` | 定时 + 手动触发的完整流水线 |

中间产物（`*.list`、临时 `*.json`、上游 YAML）由 `.gitignore` 排除，仓库里只保留 `.srs` 和 `config.json`。

## 可调项

- **编译版本**：改 `.github/workflows/update_rules.yml` 里的 `SINGBOX_VERSION`
- **SubStore 提示字段**：`generate_json.py` 默认输出纯 sing-box 合法配置；如果需要 SubStore 的 `use_all_providers`，设置环境变量 `SUBSTORE_HINT=1`
- **自定义规则**：直接改上游仓库的 `Rule/*.list`，本仓库会在下一次定时任务后自动跟进

## Credits

- 规则来源：[GotKiCry/GotKiCry_ACL_Rule](https://github.com/GotKiCry/GotKiCry_ACL_Rule)
- 上游规则集：[ACL4SSR/ACL4SSR](https://github.com/ACL4SSR/ACL4SSR)
- 核心：[SagerNet/sing-box](https://github.com/SagerNet/sing-box)

---
*由 GitHub Actions 自动维护*
