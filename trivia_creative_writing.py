#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
@Time    : 2024/4/7 17:23          
@Author  : Mingxian Gu
@File    : trivia_creative_writing
"""
import json
from startup import StartUp
import asyncio

accuracy_5 = []
accuracy_10 = []

with open('data/trivia_creative_writing/trivia_creative_writing_100_n_5.jsonl', "r") as f:
    problem_5 = [json.loads(line) for line in f]
with open('data/trivia_creative_writing/trivia_creative_writing_100_n_10.jsonl', "r") as f:
    problem_10 = [json.loads(line) for line in f]
with open('data/trivia_creative_writing/topics_pop_culture_100_gpt4_gen_PG_rated.txt', "r") as f:
    topics = f.read().splitlines()

for i in range(0, len(topics)):
    question = 'Write a short and coherent story about {%s} that incorporates the answers to the following {5} questions: ' % \
               topics[i]
    question += ' '.join(problem_5[i]['questions'])
    result = asyncio.run(StartUp(question))
    total = 0.0
    for answers in problem_5[i]['answers']:
        for answer in answers:
            if answer in result:
                total += 1.0
                break
    accuracy = total / len(problem_5[i]['answers'])
    print('------------Question Accuracy------------')
    print(f'Accuracy For Question {i+1}: {accuracy}')
    accuracy_5.append(accuracy)
    print('------------Total Accuracy------------')
    print(accuracy_5)
    with open(f'result/trivia_creative_writing/text_5/{i + 1}.txt', "w") as f:
        f.write(result)
    with open(f'result/trivia_creative_writing/accuracy_5/{i + 1}.txt', "w") as f:
        f.write(str(accuracy))










