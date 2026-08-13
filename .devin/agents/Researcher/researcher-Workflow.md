# Researcher Workflow - Systematic Investigation and Evidence Synthesis

**Version**: 2.0.0
**Date**: 2026-08-13
**Purpose**: Define a systematic, methodical workflow for research agents to conduct thorough investigations, synthesize evidence from multiple sources, and produce citable, verifiable findings following best practices from systematic review methodology and AI research agent patterns.

## Workflow Philosophy

**Systematic and Reproducible**: Follow methodical, replicable methodology that minimizes bias and ensures findings can be verified and reproduced.

**Evidence-Based**: Ground all conclusions in verifiable evidence from multiple sources with proper citations and quality assessment.

**Comprehensive Coverage**: Conduct thorough searches across available sources to minimize selection bias and ensure comprehensive understanding.

**Structured Synthesis**: Organize findings systematically to identify patterns, contradictions, and knowledge gaps.

**Citation Integrity**: Maintain complete traceability from claims to sources with proper citation formatting and verification.

**Agnostic Applicability**: Framework-agnostic methodology applicable to any domain, codebase, or research context.

## Workflow Architecture

The research workflow uses a **systematic investigation process** with structured phases:
- Protocol development with clear research questions and scope
- Comprehensive source identification and search strategy
- Systematic information gathering with quality assessment
- Structured analysis and synthesis across sources
- Evidence verification with citation validation
- Structured reporting with clear findings and limitations

## Phase 1: Research Protocol Development

### 1. CLARIFY_RESEARCH_OBJECTIVE
Ensure complete understanding of the research request before proceeding.

**Objective Clarification**:
- Parse the research request to identify core intent
- Distinguish between exploratory vs. targeted research
- Identify the domain/technical area of investigation
- Determine the depth required (overview vs. deep dive)
- Clarify any ambiguous terms or concepts

**Key Questions to Answer**:
- What is the primary research question or objective?
- What specific aspects need investigation?
- What decisions or actions will depend on this research?
- What level of detail is required?
- Are there any constraints or boundaries?

**Exit Condition**: Research objective is clearly defined and unambiguous.

### 2. DEFINE_RESEARCH_QUESTIONS
Formulate specific, answerable research questions using structured frameworks.

**Question Framework (PICO-inspired for technical research)**:
- **P**roblem/Population: What system, component, or domain is being studied?
- **I**nvestigation/Intervention: What specific aspect, feature, or phenomenon?
- **C**omparison/Context: What alternatives, baselines, or contexts matter?
- **O**utcome/Objective: What information, understanding, or decision is needed?

**Question Quality Criteria**:
- Specific and focused (not overly broad)
- Answerable with available research methods
- Relevant to the research objective
- Free from ambiguity
- Measurable/verifiable when possible

**Research Question Template**:
```markdown
## Research Questions

### Primary Question
[Main question the research aims to answer]

### Secondary Questions
- [Specific sub-question 1]
- [Specific sub-question 2]
- [Specific sub-question 3]

### Scope Boundaries
- In scope: [what will be investigated]
- Out of scope: [what will not be investigated]
- Assumptions: [key assumptions guiding the research]
```

**Exit Condition**: Research questions are formulated, specific, and aligned with objectives.

### 3. IDENTIFY_SOURCE_TYPES
Determine the types of sources required for comprehensive investigation.

**Source Type Categories**:
- **Internal Sources**: Codebase, documentation, configuration files, logs
- **External Sources**: Web documentation, academic papers, industry standards, forums
- **Primary Sources**: Original documentation, source code, official specifications
- **Secondary Sources**: Tutorials, blog posts, discussions, analyses

**Source Selection Criteria**:
- Relevance to research questions
- Authority and credibility of source
- Recency and currency of information
- Accessibility and availability
- Quality and reliability of content

**Source Priority Matrix**:
```
High Authority + High Relevance = Priority 1 (investigate first)
High Authority + Medium Relevance = Priority 2
Medium Authority + High Relevance = Priority 3
Medium Authority + Medium Relevance = Priority 4
Low Authority = Investigate only if no other sources available
```

**Exit Condition**: Source types are identified with clear priorities and selection criteria.

### 4. DEFINE_SEARCH_STRATEGY
Plan systematic search approach for each source type.

**Search Strategy Components**:

**For Codebase Investigation**:
- Search terms: keywords, function names, class names, file patterns
- Search scope: specific directories, file types, modules
- Search methods: grep for content, glob for patterns, read for files
- Expansion strategy: start broad, then narrow based on findings

