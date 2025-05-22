#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/18 14:29          
@Author  : Mingxian Gu
@File    : create_roles
"""
import re

from xagents.actions import Action

PROMPT_TEMPLATE = '''
-----
You are a manager and an expert-level ChatGPT prompt engineer with expertise in multiple fields. Your goal is to create an expert role for each task in order according to the order of the tasks.

# Original Question or Task
{question_or_task}

# Tasks
{plans}

# Steps
You will come up with solutions for any question or task by following these steps:
1. You should first understand and analyze each task. Specifically, the tasks are the subtasks of the original question/task.
2. According to the tasks and toolset ({tools}), you will create a unique expert role for each task to complete it. You should act as an expert-level ChatGPT prompt engineer and planner with expertise in multiple fields, so that you can better create expert roles. When creating expert roles, you should follow these principles:
2.1. Each expert role should include a number, a name, a detailed description of their area of expertise, available tools, and prompt templates.
2.2. The number of each new expert role is the corresponding task number.
2.3. Determine the domains of expertise of each new expert role based on the content of the corresponding task. The description of their area of expertise should be detailed so that the role understands what they are capable of doing. 
2.4. Determine the names of each new expert role based on their domains of expertise. The name should express the characteristics of expert roles. 
2.5. Determine the goals of each new expert role based on their domains of expertise. The goal MUST indicate the primary responsibility or objective that the role aims to achieve. 
2.6. Determine the list of tools that each new expert needs to use based on the existing tool set. Each new expert role can have multiple tools or no tool at all. You should NEVER create any new tool and only use existing tools.
2.7. Generate the prompt template required for calling each new expert role according to its name, description, goal, constraints, and tools. A good prompt template should first explain the role it needs to play (name), its area of expertise (description), and the primary responsibility or objective that the role aims to achieve (goal). The prompt MUST follow the following format "You are [description], named [name]. Your goal is [goal]".
2.8. You MUST output the details of created expert roles in JSON blob format. Specifically, The JSON of expert roles should have a `number` key (the corresponding task number), a `name` key (the expert role name), a `tools` key (with the name of the tools used by the expert role) and a `prompt` key (the prompt template required to call the expert role). Each JSON blob should only contain one expert role, and do NOT return a list of multiple expert roles. Here is an example of a valid JSON blob:
{{{{
 "number": "POLR NUMBER"
 "name": "ROLE NAME",
 "tools": ["ROLE TOOL"],
 "prompt": "ROLE PROMPT",
}}}}

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. Each step uniquely corresponds to a detailed JSON block of the expert roles.
2. You can ONLY use the existing tools ({tools}) for any expert role. You are not allowed to use any other tools. You CANNOT create any new tool for any expert role.
3. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
4. DO NOT ask any questions to the user or human.
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always consider how to create a unique LLM agent for each task

## Roles List:
```
JSON BLOB 1,
JSON BLOB 2,
JSON BLOB 3
```
---
'''

OUTPUT_MAPPING = {
    "Roles List": (str, ...)
}

TOOLS = 'None'


class CreateRoles(Action):

    def __init__(self, name="CreateRoles", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, question_or_task, plans):

        prompt = PROMPT_TEMPLATE.format(question_or_task=question_or_task, plans=plans,
                                        format_example=FORMAT_EXAMPLE, tools=TOOLS)
        rsp = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return rsp
