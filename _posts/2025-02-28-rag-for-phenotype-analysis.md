---
layout: post
title: "在表型分析中应用 RAG：让大模型少说胡话"
date: 2025-02-28
category: professional
ai_content: 50
image: /assets/images/posts/2025-02-28-rag-for-phenotype-analysis/cover.png
tags: [bioinformatics, RAG, HPO, AI]
excerpt: "将非标准临床描述映射到 HPO 标准术语是遗传分析的关键第一步。本文探索 RAG 如何帮助大模型减少幻觉、提升表型分析的精度。"
---
## 引言

过了一个新年回来之后，发现全中国的公司都在接入或者部署 Deepseek 模型的热潮中。我也通过上一篇的小测试可以初步确定 Deepseek 真的是一个可以用来解决真实世界问题的且国产大模型平台了。上一篇的测试理论上讲对于大模型来说太小儿科了，这次换一个进阶一些的任务。

在针对罕见病和遗传病的分子遗传分析中，由于测序检测出的变异非常多，一个重要的分析策略是基于表型进行分析。通过限定分析为表型相关基因上的变异，来提高分析效率和准确性。这个过程中第一步就是将非标准的临床描述转换成标准化的表型术语。例如病人网织红细胞百分比增高，对应 Human Phenotype Ontology (HPO) 中的 HP:0004312 
Abnormal reticulocyte morphology (网织红细胞异常)，然后可以关联到 *GATA1*、*FANCE* 等基因。看起来似乎不难，而实际上HPO术语体系包含超过17,000个术语，且层级复杂，分析人员需要熟悉其层次结构和术语定义。而临床表型描述常常非常复杂，涉及多个系统（如神经系统、骨骼系统、泌尿系统等），且表型之间可能存在关联性。同一表型很多时候有多种描述方式（例如“发育迟缓”可能被描述为“智力低下”或“运动发育落后”）。某些临床表型可能没有直接对应的HPO术语，需要选择最接近的术语或进行组合；临床记录也常常存在不完整、模糊或非标准化的描述。因此需要分析人员具备广泛的医学知识来准确识别和匹配，并将其映射到HPO术语。而这应该是一种大模型擅长的分析推理工作。

## 方法
为了更好的测试大模型在这个目标上的能力，首先我们需要设计一个有一些难度的临床描述。
> 发育迟缓/身材矮小。右耳前赘生物，性发育迟缓待排。骶1椎板未闭合。肾脏病理：光镜：FSGS。行走呈痉挛步态，容易摔跤，不会跳绳、骑自行车。食纳增加，平素一碗面/餐，1月前增加至两碗面/餐，吃零食，小便频率增加，1-2h/次，夜尿情况不详 。父母非近亲结婚。无家族遗传史。

这里包含缩写如“FSGS”、口语化描述如“不会跳绳、骑自行车”，多个连续否定描述如“无惊厥、抽搐”。这都是我们过去智能化方案中处理不理想的情况，我们来看一下大模型的表现如何。

### Deepseek V3
> 以下是将文本中的临床表型转换为Human Phenotype Ontology (HPO)的结果：
> 
> 1. **发育迟缓** - HP:0001263 (Global developmental delay)
> 
> 2. **身材矮小** - HP:0004322 (Short stature)
> 
> 3. **右耳前赘生物** - HP:0000384 (Preauricular skin tag)
> 
> 4. **性发育迟缓** - HP:0008230 (Delayed puberty)
> 
> 5. **骶1椎板未闭合** - HP:0002678 (Spina bifida occulta)
> 
> 6. **无惊厥、抽搐** - HP:0001250 (Seizures) [注：此处为否定描述，表示不存在该表型]
> 
> 7. **肾脏病理：光镜FSGS** - HP:0000097 (Focal segmental glomerulosclerosis)
> 
> 8. **行走呈痉挛步态** - HP:0002064 (Spastic gait)
> 
> 9. **容易摔跤** - HP:0002355 (Frequent falls)
> 
> 10. **不会跳绳、骑自行车** - HP:0008872 (Inability to ride a bicycle) [注：HPO中没有直接对应“跳绳”的术语，此处使用类似表型]
> 
> 11. **食纳增加** - HP:0001511 (Increased appetite)
> 
> 12. **小便频率增加** - HP:0000104 (Polyuria)
> 
> 13. **夜尿情况不详** - HP:0000017 (Nocturia) [注：此处为不详，无法确定是否存在该表型]
> 
> **注释：**
> 
> - 对于否定描述的表型（如“无惊厥、抽搐”），HPO中通常不直接记录否定表型，除非有明确的临床意义。
> 
> - 对于“骶1椎板未闭合”，HPO中对应的术语是“Spina bifida occulta”，表示隐性脊柱裂。
> 
> - 对于“肾脏病理：光镜FSGS”，HPO中对应的术语是“Focal segmental glomerulosclerosis”。
>
> 这些HPO术语可以用于进一步的临床表型分析和遗传学研究。

