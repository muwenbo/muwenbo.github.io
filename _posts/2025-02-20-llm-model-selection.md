---
layout: post
title: "基因诊断中的大模型选择：国产大模型能胜任吗？"
date: 2025-02-20
category: professional
image: /assets/images/posts/2025-02-20-llm-model-selection/cover.jpg
tags: [bioinformatics, LLM, AI]
---
## 引言

自从ChatGPT横空出世，各行业都在热议如何把LLM（大语言模型）应用到日常工作中。作为一名基因诊断领域的研究者，我也就在思考怎么用人工智能来解决基因诊断中的实际问题。

如果在国内开发和应用LLM工具，从合规性角度考虑，只能选择国产模型。那第一个要明确的就是国产大模型的能力是否足够支撑医学领域工具的开发，毕竟文心一言闹出的笑话至今令人记忆犹新。在进行大规模的测试之前，我想先用一个小的具体任务试试水，同时以ChatGPT、Claude.ai这些国际标杆模型为参考，对比一下各家模型的能力。

## 方法

具体任务其实是从日常工作中找到的灵感。在分子遗传的检测报告中，通常需要一段解释某个基因会导致何种疾病的描述。这些内容通常是从OMIM和GeneReviews这样的权威资料中提取整理翻译而来，所以这项任务有以下几个关键点：

1. **跨语言汇总**：输入数据主要来自专业知识库，以英语为主，但需要以中文总结的形式进行输出；
2. **医学术语的准确翻译**：这一项相对具有挑战性，因为分子遗传这个领域很多专业词汇的翻译并不全面，大模型可能缺少足够的双语语料来进行训练；
3. **遵守特定的格式要求**：输出必须遵循预定的结构，以保持检测报告的一致性。


那么首先需要准备测试数据。我采用OMIM数据库接口，查询并提取了一个特定基因（以*SLC2A1*为例）的关键信息，包括它和各种表型之间的对应关系，以及分子层面的描述。其中基因和表型的对应关系整理成了一个Markdown表格，而分子描述的部分则保持原来的XML格式。

