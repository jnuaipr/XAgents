#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/4 21:56          
@Author  : Mingxian Gu
@File    : custom_knowledge_action
"""
from xagents.actions.action import Action

PROMPT_TEMPLATE = '''
-----
You are a/an {field} Expert. You have expertise in the field of {field}. Your goal is to use your expertise to solve problems.

# Problem
{problem}

# Steps
You will come up with solutions for any problem or task by following these steps:
1. You should first understand and analyze the problem.
2. Use your expertise to solve the problem. Your answer MUST be accurate.

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. Your area of expertise is {field}.
2. Your answer MUST be relevant to your area of expertise.
3. Your answer MUST be a concise sentence and contain both question and answer.
4. You MUST answer the question directly without any prefixes.
5. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
6. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always consider how you can use your expertise to solve problems.

## Answer:
your answer

## Input Problem:
problem you need to solve
---
'''

OUTPUT_MAPPING = {
    "Answer": (str, ...)
}


class CustomKnowledgeAction(Action):

    def __init__(self, name="CustomKnowledgeAction", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, history=''):

        prompt = PROMPT_TEMPLATE.format(problem=self.problem, field=self.field,
                                        format_example=FORMAT_EXAMPLE, history=history)
        response = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return response