### Deepseek R1

> 以下是原文中提取的临床表型及其对应的 **Human Phenotype Ontology (HPO)** 术语：
> 

---

**临床表型与HPO对应表**

| 临床表型描述                   | HPO编号        | HPO术语名称                                                                 |
|-------------------------------|---------------|---------------------------------------------------------------------------|
| 发育迟缓                      | HP:0001263    | Global developmental delay (全面性发育迟缓)                               |
| 身材矮小                      | HP:0004322    | Short stature (身材矮小)                                                  |
| 右耳前赘生物                  | HP:0000384    | Preauricular skin tag (耳前皮赘)                                          |
| 性发育迟缓待排                | HP:0008230    | Delayed puberty (青春期延迟)                                              |
| 骶1椎板未闭合（隐性脊柱裂）   | HP:0002878    | Spina bifida occulta (隐性脊柱裂)                                          |
| 肾脏病理：光镜FSGS            | HP:0000097    | Focal segmental glomerulosclerosis (局灶节段性肾小球硬化)                 |
| 行走呈痉挛步态                | HP:0002064    | Spastic gait (痉挛步态)                                                   |
| 容易摔跤                      | HP:0002354    | Frequent falls (频繁跌倒)                                                 |
| 不会跳绳、骑自行车（运动协调差） | HP:0002072    | Poor coordination (协调能力差)                                            |
| 食纳增加（食欲亢进）          | HP:0004396    | Hyperphagia (食欲亢进)                                                    |
| 小便频率增加（多尿）          | HP:0000103    | Polyuria (多尿)                                                           |


---

> 
> **排除的阴性表型**（无需HPO转换）
> 
> - 无惊厥、抽搐  
> 
> - 无家族遗传史  
> 
> **备注**
> 
> 1. **家族史**（父母非近亲结婚、无家族遗传史）属于背景信息，不纳入HPO表型。
> 
> 2. **性发育迟缓待排** 需结合进一步检查确认，暂按疑似表型记录。
> 
> 

### ChatGPT Research
> 下面是从文本中提取出的临床表型及其对应的 HPO 术语（部分术语根据描述作了合理推断）：
> 
> 1. **发育迟缓**  
> 
>    - HPO术语：Global developmental delay  
> 
>    - HPO ID：HP:0001263
> 
> 2. **身材矮小**  
> 
>    - HPO术语：Short stature  
> 
>    - HPO ID：HP:0004322
> 
> 3. **右耳前赘生物**  
> 
>    - HPO术语：Preauricular skin tag  
> 
>    - HPO ID：HP:0000386
> 
> 4. **性发育迟缓**  
> 
>    - HPO术语：Delayed puberty  
> 
>    - HPO ID：HP:0000826
> 
> 5. **骶1椎板未闭合**  
> 
>    - HPO术语：Spina bifida occulta  
> 
>    - HPO ID：HP:0002192
> 
> 6. **肾脏病理为FSGS**  
> 
>    - HPO术语：Focal segmental glomerulosclerosis  
> 
>    - HPO ID：HP:0012535
> 
> 7. **行走呈痉挛步态**  
> 
>    - HPO术语：Spastic gait  
> 
>    - HPO ID：HP:0002143
> 
> 8. **容易摔跤**  
> 
>    - HPO术语：Frequent falling  
> 
>    - HPO ID：HP:0002325
> 
> 9. **食纳增加**  
> 
>    - HPO术语：Hyperphagia  
> 
>    - HPO ID：HP:0004395
> 
> 10. **小便频率增加**  
> 
>     - HPO术语：Increased urinary frequency  
> 
>     - HPO ID：HP:0012602
> 
> 
> **说明：**  
> “无惊厥、抽搐”属于阴性描述，因此未作为阳性表型纳入。  
> 另外，“不会跳绳、骑自行车”可能反映运动协调或运动发育障碍，但结合“痉挛步态”和“容易摔跤”已经反映出运动方面的异常，因此未单独列出。

