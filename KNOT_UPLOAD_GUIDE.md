# 如何上传到 Knot 平台

本 Skill 已经在 Knot 平台测试通过，上传步骤如下：

## 📦 准备 ZIP 包

Knot 平台要求 Skill 的 ZIP 包必须满足以下结构：

```
ADP_Integration_Skill_Knot.zip
├── SKILL.md          # 必需：Skill 文档（必须在根目录）
├── adp_client.py     # 必需：核心库文件
└── README.md         # 可选：使用指南
```

**重要**：`SKILL.md` 文件必须在 ZIP 包的**根目录**，不能在子文件夹中！

## 🚀 上传步骤

### 方式 1：使用预打包的 ZIP（推荐）

仓库中已经提供了符合 Knot 平台要求的 ZIP 包：

1. 下载 `ADP_Integration_Skill_Knot.zip`
2. 访问 Knot 平台：https://knot.woa.com
3. 进入 Skill 管理页面
4. 点击"上传 Skill"
5. 选择下载的 ZIP 文件
6. 完成上传

### 方式 2：手动打包

如果你修改了代码，需要重新打包：

```bash
# 克隆仓库
git clone https://github.com/XiaoyuanNO1/adp-integration-skill.git
cd adp-integration-skill

# 创建临时目录
mkdir knot-package
cd knot-package

# 复制文件到根目录
cp ../adp_client.py .
cp ../ADP_INTEGRATION_SKILL.md ./SKILL.md
cp ../README.md .

# 打包（确保文件在根目录）
zip -r ../ADP_Integration_Skill_Knot.zip .

# 验证结构
cd ..
unzip -l ADP_Integration_Skill_Knot.zip
```

**验证输出应该是**：
```
Archive:  ADP_Integration_Skill_Knot.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    12900  XX-XX-XXXX XX:XX   adp_client.py
    13479  XX-XX-XXXX XX:XX   SKILL.md
     8913  XX-XX-XXXX XX:XX   README.md
---------                     -------
    35292                     3 files
```

注意：文件名**不能**有子文件夹前缀（例如 ❌ `adp-integration-skill-main/SKILL.md`）

## ❌ 常见错误

### 错误 1：ZIP 包结构不正确
```
invalid zip file: 在顶层文件夹 'adp-integration-skill-main' 中未找到 SKILL.md 文件
```

**原因**：从 GitHub 下载的 ZIP 包会自动创建一个子文件夹

**解决方案**：
1. 不要直接上传从 GitHub "Download ZIP" 下载的文件
2. 使用仓库中提供的 `ADP_Integration_Skill_Knot.zip`
3. 或按照"方式 2"手动打包

### 错误 2：缺少 SKILL.md 文件
```
在顶层文件夹中未找到 SKILL.md 文件
```

**原因**：文件名错误或不在根目录

**解决方案**：
- 确保文件名是 `SKILL.md`（大写，不是 `ADP_INTEGRATION_SKILL.md`）
- 确保文件在 ZIP 包的根目录

## ✅ 验证清单

上传前请确认：

- [ ] ZIP 包中包含 `SKILL.md` 文件
- [ ] `SKILL.md` 在 ZIP 包的根目录（不在子文件夹中）
- [ ] ZIP 包中包含 `adp_client.py` 核心库
- [ ] 所有文件都在根目录（没有 `adp-integration-skill-main/` 等前缀）
- [ ] 代码中没有硬编码的 AppKey（使用 `YOUR_APP_KEY` 占位符）

## 📝 上传后配置

上传成功后，在 Knot 平台中：

1. **填写 Skill 基本信息**：
   - Skill 名称：ADP Platform Integration
   - 描述：ADP 平台 HTTP SSE 对接实现
   - 版本：1.0.0

2. **配置使用说明**：
   - 引导用户提供自己的 AppKey
   - 说明如何获取 AppKey（从 ADP 控制台）

3. **测试 Skill**：
   ```python
   from adp_client import create_client
   
   client = create_client(app_key="YOUR_APP_KEY")
   response = client.chat("你好")
   print(response)
   client.close()
   ```

## 🔗 相关链接

- **GitHub 仓库**：https://github.com/XiaoyuanNO1/adp-integration-skill
- **Knot 平台**：https://knot.woa.com
- **ADP 平台文档**：参考 SKILL.md 中的链接

## 💡 提示

- 如果上传后发现问题，可以删除并重新上传
- 建议在 Knot 平台测试环境中先测试
- 确保其他用户知道需要提供自己的 AppKey

---

如有问题，请查看 `SKILL.md` 中的详细文档或在 GitHub 提 Issue。
