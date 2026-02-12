# Knot 平台 Skill 打包指南

## 📦 格式要求

根据 Knot 平台的要求（参考：https://iwiki.woa.com/p/4016798672），一个合格的 Skill ZIP 包必须满足：

### 三个名称必须完全一致

1. **ZIP 文件名**：`adp-integration.zip`
2. **顶层文件夹名**：`adp-integration/`
3. **SKILL.md 中的 name 字段**：`adp-integration`

### SKILL.md 格式要求

```yaml
---
name: adp-integration
description: 与腾讯云 ADP (AI Dialog Platform) 平台进行 HTTP SSE 流式对话对接
version: 1.0.0
author: xiaoyuan-no1-888
tags:
  - adp
  - ai-agent
  - sse
  - chat
  - integration
category: integration
---
```

### name 字段规则

- ✅ **允许**：小写字母 `a-z`
- ✅ **允许**：数字 `0-9`
- ✅ **允许**：连字符 `-`（不能在开头或结尾）
- ❌ **禁止**：大写字母、中文、空格、下划线、引号、特殊符号
- 📏 **长度限制**：最多 64 个字符

### description 字段规则

- 📏 **长度限制**：最多 1024 个字符
- ✅ 可以包含中文和空格
- ✅ 必须清晰描述 Skill 的功能和使用场景

---

## 🔧 正确的打包方法

### 方法 1：从本仓库打包（推荐）

```bash
# 克隆仓库
git clone https://github.com/XiaoyuanNO1/adp-integration-skill.git
cd adp-integration-skill

# 创建符合 Knot 规范的文件夹
mkdir adp-integration
cp SKILL.md adp-integration/
cp adp_client.py adp-integration/
cp README.md adp-integration/

# 打包（确保顶层文件夹名为 adp-integration）
zip -r adp-integration.zip adp-integration/

# 验证
unzip -l adp-integration.zip
```

### 方法 2：直接下载预打包文件

**注意**：GitHub 的 "Download ZIP" 功能会创建一个名为 `adp-integration-skill-main` 的顶层文件夹，这会导致上传失败。

**正确做法**：
1. 访问：https://github.com/XiaoyuanNO1/adp-integration-skill
2. 在仓库根目录找到 `adp-integration.zip` 文件
3. 点击文件名 → 点击 "Download" 按钮
4. 直接使用下载的 ZIP 文件上传到 Knot

---

## ✅ 上传前验证清单

使用以下命令验证 ZIP 包格式：

```bash
# 1. 检查 ZIP 文件名
ls -1 adp-integration.zip

# 2. 检查顶层文件夹名
unzip -l adp-integration.zip | head -5

# 3. 检查 SKILL.md 中的 name
unzip -p adp-integration.zip adp-integration/SKILL.md | grep "^name:"

# 4. 完整验证
unzip -l adp-integration.zip
```

**期望输出**：

```
Archive:  adp-integration.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  02-12-2026 16:47   adp-integration/
    13724  02-12-2026 16:47   adp-integration/SKILL.md
    12900  02-12-2026 16:47   adp-integration/adp_client.py
     8913  02-12-2026 16:47   adp-integration/README.md
---------                     -------
    35537                     4 files
```

---

## ❌ 常见错误

### 错误 1：name 字段包含非法字符

```
invalid zip file: name 在位置 0 包含非法字符 '"'
```

**原因**：name 字段包含引号或其他非法字符

**解决**：确保 name 只包含小写字母、数字和连字符

### 错误 2：第一行不是 '---'

```
invalid zip file: SKILL.md 格式错误: 第 1 行必须是 '---'
```

**原因**：SKILL.md 缺少 YAML Front Matter

**解决**：确保文件第一行是 `---`

### 错误 3：name 与文件夹名不一致

```
invalid zip file: SKILL.md 中的 name 字段 'adp-integration' 与顶层文件夹名 'adp-integration-skill-main' 不一致
```

**原因**：从 GitHub "Download ZIP" 下载的包含错误的文件夹名

**解决**：使用本指南中的打包方法，或下载预打包的 `adp-integration.zip`

---

## 📝 字段约束参考

| 字段 | 是否必需 | 约束条件 |
|------|----------|----------|
| name | 是 | 最多 64 个字符。仅允许小写字母、数字和连字符。不得以连字符开头或结尾。 |
| description | 是 | 最多 1024 个字符。不能为空。描述该技能的功能及使用场景。 |
| license | 否 | 许可证名称或对捆绑许可证文件的引用。 |
| compatibility | 否 | 最多 500 个字符。指示环境要求。 |
| metadata | 否 | 用于附加元数据的任意键值映射。 |
| allowed-tools | 否 | 该技能可使用的预批准工具的空格分隔列表。 |

---

## 🔗 参考资源

- **Knot 官方文档**：https://iwiki.woa.com/p/4016798672
- **AgentSkills 规范**：https://agentskills.io/specification
- **本仓库**：https://github.com/XiaoyuanNO1/adp-integration-skill

---

## 💡 提示

1. **使用预打包文件**：仓库中提供的 `adp-integration.zip` 已经过验证，可以直接上传
2. **验证三个名称**：上传前务必验证 ZIP 文件名、顶层文件夹名、name 字段三者一致
3. **不要使用 GitHub Download ZIP**：该功能会生成错误的文件夹结构
4. **保持简单**：Skill 名称建议使用简短、描述性的英文词组

---

如有问题，请联系：xiaoyuan_no1_888