从3个模型的输出来看，均存在一些幻觉（Hallucination），给出 HPO 编号错误率很高。HP 术语名称大部分是存在的，但也有编造的情况，例如 Deepseek V3 编造了 Inability to ride a bicycle 等多个 HP 术语；ChatGPT 类似。Deepseek R1 的幻觉明显要轻一些，仅有 Hyperphagia 一例错误的 HP 名称，这个名称也是一个术语的同义词。同时大模型的优势也体现的很明显，即缩写、口语化描述、连续否定等难点都做到非常精确的拆分和转换。


### RAG实现
大家都知道检索增强生成（RAG）是一个非常实用的解决大模型幻觉的方法，那么我们也来试试看。

**整合 HPO 和 ChinaHPO 数据构建 HPO 向量存储**
```python
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import json

# Self-defined function to process HPO JSON and China HPO data files 
# then convert to Documents
# hp.json download from https://hpo.jax.org/data/ontology
# ChinaHPO https://www.chinahpo.net/chpo/#/search
documents = process_json_file('data/hp.json', chpo_nested_dict)

# Create embeddings and vectorstore
embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
)

vectorstore = FAISS.from_documents(documents=documents, embedding=embeddings)

# Save the vectorstore for future use
vectorstore.save_local(folder_path='./embeddings/hpo/')
```

**应用大模型对临床描述进行分析和拆分**
```python
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser
TEMPLATE = """你是一位医学专家，请分析给定临床描述，并按照要求进行总结:
1. 识别所有症状描述
2. 将具体描述转换为对应的标准医学术语
3. 用简洁的医学术语总结主要表现
4. 保留重要的检测信息
5. 输出以逗号分隔的格式返回，不要包含编号或其他格式

<<临床描述>>: {phenotype}
{format_instructions}
"""

# Create prompt
prompt = ChatPromptTemplate.from_template(TEMPLATE)
list_parser = CommaSeparatedListOutputParser()

# Use deepseek-V3
llm_alias = "deepseek"
# Self-defined function to run given LLM model
llm = get_llm(llm_alias)

# Create chain with streaming
chain = prompt | llm | list_parser

phenotype_description = """发育迟缓/身材矮小。右耳前赘生物，性发育迟缓待排。骶1椎板未闭合。无惊厥、抽搐。肾脏病理：光镜FSGS。
行走呈痉挛步态，容易摔跤，不会跳绳、骑自行车。食纳增加，平素一碗面/餐，1月前增加至两碗面/餐，吃零食，小便频率增加，1-2h/次，夜尿情况不详 。父母非近亲结婚。无家族遗传史。
"""

# Generate response with streaming
response = chain.invoke(
    {
        'phenotype': phenotype_description,
        'format_instructions': list_parser.get_format_instructions()
    }
)
```

**应用 RAG 检索表型相关HP术语**
```python
def hpo_retriever(vectorstore, description_cn, n=5):
    retriever = vectorstore.as_retriever(
        search_type="similarity", 
        #search_type="mmr",
        search_kwargs={"k": n}
    )
    docs = retriever.invoke(description_cn)

    output_str = ""
    for i, doc in enumerate(docs):
        output_str += doc.page_content + "\n"
    return output_str

hp_candidates_doc = ""
for i, phenotype in enumerate(phenotype_list):
    print(f"Phenotype {i+1}:{phenotype}")
    candidate_hp_return = hpo_retriever(vectorstore, phenotype, n=10)
    hp_candidates_doc += candidate_hp_return
```

**应用大模型将术语匹配到临床描述**
```python
HPO_ANALYSIS_TEMPLATE = """你是一位遗传医学专家，针对每一个临床表型描述，从HP候选中挑选最符合的HP术语。
<<临床表型描述>>: {phenotype}
<<HP候选>>: {hpo_doc}

输出时请注意：
1. 以表格形式需要输出临床表型描述，HP术语编号，HP术语英文，HP术语中文。
2. 不要对正常表现进行术语匹配。
3. 如果无符合的HP术语，则输出无。
"""

# Create prompt
prompt = ChatPromptTemplate.from_template(HPO_ANALYSIS_TEMPLATE)
chain = prompt | llm | StrOutputParser()

# Generate response with streaming
response = chain.invoke(
    {
        'phenotype': phenotype_list,
        'hpo_doc': hp_candidates_doc
    }
)
```

