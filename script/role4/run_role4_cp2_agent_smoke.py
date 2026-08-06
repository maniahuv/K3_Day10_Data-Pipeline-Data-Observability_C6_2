from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from core.config import load_settings
from core.utils import write_json, write_text
from retrieval.agent import build_agent
from retrieval.index import LocalEmbeddingIndex


def _message_to_dict(message: Any) -> dict[str, Any]:
    message_type = getattr(message, "type", message.__class__.__name__)
    content = getattr(message, "content", "")
    tool_calls = getattr(message, "tool_calls", None)
    name = getattr(message, "name", None)
    return {
        "type": str(message_type),
        "class": message.__class__.__name__,
        "name": name,
        "has_tool_calls": bool(tool_calls),
        "tool_calls": tool_calls or [],
        "content_preview": str(content)[:600],
    }


def _has_tool_activity(messages: list[Any]) -> bool:
    for message in messages:
        message_type = str(getattr(message, "type", "")).lower()
        class_name = message.__class__.__name__.lower()
        if getattr(message, "tool_calls", None):
            return True
        if message_type == "tool" or "toolmessage" in class_name:
            return True
    return False


def main() -> int:
    settings = load_settings(ROOT)
    index = LocalEmbeddingIndex.load(settings)
    first_doc = index.documents[0]
    question = f"Who authored '{first_doc['title']}'?"

    print(f"Loaded collection: {index.collection_name}")
    print(f"Question: {question}")
    print("Building agent and invoking factual question...")

    agent = build_agent(settings=settings, index=index)
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    messages = result.get("messages", [])
    final_answer = getattr(messages[-1], "content", "") if messages else ""
    used_tool = _has_tool_activity(messages)

    payload = {
        "status": "pass" if used_tool and final_answer else "fail",
        "collection_name": index.collection_name,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.model_name,
        "question": question,
        "expected_doc": {
            "paper_id": first_doc["paper_id"],
            "title": first_doc["title"],
        },
        "used_tool_before_answer": used_tool,
        "final_answer": final_answer,
        "messages": [_message_to_dict(message) for message in messages],
    }

    json_path = settings.paths.project_dir / "data" / "results" / "role4_cp2_agent_smoke.json"
    write_json(json_path, payload)

    report_path = settings.paths.project_dir / "report" / "role4" / "role4_cp2_agent_smoke.md"
    lines = [
        "# CP2 - Vai trò 4: Agent smoke test",
        "",
        "## Kết quả",
        "",
        f"- Status: {'PASS' if payload['status'] == 'pass' else 'FAIL'}",
        f"- Collection: `{index.collection_name}`",
        f"- LLM provider: `{settings.llm_provider}`",
        f"- LLM model: `{settings.model_name}`",
        f"- Used tool before answer: `{used_tool}`",
        f"- Artifact: `{json_path}`",
        "",
        "## Question",
        "",
        f"`{question}`",
        "",
        "## Final answer",
        "",
        str(final_answer),
        "",
        "## Message/tool evidence",
        "",
    ]
    for idx, message in enumerate(payload["messages"], start=1):
        lines.append(
            f"- {idx}. type=`{message['type']}`, class=`{message['class']}`, "
            f"name=`{message['name']}`, has_tool_calls=`{message['has_tool_calls']}`"
        )
    write_text(report_path, "\n".join(lines) + "\n")

    print(f"Used tool before answer: {used_tool}")
    print(f"Final answer: {final_answer}")
    print(f"Wrote JSON: {json_path}")
    print(f"Wrote report: {report_path}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
