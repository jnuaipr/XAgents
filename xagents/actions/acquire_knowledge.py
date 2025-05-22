#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/4 21:56          
@Author  : Mingxian Gu
@File    : acquire_knowledge
"""
from xagents.actions.action import Action

PROMPT_TEMPLATE = '''
-----
You are a/an {field} Expert. You have expertise in the field of {field}. Your goal is to use your expertise to answer the question.

# Question
{question}

# Steps
You will answer the question by following these steps:
1. You should first understand and analyze the question.
2. Based on your expertise, you will describe the background of the question.
3. Based on the background, you will answer the question. 

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. You have expertise in the field of {field}.
2. The answer should be as relevant to your expertise as possible.
3. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
4. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always consider how you can use your expertise to answer the question

## Background:
background of the question

## Answer:
your answer
---
'''

OUTPUT_MAPPING = {
    "Answer": (str, ...),
}


class AcquireKnowledge(Action):

    def __init__(self, name="AcquireKnowledge", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self):

        self.llm.set_temperature(self.temperature)

        prompt = PROMPT_TEMPLATE.format(question=self.question, field=self.field, format_example=FORMAT_EXAMPLE)
        response = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)
        self.llm.set_temperature(0.0)

        return response
