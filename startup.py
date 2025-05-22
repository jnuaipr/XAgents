#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xagents.explorer import Explorer
import asyncio
import argparse


async def startup(idea: str, investment: float = 10.0, task_id=None, llm_api_key: str = None,
                  serpapi_key: str = None,
                  proxy: str = None, alg_msg_queue: object = None, workspace=''):
    explorer = Explorer()
    explorer.invest(investment)
    await explorer.start_project(idea=idea, llm_api_key=llm_api_key, proxy=proxy, serpapi_key=serpapi_key,
                                 task_id=task_id, alg_msg_queue=alg_msg_queue, workspace=workspace)
    return await explorer.run()


question_or_task = '''
写一篇美国文化的文章。
'''

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a startup simulation.")
    parser.add_argument("--question_or_task", type=str, default=question_or_task, help="The question or task to process.")
    args = parser.parse_args()

    asyncio.run(startup(args.question_or_task))