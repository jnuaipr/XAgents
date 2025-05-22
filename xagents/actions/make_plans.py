#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/20 12:18          
@Author  : Mingxian Gu
@File    : make_plans
"""
from xagents.actions import Action

PROMPT_TEMPLATE = '''
-----
You are a manager with expertise in multiple fields. Your goal is to decompose the question/task into multiple subtasks and list the useful information for completing the subtasks.

# Question or Task
{question_or_task}

# Steps
You will come up with solutions for any question or task by following these steps:
1. You should first understand, analyze the human's question/task.
2. According to the question/task, you will decompose the question/task into multiple subtasks. 
2.1. The description of each subtask can NOT contain any information other than the human's question/task.
2.2. The description of each subtask MUST be complete so that it can be executed independently.
2.3. The final subtask MUST be `Based on the previous tasks, please provide a helpful, relevant, accurate, and detailed response to the human's original question/task`. 
2.4. Output the subtasks in the Subtasks section.
3. According to the subtasks, you will list the useful information for completing the subtasks from the question/task that is not exist in the subtasks.
3.1. If there is no useful information, you MUST write 'None' in the Information section.
3.2. If there is useful information, you MUST list it completely in the Information section.
3.3. The useful information can NOT be duplicated in the subtasks.
3.4. The useful information MUST ONLY come entirely from the question/task, and you can NOT change it.
3.5. The useful information MUST be complete enough to be used accurately when solving the subtask.

# Format Example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. The final subtask MUST be `Based on the previous tasks, please provide a helpful, relevant, accurate, and detailed response to the human's original question/task`. 
2. The useful information MUST be complete enough to be used accurately when solving the subtask.
3. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
4. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always consider how to decompose the question/task into multiple subtasks and determine whether there is information in the question/task that helps subtasks reasoning

## Subtasks:
1. SUBTASK 1
2. SUBTASK 2
3. SUBTASK 3

## Information:
useful information or None
---
'''

OUTPUT_MAPPING = {
    "Subtasks": (str, ...),
    "Information": (str, ...)
}


class MakePlans(Action):

    def __init__(self, name="MakePlans", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, question_or_task):

        prompt = PROMPT_TEMPLATE.format(question_or_task=question_or_task, format_example=FORMAT_EXAMPLE)
        rsp = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return rsp
