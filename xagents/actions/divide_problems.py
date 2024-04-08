#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/3 14:58          
@Author  : Mingxian Gu
@File    : divide_problems
"""
from xagents.actions import Action

PROMPT_TEMPLATE = '''
-----
You are a manager and also a professional analyst with expertise in multiple fields. Your goal is to analyze human problems/tasks, break down the problems/tasks into multiple sub-problems, and calculate the similarity between the fields of the sub-problems and existing professional fields. You should continuously improve the breakdown of the sub-problems and the similarity between the fields of the sub-problems and existing professional fields based on suggestions from the historical section.

# Question or Task
{question_or_task}

# Existing Professional Fields
{existing_fields}

# History
{history}

# Steps
You will come up with solutions for any problem or task by following these steps:
1. You should first fully understand and analyze the human problem/task.
2. According to the problem/task and the toolset ({tools}), you will decompose the problem/task into multiple sub-problems accurately. You should act as a professional analyst and planner, possessing expertise in multiple fields, in order to better decompose sub-problems and calculate the similarity of sub-problems. When decomposing sub-problems, you should follow these principles:
2.1. Each sub-problem is independent of each other and does not interfere with each other.
2.2. The decomposed sub-problems MUST be clear and singular. Specifically, each sub-problem should be simple and understandable, without ambiguity.
2.3. Predict the length of the answer to each sub-question. If the answer is longer than 1 sentence. Then you MUST discard it.
2.4. Output the sub-problems as a list with step numbers.
3. Based on the sub-problems and existing fields, you will calculate the similarity between the fields of sub-problems and existing domains. In calculating similarity, you should follow these principles:
3.1. The range of similarity values should be "low", "medium", "high".
3.2. Fully consider and analyze all provided expertise fields.
3.3. Calculate the similarity between each sub-problem's field and all existing fields in sequence according to the list of sub-problems.
3.4. Each professional field in each sub-question must correspond to a similarity.
3.5. Select existing professional fields with the similarity of "medium" or "high" for each sub-problem.
3.6. You must output the detailed information of all sub-problems' similarities in JSON blob format. Specifically, the JSON for the new expert role should contain a 'sub-problem' key (content of the sub-problem), a 'field' key (existing professional fields with "medium" or "high" similarity to the field to which the sub-problem belongs), and a 'similarity' key (corresponding similarity). Multiple fields and similarity MUST be separated by ','. Each JSON blob should only contain a single sub-problem; do NOT return a list of multiple sub-problems. Below is an example of a valid JSON blob:
{{{{
    "sub-problem": "SUB-PROBLEM CONTENT",
    "fields": "FIELD 1,FIELD 2,...",
    "similarity": "MEMBERSHIP DEGREE 1,MEMBERSHIP DEGREE 2,...",
}}}}

# Format example
Your final output should ALWAYS in the following format:
{format_example}

# Suggestions
{suggestions}

# Attention
1. You MUST think holistically when you break down the problem/task.
2. You MUST consider all existing fields when calculating the similarity of sub-problems.
3. The number of fields and the number of similarities MUST be consistent in JSON format.
4. Use '##' to separate sections, not '#', and write '## <SECTION_NAME>' BEFORE the code and triple quotes.
5. DO NOT ask any questions to the user or human. 
-----
'''

FORMAT_EXAMPLE = '''
---
## Thought
If you do not receive any suggestions, you should always consider how to break the problem into sub-problems.
If you do receive some suggestions, you should always evaluate how to enhance the previous sub-problem list and similarity of sub-problems to these suggestions and what feedback you can give to the suggesters.

## Question or Task:
the input question you must answer / the input task you must finish

## Sub-problem List:
1. SUB-PROBLEM 1
2. SUB-PROBLEM 2
3. SUB-PROBLEM 3

## Sub-problem Similarity:
```
JSON BLOB 1,
JSON BLOB 2,
JSON BLOB 3
```

## Feedback:
feedback on the historical suggestions
---
'''

OUTPUT_MAPPING = {
    "Question or Task": (str, ...),
    "Sub-problem List": (str, ...),
    "Sub-problem Similarity": (str, ...),
    "Feedback": (str, ...)
}

TOOLS = 'None'

existing_fields = '''
1. Medicine and Health
2. Computer Science and Technology
3. Economics and Finance
4. Education and Training
5. Engineering
6. Environmental Science and Energy
7. Arts and Design
8. Entertainment and Media
9. Law and Politics
10. Mathematics and Statistics
11. Physics
12. Chemistry
13. Biology
14. Psychology
15. Philosophy and Ethics
16. Sociology and Anthropology
17. History
18. Literature and Linguistics
19. Sports and Exercise Science
20. Tourism and Hotel Management
'''


class DivideProblems(Action):

    def __init__(self, name="DivideProblemsTask", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, question_or_task, history='', suggestions=''):

        prompt = PROMPT_TEMPLATE.format(question_or_task=question_or_task, existing_fields=existing_fields,
                                        format_example=FORMAT_EXAMPLE, tools=TOOLS, history=history,
                                        suggestions=suggestions)
        response = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)

        return response
