#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/4/1 14:24          
@Author  : Mingxian Gu
@File    : __init__.py
"""
from .action import Action, ActionOutput

from .make_plans import MakePlans
from .create_graph import CreateGraph
from .create_roles import CreateRoles

from .analyze_task import AnalyzeTask
from .calculate_similarity import CalculateSimilarity
from .acquire_knowledge import AcquireKnowledge
from .fusion_knowledge import FusionKnowledge

from .custom_action import CustomAction

# Predefined Actions
from .action_bank.requirement import Requirement
from .action_bank.write_code import WriteCode
from .action_bank.write_code_review import WriteCodeReview
from .action_bank.project_management import AssignTasks, WriteTasks
from .action_bank.design_api import WriteDesign
from .action_bank.write_prd import WritePRD
from .action_bank.search_and_summarize import SearchAndSummarize