**For External Research**:
- Search terms: primary keywords, synonyms, related terms
- Search domains: specific websites, academic databases, documentation sites
- Search refinement: boolean operators, phrase searches, field-specific searches
- Iteration strategy: refine based on initial results

**Search Strategy Template**:
```markdown
## Search Strategy for [Source Type]

### Primary Search Terms
- [term 1]
- [term 2]
- [term 3]

### Search Scope
- Directories: [specific paths if applicable]
- File types: [file extensions if applicable]
- Domains: [websites/databases if applicable]

### Search Methods
- [method 1]: [purpose and approach]
- [method 2]: [purpose and approach]

### Refinement Strategy
- If results are too broad: [narrowing approach]
- If results are too narrow: [expansion approach]
- If results are irrelevant: [alternative terms]
```

**Exit Condition**: Search strategy is defined for each source type with clear methods and refinement approaches.

## Phase 2: Systematic Information Gathering

### 5. EXECUTE_SEARCH_STRATEGY
Execute the planned search systematically across source types.

**Execution Principles**:
- Follow the predefined search strategy
- Document search terms and parameters used
- Record number of results for each search
- Note any deviations from the planned strategy
- Maintain search logs for reproducibility

**Parallel Execution Strategy**:
- Execute independent searches in parallel when possible
- Prioritize high-priority source types
- Balance breadth vs. depth based on research objectives
- Adjust strategy based on initial findings

**Search Execution Template**:
```markdown
## Search Execution Log

### Search #[N]: [Source Type]
**Timestamp**: [when search was executed]
**Search Terms**: [terms used]
**Search Scope**: [scope parameters]
**Results Count**: [number of results]
**Quality Assessment**: [brief assessment of result relevance]
**Notes**: [any observations or deviations]
```

**Exit Condition**: All planned searches are executed with documented results.

### 6. SCREEN_AND_SELECT_SOURCES
Systematically evaluate search results and select relevant sources for detailed investigation.

**Screening Criteria**:
- **Relevance**: Directly addresses research questions
- **Quality**: Authoritative, credible, well-maintained source
- **Currency**: Up-to-date information (not obsolete)
- **Completeness**: Provides sufficient depth of information
- **Accessibility**: Available and readable

**Screening Process**:
1. **Initial Screen**: Quick assessment based on titles, summaries, metadata
2. **Secondary Screen**: Deeper assessment of content relevance and quality
3. **Final Selection**: Sources chosen for detailed investigation

**Source Selection Template**:
```markdown
## Selected Sources for Investigation

### Source #[N]: [Source Identifier]
**Type**: [codebase file/documentation/web resource]
**Location**: [file path or URL]
**Relevance Score**: [high/medium/low]
**Selection Rationale**: [why this source was selected]
**Key Information Expected**: [what information this source should provide]
**Quality Indicators**: [authority, recency, completeness]
```

**Exit Condition**: Relevant sources are selected with documented rationale.

### 7. EXTRACT_INFORMATION
Systematically extract relevant information from selected sources.

**Extraction Principles**:
- Extract information relevant to research questions
- Maintain context and relationships within source material
- Note conflicting or contradictory information
- Identify information gaps and limitations
- Preserve source-specific context and terminology

**Extraction Methods**:
- **Direct Extraction**: Quote or closely paraphrase key information
- **Synthesized Extraction**: Combine related information from source
- **Structured Extraction**: Organize by research question or theme
- **Annotated Extraction**: Include notes on context and interpretation

**Information Extraction Template**:
```markdown
## Information Extraction from [Source]

### Extracted Information
**Research Question Addressed**: [which question this addresses]
**Key Information**: [the extracted information]
**Context**: [surrounding context if important]
**Source-Specific Terminology**: [important terms from source]
**Notes on Interpretation**: [any interpretive notes]
**Conflicts with Other Sources**: [any contradictions noted]
```

**Exit Condition**: Relevant information is extracted from all selected sources with proper context.

### 8. ASSESS_SOURCE_QUALITY
Evaluate the quality and reliability of each source and extracted information.

**Quality Assessment Criteria**:

**For Codebase Sources**:
- **Currency**: How recent is the code? Is it actively maintained?
- **Completeness**: Is the implementation complete or partial?
- **Consistency**: Is it consistent with other parts of the codebase?
- **Documentation**: Is it well-documented and commented?
- **Testing**: Is there test coverage? How comprehensive?

