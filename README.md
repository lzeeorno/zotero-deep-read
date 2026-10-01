# Zotero Deep Read

将论文精读变成可在原文上复习的 v3 批注：红色语义 bbox、全篇 `N01…` 编号、页面简短中文关键词与点击后的详细解释。编号关联替代长箭头。

这是 Codex skill；模型负责阅读与解释，Python 工具负责渲染已选定的批注。无需 NoteMR 专用坐标，不包含论文 PDF、字体文件或个人 Zotero 配置。

## 本地安装

将本仓库放入 `${CODEX_HOME:-$HOME/.codex}/skills/zotero-deep-read`，例如：

```sh
git clone https://github.com/lzeeorno/zotero-deep-read.git "${CODEX_HOME:-$HOME/.codex}/skills/zotero-deep-read"
```

在新聊天的 skill 选择器中选择 **Zotero Deep Read**，或输入 `$zotero-deep-read`。不同客户端可能用 `@` 打开选择器；文本调用采用实际 skill 名称。已打开的聊天若尚未刷新 skill 列表，开启新聊天。

示例：`使用 $zotero-deep-read 精读 Zotero 中的这篇论文，生成完整 v3 编号批注副本。`

渲染工具需要 PyMuPDF：`python3 -m pip install pymupdf`。格式、字体和命令详见 [annotation-format.md](references/annotation-format.md)。

PDF annotation 不等于已写入 Zotero 数据库的原生批注；在 Zotero 中打开并检查，按当前版本支持的方式导入。生成文件保留原文，已有文件不会被覆盖。

设计来源：用户认可的 Zotero Deep Read v3 编号方案。NoteMR 的 22 条笔记是参考实例，不是其他论文必须遵循的数量。
