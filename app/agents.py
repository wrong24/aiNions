import json
import time
import redis
from typing import Dict, List, Any, Optional
from functools import wraps
import logging
from datetime import datetime
from google.api_core.exceptions import ResourceExhausted

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.schemas import (
    ActionItem, Risk, QnARecord, L2TrackingOutput,
    L2CommunicationOutput, CrossCuttingOutput, Decision
)

logger = logging.getLogger(__name__)


class LLMConfig:
    """LLM Configuration for Google Gemini"""
    MODEL_ORCHESTRATOR = "gemini-2.0-flash"
    MODEL_WORKER = "gemini-2.0-flash"
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000


class RedisConfig:
    """Redis Configuration"""
    HOST = "localhost"
    PORT = 6379
    DB = 0
    TTL = 60


def get_redis_client() -> redis.Redis:
    """Get Redis client"""
    try:
        client = redis.Redis(
            host=RedisConfig.HOST,
            port=RedisConfig.PORT,
            db=RedisConfig.DB,
            decode_responses=True
        )
        client.ping()
        return client
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
        return None


# In-memory fallback cache
_memory_cache: Dict[str, tuple] = {}


def cache_result(ttl: int = RedisConfig.TTL):
    """Cache decorator for function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            redis_client = get_redis_client()

            # Try Redis first
            if redis_client:
                try:
                    cached = redis_client.get(cache_key)
                    if cached:
                        logger.info(f"Cache HIT: {cache_key}")
                        return json.loads(cached)
                except Exception as e:
                    logger.warning(f"Redis read error: {e}")

            # Try memory cache
            if cache_key in _memory_cache:
                cached_value, expiry = _memory_cache[cache_key]
                if time.time() < expiry:
                    logger.info(f"Memory cache HIT: {cache_key}")
                    return cached_value

            # Cache miss - execute function
            result = func(*args, **kwargs)

            # Store in Redis
            if redis_client:
                try:
                    redis_client.setex(
                        cache_key,
                        ttl,
                        json.dumps(result, default=str)
                    )
                    logger.info(f"Cached in Redis: {cache_key}")
                except Exception as e:
                    logger.warning(f"Redis write error: {e}")

            # Store in memory cache
            _memory_cache[cache_key] = (result, time.time() + ttl)

            return result
        return wrapper
    return decorator


def retry_on_429(max_retries=3, initial_delay=4):
    """Decorator to retry on Rate Limit errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except ResourceExhausted:
                    logger.warning(f"Rate limit hit (429). Retrying in {delay} seconds...")
                    time.sleep(delay)
                    retries += 1
                    delay *= 2  # Exponential backoff
                except Exception as e:
                    # Sometimes 429s are wrapped in generic exceptions
                    if "429" in str(e):
                        logger.warning(f"Rate limit hit (generic). Retrying in {delay} seconds...")
                        time.sleep(delay)
                        retries += 1
                        delay *= 2
                    else:
                        raise e
            raise Exception(f"Max retries exceeded for Rate Limit in {func.__name__}")
        return wrapper
    return decorator


class ActionItemExtractionSchema(BaseModel):
    """Schema for action item extraction"""
    action_items: List[ActionItem] = Field(default_factory=list)
    extraction_confidence: float = Field(default=0.85, ge=0, le=1)


class RiskExtractionSchema(BaseModel):
    """Schema for risk extraction"""
    risks: List[Risk] = Field(default_factory=list)
    extraction_confidence: float = Field(default=0.85, ge=0, le=1)


class QnAGenerationSchema(BaseModel):
    """Schema for Q&A generation"""
    qna_records: List[QnARecord] = Field(default_factory=list)
    generation_confidence: float = Field(default=0.85, ge=0, le=1)


