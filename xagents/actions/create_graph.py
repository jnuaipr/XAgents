#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/11 17:07          
@Author  : Mingxian Gu
@File    : create_graph
"""
from xagents.actions import Action

PROMPT_TEMPLATE = '''
-----
You are a manager with expertise in multiple fields. Your goal is to identify the predecessor steps for each step in the execution plan. 

# Question or Task
{question_or_task}

# Execution Plan
{plans}

# Steps
You will come up with solutions for any question or task by following these steps:
1. You should first understand and analyze the human's question/task.
2. According to the execution plan and question/task, you will identify the predecessor steps for each step. You should act as a professional analyst and planner, possessing expertise in multiple fields, in order to better identify the predecessor steps. When identifying the predecessor steps, you should follow these principles:
2.1. The predecessor steps of a step refers to the input of this step that requires the output of the predecessor steps.
2.2. You MUST consider all steps and analyze the dependency relationships of each steps.
2.3. You MUST output the detailed information of the predecessor steps for each step in JSON blob format. Specifically, the JSON for the predecessor tasks for each step should contain a `number` key (number of the step), a `task` key (content of the step), and a `inputs` key (number of the preceding steps corresponding to the step). Multiple preceding steps MUST be separated by ','. Each JSON blob should only contain a single step; do NOT return a list of multiple steps. Below is an example of a valid JSON blob:
{{{{
    "number": "STEP NUMBER",
    "task": "STEP CONTENT",
    "inputs": "PRECEDING STEP NUMBER 1,PRECEDING STEP NUMBER 2,..."
}}}}

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. Each step uniquely corresponds to a detailed JSON block of the predecessor steps.
2. Don't forget to identify the predecessor steps for the last step.
3. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
4. DO NOT ask any questions to the user or human.
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always consider how to identify the predecessor steps for each step

## Predecessor Steps:
```
JSON BLOB 1,
JSON BLOB 2,
JSON BLOB 3
```
---
'''

OUTPUT_MAPPING = {
    "Predecessor Steps": (str, ...)
}


class CreateGraph(Action):

    def __init__(self, name="CreateGraph", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, question_or_task, plans):

        prompt = PROMPT_TEMPLATE.format(question_or_task=question_or_task, plans=plans, format_example=FORMAT_EXAMPLE)
        rsp = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return rsp
