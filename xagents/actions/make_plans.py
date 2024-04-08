#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/6 11:25          
@Author  : Mingxian Gu
@File    : make_plans
"""
from xagents.actions import Action

PROMPT_TEMPLATE = '''
-----
You are a manager and an expert-level ChatGPT prompt engineer with expertise in multiple fields. Your goal is to provide a detailed execution plan and create multiple LLM agents based on the execution plan. You should continuously improve the execution plan and execution expert Roles List based on the suggestions in the History section.

# Question or Task
{question_or_task}

# History
{history}

# Steps
You will come up with solutions for any problem or task by following these steps:
1. You should first understand, analyze, and break down the human's problem/task.
2. Based on the content of the problem/task and the expert roles, provide a detailed execution plan with the required steps to solve the problem.
2.1. Each step is connected in turn to form a whole. Specifically, the input of the next step is the output of the previous step.
2.2. The steps in the execution plan are in a sequential and progressive relationship. Specifically, the result of the next step is an expansion of the result of the previous step.
2.3. The FINAL STEP should always be a step that says 'Based on the previous steps, please provide a helpful, relevant, accurate, and detailed response to the user's original question: XXX '.
2.4. Output the execution plan as a numbered list of steps. 
3. Based on the execution plan and toolset ({tools}), you will create a unique execution expert role for each step in the execution plan. Each step should have one and only one execution expert role. You should follow these principles when creating execution expert roles:
3.1. Each new execution expert role should include a number, name, available tools and prompt templates.
3.2. Determine the number of each new execution expert role based on the sequence number of the executed steps. Each step should have one and only one execution expert role.
3.3. Determine the domains of expertise of each new execution expert role based on the content of the corresponding step.
3.4. Determine the names of each new execution expert role based on their domains of expertise. The name should express the characteristics of expert roles. 
3.5. Determine the goals of each new execution expert role based on their domains of expertise. The goal MUST indicate the primary responsibility or objective that the role aims to achieve. 
3.6. Determine the list of tools that each new execution expert needs to use based on the existing tool set. Each new expert role can have multiple tools or no tool at all. You should NEVER create any new tool and only use existing tools.
3.7. Generate the prompt template required for calling each new execution expert role according to its name, goal and tools. A good prompt template should first explain the role it needs to play (name) and the primary responsibility or objective that the role aims to achieve (goal). The prompt MUST follow the following format "You are [name]. Your goal is [goal].".
3.8. You MUST output the details of created new execution expert roles in JSON blob format. Specifically, The JSON of new execution expert roles should have a 'number' key (the execution expert role number), a 'name' key (the execution expert role name), a 'tools' key (with the name of the tools used by the execution expert role), and a 'prompt' key (the prompt template required to call the expert role). Each JSON blob should only contain one execution expert role, and do NOT return a list of multiple execution expert roles. Here is an example of a valid JSON blob:
{{{{
 "number": "ROLE NUMBER"
 "name": "ROLE NAME",
 "tools": ["ROLE TOOL"],
 "prompt": "ROLE PROMPT",
}}}}

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Suggestions
{suggestions}

# Attention
1. Each step is connected in turn to form a whole. Specifically, the input of the next step is the output of the previous step.
2. The steps in the execution plan are in a sequential and progressive relationship. Specifically, the result of the next step is an expansion of the result of the previous step.
3. The final step in the execution plan should always be a step that says  'Based on the previous steps, please provide a helpful, relevant, accurate, and detailed response to the user's original question: XXX '.
4. Follow the steps in order to create the execution expert role. Each step should have one and only one execution expert role.
5. You can only use the existing tools {tools} for any expert role. You are not allowed to use any other tools. You CANNOT create any new tool for any expert role.
6. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
7. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
If you do not receive any suggestions, you should always consider how to develop an execution plan and create execution expert roles.
If you do receive some suggestions, you should always evaluate how to enhance the execution plan and the execution expert roles list according to these suggestions and what feedback you can give to the suggesters.

## Question or Task:
The input question you must answer / the input task you must finish.

## Execution Plan:
1. STEP 1
2. STEP 2
3. STEP 3

## Execution Expert Roles List:
```
JSON BLOB 1,
JSON BLOB 2,
JSON BLOB 3
```

## PlansFeedback:
feedback on the historical Execution Plan suggestions

## RolesFeedback:
feedback on the historical Execution Expert Roles suggestions
---
'''

OUTPUT_MAPPING = {
    "Question or Task": (str, ...),
    "Execution Plan": (str, ...),
    "Execution Expert Roles List": (str, ...),
    "PlansFeedback": (str, ...),
    "RolesFeedback": (str, ...)
}

TOOLS = 'None'


class MakePlans(Action):

    def __init__(self, name="MakePlansTask", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, question_or_task, suggestions='', history=''):

        prompt = PROMPT_TEMPLATE.format(question_or_task=question_or_task, format_example=FORMAT_EXAMPLE,
                                        tools=TOOLS, history=history, suggestions=suggestions)
        response = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return response
