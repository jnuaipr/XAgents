#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xagents.roles import Manager
from xagents.explorer import Explorer
import asyncio


async def StartUp(idea: str, investment: float = 3.0, n_round: int = 10, task_id=None,
                  llm_api_key: str = None, serpapi_key: str = None, proxy: str = None, alg_msg_queue: object = None):
    """Run a startup. Be a boss."""
    explorer = Explorer()
    explorer.hire([Manager(proxy=proxy, llm_api_key=llm_api_key, serpapi_api_key=serpapi_key)])
    explorer.invest(investment)
    await explorer.start_project(idea=idea, llm_api_key=llm_api_key, proxy=proxy, serpapi_key=serpapi_key,
                                 task_id=task_id, alg_msg_queue=alg_msg_queue)
    return await explorer.run()


question_or_task = '''
写一篇美国文化的文章。
'''

if __name__ == "__main__":
    asyncio.run(StartUp(question_or_task))