class L3Agents:
    """L3 Worker Agents - Google Gemini execution"""

    def __init__(self):
        self.gemini_orchestrator = ChatGoogleGenerativeAI(
            model=LLMConfig.MODEL_ORCHESTRATOR,
            temperature=LLMConfig.TEMPERATURE,
            max_output_tokens=LLMConfig.MAX_TOKENS,
            convert_system_message_to_human=True
        )
        self.gemini_worker = ChatGoogleGenerativeAI(
            model=LLMConfig.MODEL_WORKER,
            temperature=LLMConfig.TEMPERATURE,
            max_output_tokens=LLMConfig.MAX_TOKENS,
            convert_system_message_to_human=True
        )

    @retry_on_429()
    def extract_action_items(self, content: str, project_context: Dict[str, Any]) -> ActionItemExtractionSchema:
        """L3 Worker: Extract action items using Gemini"""
        parser = JsonOutputParser(pydantic_object=ActionItemExtractionSchema)

        system_prompt = SystemMessage(content="""You are an expert project manager AI assistant.
Analyze the given message and extract actionable items.
Return a JSON with 'action_items' array and 'extraction_confidence' score.

Each action item MUST have: id (ACT-XXX format), title, owner, priority (HIGH/MEDIUM/LOW), due_date.

Be strict: only extract items that are clear action requests, not observations.""")

        context_str = json.dumps(project_context, indent=2)
        user_prompt = HumanMessage(content=f"""Project Context:
{context_str}

Message to analyze:
{content}

{parser.get_format_instructions()}""")

        response = self.gemini_worker.invoke([system_prompt, user_prompt])
        parsed = json.loads(response.content)

        action_items = [
            ActionItem(
                id=item.get("id", f"ACT-{1000 + i}"),
                title=item["title"],
                owner=item.get("owner"),
                priority=item.get("priority", "MEDIUM"),
                due_date=item.get("due_date"),
                status="OPEN"
            )
            for i, item in enumerate(parsed.get("action_items", []))
        ]

        return ActionItemExtractionSchema(
            action_items=action_items,
            extraction_confidence=parsed.get("extraction_confidence", 0.85)
        )

    @retry_on_429()
    def extract_risks(self, content: str, project_context: Dict[str, Any]) -> RiskExtractionSchema:
        """L3 Worker: Extract risks using Gemini"""
        parser = JsonOutputParser(pydantic_object=RiskExtractionSchema)

        system_prompt = SystemMessage(content="""You are an expert risk analyst AI assistant.
Analyze the given message and identify potential risks.
Return a JSON with 'risks' array and 'extraction_confidence' score.

Each risk MUST have: id (RSK-XXX format), title, severity (CRITICAL/HIGH/MEDIUM/LOW), mitigation_strategy, owner.

Be thorough but realistic.""")

        context_str = json.dumps(project_context, indent=2)
        user_prompt = HumanMessage(content=f"""Project Context:
{context_str}

Message to analyze:
{content}

{parser.get_format_instructions()}""")

        response = self.gemini_worker.invoke([system_prompt, user_prompt])
        parsed = json.loads(response.content)

        risks = [
            Risk(
                id=item.get("id", f"RSK-{1000 + i}"),
                title=item["title"],
                severity=item.get("severity", "MEDIUM"),
                mitigation_strategy=item.get("mitigation_strategy"),
                owner=item.get("owner")
            )
            for i, item in enumerate(parsed.get("risks", []))
        ]

        return RiskExtractionSchema(
            risks=risks,
            extraction_confidence=parsed.get("extraction_confidence", 0.85)
        )

    @retry_on_429()
    def generate_qna(self, content: str, project_context: Dict[str, Any]) -> QnAGenerationSchema:
        """L3 Worker: Generate Q&A using Gemini"""
        parser = JsonOutputParser(pydantic_object=QnAGenerationSchema)

        system_prompt = SystemMessage(content="""You are an expert communication analyst AI assistant.
Analyze the given message and generate relevant Q&A records.
Return a JSON with 'qna_records' array and 'generation_confidence' score.

Each record MUST have: question, answer, confidence (0-1).

Generate questions that stakeholders might ask based on the message.""")

        context_str = json.dumps(project_context, indent=2)
        user_prompt = HumanMessage(content=f"""Project Context:
{context_str}

Message to analyze:
{content}

{parser.get_format_instructions()}""")

        response = self.gemini_worker.invoke([system_prompt, user_prompt])
        parsed = json.loads(response.content)

        qna_records = [
            QnARecord(
                question=item["question"],
                answer=item["answer"],
                confidence=float(item.get("confidence", 0.9))
            )
            for item in parsed.get("qna_records", [])
        ]

        return QnAGenerationSchema(
            qna_records=qna_records,
            generation_confidence=parsed.get("generation_confidence", 0.85)
        )


