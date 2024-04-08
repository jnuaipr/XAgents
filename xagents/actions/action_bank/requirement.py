#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xagents.actions import Action


class Requirement(Action):
    """Requirement without any implementation details"""
    async def run(self, *args, **kwargs):
        raise NotImplementedError