#### 基于 RAG 实现的 HP 术语分析结果

| 临床表型描述         | HP术语编号   | HP术语英文                                      | HP术语中文               |
|----------------------|--------------|------------------------------------------------|--------------------------|
| 发育迟缓             | HP:0001270   | Motor delay                                    | 运动发育迟缓             |
| 身材矮小             | HP:0004322   | Short stature                                  | 身材矮小                 |
| 右耳前赘生物         | HP:0000384   | Preauricular skin tag                          | 耳前皮赘                 |
| 性发育迟缓待排       | HP:0000823   | Delayed puberty                                | 青春期发育延迟           |
| 骶1椎板未闭合        | HP:0004614   | Spina bifida occulta at S1                     | S1区隐性脊柱裂           |
| 肾脏病理光镜FSGS     | HP:0000097   | Focal segmental glomerulosclerosis             | 局灶节段性肾小球硬化     |
| 痉挛步态             | HP:0002064   | Spastic gait                                   | 痉挛步态                 |
| 容易摔跤             | HP:0002359   | Frequent falls                                 | 频繁跌倒                 |
| 不会跳绳             | HP:0002312   | Clumsiness                                     | 笨拙                     |
| 不会骑自行车         | HP:0002312   | Clumsiness                                     | 笨拙                     |
| 食纳增加             | 无           | 无                                             | 无                       |
| 小便频率增加         | HP:0100515   | Pollakisuria                                   | 尿频                     |
| 夜尿情况不详         | 无           | 无                                             | 无                       |
| 父母非近亲结婚       | 无           | 无                                             | 无                       |
| 无家族遗传史         | 无           | 无                                             | 无                       |


RAG 确实解决了直接推理中的幻觉问题，但其最终准确性却不如 Deepseek V3 和 R1 的直接推理结果。例如，在“小便频率增加”这一临床表型时，多尿（Polyuria，同义词：Increased urine output）比尿频（Pollakisuria，同义词：Constant urination - Frequent urination）更为准确。同样的，对于“食纳增加”这一表述，其隐含的“食欲增加”或“多食”含义，RAG 未能成功匹配到 Polyphagia（同义词：Hyperphagia - Voracious appetite - Increased appetite）这一术语。这些问题的出现，可能是由于词组过短，且构建向量数据的语料主要以英文原文为主，导致向量数据检测准确性不足，后续的HP 分析自然也就不会产生准确结果。

### 验证 Deepseek R1 幻觉程度
在这项任务中，RAG 可能并非最优解。相比之下，也许采用 Deepseek 的推理结果，并根据 HP 英文名称在 HPO 数据中进行校验，能够获得更佳的结果。那么如果采用这个策略，Deepseek R1 编造 HP 术语的的比例是怎么样的呢？

再做一个小实验，采用另一个模型 gpt-4o-mini 针对《第一批罕见病目录》的121种罕见病，每一个病生成一个不超过200字的临床描述。然后针对这些具有差别性的描述采用直接推理的方式进行 HP 分析。因为我们的目标是评估 Deepseek R1 生成 HP 术语时的幻觉程度，所以这里临床描述是否吻合具体疾病、是否足够丰富并不是我们关注的重点。

> **21-羟化酶缺乏症临床描述示例**
>
> 患者为一名8岁女孩，主诉近期出现疲劳、食欲不振及体重下降。体检发现她的皮肤色素沉着明显，尤其是在肘部和膝盖处。家长提到她在出生后曾有过呕吐和脱水的情况，且月经初潮延迟。实验室检查显示电解质失衡，钠水平偏低，钾水平偏高。激素水平检测结果显示皮质醇和醛固酮水平异常。患者的家族史中有类似症状的亲属，提示可能的遗传因素。医生建议进行进一步的内分泌评估和基因检测，以明确诊断并制定相应的治疗方案。


答案揭晓，在 Deepseek R1 直接推理分析这些临床描述生成的1469个 HP 术语英文名称中，78.8%（n=1151）是真实存在的。


## 总结
在这项测试中，直接推理能更优秀的处理一些难词、罕见词，但存在幻觉问题，需要额外的校验步骤进行修正。而 RAG 方法则相反。至于哪种方式准确性更好，仍需要基于有标注数据进一步验证。
