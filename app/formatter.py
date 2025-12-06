import logging
from typing import Dict, Any
from datetime import datetime

from schemas import OrchestrationState, ExecutionResult, TaskType

logger = logging.getLogger(__name__)


class NionFormatter:
    """Formatter for NION ORCHESTRATION MAP output"""

    @staticmethod
    def generate_nion_map(state: OrchestrationState) -> str:
        """Generate NION ORCHESTRATION MAP from orchestration state"""

        lines = []

        # Header
        lines.append("=" * 90)
        lines.append("NION ORCHESTRATION MAP")
        lines.append("=" * 90)

        # Message Metadata
        lines.append("")
        lines.append("MESSAGE METADATA")
        lines.append("-" * 90)
        lines.append(f"  Message ID: {state.input_message.message_id or 'AUTO-GENERATED'}")
        lines.append(f"  Sender: {state.input_message.sender}")
        lines.append(f"  Project: {state.input_message.project_id}")
        lines.append(f"  Timestamp: {state.input_message.timestamp or datetime.utcnow().isoformat()}")
        lines.append(f"  State ID: {state.state_id}")
        lines.append(f"  Message: {state.input_message.message[:100]}{'...' if len(state.input_message.message) > 100 else ''}")

        # L1 Plan
        lines.append("")
        lines.append("=== L1 PLAN ===")
        lines.append("-" * 90)
        if state.plan:
            for i, task in enumerate(state.plan, 1):
                domain_display = task.domain.value
                lines.append(f"  [TASK-{i:03d}] Domain: {domain_display}")
                lines.append(f"    Task ID: {task.task_id}")
                lines.append(f"    Description: {task.description}")
                lines.append(f"    Priority: P{task.priority}")
                lines.append(f"    Status: {task.status}")
                lines.append("")
        else:
            lines.append("  No tasks planned")

        # L2/L3 Execution Results
        lines.append("")
        lines.append("=== L2/L3 EXECUTION ===")
        lines.append("-" * 90)

        if state.execution_results:
            for task_id, result in sorted(state.execution_results.items()):
                lines.append(f"  [{task_id}] {result.task_type.value}")
                lines.append(f"    Status: {result.status}")
                lines.append(f"    Duration: {result.duration_ms:.2f}ms")

                output = result.output
                if isinstance(output, dict):
                    # L2_Tracking Output
                    if "action_items" in output:
                        action_items = output.get("action_items", [])
                        if action_items:
                            lines.append(f"    ACTION ITEMS ({len(action_items)}):")
                            for ai in action_items:
                                lines.append(f"      • {ai['id']}: {ai['title']}")
                                lines.append(f"        Owner: {ai.get('owner', 'Unassigned')}, Priority: {ai.get('priority')}, Status: {ai.get('status')}")
                                if ai.get('due_date'):
                                    lines.append(f"        Due: {ai['due_date']}")

                    if "risks" in output:
                        risks = output.get("risks", [])
                        if risks:
                            lines.append(f"    RISKS ({len(risks)}):")
                            for risk in risks:
                                lines.append(f"      • {risk['id']}: {risk['title']}")
                                lines.append(f"        Severity: {risk.get('severity')}, Owner: {risk.get('owner', 'TBD')}")
                                if risk.get('mitigation_strategy'):
                                    lines.append(f"        Mitigation: {risk['mitigation_strategy']}")

                    if "decisions" in output:
                        decisions = output.get("decisions", [])
                        if decisions:
                            lines.append(f"    DECISIONS ({len(decisions)}):")
                            for decision in decisions:
                                lines.append(f"      • {decision['id']}: {decision['title']}")
                                lines.append(f"        Rationale: {decision.get('rationale')}")
                                if decision.get('impact'):
                                    lines.append(f"        Impact: {decision['impact']}")

                    # L2_Communication Output
                    if "qna_records" in output:
                        qna_records = output.get("qna_records", [])
                        if qna_records:
                            lines.append(f"    Q&A RECORDS ({len(qna_records)}):")
                            for qna in qna_records:
                                lines.append(f"      Q: {qna['question']}")
                                lines.append(f"      A: {qna['answer']}")
                                lines.append(f"      Confidence: {qna.get('confidence', 0.9):.2f}")

                    # Cross_Knowledge Output
                    if "knowledge_context" in output:
                        knowledge = output.get("knowledge_context", {})
                        if knowledge and "error" not in knowledge:
                            lines.append(f"    KNOWLEDGE CONTEXT:")
                            lines.append(f"      Project: {knowledge.get('project_name', 'Unknown')}")
                            lines.append(f"      Budget: ${knowledge.get('budget', 'N/A')}")
                            lines.append(f"      Timeline: {knowledge.get('timeline', 'N/A')}")
                            lines.append(f"      Team Size: {len(knowledge.get('team_members', []))}")
                            lines.append(f"      Tech Stack: {', '.join(knowledge.get('tech_stack', []))}")
                            if knowledge.get('constraints'):
                                lines.append(f"      Constraints: {knowledge['constraints']}")

                lines.append("")
        else:
            lines.append("  No execution results")

        # Summary
        lines.append("")
        lines.append("=== EXECUTION SUMMARY ===")
        lines.append("-" * 90)
        total_tasks = len(state.execution_results)
        successful_tasks = sum(1 for r in state.execution_results.values() if r.status == "SUCCESS")
        failed_tasks = sum(1 for r in state.execution_results.values() if r.status == "FAILED")
        partial_tasks = sum(1 for r in state.execution_results.values() if r.status == "PARTIAL")

        lines.append(f"  Total Tasks Executed: {total_tasks}")
        lines.append(f"  Successful: {successful_tasks}")
        lines.append(f"  Failed: {failed_tasks}")
        lines.append(f"  Partial: {partial_tasks}")
        lines.append(f"  Overall Status: {'COMPLETED' if failed_tasks == 0 else 'FAILED'}")

        # Logs
        if state.logs:
            lines.append("")
            lines.append("=== EXECUTION LOGS ===")
            lines.append("-" * 90)
            for log in state.logs[-10:]:  # Last 10 logs
                lines.append(f"  {log}")

        # Footer
        lines.append("")
        lines.append("=" * 90)

        return "\n".join(lines)

    @staticmethod
    def generate_json_output(state: OrchestrationState) -> Dict[str, Any]:
        """Generate JSON output of orchestration state"""
        return {
            "state_id": state.state_id,
            "message_metadata": {
                "message_id": state.input_message.message_id,
                "sender": state.input_message.sender,
                "project_id": state.input_message.project_id,
                "timestamp": state.input_message.timestamp.isoformat() if state.input_message.timestamp else None
            },
            "plan": [
                {
                    "task_id": task.task_id,
                    "domain": task.domain.value,
                    "description": task.description,
                    "priority": task.priority,
                    "status": task.status
                }
                for task in state.plan
            ],
            "execution_results": {
                task_id: {
                    "task_id": result.task_id,
                    "task_type": result.task_type.value,
                    "status": result.status,
                    "duration_ms": result.duration_ms,
                    "output": result.output
                }
                for task_id, result in state.execution_results.items()
            },
            "logs": state.logs
        }
