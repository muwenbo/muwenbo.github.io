# 燃烧token不是程序员的特权，遗传分析师们，请把你们的订阅买起来

## TR;LD 

我实现了一个ClinGen Aware Variant Classification Skill，配合claude code, codex等 AI 编程工具，实现精确的、有依据的，符合ClinGen规范的变异评级。Find it at https://github.muwenbo.com/vcep-aware-classifier-skills

## 引言
基于AI变异评级一直是一个我在考虑实现，但却不知道该如何下手的一块儿硬骨头。对于变异评级，其实已经有很多自动化评级的工具，我自己也开发过这种工具。这种工具的共同问题是，即使我们不考虑无法由于无法处理主要来自文献的功能研究（PS3/BS3）、家系证据（PP1/BS4）或其他分子原因的证据而导致的评级偏差，只关注能基于数据库注释进行分析的评级证据（例如PP3/PS1等），这类工具的证据和专家的选择也是有很大差异的。这主要是因为ACMG指南里主要还是一个通用性指导，并没有对各个证据的判断给予明确的阈值，于是各个自动化评级工具都会基于自己的理解、方法论等制定各自的阈值。

ClinGen 专家组根据各个专病，以及基因在疾病的特色制定了更细化的评级细则。但由于依然是描述性的细则，其中包含的很多附录流程和说明有PPT, 有word, 有excel，格式很不结构化。如果要把某一细则完全程序化的实现出来，需要大量的人工梳理工作。所以即使是Varsome这种商业化的平台，都很难提供符合 ClinGen 的证据匹配。



而去年10月份Claude 发布 skill以来，看到他的惊艳效果，我知道这就是现阶段变异评级的终极答案。

如果你还不知道什么叫 Skills，简单说就是一种让 AI 掌握特定领域知识和工作流程的机制。它的核心思路是：通用模型 + Skills（领域知识）+ Tools（工具调用）来实现类似 Agent 的能力，但你不需要操心什么规划器、执行器、工具协议这些复杂的东西，Claude code、Codex 这类 AI 编程工具会自己处理。

以前我总想着怎么搭 workflow 或者构建多级智能体，但这些预定义的流程面对变异评级的复杂性时，灵活性往往不够。现在用 AI + Skills 的方式，Skills 就像是给 AI 提供的"变异评级说明书"，它能快速掌握领域知识，同时还保留了自主调用工具、搜索网络、灵活决策的能力。不用把所有路径都提前设计好，AI 可以根据实际情况动态应对。


## 从变异评级的角度，Skill该怎么设计？

和所有 AI 处理专业工作的需求一样，我们需要提供充分的上下文，或者说降低 AI 自己准备上下文的努力。那么变异评级所需的上下文大致就是以下 4 个。

### VCEP 专家组评级指南

既然我们的目标是构造符合 ClinGen 规范的变异评级，那么第一步肯定是为 AI 提前准备 ClinGen 规范。我们将每一个 VCEP 的各类格式的文件整合成一个 AI 更容易阅读的 markdown 格式。这样在后续分析中，AI 自己就不用去 ClinGen 网站上查找学习规范了，同时也便于我们根据自己的需求和分析过程中的遇到的问题具体调整。

下载和分析 ClinGen 规范的 skill 也打包在这个skill了。
目前所有可用的 ClinGen 规范也以及处理好也一起打包在 skill 里面了（价值超过 500美金 token）。不过是否完整我还是有一点疑虑的。因为各个 ClinGen 专病规范的文档质量有很大差异，有些规范的图片质量比较差，有的规范里文字极其简略，我对 AI 分析的质量还有些疑虑的。由于有100多个规范，数量比较多，我也没有一一审阅过。

[add picture, a picture of the summary ]

### 变异注释

AI 需要人群频率，insilico prediction of deleterious effect, 变异类型等完整的变异注释可以来提供数据库类证据判定所需的信息了。

