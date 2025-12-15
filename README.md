# GotKiCry ACL Rule for SingBox

Welcome to the automated build repository for SingBox ACL rules. This project serves as a compilation pipeline that transforms upstream ACL rules into SingBox-compatible binary formats and generates ready-to-use configurations.

## 📖 Overview

This repository is designed to be a "set-and-forget" solution for SingBox users. It automatically synchronizes with [GotKiCry/GotKiCry_ACL_Rule](https://github.com/GotKiCry/GotKiCry_ACL_Rule), compiles the rules into SingBox's native Rule Set (`.srs`) format, and generates a fully functional `config.json`.

**Key Features:**

- **Automated Synchronization**: Daily updates from the upstream rule source.
- **Binary Compilation**: Rules are compiled into `.srs` format for optimal performance in SingBox.
- **Dynamic Configuration**: Automatically generates a `config.json` incorporating the latest rule sets and GeoIP databases.
- **Clean Repository**: Intermediate build artifacts are ephemeral; only the final production-ready files are committed.

## 🚀 Usage

### As a Remote Configuration

You can directly use the generated configuration file in your SingBox client.

**Configuration URL:**
```
https://raw.githubusercontent.com/GotKiCry/GotKiCry_ACL_Rule_SingBox/master/config.json
```

### Build Process

The automated workflow performs the following steps:
1.  **Fetch**: Retries the latest `ACL4SSR` configuration and rule lists from the upstream repository.
2.  **Compile**: Converts text-based `.list` files into binary `.srs` rule sets.
3.  **Generate**: Assembles the `config.json` with the correct remote links to the compiled rule sets.
4.  **Publish**: Pushes the updated artifacts to the `master` branch.

## 📂 Repository Structure

| File/Directory | Description |
| :--- | :--- |
| `config.json` | The final, ready-to-use SingBox configuration file. |
| `ruleset/` | Contains the compiled `.srs` binary rule sets. |
| `scripts/` | Python scripts used for the build process (`update`, `compile`, `generate`). |
| `.github/` | GitHub Actions workflow definitions. |

## ⚠️ Integrity Note

This repository uses a forced-update strategy to maintain a clean history. The `master` branch reflects the latest valid build state. Please avoid using this repository as a base for long-term forks without understanding the history rewrite mechanism.

## 🔗 Credits

- **Rule Source**: [GotKiCry/GotKiCry_ACL_Rule](https://github.com/GotKiCry/GotKiCry_ACL_Rule)
- **Core Core**: [SagerNet/sing-box](https://github.com/SagerNet/sing-box)

---
*Maintained by GotKiCry via GitHub Actions*
