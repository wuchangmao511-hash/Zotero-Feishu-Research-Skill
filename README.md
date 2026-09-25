# Zotero Feishu Research

本地论文阅读与知识管理工具。

用户只需提供 Zotero 中的论文标题，系统便可通过 Zotero Local API读取论文元数据和本地 PDF，生成结构化中文阅读笔记，并同步至飞书知识库与 Paper Library。

## 核心功能

- 通过 Zotero Local API 查询论文
- 自动定位本地 PDF attachment
- 获取 Zotero 索引全文
- 使用 PyMuPDF 提取 PDF 全文
- 生成结构化中文论文笔记
- 同步到飞书知识库
- 使用 Zotero Key 更新或创建 Paper Library 记录
- Zotero 全程只读

## 安全说明

本项目不会读取 `zotero.sqlite`，也不会修改 Zotero 中的论文、标签、
附件、笔记或 Collection。