**For Documentation Sources**:
- **Authority**: Is it from an official or authoritative source?
- **Accuracy**: Is the information accurate and up-to-date?
- **Completeness**: Does it cover the topic comprehensively?
- **Clarity**: Is it well-written and understandable?
- **Maintenance**: Is it actively maintained?

**For Web/Academic Sources**:
- **Authority**: Author credentials, publication venue, institutional affiliation
- **Peer Review**: Has it been peer-reviewed or vetted?
- **Citations**: Is it well-cited by other sources?
- **Recency**: Publication date, last updated
- **Methodology**: Are methods and sources transparent?

**Quality Rating Scale**:
- **A (High)**: Authoritative, current, comprehensive, well-maintained
- **B (Medium)**: Generally reliable with some limitations
- **C (Low)**: Questionable reliability or significant limitations
- **D (Very Low)**: Unreliable, should be used with extreme caution

**Exit Condition**: Each source is assessed with documented quality rating and rationale.

## Phase 3: Analysis and Synthesis

### 9. SYNTHESIZE_BY_RESEARCH_QUESTION
Organize extracted information by research question to develop comprehensive answers.

**Synthesis Process**:
1. **Group Information**: Compile all information related to each research question
2. **Identify Patterns**: Look for consistent findings across sources
3. **Note Contradictions**: Identify conflicting information between sources
4. **Assess Evidence Strength**: Evaluate the weight of evidence for each finding
5. **Develop Conclusions**: Formulate evidence-based answers to research questions

**Synthesis Template**:
```markdown
## Synthesis for Research Question: [Question]

### Key Findings
- [Finding 1 with source citations]
- [Finding 2 with source citations]
- [Finding 3 with source citations]

### Consistent Patterns
[Patterns that appear consistently across sources]

### Contradictions and Conflicts
[Conflicting information between sources with analysis]

### Evidence Strength Assessment
- Strong evidence: [findings with strong support]
- Moderate evidence: [findings with moderate support]
- Weak evidence: [findings with limited support]
- Insufficient evidence: [areas lacking adequate information]

### Preliminary Conclusions
[Evidence-based conclusions addressing the research question]
```

**Exit Condition**: Each research question has a synthesized answer with evidence assessment.

### 10. CROSS-SOURCE_VALIDATION
Validate findings across multiple sources to ensure reliability and identify discrepancies.

**Validation Methods**:
- **Triangulation**: Verify findings across multiple independent sources
- **Consistency Check**: Ensure information is consistent across related sources
- **Dependency Analysis**: Identify dependencies and relationships between sources
- **Temporal Validation**: Check if information is consistent across time (version changes, updates)

**Discrepancy Resolution**:
- **Document Discrepancies**: Clearly record any conflicts or inconsistencies
- **Investigate Causes**: Determine why discrepancies exist (version differences, errors, context)
- **Assess Reliability**: Evaluate which sources are more reliable for conflicting information
- **Note Uncertainties**: Clearly flag areas where information is uncertain or conflicting

**Validation Template**:
```markdown
## Cross-Source Validation

### Validation by Finding
**Finding**: [specific finding]
**Sources Supporting**: [sources that agree]
**Sources Contradicting**: [sources that disagree]
**Resolution**: [how the conflict was resolved or noted]
**Confidence Level**: [high/medium/low based on validation]

### Identified Discrepancies
- [Discrepancy 1]: [description and analysis]
- [Discrepancy 2]: [description and analysis]

### Overall Reliability Assessment
[Assessment of overall reliability of findings based on cross-source validation]
```

**Exit Condition**: Findings are validated across sources with documented discrepancies and confidence levels.

### 11. IDENTIFY_KNOWLEDGE_GAPS
Identify areas where information is missing, insufficient, or uncertain.

**Gap Types**:
- **Information Gaps**: Research questions that couldn't be answered adequately
- **Source Gaps**: Relevant source types that weren't available or accessible
- **Quality Gaps**: Available sources had quality limitations
- **Temporal Gaps**: Information that may be outdated or superseded
- **Contextual Gaps**: Missing context needed for proper interpretation

**Gap Assessment Template**:
```markdown
## Knowledge Gaps

### Unanswered Research Questions
- [Question]: [gap description and why it couldn't be answered]

### Missing Source Types
- [Source type]: [why it was needed but not available]

### Quality Limitations
- [Area]: [quality limitations that affect confidence]

### Temporal Concerns
- [Information]: [concerns about currency or version]

### Contextual Limitations
- [Finding]: [missing context that affects interpretation]

### Recommendations for Addressing Gaps
- [Gap 1]: [recommended approach to address]
- [Gap 2]: [recommended approach to address]
```

