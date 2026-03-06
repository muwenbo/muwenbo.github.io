## 引言

在遗传病和罕见病的分子诊疗过程中，目前的行业标准是基于 ACMG（美国医学遗传学会）的指南开展。ACMG 指南中提供了一整套系统的方法来解读基因组数据，并评估变异对患者的临床影响。在具体的遗传基因数据解读中，判断一个变异是否能解释病人的临床表型，除了考虑基因-疾病的相关性（上篇已讨论），还必须评估变异的致病性。

具体来说，ACMG 将变异分为五个等级：

- **致病变异（Pathogenic, P）**：已知会导致疾病。
- **可能致病变异（Likely Pathogenic, LP）**：有较强证据支持致病性，但尚未完全确认。
- **良性变异（Benign, B）**：通常与疾病无关。
- **可能良性变异（Likely Benign, LB）**：可能对健康无影响，但证据尚不充分。
- **不确定意义的变异（Variant of Uncertain Significance, VUS）**：临床影响不明，需进一步研究。

那本篇我们将继续大模型在分子遗传诊断中的应用探索，尝试构建一个 AI Workflow 来解决这个问题。之所以称之为“workflow”而非“agent”，是因为本篇的打算还是使用大模型按照一定的流程处理数据和执行任务，而非实现一个可以自主决策或动态响应的 AI。但现在凡是跟 AI 挂钩的东西都叫“智能体”了，那我们自称 AI 智能体可能也不是不可以。

---

## 实现方法

### 开发平台

支持构建 AI workflow/agent 的编排工具有很多，像Coze、n8n、Dify。他们都能提供了易用的界面和 API，让我们可以少写代码，把精力多专注在问题的解决方案上。用来做概念验证或是原型设计都是不错的工具。我目前选择的是开源的 Dify ，并将其部署在本机上，方便调用本地的数据和资源。

### 输入数据

在处理复杂问题时，大模型常常会一本正经地胡说八道。因此，我不觉得类似“请对 NM_000142.5(FGFR3):c.2408del (p.Gly803fs) 基于ACMG指南进行评级”这样的指令能获得满意的结果。我们至少应该向大模型提供可以进行评级的数据基础。

通过 ACMG 指南，我们可以拆解出评级所需的四类关键数据：

1. **变异级别的注释信息**：包括变异命名、碱基变化、人群频率、致病性算法预测等。
2. **基因相关信息**：如致病机理（disease-causing mechanism）、基因约束（gene constraint）、基因-疾病临床有效性（clinical validity）等。
3. **转录本信息**：包括转录本长度、编码区结构、NMD 阈值等。
4. **最新的文献或病例研究**：如功能研究（functional studies）、共分离数据（co-segregation）、de novo 发生情况等。

我们需要分别针对性的做准备：
1. **变异数据**：可以使用 Ensembl VEP 来进行注释，给定变异坐标，输出基本上可以涵盖变异级别包括HGVS命名、人群频率、Unipot domain 等大量信息。然后搭建一个可供 Dify 调用的注释 RESTful API。
2. **基因数据**：我们将OMIM、ClinGen、gnomAD 和 Decipher 中基因相关的数据库收集并基于 gene ID 整合到一起，包含pLI、LOEUF、 TS score, HI score, OMIM phenotype 等基因相关的信息。然后封装成可供 Dify 查询的 RESTful API。
3. **转录本数据**：来源于 NCBI 的 gff 文件。我们不想让模型做推理的同时，还要做数学计算。所以这里提前计算了每个转录本的长度、外显子结构，并根据 50-55 nt 规则估算 NMD 阈值。对于像 *PTEN*、*CDH* 等一些 ClinGen 有特殊规定的基因，也可以直接修正具体数值来测试大模型对 NMD 的判读准确性。
4. **文献或病例研究**：目前像 SerpApi, Tavily 等主流的支持 AI 搜索的工具大多是执行网页搜索，返回的结果主要是 ClinVar 数据的总结，无法得到我们想要的来着文献内容的 de novo 发生情况、功能性研究或替代分子机制（alternative molecular basis）等信息。唯一较符合需求的是 scite.ai，它可以基于自定义提示词收集文章，并提取相关研究数据。可惜免费账户无法调用 API，因此无法直接整合进这个 workflow 中。只能将他的文献总结作为手动输入到 workflow 中。