--- 
> Criteria Based on Database/Computational Annotation
>
> Population frequency databases (gnomAD, ExAC, etc.): 
> - BA1 – Allele frequency >5% (standalone benign) 
> - BS1 – Allele frequency greater than expected for disorder 
> - BS2 – Observed in healthy adults (for penetrant conditions) 
> - PM2 – Absent or extremely low frequency in population databases
> 
> Variant databases (ClinVar, HGMD, locus-specific databases):
> - PS1 – Same amino acid change as established pathogenic variant (different nucleotide)
> - PM5 – Novel missense at residue where different pathogenic missense seen before
> 
> Computational/predictive tools:
> - PP3 – Multiple computational tools support deleterious effect
> - BP4 – Multiple computational tools suggest no impact
> - BP7 – Silent variant with no predicted splice impact
> 
> Sequence analysis (variant type/location):
> 
> - PVS1 – Null variant in gene where LOF is established mechanism
> - PM1 – Located in mutational hotspot or critical functional domain
> - PM4 – Protein length change (in-frame indel or stop-loss) in non-repeat region
> - BP1 – Missense in gene where only truncating variants cause disease
> - BP3 – In-frame indel in repetitive region without known function
--- 

考虑到评级的用户是遗传分析师，所以输入一是 HGVS 命名。所以在变异注释这一步需要能够基于 HGVS 获取到全量的变异信息。同时希尽量不需要安装VEP, Annovar 这类专门的注释软件，因为这些软件一般安装困难，同时需要准备数量巨大的参考数据。
也尽量减少对于 Varsome 这种需要付费的网站的的需求，优先依赖公共可用的途径。后来发现 Ensembl 以及提供了功能强大的 API 集来实现这一步骤。当然 Ensembl 数据中很多参考数据版本一般会落后于最新版本。
![alt text](image.png)


### 变异所在区域的信息
变异注释一般只会获得单个变异的信息，但有些证据是需要变异所在区域的信息的。例如 PM1 中的 a mutational hot spot 和 well-established functional domain without benign variation, 以及 PS1 中的变异previously established pathogenic variant regardless of nucleotide change。这里我们利用公共可用的 API 暂时实现3个，变异所在区域的所有 ClinVar 变异的信息，变异所在基因的 Uniprot domain 的信息，以及变异所在区域的所有 gnomAD 变异信息。


### 文献的获取和分析

下面这些基于文献的证据一直变异评级中的难点，也是各种自动化分析方法无法实现的。其中主要3个难点需要我们来探索是否能通过 AI 解决或者部分解决。

--- 
> Criteria Requiring Case-Level Data (Internal Cases or Publications)
> 
> Pathogenic evidence:
> - PS2 – De novo (confirmed parentage) in a patient with disease and no family history
> - PS4 – Prevalence in affected individuals significantly increased vs. controls (requires case-control data)
> - PM6 – Assumed de novo (without confirmed parentage)
> - PM3 – Detected in trans with pathogenic variant (recessive disorders)
> - PP1 – Co-segregation with disease in multiple affected family members
> - PP4 – Patient's phenotype highly specific for gene
> 
> Benign evidence:
> - BS4 – Lack of segregation in affected family members
> - BP2 – Observed in trans with a dominant pathogenic variant, or in cis with a pathogenic variant
> - BP5 – Variant found in case with alternate molecular cause – requires case data but sometimes in- ferable from databases
> 
> Functional data (often from publications but standardizable):
> - PS3 – Well-established functional studies show deleterious effect
> - BS3 – Well-established functional studies show no deleterious effect
--- 


1. 如何找到相关文献？
首先，AI 编程工具本身就具有强大的网络搜索的能力，例如我让他尝试搜索一个 ClinGen收录变异 NM_000545.8(HNF1A):c.745T>C (p.Ser249Pro) 相关文献，他会依次构建下面这些关键词进行反复尝试
- NM_000545.8 HNF1A c.745T>C p.Ser249Pro variant
- HNF1A Ser249Pro pathogenic variant MODY diabetes
- "c.745T>C" HNF1A ClinVar
- HNF1A "745T>C" OR "Ser249Pro" diabetes publication

我也主动指导 AI 将变异拆分成一些关键词进行搜索，例如基于HNF1A + ("745T>C" | "745T->C" | "745T-->C" | "745T/C" | "Ser249Pro" | "S249P") 进行模糊搜索

同时也应用 LitVar2 的接口进行尝试。

不幸的是，不管哪种尝试，结果都令人失望，基于我测试的几个案例，不论哪种方式都很难找到中 ClinGen 专家对这个变异评级所采用的的文献。只能说文献搜索这里还有很多工作可以做。不知道读者里谁有 Mastermind 的订阅，到底 Mastermind 是不是像他们宣传的那么厉害，能准确定位到变异相关的文献。


2. 能否从文献中找到具体证据类型，并结合ClinGen 规范进行正确的升降级？
即使搜索不顺利，但实际分析过程中，分析人员还是有可能通过其他途径获取到文章，然后应用 AI 协助阅读并补充到评级证据中，所以我需要验证 AI 是否能够准确阅读文献并匹配证据。还是以这个变异评级的举例子。HNF1A p.Ser249Pro 的评级涉及 2 个文献，这 2 篇文献也代表了评级过程中可能遇到的 2 个经典困境。

