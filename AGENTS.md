# Research Paper Agent

本项目用于：

Zotero → Codex → 飞书知识库 → 飞书 Paper Library

## 1. Source of Truth

Zotero 是论文原始资料和 bibliographic metadata 的唯一主数据源。

禁止直接读取或修改 `zotero.sqlite`。

使用 Zotero Local API：

`http://localhost:23119/api/`

访问 Zotero。

读取 `research.config.json` 获取当前配置。

## 2. Zotero

查询当前用户时使用：

`/users/0/...`

用户给出论文标题、作者、DOI、Zotero Key 或关键词后：

先查询 Zotero。

优先获取：

* Zotero Key
* Title
* Authors
* Year
* Venue
* DOI
* URL
* Collections
* Tags

Metadata 优先信任 Zotero。

只有 Zotero 中对应字段为空时，才从论文 PDF 补充。

## 3. PDF

找到 bibliographic item 后，查询其 children。

选择 `contentType = application/pdf` 的 attachment。

优先获取 Zotero full-text：

`/users/0/items/{attachmentKey}/fulltext`

同时通过：

`/users/0/items/{attachmentKey}/file/view/url`

获得本地 PDF 路径。

不得只根据 Abstract 写论文笔记。

必须尽量阅读全文，包括：

* Abstract
* Introduction
* Related Work
* Method
* Experiments
* Ablation
* Discussion
* Limitations
* Conclusion
* 重要 Appendix

Zotero full-text 用于全文阅读。

真实 PDF 用于确认：

* 页码
* 表格
* 图
* 数学公式
* 实验结果
* Ablation
* Appendix

如果 Zotero 没有 full-text，则使用本地 PDF 提取全文。

## 4. Paper Analysis

必须明确区分三类内容：

### Paper Claim

论文作者明确提出或实验支持的内容。

### Interpretation

对论文方法和结果的解释。

### Further Thought

基于论文产生的进一步研究思路。

不得把 Interpretation 或 Further Thought 写成论文作者的原始结论。

## 5. Markdown Note

每篇论文生成：

`notes/{year}-{short-title}.md`

结构：

# Paper Information

包含：

* Title
* Authors
* Year
* Venue
* DOI
* URL
* Zotero Key
* Zotero Collections
* Zotero Tags

# TL;DR

使用 3–5 句话解释：

* 解决什么问题
* 核心方法是什么
* 得到了什么结果
* 最值得关注的意义是什么

# Research Question

# Motivation

# Key Contributions

# Method

重点解释：

* 整体框架
* 输入输出
* 关键模块
* 算法
* 数学公式
* Loss Function
* Training
* Inference

不要只是翻译论文原文。

# Experiments

包括：

* Dataset
* Baselines
* Evaluation Metrics
* Implementation
* Main Results

重要结果尽量给出具体数值。

# Ablation Study

解释：

* 去掉了什么
* 性能发生什么变化
* 可以支持什么结论

# Key Findings

# Limitations

区分：

* Authors' stated limitations
* Additional observations

# My Understanding

用适合研究生科研的语言重新解释论文。

重点回答：

“这篇论文真正的新东西是什么？”

# Research Ideas

明确标记为 Further Thought。

不得冒充论文作者观点。

# Important Pages

记录重要：

* Page
* Figure
* Table
* Equation

# Related Papers

只记录与理解或后续研究明显相关的论文。

## 6. Feishu Knowledge Base

本地 Markdown 创建成功之后，再写飞书。

读取：

`research.config.json → feishu.wiki_parent_url`

使用已经安装的飞书官方 CLI 和相关 Skills。

优先使用：

* lark-doc
* lark-markdown
* lark-wiki
* lark-drive

创建论文知识库文档。

标题格式：

`[{Year}] {Title}`

尽量保留：

* Heading
* List
* Table
* Code
* Formula

根据 Zotero Collection 优先决定知识库分类。

如果不存在合理分类，可根据论文主题选择分类。

无法确定时使用：

`Others`

## 7. Paper Library

飞书多维表格只承担论文索引、筛选、检索和跳转功能。

不得将完整 Method、Experiments、Limitations 等长篇论文分析重复写入 Paper Library。

写入以下字段：

* 论文标题
* 作者
* 年份
* 期刊/会议
* 期刊分区
* 中科院分区
* 研究主题
* Zotero标签
* 阅读状态
* 一句话总结
* 论文链接
* 飞书笔记
* 阅读日期
* Zotero Key

