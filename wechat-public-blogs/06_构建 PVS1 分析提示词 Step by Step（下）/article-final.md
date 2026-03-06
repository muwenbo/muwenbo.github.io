## 验证过程

PVS1 分析提示词的构建不可能一蹴而就。在验证过程遇到各种挑战，然后需要不断钻研、调整。正是这些挑战让整个过程充满了趣味。AI 会从每一次“失误”中汲取教训，并在下一次表现得更聪明、更可靠。


![](https://files.mdnice.com/user/90337/6fe1112d-ac76-4ff1-ac56-4149a72e7fee.png)
*PVS1 Nonsense or Frameshift 决策树*

---

**NM_000142.5(*FGFR3*):c.1632_1633del (p.Cys545HisfsTer17)**

第一个测试就翻车了。很显然，大模型的知识非常渊博，在FGFR3致病机制的判断上，他准确判定出 *FGFR3* 的致病机制是 gain-of-function，但由于存在 CATSHL syndrome 的特例，认定 loss-of-function 也是致病机制，然后将该变异判定为 PVS1。这里的关键是，我并没有提供关于致病机制的文字型输入，这意味着大模型已经有足够的知识去自动进行判定。


![](https://files.mdnice.com/user/90337/25160fc9-6fb7-43cf-badf-7b5bd1544353.png)
*大模型对FGFR3致病机制的描述*

但我们目前还没有设计针对单独疾病进行评级的机制，所以希望他能够依据主要的致病机制进行判定。我首先尝试加上一条约束：“Unless specifically analyzing a variant for a rare alternative phenotype, apply the classification based on the primary disease mechanism associated with the gene's most common phenotype”。但 AI 还是坚持把 CATSHL syndrome 的情况考虑进来。我想可能由于当前的提示词已经承载了非常复杂细节的分析需求，并且大模型对致病机制的判定其实是全面且正确的，仅仅一句话的限定不够改变 AI 的整体分析思路。

于是，我决定将致病机制的分析单独拆成一个模块，将其输出作为PVS1分析的输入。这样，主提示词中仅保留了必要的约束，最终成功让AI基于 gain of function 分析并判定该变异不适用PVS1。

> You are a genetic variant curation expert specializing in analyzing Gene-Disease Mechanism for  the classification of PVS1. Your task is to determine if loss-of-function (LoF) is an established disease mechanism for the gene below.
> 
> <gene_annotation>
> {gene_annotation}
> </gene_annotation>
> 
> Consider:
> - Is the gene associated with haploinsufficiency?
> - Is the disease caused by dominant negative effects?
> - Is the disease recessive, requiring biallelic variants?
> - Is there evidence from functional studies or model organisms supporting LoF as the mechanism?
>
> Provide evidence supporting your determination

*致病机制分析提示词*

**参考结果**
- AutoPVS1
    - Unmet
    - Nonsense or Frameshift -> Predicted to undergo NMD -> Exon is present in biologically-relevant transcript(s) -> VeryStrong -> Unmet (Adjusted Strength)

- Varsome
    - PVS1
    - Null variant (frame-shift) in gene FGFR3, predicted to cause NMD. Loss-of-function is a known mechanism of disease (gene has 15 reported pathogenic LOF variants). The exon affects 1 functional domain: UniProt protein FGFR3_HUMAN domain 'Protein kinase'. The exon contains 9 pathogenic variants. The truncated region contains 33 pathogenic variants.

--- 

**NM_000314.8(*PTEN*):c.1003C>T (p.Arg335Ter)**

在 *PTEN* 基因的致病机制判断上，大模型没有问题。这个变异主要用来测试模型能否正确判断变异是触发 NMD 还是逃脱 NMD。当我们不给定任何 NMD 阈值时，模型自称采用的是 50 nt 规则来进行 NMD 判定，但其实计算结果并不正确。

> NMD Prediction:
> * The variant introduces a premature termination codon (PTC) at codon 335.
> * The PTEN transcript NM_000314.8 has 9 exons; this variant is in exon 8.
> * The PTC is >50–55 nucleotides upstream of the final exon-exon junction, so it is predicted to trigger NMD.

*无阈值时，模型对 NMD 计算的说明*

当我们通过转录本注释模块设定 NMD 阈值为依据 50 nt 规则计算的 c.976 时，模型却犯了经典的无法比较数字大小的错误。总是坚持认为 c.1003 小于 c.976，从而判断变异位于阈值的上游。即使我把这项比较大小的工作单独调用模型进行，AI 仍然无法得到正确的结果。我猜测碱基命名里面的 ”c.” 让这个比较更容易出错。

虽然我们可以通过构建更复杂的提示词最终实现正确判定，但没有必要，也会影响整个流程的速度。所以我决定用代码来实现，将判定结果作为主提示词的输入。最终在设定 c.976 为 NMD 阈值时，模型按照正确的决策树路径将变异评为 PVS1_Strong。当设定 ClinGen 专家组指定的 c.1121 时，变异被评为 PVS1。模型成功判定 NMD 的状态，并做出正确的 PVS1 评级。

**参考结果**
- AutoPVS1
    - PVS1
    - PTEN gene-specific criteria: Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon, single or multi-exon deletion) predicted to result in nonsense-mediated decay or causing truncation/frameshift at or 5′ to c.1121 (NM_000314.4). --> PVS1 VeryStrong

- Varsome
    - PVS1
    - Null variant (nonsense) in gene PTEN, not predicted to cause NMD. Loss-of-function is a known mechanism of disease (gene has 877 reported pathogenic LOF variants). The exon affects 2 functional domains: UniProt protein PTEN_HUMAN Mutagen sequence annotations 'KANKDKANR -> AAGADAANA: Reduces growth suppression activity and promotes anchorage-independent growth. Reduces binding to phospholipid membranes in vitro' and UniProt protein PTEN_HUMAN domain 'C2 tensin-type'.

---

**NM_000203.5(*IDUA*):c.1799del (p.Pro599_Ser600insTer)**

这个变异的设计目的是测试AI是否能成功计算移除蛋白质的比例，并判断是否满足10%的阈值。若能直接判定，则无需像 NMD 判定那样额外编写代码模块。AI 成功计算出该变异移除的蛋白质比例约为8%，并依据决策树路径判定为 PVS1_Moderate。但令人意外的是，AI 最终自作主张，将其提升为PVS1_Strong。

虽然这一升级未必正确，但从工具使用者的角度来看，增加一个额外的思考维度并不一定是坏事。或许，这正是AI超越人类的地方吧？因此，我并不打算对提示词进行调整，以限制AI的这种“额外思考”。


![](https://files.mdnice.com/user/90337/73d2f9ff-760b-4d31-a282-20f0209bcb8a.png)
*AI 对 NM_000203.5(IDUA):c.1799del (p.Pro599_Ser600insTer) PVS1的额外思考*

**参考结果**
- AutoPVS1
    - PVS1_Moderate
    - Nonsense or Frameshift -> Not predict to undergo NMD -> Role of region in protein function is unknown -> LoF variants in this exon are not frequent in the general population and exon is present in biologically-relevant transcripts -> Variant removes <10% of protein -> Moderate

- Varsome
    - PVS1_Strong
    - Null variant (nonsense) in gene IDUA, not predicted to cause NMD. Loss-of-function is a known mechanism of disease (gene has 254 reported pathogenic LOF variants). The truncated region contains 35 pathogenic variants. It removes 8.26% of the protein.

--- 

**NM_001369369.1(*FOXN1*):c.1315del (p.Leu439CysfsTer111)**

这次变异再次出问题，但这并不是 AI 的错。*FOXN1* 基因的 NMD 阈值根据 50 nt 规则计算为c.1577，由于我们的 NMD 判定是基于“c.”中的碱基位置进行，错误地将变异判断为 NMD 阈值的上游。然而，正确的判定应基于新的终止密码子的位置。对于此变异，新的终止密码子位于 p.Leu439CysfsTer111中的 439 + 111 = 550。只需稍微优化NMD判定的代码，就能修正这一问题，最终，变异按照预期路径被评级为 PVS1_Strong。

**参考结果**
- AutoPVS1
    - PVS1_Strong
    - Nonsense or Frameshift -> Not  predict to undergo NMD -> role of region in protein function is unknown -> removes > 10% of protein -> Strong

- Varsome
    - PVS1 
    - Null variant (frame-shift) in gene FOXN1, not predicted to cause NMD. Loss-of-function is a known mechanism of disease (gene has 62 reported pathogenic LOF variants). The exon affects 1 functional domain: UniProt protein FOXN1_HUMAN region of interest 'Disordered'.

--- 

**NM_001310338.2(*MGME1*):c.525_526del (p.Cys175Ter)**

![](https://files.mdnice.com/user/90337/31c5a5d6-b6b8-4865-b18f-00dac7e57055.png)
*MGME1 基因结构*

这个变异的主要目的是测试AI是否能正确判定变异是否位于生物学上有意义的转录本（biologically relevant transcripts）中。由于我们没有提供用于判定的数据，AI 一开始的输出有些“胡说八道”，但也不难理解。

![](https://files.mdnice.com/user/90337/ce92871d-72ad-4668-9039-f29fe0eb4170.png)
*模型对 NM_001310338.2 是否是生物学上有意义转录本的判读*

同样的，我们将“生物学上有意义的转录本”的判定作为一个单独的模型调用，并且为这一步也设计专属的 思维链提示词来解决这个问题。具体分析思路包括：
- 确定变异位置，检查变异在注释转录本中的外显子编号和具体位置。
- 优先考虑经典转录本（canonical transcript）和 MANE Select 转录本，确认变异是否位于这些生物学相关转录本的外显子中。
- 审查其他转录本结构。如果该外显子在许多转录本中被跳过或是可变剪接的一部分，可能降低变异的功能相关性。
- 评估功能影响。在生物学相关外显子中也具有显著功能影响的变异（如截断、功能丧失）更可能影响基因功能。

最终，AI 成功将该变异按照预期路径判定为不适用 PVS1。不过，面对更复杂的情况时，我对 AI 是否总能做出准确判断还是持保留态度。由于行业内的评级仍以经典转录本和 MANE Select 转录本为主，这类变异在现有数据库中难以找到，所以也难以基于专家评级对 AI 在这一步的表现进一步验证。


![](https://files.mdnice.com/user/90337/38852d4a-5f2f-4413-bdc2-1ce072dc99d2.png)
*优化后模型对 NM_001310338.2 是否是生物学上有意义转录本的判读*

**参考结果**
- AutoPVS1
	- NA
	- NM_052865.4:c.511+2350_511+2351del. This variant type is incompatible with recommendations for interpreting the PVS1 criterion.
    - AutoPVS1 在这一步的处理是只分析最有意义的转录本，一般即经典转录本或 MANE Select 转录本

- Varsome
    - PVS1
    - Null variant (nonsense) in gene MGME1, predicted to cause NMD. Loss-of-function is a known mechanism of disease (gene has 12 reported pathogenic LOF variants). The truncated region contains 7 pathogenic variants.

---
 
**NM_001503.4(*GPLD1*):c.2440C>T(p.Gln814Ter)**

此变异是设计来验证当外显子中存在人群中的高频 LoF 变异时，AI 是否能正确判读。根据 gnomAD 数据库，这个变异所在的外显子包含一个高频的 p.Val815SerfsTer47 LoF变异，在 Finnish European 中人群频率约 2%，应该是可以认为外显子中存在人群中的高频 LoF 变异。

尽管 *GPLD1* 的致病机制不是 LoF，AI 会根据这个原因判读 PVS1 不适用。但我们的提示词是设计了让 AI 输出中间分析过程的，所以依然可以根据 AI 的输出来判断 AI 是否识别到外显子中存在人群中的高频 LoF 变异的情况。

![](https://files.mdnice.com/user/90337/d7b55c32-e8c1-4d2b-9f97-ac58149308c8.png)
*gnomAD数据库中 NM_001503.4(GPLD1):c.2440C>T(p.Gln814Ter) 上下游 20bp 的变异分布*

毫无意外，AI 给出的是没有外显子中存在高频 LoF 的变异的证据。要想解决，我们需要把这种数据以输入方式提供给模型，模型才能有判断的依据。这里我们借鉴 AutoPVS1 的实现方式，也就是对所有基因的各个外显子中 LoF 的变异分布及其人群频率进行预计算。然后将这个数据实现为可供我们 workflow 调用的API。当有所在外显子 LoF 变异人群频率的数据时，AI 就可以成功的进行判读了。


![](https://files.mdnice.com/user/90337/e8d7004c-8c2a-4fb7-83fd-520664941feb.png)
*模型对 NM_001503.4(GPLD1):c.2440C>T(p.Gln814Ter) 所在外显子变异人群频率的分析结果*

**参考结果**
- AutoPVS1
    - Unmet
    - Nonsense or Frameshift -> Not predict to undergo NMD -> Role of region in protein function is unknown -> LoF variants in this exon are frequent in the general population and/or exon is absent from biologically-relevant transcripts -> Unmet

- Varsome
    - Not met
    - Null variant (nonsense) in gene GPLD1, not predicted to cause NMD. Loss-of-function is a known mechanism of disease (gnomAD Loss-of-Function Observed/Expected = 0.614 is less than 0.755). There are no reported pathogenic truncating LOF variants and neither the exon nor the truncated region affect a known functional domain.

---

**NM_020686.6(*ABAT*):c.1306C>T (p.Arg436Ter)**

*ABAT* 在 ClinGen 定义中为 Moderate 的临床有效性，也叫基因-疾病有效性（Gene-Disease Validity）。我们的预期是无论变异根据决策树的 PVS1 的评级如何，都需要进行降级处理。经过前面的调整，我们的 AI 终于可以一步到位的给出符合预期的 PVS1_Strong 评级。


![](https://files.mdnice.com/user/90337/06bae0a2-5539-428d-b30e-fc79551d29b2.png)
*模型基于基因-疾病有效性对ABAT变异的降级处理*

当然这里并非完全正确。因为在 PVS1 的评级文章中，在临床有效性为 Moderate 的同时，还有以下2个额外的条件，并且是“且(AND)”的要求。但这2个数据除非有大量案例历史数据或者文献检索，是完全无法获取的，AI 自然也无能为力。AI 能做到现在这个程度，我已经非常满意了。
- 2 or more LOF variants have been previously associated with the phenotype (must be across more than 1 exon)
- Null mouse model recapitulates disease phenotype

**参考结果**
- AutoPVS1
    - PVS1_Strong
    - Nonsense or Frameshift -> Predicted to undergo NMD -> Exon is present in biologically-relevant transcript(s) -> VeryStrong
    - AutoPVS1 并不包含基因-疾病有效性信息，但支持手动修改。当选择 Moderate 的基因-疾病有效性时，会根据规则提示降级。

- Varsome
    - PVS1
    - Null variant (nonsense) in gene ABAT, predicted to cause NMD. Loss-of-function is a known mechanism of disease (gene has 26 reported pathogenic LOF variants). The exon contains 2 pathogenic variants. The truncated region contains 3 pathogenic variants.

--- 

**NM_000284.4(*PDHA1*):c.1142_1145dup (p.Trp383SerfsTer6)**

到这里，我对AI的判断已经有了相当高的信心，但我仍然希望进一步考察它对证据强度降级的处理能力。恰巧在 ClinVar 中发现了这个变异，它有多个检测机构提交的评级结果。ClinGen 专家给出的评级为 PVS1_Moderate，而其他两个机构直接给出了 PVS1，没有考虑降级。我们AI的结果完全符合预期，并与 ClinGen 专家的评级一致。

不知道是不是可以大胆吹牛：我们的 AI workflow 在 Nonsense 或 Frameshift 变异的 PVS1 判定上，已经超越了许多不那么资深的分析人员。


> **PVS1 Moderate**
> 
> Justification: This variant is a frameshift in the final exon of a biologically relevant transcript, escapes nonsense-mediated decay (NMD), and removes less than 10% of the protein. While the gene has a well-established loss-of-function (LoF) disease mechanism, the location of the variant limits the strength of PVS1 evidence to moderate per the ACMG/AMP PVS1 decision tree.

*ClinGen 专家对 NM_000284.4(PDHA1):c.1142_1145dup (p.Trp383SerfsTer6) 的 PVS1 结论*

**参考结果**
- AutoPVS1
    - PVS1_Moderate
    - Nonsense or Frameshift -> Not predict to undergo NMD -> Role of region in protein function is unknown -> LoF variants in this exon are not frequent in the general population and exon is present in biologically-relevant transcripts -> Variant removes <10% of protein -> Moderate

- Varsome
    - PVS1_Strong
    - Null variant (frame-shift) in gene PDHA1, not predicted to cause NMD. Loss-of-function is a known mechanism of disease (gene has 75 reported pathogenic LOF variants). The truncated region contains 12 pathogenic variants. It removes 2.30% of the protein.


## AI vs. AutoPVS1 vs. Varsome

在这一系列变异的测试实验中，Varsome 的 PVS1 评级显得过于激进了，可能是因为它拥有大量的 LoF 变异数据，进而让更多基因的致病机制被认为是 LoF，更多区域被认为是功能关键。而 AutoPVS1 则在大部分案例中都取得相当准确的结果，难怪在业内广受认可。AI 的优势也仅仅是能够提供更丰富、易于理解的解释和说明。这也让我产生了自我怀疑，这种使用大模型的方式是否已经偏离了应用 AI 的初衷？因为我们实际上是通过不断加限制来引导模型回归决策树路径。


## 最终的 AI workflow 

经过不断的调整，不仅是提示词的变化，还包括多个子分析模块，现在的 workflow 比上个版本复杂了很多。简单总结如下：
1. 新增了基于 API 结合代码实现的外显子中 LoF 变异的人群频率数据。
2. 新增了基于代码的 NMD 判读。
3. 新增了基于大模型基因致病机制判定。
4. 新增了基于大模型的生物学有意义转录本判定。

![](https://files.mdnice.com/user/90337/c0582817-d96d-41be-96ce-4f4fe89e7d99.png)
*PVS1 workflow v2*

## 结果示例
呈现一下 NM_000314.8(PTEN):c.1003C>T (p.Arg335Ter) 的完整的输出，大模型严密的遵守了我们对输出格式的要求。

> Based on systematic evaluation of NM_000314.8:c.1003C>T (p.Arg335Ter) in PTEN:
> 
> PVS1 Classification: PVS1_Strong  
> Justification: This is a nonsense variant in the PTEN gene that escapes nonsense-mediated decay (NMD) but truncates a significant portion of the protein, including part of a critical functional domain. Loss-of-function (LoF) is a well-established disease mechanism for PTEN, and the variant meets criteria for PVS1_Strong based on the ACMG/AMP PVS1 decision tree.
>
> Variant Summary:
> - Variant: NM_000314.8:c.1003C>T (p.Arg335Ter)
> - Genomic Location: chr10:87961095 C>T (GRCh38)
> - Variant Type: Single nucleotide variant (SNV), nonsense (stop_gained)
> - Gene: PTEN
> - Transcript: NM_000314.8 (MANE Select)
> - Exon: 8 of 9
> - Protein Change: p.Arg335Ter
> - Protein Length: 403 amino acids (NP_000305.3)
> 
> Gene-Disease Mechanism:
> - PTEN is associated with multiple autosomal dominant disorders (e.g., Cowden syndrome, Lhermitte-Duclos disease, macrocephaly/autism syndrome).
> - ClinGen haploinsufficiency (HI) score: 3 (sufficient evidence for dosage pathogenicity).
> - LoF is a well-established mechanism of disease for PTEN.
> - Therefore, PVS1 is applicable for LoF variants in PTEN.
> 
> NMD Prediction:
> - The variant is located at c.1003, which is downstream of the NMD threshold (c.976) for NM_000314.8.
> - NMD Prediction: Escape NMD
> 
> Transcript Relevance:
> - The variant affects exon 8 of 9 in NM_000314.8, the MANE Select and canonical transcript.
> - Exon 8 is present in all biologically relevant transcripts (e.g., NM_001304717.5, NM_001304718.2).
> - Therefore, the exon is considered biologically relevant.
> 
> Critical Domain Analysis:
> - PTEN contains two major functional domains:
>   1. Phosphatase domain (residues ~14–185)
>   2. C2 domain (residues ~186–351)
> - The p.Arg335Ter variant truncates the protein within the C2 domain, which is critical for membrane binding and proper localization of PTEN.
> - The truncation removes part of the C2 domain and the entire C-terminal tail (residues 352–403), which is important for protein stability and regulation.
> - Functional studies have shown that truncations in this region impair PTEN function.
> - Therefore, the variant affects a critical region of the protein.
> 
> Population Data:
> - The variant is present in ClinVar with multiple submissions as pathogenic or likely pathogenic.
> - No evidence of high allele frequency in gnomAD or other population databases.
> - No evidence that LoF variants in this exon are frequent in the general population.
> 
> Protein Impact:
> - The full-length PTEN protein is 403 amino acids.
> - The variant introduces a stop codon at position 335.
> - Truncation removes 403 - 335 = 68 amino acids.
> - Percent of protein removed: (68 / 403) × 100 ≈ 16.9%
> - Therefore, the variant removes more than 10% of the protein.
> 
> Decision Tree Application:
> 1. Is the variant predicted to undergo NMD?
>    - No, it escapes NMD.
> 2. Is the role of the region in protein function known?
>    - Yes, the C2 domain and C-terminal tail are critical for PTEN function.
> 3. Is the truncated/altered region critical to protein function?
>    - Yes, the variant truncates part of the C2 domain and the entire regulatory tail.
> → Classification: PVS1_Strong
> 
> PVS1 Classification: PVS1_Strong
> 
> Evidence Summary:
> - The variant is a nonsense mutation in PTEN, a gene with a well-established LoF disease mechanism.
> - It escapes NMD but truncates a critical portion of the protein, including part of the C2 domain and the regulatory tail.
> - The affected exon is present in all biologically relevant transcripts.
> - The truncation removes >10% of the protein and affects a functionally important region.
> - Therefore, per the ACMG/AMP PVS1 decision tree, this variant meets criteria for PVS1_Strong.

## 总结

AI 在基因变异判定中确实具有强大潜力，但也提醒我们，搭建 AI workflow 仅仅是起点。在复杂的临床遗传学分析中，如果不准备好充足的“上下文”数据，妄想大模型可以一站式解决问题是不现实的。人工智能仍然需要充分的监控与调整，才能确保其输出结果的准确性和可靠性。我们成功构建了一个高度精确的 Nonsense 或 Frameshift 变异 PVS1 分析流程，而这才只是开始。Splicing 变异 PVS1 评级挑战会更大。例如：
- 该如何判断或预测变异是否导致外显子跳跃（Exon skipping）？
- 是否存在隐匿剪接位点（cryptic splice site）进而扰乱了阅读框？
- 该如何确定能够验证每条评级路径的 splicing 变异位点？

这都是我们接下来需要妥善解决的问题。
