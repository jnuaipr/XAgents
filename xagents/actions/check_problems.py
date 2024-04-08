#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/8 10:04          
@Author  : Mingxian Gu
@File    : CheckPorblems
"""
from .action import Action
import re

PROMPT_TEMPLATE = '''
-----
You are a ChatGPT executive observer expert skilled identifying dismantled sub-problems and the similarity between sub-problems and professional fields. Your goal is to check whether the subproblem meets the requirements and give your improvement suggestions. You can refer to historical suggestions in the History section, but try not to repeat them.

# Question or Task
{question_or_task}

# Sub-problem And Its Similarity To The Fields
{sub_problems}

# History
{history}

# Steps
You will check the Sub-problem And Its Similarity To The Fields by following these steps:
1. You should first understand, analyze, and disassemble the human's problem/task.
2. According to the problem/task, you should check if the Sub-problem And Its Similarity To The Fields meets the following requirements:
2.1. Each sub-problem should be independent of each other and not interfere with each other.
2.2. Each sub-question should be clear and singular. Specifically, each sub-question should be simple and easy to understand without ambiguity.
2.3. The answer to each sub-question should be a concise and complete sentence.
2.4. The detailed information of all sub-problems' similarities should be in JSON blob format. Specifically, the JSON for the new expert role should contain a 'sub-problem' key (content of the sub-problem), a 'field' key (existing professional fields with "medium" or "high" similarity to the field to which the sub-problem belongs), and a 'similarity' key (corresponding similarity). Multiple fields and similarity MUST be separated by ','. Each JSON blob should only contain a single sub-problem; do NOT return a list of multiple sub-problems. Below is an example of a valid JSON blob:
{{{{
    "sub-problem": "SUB-PROBLEM CONTENT",
    "fields": "FIELD 1,FIELD 2,...",
    "similarity": "MEMBERSHIP DEGREE 1,MEMBERSHIP DEGREE 2,...",
}}}}
3. Output a summary of the inspection results above. If you find any errors or have any suggestions, please state them clearly in the Suggestions section. If there are no errors or suggestions, you MUST write 'No Suggestions' in the Suggestions section.

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. You can refer to historical suggestions and feedback in the History section but DO NOT repeat historical suggestions.
2. The answer to each sub-question should be a concise and complete sentence.
3. If you find any errors or have any suggestions, please state them clearly in the Suggestions section. If there are no errors or suggestions, you MUST write 'No Suggestions' in the Suggestions section.
4. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
5. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always think about if there are any errors or suggestions for the Sub-problem And Its Similarity To The Fields

## Suggestions:
1. ERROR1/SUGGESTION1
2. ERROR2/SUGGESTION2
2. ERROR3/SUGGESTION3
---
'''

OUTPUT_MAPPING = {
    "Suggestions": (str, ...),
}

TOOLS = 'None'


class CheckProblems(Action):
    def __init__(self, name="CheckProblemsTask", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, context, history=''):

        question_or_task = re.findall('## Question or Task:([\s\S]*?)##', str(context))[0]
        sub_problems = re.findall('## Sub-problem Similarity:([\s\S]*?)##', str(context))[0]

        prompt = PROMPT_TEMPLATE.format(question_or_task=question_or_task, sub_problems=sub_problems,
                                        format_example=FORMAT_EXAMPLE, history=history, tools=TOOLS)
        rsp = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return rsp
