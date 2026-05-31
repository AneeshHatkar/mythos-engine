import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.schemas.global_refs import ReviewStatus
from backend.app.schemas.human_review import HumanReviewRecord


class HumanReviewStore:
    """Persistent queue for human approval/rejection of risky or high-value outputs."""

    def __init__(self, root: str | Path = "reports/human_review") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.records_path = self.root / "human_review_records.jsonl"

    def enqueue(self, review: HumanReviewRecord | Dict[str, Any]) -> Dict[str, Any]:
        record = review if isinstance(review, HumanReviewRecord) else HumanReviewRecord.model_validate(review)

        with self.records_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record.model_dump(), sort_keys=True, ensure_ascii=False) + "\n")

        return {
            "success": True,
            "review_id": record.review_id,
            "target_entity_id": record.target_ref.entity_id,
            "review_queue_type": record.review_queue_type,
            "review_status": record.review_status,
        }

    def list_reviews(
        self,
        *,
        status: Optional[str] = None,
        queue_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        records = self._read_all()

        if status:
            records = [item for item in records if str(item.get("review_status")) == status]
        if queue_type:
            records = [item for item in records if str(item.get("review_queue_type")) == queue_type]

        return records

    def update_status(
        self,
        *,
        review_id: str,
        status: ReviewStatus,
        reviewer: Optional[str] = None,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        records = self._read_all()
        updated = None

        for item in records:
            if item.get("review_id") == review_id:
                item["review_status"] = status.value
                if status == ReviewStatus.APPROVED:
                    item["approved_by_human"] = reviewer or "human_reviewer"
                if status == ReviewStatus.REJECTED:
                    item["rejected_by_human"] = reviewer or "human_reviewer"
                if note:
                    item.setdefault("notes", []).append(note)
                updated = item
                break

        if updated is None:
            return {"success": False, "reason": "review_not_found", "review_id": review_id}

        self.records_path.write_text(
            "\n".join(json.dumps(item, sort_keys=True, ensure_ascii=False) for item in records) + "\n",
            encoding="utf-8",
        )

        return {
            "success": True,
            "review_id": review_id,
            "review_status": updated["review_status"],
        }

    def _read_all(self) -> List[Dict[str, Any]]:
        if not self.records_path.exists():
            return []

        records = []
        with self.records_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
