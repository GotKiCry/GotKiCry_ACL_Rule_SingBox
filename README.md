# My ACL Rules

这个项目用于自动维护和更新 ACL 规则，配合 Clash 或 Sing-box 使用。
规则文件通过 GitHub Actions 定期从上游源同步。

## 目录结构

- `ACL4SSR_Online_Full_WithIcon.yaml`: 主要的配置文件 (包含规则组和上游源定义)。
- `Rule/` (或 `ruleset/`): 存放下载的规则文件。
- `scripts/`: 包含更新脚本。
- `.github/workflows/`: 包含自动更新的工作流定义。

## 如何使用

1.  **自动化**: GitHub Action 会每天运行一次，自动拉取最新规则并提交到本仓库。
2.  **手动**: 你可以手动触发 `.github/workflows/update_rules.yml` 工作流进行更新。
3.  **引用**: 在你的客户端配置中，可以直接引用本仓库的 raw 文件地址，或者克隆本仓库到本地使用。

## 自定义

修改 `ACL4SSR_Online_Full_WithIcon.yaml` 中的 `rule-providers` 部分来添加或删除规则源。