- PMID:16249556 Renal malformations may be linked to mutations in the hepatocyte nuclear factor-1alpha (MODY3) gene

尽管这是一篇 2005 年的文章，但是处于付费墙后面，除非人为准备 PDF 格式的文章，否则没有公共可用的途径让 AI 获取到正文。

- PMID:23771925 Prevalence, characteristics and clinical diagnosis of maturity onset diabetes of the young due to mutations in HNF1A, HNF4A, and glucokinase: results from the SEARCH for Diabetes in Youth

这篇文章是有包含这个变异，但是仅在补充材料的表格中有收录。不知道是不是因为这个原因，这个变异在 HGMD 中也没有收录这篇文章，只能赞叹 ClinGen 专家还是厉害。

那我们提前下载好第一篇文章，并提供第二篇文章的PMID，AI 能否正确的找到证据呢？

- 毫无意外，在提前准备好PMID:16249556的 PDF 文件的情况下，AI 可以准确的理解文章并且将案例匹配到 PS4 的计数中
- 对于PMID:23771925，AI 自带的 WebSearch 功能会自动进行搜索，并进行总结，但总结的过程中很容易忽略掉变异这种细节信息。所以这里需要我们自己补充文章下载的能力，将完整文章下载下来再进行分析。不过尽管这样，在这个测试例中，这个案例还是无法匹配到 PS4 的计数中。因为 NIH/PMC 的反机器人机制让文章下载工具无法获取补充材料，而这个变异的案例仅出现在补充材料中。

### 评级分析

至于完整评级分析方法，我们可以完全充分相信 AI 的自主决策能力，不需要像我是之前做 PVS1 工作流的那样精细控制。至于这套 skill 到底表现如何，我会在下面几篇给出具体的案例分析。总结来说，文献准确检索仍然需要更专业的工具，但如果能人工准备好可能相关的文章，AI 已经可以非常精确的实现 ClinGen 专家级别的变异评级了。

并且这种方法还有无限的上限，你可以轻松的指引 AI 升级这套技能。当你学会 AI + skill 的组合，就可以完全抛弃 Vicuña 这种套壳工具了

### One more thing
我本来调用 AI 为一件其他事情生成一下可视化报告，没想到用错在变异评级的窗口，然后 AI 就在后面猛干，在没有给任何设计要求的前提下，生成的 html 的报告效果惊人。考虑到相比于CLI的输出，对于非程序员的用户更友好。我稍作调整，就固化成一个漂亮的报告模版。


## How to use
使用非常简单，当你安装完 skill 后，只需要输入

```
/variant-classifier 任何格式的变异命名
```

他会基本沿着下面这些步骤的进行变异分析，但并不一定严格遵循，使用的过程中国呢也可以随时中断。

1. Parse Input and Annotate Variant
2. Check for VCEP Specification
3. Retrieve Paper metadata
4. User Verification about if fetch full content for papers or add internal case data. (也是check一下你自己的钱包够不够充足，如果文章数量比较多，下载并阅读所有文献的token量是非常大的) 
5. Extract Case-Level Evidence (AI's Task)
6. Get Splice Predictions (if relevant)
7. Use all information gathered from previous steps and run score based classification
8. Present Results
    - Final classification (Pathogenic, Likely Pathogenic, VUS, Likely Benign, Benign)
    - Criteria met with evidence summary
    - Point totals (pathogenic vs benign)
    - Confidence level
    - Recommendations
9. Generate HTML Report (Optional)


## 讨论

一个有趣的思考，以前网站开发都要做Search Engine Optimization (SEO) , 现在都要进行Generative Engine Optimization (GEO)。大家写文章，也要考虑GEO了，因为以后文章可能都是AI写，AI读了，让你的文章更容易被AI处理，才能在引用次数的获得先机。例如最基础的，表格尽量结构化一些，少合并单元格；尽量发表到能open access的期刊上。

最后感谢也要赞叹Ensemble, NCBI and UCSC的长期积累，他们的服务提供强大的API集。在开始之前，考虑到遗传分析里面涉及到大量的专业数据，可能需要自己去开发和实现工具供AI调用。但整个实现下来，发现完全不用重新造轮子。基本上所有的数据获取，都可以通过他们的接口直接获取。


