# 阶段 5：RAG

课程编号：32–46  
前置阶段：阶段 4  
阶段目标：先从零实现检索增强生成，再学习向量库、混合检索、重排和托管检索。

## 核心数据流

```text
文档 → 清洗 → 切块 → Embedding → 索引
问题 → 检索 → 候选块 → 重排 → 上下文 → 模型回答与引用
```

## 课程

| 课程 | 文件 | 唯一目标 |
|---|---|---|
| 32 | `lessons/32_read_document.py` | 读取并清洗一个本地文档 |
| 33 | `lessons/33_chunk_text.py` | 将长文本切成可检索的块 |
| 34 | `lessons/34_chunk_overlap.py` | 观察重叠切块对语义完整性的影响 |
| 35 | `lessons/35_create_embedding.py` | 将文本转换为向量 |
| 36 | `lessons/36_cosine_similarity.py` | 手动计算余弦相似度 |
| 37 | `lessons/37_top_k_retrieval.py` | 获取相似度最高的 K 个文本块 |
| 38 | `lessons/38_first_rag.py` | 串联检索结果与模型生成 |
| 39 | `lessons/39_rag_citations.py` | 在答案中保留可验证来源 |
| 40 | `lessons/40_vector_store.py` | 使用向量库存储和查询索引 |
| 41 | `lessons/41_metadata_filter.py` | 按来源、类别或时间过滤 |
| 42 | `lessons/42_hybrid_search.py` | 合并关键词检索与向量检索 |
| 43 | `lessons/43_rerank.py` | 对候选结果重新排序 |
| 44 | `lessons/44_rag_eval.py` | 分开评测检索质量与回答质量 |
| 45 | `lessons/45_retrieval_as_tool.py` | 将检索包装成 Agent 可调用工具 |
| 46 | `lessons/46_hosted_file_search.py` | 使用托管 File Search 对比自建 RAG |

## 阶段作品

一个可回答本地资料问题、提供来源引用、支持元数据过滤并有基础评测集的知识库 Agent。

## 完成标准

- 能解释 RAG 与模型训练、对话记忆的区别。
- 能从零说明切块、Embedding、相似度和 Top-K。
- 没有检索证据时不编造来源。
- 能分析“没检索到”和“检索到但答错”两种不同失败。
- 能说明自建 RAG 与托管 File Search 的取舍。

## 本阶段不学习

不把 MCP 当作向量数据库，不提前实现多 Agent 编排。