### 论文标题

使用 Zotero Title。

### 作者

使用 Zotero Authors。

### 年份

使用 Zotero Year。

### 期刊/会议

优先从 Zotero metadata 中获取：

* Publication Title
* Journal
* Proceedings Title
* Conference Name

对于期刊论文，填写正式期刊名称。

对于会议论文，填写正式会议名称，例如：

* NeurIPS
* ICML
* ICLR
* ACL
* EMNLP
* CVPR

### 期刊分区

用于记录 JCR Quartile。

允许值：

* Q1
* Q2
* Q3
* Q4
* 未查询
* 不适用

仅期刊论文填写实际分区。

会议论文填写：

不适用

不得根据期刊名称、影响因子或经验自行猜测分区。

如果没有可靠来源确认，则填写：

未查询

### 中科院分区

用于记录中科院期刊分区。

允许值：

* 1区
* 2区
* 3区
* 4区
* 未查询
* 不适用

仅期刊论文填写。

会议论文填写：

不适用

不得将 JCR Quartile 直接转换为中科院分区。

没有可靠来源时填写：

未查询

### 研究主题

使用多选字段。

根据 Zotero Collection、Zotero Tags 和论文内容确定较高层级的研究方向。

例如：

* LLM
* RAG
* Agent
* Knowledge Graph
* Multimodal
* Recommendation
* NLP
* CV

避免创建过度细碎的主题。

### Zotero标签

同步 Zotero Tags。

不得删除或修改用户原有 Zotero Tags。

### 阅读状态

允许：

* 未读
* 阅读中
* 已读

只有在论文完整阅读、本地 Markdown 创建成功、飞书知识库笔记成功创建后，才设置为：

已读

### 一句话总结

生成 50–100 个中文字符。

只回答：

“这篇论文最核心做了什么？”

不要写成长摘要。

### 论文链接

优先顺序：

1. DOI URL
2. arXiv URL
3. Publisher URL
4. Zotero URL

### 飞书笔记

写入对应飞书知识库论文阅读笔记 URL。

### 阅读日期

记录完整论文阅读和入库流程完成日期。

### Zotero Key

必须保存。

用于 Zotero 与 Paper Library 的唯一关联和去重。

默认视图可以隐藏此字段。


## 9. Failure Safety

执行顺序必须是：

Zotero
→ 本地 Markdown
→ 飞书知识库
→ Paper Library

如果 Zotero 查询失败：

停止写飞书。

如果论文没有成功阅读：

停止写飞书。

如果本地 Markdown 创建失败：

停止写飞书。

如果飞书知识库创建失败：

不要把 Paper Library 标记为已读。

任何一步失败必须明确报告失败位置。

## 10. Zotero Writes

当前工作流只允许读取 Zotero。

未经用户明确要求：

不得修改 Zotero item、tag、note、attachment 或 collection。

## 11. Completion Report

完成一篇论文后报告：

* Title
* Zotero Key
* PDF attachment key
* Zotero Collection
* 本地 Markdown 路径
* 飞书知识库位置
* 飞书文档 URL
* Paper Library：created / updated
* 是否检测到重复记录
* 是否存在无法可靠读取的内容
## 12.飞书公式写入规则

论文笔记中经常包含数学公式，因此写入飞书云文档时必须特别处理公式。

### 写入格式

创建或更新论文笔记时，必须显式使用：

--doc-format markdown

不得依赖 lark-cli 默认格式。

例如创建文档时应使用类似：

lark-cli docs +create \
  --doc-format markdown \
  --content "@./notes/paper.md"

如果写入已有文档，也必须显式指定：

--doc-format markdown

### LaTeX 公式

本地 Markdown 中的公式统一使用 LaTeX。

行内公式：

$ \mathbf{x} = [x,y,z]^T $

独立公式：

$$
\mathbf{p}'(s)=\mathbf{R}(s)\mathbf{v}(s)
$$

复杂公式必须使用标准 LaTeX，例如：

$$
\frac{\partial \mathbf{n}}{\partial s}
+
\mathbf{f}=0
$$

$$
\frac{\partial \mathbf{m}}{\partial s}
+
\mathbf{p}'\times\mathbf{n}
+
\mathbf{l}=0
$$

不得把公式放在代码块中。

错误：

```latex
E = mc^2