![](https://files.mdnice.com/user/90337/c9ca4938-5d8b-4b88-93b7-016f9ce123cd.png)

![](https://files.mdnice.com/user/90337/77089803-2b69-4b36-9703-475dc12bd536.png)


### 模型及提示词构建

在模型方面使用具备推理能力的 GPT-o1 模型。理论上讲推理型模型会自行组织思维链（Chain of Thought, CoT），所以这里这次测试我先假设AI已经全知全能、超越人类，不特意指定推理步骤，而是只规定角色和输出格式，剩下的交给大模型自由发挥。

**提示词**：
> You are a genetic variant curation expert. Your role is to analyze genetic variant information and apply established classification guidelines to determine clinical significance according to ACMG/AMP or other relevant guidelines. You should explain your reasoning throughout the classification process."
> 
> ## Input:
> 
> <variant_annotation>
> {{variant_annotation}}
> </variant_annotation>
> 
> <gene_annotation>
> {{gene_annotation}}
> </gene_annotation>
> 
> <transcript_annotation>
> {{transcript_annotation}}
> </transcript_annotation>
> 
> <research_summary>
> {{research_summary}}
> <research_summary>
> 
> ## Additional Considerations:
> 
> 1. ClinGen Expert Panel Specifications: If applicable, incorporate expert panel recommendations.
> 2. Gene-Disease Validity: Consider whether the gene is established to be associated with the condition.
> 3. Evidence Strength: Clearly state which ACMG/AMP criteria were applied and how they contribute to the classification.
> 
> ## Output Format:
> 
> Variant Analysis for [variant] in [gene]:
> - Final Classification:
> [Pathogenic / Likely pathogenic / VUS / Likely benign / Benign]
> 
> - Evidence Summary (with ACMG/AMP Criteria Applied):
> Population Data: [e.g., ExAC, gnomAD, allele frequency] – [BA1 / PM2 / etc.]
> Computational and Predictive Data: [e.g., in silico tools, conservation] – [PP3 / BP4 / etc.]
> Functional Data: [e.g., experimental evidence of impact on gene/protein function] – [PS3 / BS3 / etc.]
> Segregation Data: [e.g., segregation with disease in families] – [PP1 / BS4 / etc.]
> Phenotypic Specificity: [e.g., phenotype match to disease] – [PP4 / BP5 / etc.]
> Other Supporting Evidence: [if applicable] – [e.g., PS2, BP1, etc.]
> 
> - Classification Justification:
> Summarize how the applied evidence codes led to the final classification decision. Clearly explain whether criteria were met at strong, moderate, or supporting levels, and how they collectively support the determination of pathogenicity or benignity.


### AI Workflow 构建

这样，我们就有了足够的准备来构建一个最基础的 AI Workflow 了，按顺序依次完成变异注释、基因注释、转录本注释以及模型推理。

![](https://files.mdnice.com/user/90337/7ec823c2-d38a-4032-9ae3-c1821c3d415b.png)


到了这个阶段，可以宣称胜利了——我们已经成功搭建了一站式 AI 遗传分子诊断大模型，bla bla bla。不过作为还有一些节操的开发者，即使是并不追求严谨的概念验证，也还是需要挑几个变异测试和评估一下。

---

## 测试

我们从 ClinGen 的 Variant Curation 数据库中选取 VUS、LP、P 各一个变异进行测试。这些变异均由 ClinGen 专家评定，且附有证据代码和详尽解释，因此不仅可以用来比较 AI 最终的评级准确性，也可以评估他的思考过程是否和人类专家相符。为了避免篇幅过长，后2个测试用例就不贴具体的 AI 输出了，仅做简单的总结。

### 用例1
**变异**： NM_000314.8(PTEN):c.283C>A (p.Pro95Thr) 

**评级**：
VUS (PP2_Moderate+PP3+PM2_Supporting)

> **ClinGen专家总结**：
> NM_000314.8(PTEN):c.283C>A (p.Pro95Thr) is currently classified as a variant of uncertain significance for PTEN Hamartoma Tumor syndrome in an autosomal dominant manner using modified ACMG criteria (ACMG Classification Rules Specified for PTEN Variant Curation version 3.1.0). Please see a summary of the rules and criteria codes in the “PTEN ACMG Specifications Summary” document (assertion method column). PP2: PTEN is defined by the PTEN Expert Panel as a gene that has a low rate of benign missense variation and where missense variants are a common mechanism of disease. PP3: REVEL score > 0.7 (score of this variant = 0.854). PM2_P: Absent in gnomAD.

**AI结果**：
> Variant Analysis for chr10:87933042 C>A (NM_000314.8(PTEN):c.283C>A, p.Pro95Thr) in PTEN:
> 
> --------------------------------------------------------------------------------
> 
> • Final Classification:  
> 
> Likely Pathogenic
> 
> --------------------------------------------------------------------------------
> 
> • Evidence Summary (with ACMG/AMP Criteria Applied):
> 
> ► Population Data (PM2):  
> 
> No population frequency data were provided for this variant. PTEN is under strong purifying selection, and most pathogenic variants are rare or absent in population databases. Inferred absent/very low frequency → PM2 (Moderate)  
> 
> ► Computational and Predictive Data (PP3):  
> 
> Multiple in silico tools (PolyPhen: “probably damaging,” SIFT: “deleterious”) predict a deleterious effect on protein structure/function. The affected residue (p.Pro95) lies within PTEN’s phosphatase domain, which is crucial for function. These predictions support pathogenicity → PP3 (Supporting)
> 
> ► Gene-Specific Considerations (PM1, PP2):  
> 
> • PTEN is a tumor suppressor gene in which missense variants are a well-known mechanism of disease.  
> 
> • p.Pro95 is in the critical phosphatase domain of PTEN (spanning roughly amino acids 14–185), which is a mutational hotspot with few benign variants. This supports PM1 (Moderate).  
> 
> • Because PTEN has a low rate of benign missense variation and missense changes are a frequent cause of disease in this gene, PP2 (Supporting) also applies.
> 
> ► Other Data:  
> 
> • Conflicting ClinVar interpretations (Uncertain Significance vs. Likely Pathogenic) underscore that not all data are fully concordant, but the overall weight of evidence from rarity, domain location, and computational predictions leans toward pathogenicity.
> 
> (No direct segregation, phenotypic, or functional assay data are provided here to apply PS3, PP1, PP4, etc., and no high-level population evidence is provided to invoke BA1/BS1.)
> 
> --------------------------------------------------------------------------------
> 
> • Classification Justification:
> 
> This missense variant occurs in a critical domain of PTEN and is predicted to have a deleterious effect by multiple computational tools. It appears rare or absent in population databases (PM2) and falls within a known functionally important region with few benign variants (PM1). PTEN is known to harbor disease-causing missense variants (PP2), and strong in silico predictions further support pathogenicity (PP3). The collective evidence fulfills at least two Moderate (PM1 + PM2) and two Supporting (PP2 + PP3) criteria, consistent with an overall assessment of Likely Pathogenic under ACMG/AMP guidelines.

**专家vs.AI**:
1. 共同点

专家和 AI 都引用的ACMG 证据：
- **PP2（基因的疾病相关性）**：PTEN 主要通过错义变异致病，且错义变异较少是良性变异。
- **PP3（生物信息学预测）**：REVEL 评分较高（>0.7），表明该变异可能影响蛋白功能。
- **PM2（人群数据库频率）**：该变异在 gnomAD 等人群数据库中缺失或极为罕见。

2. 评级分歧的关键点

| 证据项              | **专家（VUS）**                                                    | **AI（Likely Pathogenic）**                                           |
|---------------------|---------------------------------------------------------------------|-------------------------------------------------------------------------|
| **PM1（关键功能区域）** | 未提及                                                             | 认为该变异位于 PTEN 重要功能区域，且该区域内良性变异较少                   |
| **PM2（低频率证据）**  | 采用 PM2_P（弱证据）                                               | 采用 PM2（中等证据）                                                   |
| **综合证据解读**      | 仅采用 **PP2、PP3、PM2_P**，证据不够充分，无法确定致病性              | 采用 **PM1、PM2、PP2、PP3**，符合 “2个 Moderate + 2个 Supporting” 证据要求，达到 **Likely Pathogenic** 级别 |


### 用例2
**变异**：NM_000277.1(PAH):c.1066-7C>A

**评级**：
Likely Pathogenic (PP4_Moderate+PM2+PM3)

**专家vs.AI**:
1. 共同点

专家和 AI 都引用的ACMG 证据：
- **PM2（低频率证据）**：该变异在 gnomAD 中的频率极低，符合 **PAH** 为稀有的常染色体隐性遗传疾病的背景。
- **PP3（生物信息学预测）**：该变异位于 **3′ 剪接接受位点** 附近，虽然功能尚未确认，但生物信息学工具通常预测靠近剪接位点的区域可能影响剪接。

2. 评级分歧的关键点

| 证据项              | **专家（Likely Pathogenic）**                                      | **AI（VUS）**                                                 |
|---------------------|--------------------------------------------------------------------|------------------------------------------------------------------|
| **家系共分离数据**    | 未提供相关数据，认为该变异 **在同源合子状态下检测到**，支持致病性。 | **无家系共分离数据**，因此 **PP1 / BS4** 无法应用。            |
| **临床观察和功能研究** | 有三个病例报道显示该变异与 PAH 缺乏相关（PMID: 12655553，21147011，21307867）。  | **缺乏功能研究**，没有明确证据支持该变异影响功能，因此不能应用 **PS3/BS3**。 |
| **表型特异性**        | 变异与 PAH 临床表现存在相关。                                    | **没有明确的表型关联**，因此 **PP4/BP5** 无法应用。           |


### 用例3
**变异**：NM_000051.4(ATM):c.3576G>A (p.Lys1192=)

**评级**：
Pathogenic (PM3_Very Strong+PVS1_Strong)

**专家vs.AI**:
1. 共同点

专家和 AI 都认为该变异对 **ATM 基因功能** 有影响，且都提供了支持性证据。具体的共同点包括：
- **PM2（低频率证据）**：该变异在 **gnomAD** 数据库中非常罕见，符合低频率要求，支持该变异可能与疾病相关。
- **功能数据（PS3）**：专家和 AI 都提到该变异通过 **实验确认** 导致 **外显子跳跃（exon skipping）**，进而引发 **ATM 蛋白的框移缺失**，从而影响蛋白功能。
- **表型特异性（PP4）**：该变异在 **Ataxia-Telangiectasia（共济失调-毛细血管扩张症）** 和 **ATM 相关癌症**（如黑色素瘤）患者中有报告，符合 **ATM** 基因在疾病中的致病作用。

2. 评级分歧的关键点

| 证据项                    | **专家 (Pathogenic)**                                                         | **AI (Likely Pathogenic)**                                                         |
|---------------------------|--------------------------------------------------------------------|--------------------------------------------------------------------|
| **PVS1（无义变异影响功能）** | 提到该变异 **影响RNA**，被认为 **强致病性证据**（RNA分析确认）。       | 没有使用 **PVS1**，但 **功能数据** 通过 **PS3** 得到支持。          |
| **PM3（同位致病变异）**     | 强调该变异导致 **外显子跳跃**，并且在多名 **Ataxia-Telangiectasia** 患者中检测到。 | 未采用。   |
| **ClinVar支持性证据**      | 未提及 **ClinVar** 支持。                                          | 该变异在 **ClinVar** 中有 **致病性或可能致病性** 的报告，支持性证据。 |


---

## 结语

在对这几个测试用例以及其他未展示的用例分析后，可以总结出以下几点：

1. AI 的判断直觉还不错。基本不会出现像从致病变异（Pathogenic）判断为良性（Benign），或者反过来这种严重跑偏的情况。但从思考过程的输出来看，AI 并不严格遵从 ACMG 指南的标准流程进行解读。

2. AI 对 PM2（低频率证据）、PP3（生物信息学预测）等明确数据层面的分析做得比较到位。但是，像 PVS1 这种复杂且需要多重分析的证据，AI 在准确性仍然有待提高。针对 PVS1 证据的分析，可能还是需要单独设计特定的 workflow。此外，证据权重的微调，AI 目前是无法完成的。

3. AI 在评级过程中经常倾向于参考 ClinVar 数据库。如果某些变异在 ClinVar 中的数据不够可靠，很可能会导致 AI 产生错误的判断。而 ClinGen 早已经建议在 PP5 和 BP6 上不要使用 ClinVar 数据。

4. 文献研究和病例数据的分析仍有较大提升空间。虽然特定的 AI 工具能进行文献的搜索和分析，但在专家评级中使用的文献，AI 基本无法精准自动找到。这个问题并不在于推理模型本身，而是现有的文献检索和分析技术仍然不够理想。短期内可能还是需要采用人工提供相关文献内容，由 AI 辅助分析的方式。

总体来说，当前的 AI Workflow 还不能一站式解决问题。想要投入临床应用，需要进一步拆解和完善评级过程中的各个环节。
