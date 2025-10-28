# RWA Compliance Knowledge Base - PDF Documents

## 📚 监管文档目录

本目录存放RWA合规Agent使用的监管政策PDF文档。

## 📥 文档列表

### 已配置的PDF文档

以下文档应放置在此目录下：

| 文件名 | 地区 | 描述 | 下载链接 |
|--------|------|------|----------|
| `hk_sfc_tokenisation.pdf` | 香港 | 香港证监会(SFC)代币化研讨会文件 | [下载](https://www.sfc.hk/-/media/files/PCIP/FAQ-PDFS/HKIFA-tokenisation-seminar-10-Jan-2024.pdf) |
| `uk_fca_crypto.pdf` | 英国 | 英国金融行为监管局(FCA)加密资产监管咨询文件 | [下载](https://www.fca.org.uk/publication/consultation/cp25-28.pdf) |
| `oecd_tokenisation.pdf` | 国际 | 经合组织(OECD)理解金融市场资产代币化报告 | [下载](https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/11/understanding-the-tokenisation-of-assets-in-financial-markets_2e657111/c033401a-en.pdf) |

## 🚀 自动下载

使用提供的下载脚本自动获取所有文档：

```bash
# 从agents目录运行
cd agents
python download_compliance_docs.py
```

脚本会：
- ✅ 自动创建此目录
- ✅ 下载所有配置的PDF文档
- ✅ 验证文件完整性
- ✅ 跳过已存在的文件

## 📝 手动下载

如果自动下载失败，请手动下载：

### 香港SFC文档
1. 访问: https://www.sfc.hk/-/media/files/PCIP/FAQ-PDFS/HKIFA-tokenisation-seminar-10-Jan-2024.pdf
2. 另存为: `hk_sfc_tokenisation.pdf`
3. 放置到本目录

### 英国FCA文档
1. 访问: https://www.fca.org.uk/publication/consultation/cp25-28.pdf
2. 另存为: `uk_fca_crypto.pdf`
3. 放置到本目录

### OECD文档
1. 访问: https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/11/understanding-the-tokenisation-of-assets-in-financial-markets_2e657111/c033401a-en.pdf
2. 另存为: `oecd_tokenisation.pdf`
3. 放置到本目录

## 🔍 文档内容概览

### 香港SFC代币化研讨会
- **主题**: 资产代币化监管框架
- **关键内容**:
  - VASP牌照要求
  - 专业投资者vs零售投资者
  - 产品授权要求
  - 反洗钱/反恐怖融资规则

### 英国FCA加密资产监管
- **主题**: 加密资产监管咨询
- **关键内容**:
  - 金融推广制度
  - 受监管vs非受监管代币
  - 电子货币和支付服务
  - 稳定币和DeFi监管提案

### OECD资产代币化报告
- **主题**: 理解金融市场资产代币化
- **关键内容**:
  - 国际代币化趋势
  - 监管挑战和机遇
  - 最佳实践建议
  - 跨境监管协调

## ✅ 验证文件

检查文件是否正确下载：

```bash
# Windows PowerShell
Get-ChildItem -Path knowledge\compliance -Filter *.pdf

# Linux/Mac
ls -lh knowledge/compliance/*.pdf
```

应该看到3个PDF文件。

## 🔒 使用说明

这些PDF文档被RWA合规Agent的RAG系统使用：

1. **文档加载**: Agent启动时自动加载
2. **向量化**: 使用Azure OpenAI Embedder转换为向量
3. **存储**: 保存在LanceDB向量数据库
4. **检索**: 用户提问时自动检索相关内容

## ⚠️ 注意事项

1. **版权**: 这些文档来自官方监管机构，仅用于学习和研究
2. **更新**: 监管政策可能更新，建议定期检查原始来源
3. **容量**: PDF文件总大小约10-50MB，确保有足够磁盘空间
4. **网络**: 下载可能需要稳定的网络连接，某些链接可能需要VPN

## 📂 目录结构

```
knowledge/
└── compliance/
    ├── README.md (本文件)
    ├── hk_sfc_tokenisation.pdf
    ├── uk_fca_crypto.pdf
    └── oecd_tokenisation.pdf
```

## 🆘 问题排查

### 下载失败
- 检查网络连接
- 尝试使用VPN
- 手动下载并放置文件

### 文件损坏
- 删除损坏的PDF
- 重新运行下载脚本
- 验证文件大小是否合理

### Agent无法加载
- 检查文件名是否正确
- 确认embedder配置正确
- 查看Agent日志了解详细错误

## 📞 获取帮助

如有问题：
1. 查看 [合规Agent文档](../../agents/RWA_COMPLIANCE_AGENT_README.md)
2. 查看 [快速启动指南](../../agents/COMPLIANCE_QUICK_START.md)
3. 提交GitHub Issue

---

**最后更新**: 2025-10-28
