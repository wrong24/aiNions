import json
import time
import uuid
from typing import Dict, Any, List
from datetime import datetime
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from schemas import (
    OrchestrationState, InputMessage, Task, TaskType,
    L2TrackingOutput, L2CommunicationOutput, CrossCuttingOutput,
    ExecutionResult, Decision
)
from agents import L3Agents, CrossCuttingAgents

logger = logging.getLogger(__name__)


class L1Plan(BaseModel):
    """L1 Planning output"""
    tasks: List[Task] = Field(default_factory=list)
    reasoning: str = ""


class NionGraph:
    """LangGraph orchestration engine"""

    def __init__(self):
        self.graph = StateGraph(OrchestrationState)
        self.l3_agents = L3Agents()
        self.l1_llm = ChatOpenAI(model="gpt-4o", temperature=0.7, max_tokens=1500)

        self._build_graph()

    def _build_graph(self):
        """Build the LangGraph state graph"""

        # Add nodes
        self.graph.add_node("L1_Orchestrator", self._node_l1_orchestrator)
        self.graph.add_node("L2_Tracking", self._node_l2_tracking)
        self.graph.add_node("L2_Communication", self._node_l2_communication)
        self.graph.add_node("Cross_Knowledge", self._node_cross_knowledge)
        self.graph.add_node("Evaluator", self._node_evaluator)

        # Add edges
        self.graph.add_edge(START, "L1_Orchestrator")

        # Conditional routing from L1 to L2s and Cross-Cutting
        self.graph.add_conditional_edges(
            "L1_Orchestrator",
            self._router_l1_to_l2,
            path_map={
                "L2_Tracking": "L2_Tracking",
                "L2_Communication": "L2_Communication",
                "Cross_Knowledge": "Cross_Knowledge",
                "Evaluator": "Evaluator"
            }
        )

        # All L2s and Cross-Cutting route to Evaluator
        self.graph.add_edge("L2_Tracking", "Evaluator")
        self.graph.add_edge("L2_Communication", "Evaluator")
        self.graph.add_edge("Cross_Knowledge", "Evaluator")

        # Evaluator routes to END
        self.graph.add_edge("Evaluator", END)

        self.compiled_graph = self.graph.compile()

    def _node_l1_orchestrator(self, state: OrchestrationState) -> OrchestrationState:
        """L1 Node: Parse message and create plan (NO DIRECT L3 ACCESS)"""
        logger.info(f"[L1] Processing message: {state.input_message.message_id}")

        start_time = time.time()

        system_prompt = SystemMessage(content="""You are the L1 Orchestrator for the Nion system.
Your role is to analyze incoming messages and create a high-level delegation plan.

CRITICAL CONSTRAINT: You MUST ONLY delegate to these L2 Domain Coordinators:
1. L2_Tracking - For action items, risks, decisions
2. L2_Communication - For Q&A and communication needs
3. Cross_Knowledge - For knowledge retrieval

You CANNOT directly access or delegate to L3 workers (action_item_extractor, risk_extractor, etc.).
L2 coordinators will manage L3 execution internally.

Output a JSON with:
{
  "tasks": [
    {"task_id": "PLAN-001", "domain": "L2_Tracking", "description": "...", "priority": 1},
    ...
  ],
  "reasoning": "..."
}""")

        user_prompt = HumanMessage(content=f"""Analyze this message and create an orchestration plan:

Message: {state.input_message.message}
Sender: {state.input_message.sender}
Project: {state.input_message.project_id}

Output JSON following the schema.""")

        response = self.l1_llm.invoke([system_prompt, user_prompt])

        try:
            plan_data = json.loads(response.content)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse L1 response: {response.content}")
            plan_data = {
                "tasks": [
                    {"task_id": "PLAN-001", "domain": "L2_Tracking", "description": "Analyze message for actions", "priority": 1},
                    {"task_id": "PLAN-002", "domain": "Cross_Knowledge", "description": "Retrieve project context", "priority": 1}
                ],
                "reasoning": "Default plan due to parse error"
            }

        tasks = []
        for task_data in plan_data.get("tasks", []):
            domain_str = task_data.get("domain", "L2_Tracking")
            # Map string domain to TaskType enum
            domain_map = {
                "L2_Tracking": TaskType.L2_TRACKING,
                "L2_Communication": TaskType.L2_COMMUNICATION,
                "Cross_Knowledge": TaskType.CROSS_KNOWLEDGE
            }
            domain = domain_map.get(domain_str, TaskType.L2_TRACKING)

            task = Task(
                task_id=task_data.get("task_id", f"PLAN-{len(tasks) + 1}"),
                domain=domain,
                description=task_data.get("description", ""),
                priority=task_data.get("priority", 1),
                status="IN_PROGRESS"
            )
            tasks.append(task)

        state.plan = tasks
        state.logs.append(f"[L1] Created plan with {len(tasks)} tasks")
        logger.info(f"[L1] Plan created with {len(tasks)} tasks in {time.time() - start_time:.2f}s")

        return state

    def _router_l1_to_l2(self, state: OrchestrationState) -> str:
        """Route from L1 to L2 based on plan"""
        if not state.plan:
            return "Evaluator"

        # Route to first high-priority task
        next_task = min(state.plan, key=lambda t: t.priority)

        if next_task.domain == TaskType.L2_TRACKING:
            return "L2_Tracking"
        elif next_task.domain == TaskType.L2_COMMUNICATION:
            return "L2_Communication"
        elif next_task.domain == TaskType.CROSS_KNOWLEDGE:
            return "Cross_Knowledge"

        return "Evaluator"

    def _node_l2_tracking(self, state: OrchestrationState) -> OrchestrationState:
        """L2 Node: Tracking & Execution Domain - Calls L3 Workers"""
        logger.info("[L2_Tracking] Executing tracking domain")

        start_time = time.time()

        # First retrieve knowledge context
        knowledge = CrossCuttingAgents.retrieve_knowledge(state.input_message.project_id)

        # Call L3 workers
        action_items_result = self.l3_agents.extract_action_items(
            state.input_message.message,
            knowledge
        )
        risks_result = self.l3_agents.extract_risks(
            state.input_message.message,
            knowledge
        )

        # Extract decisions from content (simple heuristic)
        decisions = []
        if "willing to pay" in state.input_message.message.lower():
            decisions.append(Decision(
                id="DEC-001",
                title="Budget increase approved by customer",
                rationale="Customer feedback indicates willingness to fund feature enhancement",
                impact="Enables accelerated feature roadmap"
            ))

        output = L2TrackingOutput(
            action_items=action_items_result.action_items,
            risks=risks_result.risks,
            decisions=decisions
        )

        result = ExecutionResult(
            task_id="L2_TRACKING_001",
            task_type=TaskType.L2_TRACKING,
            status="SUCCESS",
            output=output.dict(),
            duration_ms=(time.time() - start_time) * 1000
        )

        state.execution_results["L2_TRACKING_001"] = result
        state.logs.append(f"[L2_Tracking] Completed: {len(action_items_result.action_items)} actions, {len(risks_result.risks)} risks")

        return state

    def _node_l2_communication(self, state: OrchestrationState) -> OrchestrationState:
        """L2 Node: Communication Domain - Calls L3 Workers"""
        logger.info("[L2_Communication] Executing communication domain")

        start_time = time.time()

        knowledge = CrossCuttingAgents.retrieve_knowledge(state.input_message.project_id)

        # Call L3 worker for Q&A
        qna_result = self.l3_agents.generate_qna(
            state.input_message.message,
            knowledge
        )

        output = L2CommunicationOutput(
            qna_records=qna_result.qna_records
        )

        result = ExecutionResult(
            task_id="L2_COMMUNICATION_001",
            task_type=TaskType.L2_COMMUNICATION,
            status="SUCCESS",
            output=output.dict(),
            duration_ms=(time.time() - start_time) * 1000
        )

        state.execution_results["L2_COMMUNICATION_001"] = result
        state.logs.append(f"[L2_Communication] Completed: {len(qna_result.qna_records)} Q&A records")

        return state

    def _node_cross_knowledge(self, state: OrchestrationState) -> OrchestrationState:
        """Cross-Cutting Node: Knowledge Retrieval with caching"""
        logger.info("[Cross_Knowledge] Retrieving knowledge context")

        start_time = time.time()

        knowledge = CrossCuttingAgents.retrieve_knowledge(state.input_message.project_id)

        output = CrossCuttingOutput(
            knowledge_context=knowledge
        )

        result = ExecutionResult(
            task_id="CROSS_KNOWLEDGE_001",
            task_type=TaskType.CROSS_KNOWLEDGE,
            status="SUCCESS",
            output=output.dict(),
            duration_ms=(time.time() - start_time) * 1000
        )

        state.execution_results["CROSS_KNOWLEDGE_001"] = result
        state.cross_cutting_context = knowledge
        state.logs.append(f"[Cross_Knowledge] Retrieved context for {state.input_message.project_id}")

        return state

    def _node_evaluator(self, state: OrchestrationState) -> OrchestrationState:
        """Evaluator Node: Assess execution quality"""
        logger.info("[Evaluator] Assessing execution results")

        evaluation = CrossCuttingAgents.evaluate_output(state.execution_results)
        state.logs.append(f"[Evaluator] {evaluation['overall_status']}: {evaluation['successful_tasks']}/{evaluation['total_tasks']} tasks successful")

        return state

    async def ainvoke(self, input_message: InputMessage) -> OrchestrationState:
        """Asynchronously invoke the graph"""
        state = OrchestrationState(
            input_message=input_message,
            state_id=str(uuid.uuid4())
        )
        logger.info(f"[Graph] Starting orchestration: {state.state_id}")

        result_state = self.compiled_graph.invoke(state, {"recursion_limit": 25})
        logger.info(f"[Graph] Orchestration completed: {state.state_id}")

        return result_state

    def invoke(self, input_message: InputMessage) -> OrchestrationState:
        """Synchronously invoke the graph"""
        state = OrchestrationState(
            input_message=input_message,
            state_id=str(uuid.uuid4())
        )
        logger.info(f"[Graph] Starting orchestration: {state.state_id}")

        result_state = self.compiled_graph.invoke(state, {"recursion_limit": 25})
        logger.info(f"[Graph] Orchestration completed: {state.state_id}")

        return result_state