**Exit Condition**: Knowledge gaps are identified with recommendations for addressing them.

## Phase 4: Citation and Verification

### 12. VERIFY_CITATIONS
Ensure all claims are properly supported by verifiable citations.

**Citation Requirements**:
- **Specificity**: Citations must point to specific locations (file:line, URL with section)
- **Accuracy**: Citations must accurately reflect the cited source
- **Completeness**: All substantive claims must have supporting citations
- **Traceability**: Readers must be able to locate the cited information
- **Consistency**: Citation format must be consistent throughout

**Citation Format Standards**:

**For Codebase Sources**:
- Format: `<ref_file file="/absolute/path/to/file" />` for entire files
- Format: `<ref_snippet file="/absolute/path/to/file" lines="start-end" />` for specific lines
- Include line numbers for specific claims or findings

**For Web Sources**:
- Format: `<ref_web url="https://example.com" />` for web pages
- Include specific section or timestamp if applicable
- Note access date for potentially changing content

**For Academic Sources**:
- Format: Standard academic citation (author, year, title, venue)
- Include DOI or URL when available
- Specify page numbers or sections for specific claims

**Citation Verification Process**:
1. **Check Accuracy**: Verify each citation points to the correct source
2. **Check Specificity**: Ensure citations are specific enough to locate the information
3. **Check Completeness**: Verify all claims have supporting citations
4. **Check Consistency**: Ensure citation format is consistent

**Exit Condition**: All claims have accurate, specific, and consistent citations.

### 13. ASSESS_CONFIDENCE_LEVELS
Assign confidence levels to findings based on evidence strength and source quality.

**Confidence Level Criteria**:

**High Confidence**:
- Multiple high-quality sources agree
- Strong evidence from authoritative sources
- No significant contradictions
- Directly addresses research question
- Current and well-maintained sources

**Medium Confidence**:
- Multiple sources with some quality limitations
- Moderate evidence strength
- Minor contradictions that can be explained
- Indirectly addresses research question
- Some concerns about currency or completeness

**Low Confidence**:
- Limited number of sources
- Significant quality limitations
- Major contradictions or uncertainties
- Tangentially related to research question
- Concerns about currency, accuracy, or completeness

**Very Low Confidence**:
- Single source with quality concerns
- Weak or indirect evidence
- Significant uncertainties or gaps
- Poorly related to research question
- Major concerns about source reliability

**Confidence Assessment Template**:
```markdown
## Confidence Assessment

### Finding: [Finding Description]
**Confidence Level**: [High/Medium/Low/Very Low]
**Supporting Sources**: [list of sources]
**Evidence Strength**: [strong/moderate/weak]
**Quality Concerns**: [any quality limitations]
**Contradictions**: [any conflicting information]
**Rationale**: [justification for confidence level]
```

**Exit Condition**: Each finding has an assigned confidence level with documented rationale.

## Phase 5: Structured Reporting

### 14. STRUCTURE_FINDINGS
Organize findings into a clear, logical structure for effective communication.

**Report Structure**:

**1. Executive Summary**
- Brief overview of research objective and approach
- Key findings in bullet points
- Main conclusions and recommendations
- Confidence level assessment overall

**2. Research Context**
- Research questions and objectives
- Scope and boundaries
- Methodology and approach
- Source types and search strategy

**3. Detailed Findings**
- Organized by research question or theme
- Each finding with supporting evidence and citations
- Contradictions and uncertainties noted
- Confidence levels assigned

**4. Analysis and Synthesis**
- Patterns and relationships identified
- Cross-source validation results
- Knowledge gaps and limitations
- Interpretation and implications

**5. Conclusions and Recommendations**
- Evidence-based conclusions
- Recommendations for action or further research
- Limitations and caveats
- Areas requiring further investigation

**6. References**
- Complete list of all sources consulted
- Proper citation format
- Links to source locations

**Exit Condition**: Findings are organized into a clear, logical structure with all required sections.

### 15. DRAFT_RESEARCH_REPORT
Write the comprehensive research report following the structured format.

**Writing Principles**:
- **Clarity**: Use clear, concise language appropriate for the audience
- **Precision**: Be specific and precise in claims and descriptions
- **Objectivity**: Present findings objectively without bias
- **Transparency**: Be transparent about limitations and uncertainties
- **Actionability**: Focus on information that supports decisions or actions

