#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/8 11:59          
@Author  : Mingxian Gu
@File    : check_execution_roles
"""
from .action import Action
import re

PROMPT_TEMPLATE = '''
-----
You are a ChatGPT executive observer expert skilled in identifying problem-solving plans and errors in the execution process. Your goal is to check if the Execution Expert Roles following the requirements and give your improvement suggestions. You can refer to historical suggestions in the History section, but try not to repeat them.

# Question or Task
{question_or_task}

# Execution Plan
{execution_plan}

# Execution Expert Roles
{execution_roles}

# History
{history}

# Steps
You will check the Execution Expert Roles by following these steps:
1. You should first understand, analyze the execution plan.
2. According to the execution plan and the toolset ({tools}), you should check the Execution Expert Roles following requirements:
2.1. Each step should have one and only one execution expert role.
2.2. Each new execution expert role should include a number, name, available tools and prompt templates.
2.3. The number of the execution expert role should be the corresponding step number. 
2.4. You should assign a clear and specific domain of expertise to each new execution expert role based on content of the corresponding step.
2.5. You should give a meaningful and expressive name to each new execution expert role based on their domain of expertise. The name should reflect the characteristics and functions of the expert role. 
2.6. You should state a clear and concise goal for each new execution expert role based on their domain of expertise. The goal must indicate the primary responsibility or objective that the expert role aims to achieve. 
2.7. You should select the appropriate tools that each new execution expert role needs to use from the existing tool set. Each new expert role can have multiple tools or no tool at all, depending on their functions and needs. You should never create any new tool and only use the existing ones
2.8. You should generate the prompt template required for calling each new execution expert role according to its name, goal and tools. A good prompt template should first explain the role it needs to play (name) and the primary responsibility or objective that the role aims to achieve (goal). The prompt MUST follow the following format "You are [name]. Your goal is [goal].".
2.9. You should follow the JSON blob format for creating new execution expert roles. Specifically, The JSON of new execution expert roles should have a 'number' key (the execution expert role number), a 'name' key (the execution expert role name), a 'tools' key (with the name of the tools used by the execution expert role), and a 'prompt' key (the prompt template required to call the expert role). Each JSON blob should only contain one execution expert role, and do NOT return a list of multiple execution expert roles. Here is an example of a valid JSON blob:
{{{{
 "number": "ROLE NUMBER"
 "name": "ROLE NAME",
 "tools": ["ROLE TOOL"],
 "prompt": "ROLE PROMPT",
}}}}
3. Output a summary of the inspection results above. If you find any errors or have any suggestions, please state them clearly in the Suggestions section. If there are no errors or suggestions, you MUST write 'No Suggestions' in the Suggestions section.

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. You can refer to historical suggestions and feedback in the History section but DO NOT repeat historical suggestions.
2. Each step should have one and only one execution expert role.
3. All execution expert roles can only use the existing tools ({tools}) for any expert role. They are not allowed to use any other tools. You CANNOT create any new tool for any execution expert role.
4. If you find any errors or have any suggestions, please state them clearly in the Suggestions section. If there are no errors or suggestions, you MUST write 'No Suggestions' in the Suggestions section.
5. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
6. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always think about if there are any errors or suggestions for the Execution Expert Roles

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


class CheckExecutionRoles(Action):
    def __init__(self, name="CheckExecutionRolesTask", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, context, history=''):

        question_or_task = re.findall('## Question or Task:([\s\S]*?)##', str(context))[0]
        execution_plan = re.findall('## Execution Plan:([\s\S]*?)##', str(context))[0]
        execution_roles = re.findall('Execution Expert Roles List:([\s\S]*?)##', str(context))[0]

        prompt = PROMPT_TEMPLATE.format(question_or_task=question_or_task, execution_plan=execution_plan,
                                        execution_roles=execution_roles, format_example=FORMAT_EXAMPLE, history=history, tools=TOOLS)
        rsp = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return rsp
