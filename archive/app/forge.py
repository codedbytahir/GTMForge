# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import logging
import re
from collections.abc import AsyncGenerator
from typing import Literal

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.genai import types as genai_types
from pydantic import BaseModel, Field
from app.agents.ideation_agent.agent import IdeationAgent

forge_agent = LlmAgent(
    name="Forge",
    description="Make GTMForge Agent",
    model="gemini-2.5-flash",
    instruction="You are a marketing and sales expert with a deep understanding of the GTM process. You are helping a company create a GTM strategy for a new product.",
    # sub_agents=[
    #     IdeationAgent()
    # ],
    tools=[
        # AgentTool(
        #     agent=deep_research_agent,
        # ),
    ],
)

