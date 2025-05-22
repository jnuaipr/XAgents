#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/3/24 19:34          
@Author  : Mingxian Gu
@File    : fusion_knowledge
"""
from xagents.actions import Action

PROMPT_TEMPLATE = '''
-----
You are a linguist and have expertise in multiple fields. Your goal is to filter out the correct answers and combine the answers based on weights.

# Question
{question}

# Weights And Corresponding Answers
{answers_weight}

# Steps
You will filter out the correct answers and combine the answers by following these steps:
1. You should first understand and analyze the question.
3. According to the weight, and the answer corresponding to the weight, you need to filter out the correct answer.
3.1. Check each answer to see if it fits the question. 
3.2. Output the possible answers that match the question and the corresponding weights in the Possible Answers section.
4. Based on the possible answers and the corresponding weights, you need to merge multiple answers into one answer according to the weight.
4.1. If there is no answer that matches the question, you will answer the question directly. The final answer is your answer.
4.2. If there is only one answer that matches the question, you do nothing and the final answer is this.
4.3. If there are more than two answers that match the question, you will semantically fuse the answers into one final answer based on weights. 
4.3.1. If you are unsure of the answer to the question, then you will try to combine as many possible correct answers into one.

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. If you are unsure of the answer to the question, then you will try to combine as many possible correct answers into one.
2. The final answer MUST be clear, not ambiguous.
3. The final answer MUST be helpful, relevant, accurate, and detailed.
4. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
5. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always consider how to accurately combine answers based on weights

## Possible Answers
### Weight: WEIGHT 1
ANSWER CORRESPONDING TO WEIGHT 1
### Weight: WEIGHT 2
ANSWER CORRESPONDING TO WEIGHT 2
### Weight: WEIGHT 3
ANSWER CORRESPONDING TO WEIGHT 3

## Answer:
the final answer
---
'''

OUTPUT_MAPPING = {
    "Answer": (str, ...)
}


class FusionKnowledge(Action):

    def __init__(self, name="FusionKnowledge", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, question, answers_weight):

        prompt = PROMPT_TEMPLATE.format(question=question, answers_weight=answers_weight, format_example=FORMAT_EXAMPLE)
        rsp = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return rsp
