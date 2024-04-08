#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xagents.roles import Role
from xagents.actions import Requirement, ActionOutput, DivideProblems, CheckProblems, MakePlans, CheckPlans, \
    CheckExecutionRoles
from xagents.system.logs import logger
from xagents.system.schema import Message


class Manager(Role):
    def __init__(self, name="Manager", profile="Manager", goal="Efficiently to finish the tasks or solve the problem",
                 constraints="", serpapi_key=None, **kwargs):
        super().__init__(name, profile, goal, constraints, **kwargs)
        self._init_actions([DivideProblems, MakePlans])
        self._watch([Requirement])

    async def _act(self) -> Message:

        problems, plans = '', ''
        num_steps = 3

        # 拆解问题，计算领域相似度，生成知识型专家参数
        # self._set_state(0)
        # logger.info(f"{self._setting}: ready to {self._rc.todo}")
        # problems = await self._rc.todo.run(question_or_task=self._rc.important_memory)
        # steps, consensus = 0, False
        # history_problems, suggestions_problems = '', ''
        # suggestions = ''
        # while not consensus and steps < num_steps:
        #     self._set_state(0)
        #     logger.info(f"{self._setting}: ready to {self._rc.todo}")
        #     problems = await self._rc.todo.run(question_or_task=self._rc.important_memory, history=history_problems,
        #                                        suggestions=suggestions)
        #     history_problems = str(problems.instruct_content)
        #
        #     if 'no suggestions' not in suggestions_problems.lower():
        #         self._set_state(1)
        #         logger.info(f"{self._setting}: ready to {self._rc.todo}")
        #         problems_feedback = f"## Sub-problems Suggestions\n{suggestions_problems}\n\n## Feedback\n{problems.instruct_content.Feedback}"
        #         _suggestions_problems = await self._rc.todo.run(context=problems.content, history=problems_feedback)
        #         suggestions_problems += _suggestions_problems.instruct_content.Suggestions
        #         suggestions = f"## Sub-problems Suggestions\n{_suggestions_problems.instruct_content.Suggestions}\n\n"
        #
        #     if 'no suggestions' in suggestions_problems.lower():
        #         consensus = True
        #     steps += 1

        # 指定执行计划，动作型专家参数
        # steps, consensus = 0, False
        # history_plans_roles, suggestions_plans, suggestions_roles = '', '', ''
        # suggestions = ''
        # while not consensus and steps < num_steps:
        #     self._set_state(2)
        #     logger.info(f"{self._setting}: ready to {self._rc.todo}")
        #     plans = await self._rc.todo.run(question_or_task=self._rc.important_memory, history=history_plans_roles,
        #                                     suggestions=suggestions)
        #     history_plans_roles = str(plans.instruct_content)
        #
        #     if 'no suggestions' not in suggestions_plans.lower() or 'no suggestions' not in suggestions_roles.lower():
        #         self._set_state(3)
        #         logger.info(f"{self._setting}: ready to {self._rc.todo}")
        #         history_plans = f"## Execution Plan Suggestions\n{suggestions_plans}\n\n## Feedback\n{plans.instruct_content.PlansFeedback}"
        #         _suggestions_plans = await self._rc.todo.run(plans.content, history=history_plans)
        #         suggestions_plans += _suggestions_plans.instruct_content.Suggestions
        #
        #         self._set_state(4)
        #         logger.info(f"{self._setting}: ready to {self._rc.todo}")
        #         history_roles = f"## Execution Expert Roles Suggestions\n{suggestions_roles}\n\n## Feedback\n{plans.instruct_content.RolesFeedback}"
        #         _suggestions_roles = await self._rc.todo.run(plans.content, history=history_roles)
        #         suggestions_roles += _suggestions_roles.instruct_content.Suggestions
        #
        #         suggestions = f"## Execution Plan Suggestions\n{_suggestions_plans.instruct_content.Suggestions}\n\n## Execution Expert Roles Suggestions\n{_suggestions_roles.instruct_content.Suggestions}"
        #
        #     if 'no Suggestions' in suggestions_plans.lower() and 'no Suggestions' in suggestions_roles.lower():
        #         consensus = True
        #     steps += 1

        self._set_state(1)
        logger.info(f"{self._setting}: ready to {self._rc.todo}")
        plans = await self._rc.todo.run(question_or_task=self._rc.important_memory)

        response = problems.content + plans.content

        if isinstance(response, ActionOutput):
            msg = Message(content=response.content, instruct_content=response.instruct_content,
                          role=self.profile, cause_by=type(self._rc.todo))
        else:
            msg = Message(content=response, role=self.profile, cause_by=type(self._rc.todo))
        self._rc.memory.add(msg)

        return msg
