from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class DomainType(str, Enum):
    TRACKING_EXECUTION = "TRACKING_EXECUTION"
    COMMUNICATION_COLLABORATION = "COMMUNICATION_COLLABORATION"
    LEARNING_IMPROVEMENT = "LEARNING_IMPROVEMENT"


class TaskType(str, Enum):
    L2_TRACKING = "L2_Tracking"
    L2_COMMUNICATION = "L2_Communication"
    CROSS_KNOWLEDGE = "Cross_Knowledge"


class L3TaskType(str, Enum):
    ACTION_ITEM_EXTRACTION = "action_item_extraction"
    RISK_EXTRACTION = "risk_extraction"
    QNA_GENERATION = "qna_generation"


class ActionItem(BaseModel):
    id: str
    title: str
    owner: Optional[str] = None
    priority: str = Field(default="MEDIUM", pattern="^(HIGH|MEDIUM|LOW)$")
    due_date: Optional[str] = None
    status: str = Field(default="OPEN", pattern="^(OPEN|IN_PROGRESS|CLOSED)$")


class Risk(BaseModel):
    id: str
    title: str
    severity: str = Field(default="MEDIUM", pattern="^(CRITICAL|HIGH|MEDIUM|LOW)$")
    mitigation_strategy: Optional[str] = None
    owner: Optional[str] = None


class Decision(BaseModel):
    id: str
    title: str
    rationale: str
    impact: Optional[str] = None


class QnARecord(BaseModel):
    question: str
    answer: str
    confidence: float = Field(default=0.9, ge=0, le=1)


class Task(BaseModel):
    task_id: str
    domain: TaskType
    description: str
    priority: int = 1
    status: str = Field(default="PENDING", pattern="^(PENDING|IN_PROGRESS|COMPLETED|FAILED)$")


class InputMessage(BaseModel):
    message: str
    sender: str
    project_id: str
    message_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "The customer demo went great! Add real-time notifications.",
                "sender": "Sarah Chen",
                "project_id": "PRJ-ALPHA",
                "message_id": "MSG-001"
            }
        }


class L2TrackingOutput(BaseModel):
    domain: TaskType = TaskType.L2_TRACKING
    action_items: List[ActionItem] = []
    risks: List[Risk] = []
    decisions: List[Decision] = []
    logs: List[str] = []


class L2CommunicationOutput(BaseModel):
    domain: TaskType = TaskType.L2_COMMUNICATION
    qna_records: List[QnARecord] = []
    logs: List[str] = []


class CrossCuttingOutput(BaseModel):
    domain: TaskType = TaskType.CROSS_KNOWLEDGE
    knowledge_context: Dict[str, Any] = {}
    cache_hit: bool = False
    logs: List[str] = []


class ExecutionResult(BaseModel):
    task_id: str
    task_type: TaskType
    status: str = Field(pattern="^(SUCCESS|FAILED|PARTIAL)$")
    output: Dict[str, Any]
    error: Optional[str] = None
    duration_ms: float


class OrchestrationState(BaseModel):
    input_message: InputMessage
    plan: List[Task] = []
    execution_results: Dict[str, ExecutionResult] = {}
    cross_cutting_context: Dict[str, Any] = {}
    logs: List[str] = []
    state_id: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
