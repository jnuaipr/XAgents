#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/8 17:30          
@Author  : Mingxian Gu
@File    : calculate_similarity
"""
import re
from xagents.actions import Action
from xagents.system.rules import RULES

PROMPT_TEMPLATE = '''
-----
You are a manager and also a professional analyst with expertise in multiple fields. Your goal is to calculate how similar the question's field is to existing fields of expertise and pick out the more similar fields for the question.

# Question
{question}

# Existing Professional Fields
{existing_fields}

# Steps
You will come up with solutions for any question or task by following these steps:
1. You should understand and analyze the question.
2. Based on the question and existing fields, you will calculate the similarity between the fields of the question and existing professional fields. When calculating similarity, you should follow these principles:
2.1. The range of similarity values should be "Low", "Medium", "High".
2.2. Fully consider and analyze all provided expertise fields.
2.3. Calculate the similarity between the question's field and all existing fields.
2.4. Each professional field MUST correspond to a similarity.
2.5. Select existing professional fields with the similarity of "Medium" or "High" for the question.
2.6. Output the detailed information of selected fields and its corresponding similarity. Specifically, ':' is preceded by the selected professional field, followed by the corresponding similarity.

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. You MUST consider all existing fields when calculating the similarity of the question.
2. The number of fields selected cannot exceed 3.
3. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
4. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always consider how to calculate the similarity between the fields of the question and existing professional fields

## Selected Fields:
FIELD 1: SIMILARITY 1
FIELD 2: SIMILARITY 2
FIELD 3: SIMILARITY 3
---
'''

OUTPUT_MAPPING = {
    "Selected Fields": (str, ...)
}


class CalculateSimilarity(Action):

    def __init__(self, name="CalculateSimilarity", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, question):

        prompt = PROMPT_TEMPLATE.format(question=question, existing_fields=RULES.rules, format_example=FORMAT_EXAMPLE)
        rsp = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return rsp
