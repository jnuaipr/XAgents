#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/4 22:30          
@Author  : Mingxian Gu
@File    : custom_execution_action
"""
from xagents.actions.action import Action

PROMPT_TEMPLATE = '''
-----
{role} You need to complete a step in the execution plan. Base on the following execution result of the previous agents and existing knowledge, complete the following step as best you can. You MUST prioritize existing knowledge.

# Original Question or Task
{question_or_task}

# Step You Need To Complete
{step}

# Execution Result of Previous Agents 
{previous_result}

# Existing Knowledge
{existing_knowledge}

# Tools 
You have access to the following tools:
{tools}

# Steps
You will come up with solutions for any problem or task by following these steps:
1. You should understand and analyze the execution result of the previous agents.
2. You should understand and analyze the existing knowledge.
3. You should understand and analyze the step you need to complete.
3. Based on the results of previous agents, and existing knowledge, you should do your best to complete the step you need to complete. You should follow these principles when completing the step:
3.1. You MUST strictly follow the requirements of the steps. 
3.2. You MUST prioritize existing knowledge.
3.3. You MUST complete the step based on the results of previous agent executions. 
3.4. Your answer can NOT deviate from the original question/task.

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Attention
1. You MUST prioritize existing knowledge.
2. You MUST complete the step based on the results of previous agent executions. 
3. Your answer can NOT deviate from the original question/task.
4. Your answer MUST be helpful, relevant, accurate, and detailed.
5. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
6. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
you should always consider how to better utilize your existing knowledge and complete the step you need to complete better

## Answer:
your final answer
---
'''

OUTPUT_MAPPING = {
    "Answer": (str, ...)
}


class CustomExecutionAction(Action):

    def __init__(self, name="CustomExecutionAction", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, step, previous_result, existing_knowledge, history=''):

        prompt = PROMPT_TEMPLATE.format(role=self.role_prompt, step=step, previous_result=previous_result,
                                        existing_knowledge=existing_knowledge, tools=self.tools,
                                        format_example=FORMAT_EXAMPLE, history=history,
                                        question_or_task=self.question_or_task)
        response = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return response
