#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/3/24 19:34          
@Author  : Mingxian Gu
@File    : fusion_answer
"""
from xagents.actions import Action

PROMPT_TEMPLATE = '''
-----
You are a linguist and have expertise in multiple fields. Your goal is to filter out the correct answers and combine the answers based on weights.

# Problem
{problem}

# Weights And Corresponding Answers
{answers_weight}

# Steps
You will come up with solutions for any problem or task by following these steps:
1. You should first understand and analyze the problem.
2. According to the problem, the weight, and the answer corresponding to the weight, you need to filter out the correct answer.
2.1. Check each answer to see if it fits the problem.
2.2. Keep answers and corresponding weights that match the problem.
3. Based on the retained answers and corresponding weights, you need to merge multiple answers into one answer according to the weight. When blending answers, you need to follow these principles：
3.1. If there is no answer that matches the question, you will answer the question directly. The final answer is your answer.
3.2. If there is only one answer that matches the question, you do nothing and the final answer is this.
3.3. If there are more than two answers that match the question, you will semantically fuse the two answers into one final answer based on weights.

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. Your final answer can ONLY have one.
2. Your answer MUST be a concise sentence and contain both question and answer.
3. You MUST answer the question directly without any prefixes.
4. You can NOT simply piece together the answer. You MUST combine the answers semantically.
5. The final answer MUST be helpful, relevant, accurate, and detailed.
6. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
7. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always consider how to accurately fuse answers based on weights

## Final Answer:
the final answer

## Input Problem:
the input problem
---
'''

OUTPUT_MAPPING = {
    "Input Problem": (str, ...),
    "Final Answer": (str, ...)
}


class FusionAnswer(Action):

    def __init__(self, name="FusionAnswerTask", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, problem, answers_weight, history=''):

        prompt = PROMPT_TEMPLATE.format(problem=problem, answers_weight=answers_weight, format_example=FORMAT_EXAMPLE,
                                        history=history)
        response = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return response