class CrossCuttingAgents:
    """Cross-Cutting Agents - Knowledge Retrieval & Evaluation"""

    MOCK_KNOWLEDGE_BASE = {
        "PRJ-ALPHA": {
            "project_name": "Project Alpha - Real-time Customer Platform",
            "team_members": ["Sarah Chen (Product Manager)", "John Doe (Lead Engineer)", "Alice Smith (QA)"],
            "budget": 150000,
            "timeline": "Q1-Q2 2025",
            "current_features": ["user_authentication", "dashboard", "analytics_reporting"],
            "tech_stack": ["Python", "React", "PostgreSQL", "Redis"],
            "recent_updates": "Customer demo scheduled for Q4 2024. Positive feedback expected.",
            "constraints": "Real-time features require WebSocket infrastructure and Redis caching.",
            "precedents": "Similar feature (push_notifications) added in PRJ-BETA with 18% cost increase and 6-week timeline.",
            "stakeholders": ["Executive Team", "Engineering Team", "Customer Success"],
            "risk_threshold": "HIGH",
            "approval_authority": "VP Product & Finance"
        },
        "PRJ-BETA": {
            "project_name": "Project Beta - Enterprise Analytics",
            "team_members": ["Tom Wilson", "Emma Davis"],
            "budget": 200000,
            "timeline": "Q2-Q3 2025",
            "current_features": ["data_ingestion", "reporting", "notifications"],
            "tech_stack": ["Java", "Kafka", "Elasticsearch"],
            "recent_updates": "Phase 2 in progress.",
            "constraints": "Latency SLA: <100ms for queries",
            "precedents": None,
            "stakeholders": ["CTO", "Finance"],
            "risk_threshold": "MEDIUM",
            "approval_authority": "CTO"
        }
    }

    @staticmethod
    @cache_result(ttl=60)
    def retrieve_knowledge(project_id: str) -> Dict[str, Any]:
        """Cross-Cutting Agent: Retrieve knowledge from Redis or mock DB"""
        project_data = CrossCuttingAgents.MOCK_KNOWLEDGE_BASE.get(
            project_id,
            {"error": f"Project {project_id} not found", "available_projects": list(CrossCuttingAgents.MOCK_KNOWLEDGE_BASE.keys())}
        )
        return project_data

    @staticmethod
    def evaluate_output(execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-Cutting Agent: Evaluate execution quality"""
        evaluation = {
            "total_tasks": len(execution_results),
            "successful_tasks": sum(1 for r in execution_results.values() if r.get("status") == "SUCCESS"),
            "failed_tasks": sum(1 for r in execution_results.values() if r.get("status") == "FAILED"),
            "average_confidence": 0.0,
            "overall_status": "COMPLETED",
            "recommendations": []
        }

        total_confidence = 0
        count = 0
        for result in execution_results.values():
            output = result.get("output", {})
            if "extraction_confidence" in output:
                total_confidence += output["extraction_confidence"]
                count += 1
            elif "generation_confidence" in output:
                total_confidence += output["generation_confidence"]
                count += 1

        if count > 0:
            evaluation["average_confidence"] = total_confidence / count

        if evaluation["failed_tasks"] > 0:
            evaluation["overall_status"] = "PARTIAL"
            evaluation["recommendations"].append("Review failed tasks for issues")

        if evaluation["average_confidence"] < 0.75:
            evaluation["recommendations"].append("Consider re-running with higher model precision")

        return evaluation