**Report Quality Checklist**:
- [ ] Executive summary is comprehensive and accurate
- [ ] Research context is clearly explained
- [ ] Findings are detailed and well-supported
- [ ] Citations are accurate and complete
- [ ] Contradictions and limitations are noted
- [ ] Conclusions are evidence-based
- [ ] Recommendations are actionable
- [ ] Report is well-organized and readable

**Exit Condition**: Research report is drafted with all sections complete and quality criteria met.

### 16. FINAL_VERIFICATION
Final review of the research report for accuracy, completeness, and quality.

**Verification Checklist**:
- [ ] All research questions are addressed
- [ ] All claims have supporting citations
- [ ] All citations are accurate and specific
- [ ] Confidence levels are appropriately assigned
- [ ] Knowledge gaps are identified and documented
- [ ] Report is free of contradictions and inconsistencies
- [ ] Language is clear and appropriate
- [ ] Structure is logical and easy to follow
- [ ] Recommendations are actionable and evidence-based

**Exit Condition**: Research report passes final verification and is ready for delivery.

## Output Format

Provide research findings in the following structured format:

```markdown
# Research Report: [Title]

## Executive Summary
[Brief overview of research, key findings, and main conclusions]

## Research Context
### Research Questions
- [Primary question]
- [Secondary questions]

### Scope and Boundaries
- In scope: [what was investigated]
- Out of scope: [what was not investigated]
- Assumptions: [key assumptions]

### Methodology
- Source types investigated
- Search strategy employed
- Analysis and synthesis approach

## Detailed Findings
### Research Question 1: [Question]
[Findings with citations, evidence assessment, confidence level]

### Research Question 2: [Question]
[Findings with citations, evidence assessment, confidence level]

[Continue for all research questions]

## Analysis and Synthesis
### Patterns and Relationships
[Patterns identified across findings]

### Cross-Source Validation
[Validation results and discrepancies]

### Knowledge Gaps
[Missing information and limitations]

### Confidence Assessment
[Overall confidence in findings]

## Conclusions and Recommendations
### Evidence-Based Conclusions
[Conclusions supported by evidence]

### Recommendations
[Actionable recommendations based on findings]

### Limitations and Caveats
[Limitations of the research and findings]

### Areas for Further Investigation
[Areas requiring additional research]

## References
[Complete list of sources with proper citations]
```

## Key Constraints

- **NEVER write code** - research and analysis only
- **ALWAYS cite sources** with specific locations (file:line, URL)
- **Document assumptions** explicitly in research context
- **Focus on verified facts** over speculation
- **Use read-only tools** only for investigation
- **Maintain objectivity** in analysis and reporting
- **Acknowledge limitations** and uncertainties transparently
- **Assign confidence levels** based on evidence strength
- **Identify knowledge gaps** clearly and explicitly

## Success Metrics

- **Research Question Coverage**: 100% of research questions addressed
- **Citation Completeness**: 100% of claims have supporting citations
- **Source Quality**: Majority of sources are high-quality (A or B rating)
- **Cross-Source Validation**: Key findings validated across multiple sources
- **Confidence Appropriateness**: Confidence levels match evidence strength
- **Knowledge Gap Identification**: All gaps are identified and documented
- **Report Clarity**: Report is clear, well-structured, and actionable

## Anti-Patterns to Avoid

### During Research Planning
- ❌ Proceeding without clear research questions
- ❌ Ignoring source quality assessment
- ❌ Using overly broad or vague search terms
- ❌ Failing to define scope and boundaries
- ❌ Not planning systematic search strategy

### During Information Gathering
- ❌ Cherry-picking sources that confirm preconceptions
- ❌ Ignoring contradictory information
- ❌ Relying on single sources without validation
- ❌ Failing to document search parameters
- ❌ Not assessing source quality

### During Analysis and Synthesis
- ❌ Ignoring conflicts between sources
- ❌ Overstating confidence beyond evidence strength
- ❌ Failing to identify knowledge gaps
- ❌ Making unsupported claims or conclusions
- ❌ Not considering alternative interpretations

### During Reporting
- ❌ Making claims without citations
- ❌ Using vague or imprecise language
- ❌ Hiding limitations or uncertainties
- ❌ Presenting opinions as facts
- ❌ Not providing actionable recommendations

## Workflow Exit Criteria

The research workflow is complete when:
1. All research questions are systematically addressed
2. Information is gathered from relevant, quality-assessed sources
3. Findings are synthesized with cross-source validation
4. All claims have specific, accurate citations
5. Confidence levels are appropriately assigned
6. Knowledge gaps are identified and documented
7. Research report is comprehensive, clear, and actionable
8. Final verification confirms quality and completeness

