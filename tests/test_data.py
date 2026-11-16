import collections
from src.data.synthetic_tasks import TASKS
from src.data.build import validate_task


def test_synthetic_set():
    assert len(TASKS) == 40
    for i, t in enumerate(TASKS):
        validate_task({**t, "task_id": f"X_{i}"})
    c = collections.Counter(t["category"] for t in TASKS)
    assert c == {"meeting_summary": 4, "email_draft": 12, "research_brief": 6, "slide_outline": 10, "data_extraction": 8}