###### OMIM Phenotype-Gene Relationships
![](https://files.mdnice.com/user/90337/c1bca6d7-06d4-4eb2-b0ce-a3694b25555a.png)

###### OMIM Molecular Genetics
> GLUT1 Deficiency Syndrome 1 In patients with a transport defect of glucose across the blood-brain barrier, consistent with GLUT1 deficiency syndrome-1 (GLUT1DS1; {606777}), {43:Seidner et al. (1998)} identified heterozygous mutations in the SLC2A1 gene ({138140.0001}-{138140.0003}). Two of the patients had been reported by  ……

接下来，采用 LangChain 的 PromptTemplate 创建了一个标准的提示模板，列出我的四个要求：

1. 说明基因和疾病之间是什么关系，重点解释基因变异是怎么导致这些疾病的，需要提到遗传方式。
2. 如果包含具体的患者信息，总结可能会出现的临床表现。
3. 疾病名称的格式要求：中文名（英文名）[MIM：OMIM编号]。
4. 最终输出的格式要求：一段话，不能超过500字。


```python
from langchain.prompts import ChatPromptTemplate

template = """作为遗传学专家，你的职责是阅读基因相关的英文信息，
并总结归纳成基因疾病相关性的描述。请遵循以下准则：
1. 以基因名称为主语进行描述，需求强调基因的致病变异会导致相关疾病，并说明遗传模式。
2. 如果基因信息中包含疾病的患者信息，需要简要总结疾病的患者可能存在的临床表现。
3. 疾病名称需要为中文名（英文名）[MIM:omim id]的格式。
4. 不分行，以一个段落进行输出；字数不超过500字。
<<表型关系/phenotype map>>: {phenotype}
<<基因信息/molecular genetics>>:{molecular_genetics}
"""

prompt = ChatPromptTemplate.from_template(template)
```


模型方面则主要采用各家主打性价比、中等水平的模型，因为这次测试的任务既不包含长文，也不需要很强的推理能力，属于较为基础的提示词理解。按照各家的宣传材料，中等水平的模型也都是足以胜任的。

- 字节跳动 Doubao-pro-32k-240615
- 阿里巴巴 Qwen-plus
- Meta开源 Llama3–70b-instruct
- OpenAI GPT-4o-mini
- Anthropic Claude-3-opus-20240229
- 月之暗面 Moonshot-v1-128k
- 深度求索 DeepSeek-V3

###### 调用LLM模型的示例代码（以Claude.ai为例）
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
claude_llm = ChatAnthropic(model='claude-3-opus-20240229',temperature = 0.0)
chain = prompt | claude_llm | StrOutputParser()
response = chain.invoke({'phenotype': phenotype_markdown_table, 'molecular_genetics': molecular_genetics})
display(Markdown(response))
```

## 结果评估

###### Doubao-pro-32k-240615
> SLC2A1 基因的致病变异会导致多种疾病。其遗传模式包括常染色体显性遗传、常染色体隐性遗传。
> 
> 特发性全身性癫痫易感性 12（Epilepsy, idiopathic generalized, susceptibility to, 12）[MIM:614847]，患者可能存在轻度至中度智力障碍、轻度共济失调、肌阵挛、运动诱发的阵发性运动障碍等临床表现。
> 
> 肌张力障碍 9（Dystonia 9）[MIM:601042]，患者多在儿童期发病，表现为阵发性舞蹈手足徐动症和进行性痉挛性截瘫，多数存在一定程度的认知障碍，还可能有癫痫、偏头痛、共济失调等症状。
> 
> 婴儿起病的严重 GLUT1 缺乏综合征 1（GLUT1 deficiency syndrome 1, infantile onset, severe）[MIM:606777]，患者可能有全身性强直阵挛性癫痫、肌阵挛性癫痫、轻度痉挛性双侧瘫痪、发育迟缓、中度智力障碍、小脑性共济失调、锥体束征等。
> 
> 儿童起病的 GLUT1 缺乏综合征 2（GLUT1 deficiency syndrome 2, childhood onset）[MIM:612126]，患者可能有精神运动发育迟缓、中度智力障碍、水平眼球震颤、构音障碍、肢体共济失调、反射亢进、肢体肌张力障碍姿势等。
> 
> 伴有神经系统缺陷的 stomatin 缺陷性冷性血细胞增多症（Stomatin-deficient cryohydrocytosis with neurologic defects）[MIM:608885]。

###### Qwen-plus
> SLC2A1基因的致病变异可导致多种神经系统疾病，包括苯丙糖转运蛋白缺乏症1型（GLUT1DS1；606777）、苯丙糖转运蛋白缺乏症2型（GLUT1DS2；612126）、与SLC2A1相关的神经缺陷性冷水溶血症（SDCHCN；608885）、特发性全身性癫痫12型易感性（EIG12；614847）及肌张力障碍9型（DYT9；601042）。这些变异主要通过常染色体显性遗传模式传递，少数情况下也可通过常染色体隐性方式遗传。苯丙糖转运蛋白缺乏症1型表现为婴儿期严重的症状，包括发育迟缓、肌阵挛发作、智力障碍、共济失调和腿部锥体束征等。该疾病还可能导致低脑脊液葡萄糖水平（hypoglycorrhachia）。苯丙糖转运蛋白缺乏症2型则通常在儿童期发病，特征为发作性运动障碍、共济失调、构音障碍等症状，且部分患者无癫痫发作。与SLC2A1相关的神经缺陷性冷水溶血症表现为新生儿期出现神经缺陷和红细胞膜阳离子泄漏，导致假性高钾血症和红细胞溶解。特发性全身性癫痫12型易感性表现为早发性失神发作，部分患者伴有轻度至中度智力障碍、轻微共济失调或运动诱导的发作性运动障碍。肌张力障碍9型则表现为儿童期发作的舞蹈手足徐动症和进展性痉挛性截瘫，伴随认知障碍、癫痫发作、偏头痛等症状。上述疾病均与SLC2A1基因突变有关，表明该基因在维持正常神经系统功能方面起关键作用。

###### Llama3–70b-instruct
> SLC2A1基因的致病变异会导致多种疾病，包括 GLUT1缺乏症候群1（GLUT1DS1，606777）[MIM:606777]、GLUT1缺乏症候群2（GLUT1DS2，612126）[MIM:612126]、 idiopathic generalized epilepsy 12（EIG12，614847）[MIM:614847]、Dystonia 9（DYT9，601042）[MIM:601042] 和 Stomatin-deficient cryohydrocytosis with neurologic defects（SDCHCN，608885）[MIM:608885]。这些疾病的遗传模式为 autosomal dominant 或 autosomal recessive。
> 
> GLUT1DS1的患者可能存在发育迟缓、智力障碍、癫痫、肌张力障碍、共济失调和视力障碍等临床表现。GLUT1DS2的患者可能存在发育迟缓、智力障碍、癫痫、运动障碍和视力障碍等临床表现。EIG12的患者可能存在癫痫、智力障碍和运动障碍等临床表现。DYT9的患者可能存在舞蹈症、痉挛性麻痹和智力障碍等临床表现。SDCHCN的患者可能存在神经系统损害、红细胞膜缺陷和低血糖等临床表现。

###### GPT-4o-mini
> SLC2A1基因的致病变异与多种疾病相关，包括葡萄糖转运缺陷综合征1（GLUT1缺乏症1，GLUT1DS1）[MIM:606777]、葡萄糖转运缺陷综合征2（GLUT1缺乏症2，GLUT1DS2）[MIM:612126]、特发性全身性癫痫易感性12（EIG12）[MIM:614847]、以及肌张力障碍9（Dystonia 9，DYT9）[MIM:601042]。SLC2A1基因的突变通常以常染色体显性遗传模式传递。GLUT1缺乏症1的患者可能表现为全身性强直-阵挛性癫痫、发育迟缓、轻度智力障碍、运动协调障碍等症状；而GLUT1缺乏症2的患者则可能出现运动发育延迟、横向眼震、言语不清、肢体共济失调等表现。特发性全身性癫痫易感性12的患者通常在4岁之前出现缺失性癫痫，可能伴有轻度至中度智力障碍和运动失调。肌张力障碍9的患者则可能在儿童期出现阵发性舞蹈样运动和进行性痉挛性下肢麻痹，且大多数患者存在一定程度的认知障碍。SLC2A1基因的突变导致的葡萄糖转运缺陷，影响了血脑屏障的功能，进而引发神经系统的多种病理表现。

###### Claude-3-opus-20240229
> SLC2A1基因的致病变异可导致多种疾病。杂合突变可引起婴儿期发病的1型葡萄糖转运蛋白缺乏综合征（GLUT1 deficiency syndrome 1, infantile onset, severe）[MIM:606777]，常染色体显性或隐性遗传；儿童期发病的2型葡萄糖转运蛋白缺乏综合征（GLUT1 deficiency syndrome 2, childhood onset）[MIM:612126]，常染色体显性遗传；常染色体显性遗传的9型原发性扭转痉挛（Dystonia 9）[MIM:601042]；常染色体显性遗传的特发性全身性癫痫易感性12型（Epilepsy, idiopathic generalized, susceptibility to, 12）[MIM:614847]；以及常染色体显性遗传的神经系统异常的缺乏Stomatin的冷凝集素血症（Stomatin-deficient cryohydrocytosis with neurologic defects）[MIM:608885]。患者的临床表现包括癫痫发作、运动障碍如舞蹈病和肌张力障碍、发育迟缓和智力低下等。SLC2A1基因编码葡萄糖转运蛋白GLUT1，突变会影响GLUT1蛋白的细胞内定位、降低葡萄糖转运功能，从而导致神经系统能量代谢障碍和红细胞膜离子通透性异常。

###### Moonshot-v1-128k
> SLC2A1基因的致病变异可导致多种疾病，包括癫痫、肌张力障碍、GLUT1缺乏综合征等，遗传模式主要为常染色体显性遗传。患者可能出现的临床表现包括全面性强直阵挛发作、肌阵挛发作、轻度精神发育迟滞、抑郁、偏头痛、轻度痉挛性双瘫、发育迟缓、复杂部分性发作、中度精神发育迟滞、小脑共济失调、轻度锥体束征、低血糖性脑脊液等。其中，GLUT1缺乏综合征1型（GLUT1DS1；606777）表现为婴儿期严重发作，包括全面性发作、发育迟缓、小脑共济失调等；GLUT1缺乏综合征2型（GLUT1DS2；612126）表现为儿童期发作，包括发作性运动诱发性运动障碍、轻至中度精神发育迟滞、水平眼球震颤、构音障碍、肢体共济失调、腱反射亢进、肢体肌张力障碍等。特发性全面性癫痫12型（EIG12；614847）主要表现为儿童期发作的失神发作。肌张力障碍9型（DYT9；601042）表现为儿童期发作的发作性舞蹈手足徐动症和进行性痉挛性截瘫，部分患者伴有认知障碍、癫痫发作、偏头痛和共济失调等。[MIM:138140]

###### DeepSeek-V3
> SLC2A1基因的致病变异可导致多种疾病，其遗传模式主要为常染色体显性遗传。SLC2A1基因突变与葡萄糖转运蛋白1缺乏综合征1型（GLUT1 deficiency syndrome 1, infantile onset, severe）[MIM:606777]相关，患者表现为婴儿期严重的神经系统症状，包括癫痫发作、发育迟缓、智力障碍和小脑性共济失调。此外，SLC2A1基因突变还与葡萄糖转运蛋白1缺乏综合征2型（GLUT1 deficiency syndrome 2, childhood onset）[MIM:612126]相关，患者表现为儿童期发病的运动障碍、发育迟缓和癫痫，部分患者伴有溶血性贫血。SLC2A1基因突变还可导致阵发性运动诱发性运动障碍（Paroxysmal exercise-induced dyskinesias）和特发性全面性癫痫12型（Epilepsy, idiopathic generalized, susceptibility to, 12）[MIM:614847]，患者表现为儿童期发病的癫痫发作、轻度智力障碍和运动障碍。SLC2A1基因突变还与肌张力障碍9型（Dystonia 9）[MIM:601042]相关，患者表现为儿童期发病的阵发性舞蹈手足徐动症和进行性痉挛性截瘫，部分患者伴有认知障碍、癫痫和偏头痛。此外，SLC2A1基因突变还与缺乏stomatin的冷溶血性贫血伴神经系统缺陷（Stomatin-deficient cryohydrocytosis with neurologic defects）[MIM:608885]相关，患者表现为神经系统症状和溶血性贫血。

在这个简单测试中，Claude-3-opus和DeepSeek-V3是明显的胜者，他们生成的结果几乎不需要修改，GPT-4o-mini紧随其后。其他模型的结果则有些差强人意了。具体来讲：

- **翻译准确度**：DeepSeek-V3和Claude-3-opus在翻译这个测试中的复杂医学术语时格外优秀，其他几个模型在处理"GLUT1"这样的缩写时就比较吃力了，而Qwen-plus则给出了错误的名称翻译；
- **症状描述**：所有模型都表现不错，都能较好的总结基因变异相关的临床表现，说明它们都能理解提供的医学信息。但总结后的可读性方面，Llama3–70b-instruct和Doubao-pro表型较差；
- **格式要求**：DeepSeek-V3、Doubao-pro和Claude-3-opus严格按照要求的格式写疾病名称，其他模型或多或少没有按照要求完成；
- **输出结构**：Doubao-pro和Llama3 70b没有实现以一段话进行输出，看起来对对较复杂的提示词理解处理并不理想。

## 总结
通过这个小实验，我观察到不同的LLM在处理专业医学任务时，其性能表现是存在显著差异的。所以在将AI技术应用于关键的医疗工作之前，其实需要较为审慎的进行模型对比和选择。当前LLM模型的迭代速度极快，业界往往追逐最新、最热门的模型，未来更换LLM应用的底层基底模型将变得司空见惯。然而，本次实验也提醒我，基底模型的更换可能对成熟应用的性能产生决定性的影响。因此，在切换基底模型之前，进行充分的验证和测试是至关重要的。

当然，这个测试存在很多局限性。首先，这仅是一个基于单例的测试，而非基于数据集的全面评估。因此，对于不同的基因，前文所述各模型的优劣结论是否依然成立，尚不得而知。其次，这并非一个公平的测试，我所测试的这些模型在成熟度和参数数量上是存在代差的。例如，DeepSeek-V3和Moonshot-v1-128k均为最新模型，而其他模型则可能是半年甚至一年前的版本。

业内广泛认可的DeepSeek-V3毫无疑问表现出色。我没有测试阿里最新的Qwen-Max和字节的Doubao-1.5-pro，他们也许已经解决了Qwen-plus和Doubao-pro在我的测试中所出现的问题。不过，至少进入2025年，国产大模型已经具备足够的性能，以支持一些严肃生产工具的开发了。AI技术在医疗领域的应用潜力巨大，但在实际应用中，我们还是需要谨慎选择模型，打磨提示词，并充分考虑其性能、结果准确性和局限性。


