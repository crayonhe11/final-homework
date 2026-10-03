"""课程版间隔复习，不是 FSRS。仅到期后的独立答对增加间隔。"""
from datetime import datetime, timedelta, timezone

INTERVAL_DAYS = (1, 3, 7, 14, 30)


def parse_time(value):
    try:
        stamp = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return stamp.replace(tzinfo=timezone.utc) if stamp.tzinfo is None else stamp.astimezone(timezone.utc)


def review_schedule(history):
    """从日志重建状态；提前刷题不推迟到期时间，无效旧时间不参与调度。"""
    states = {}
    rows = [(parse_time(r.get('created_at')), i, r) for i, r in enumerate(history)]
    for stamp, _, row in sorted((r for r in rows if r[0] is not None), key=lambda r: (r[0], r[1])):
        qid = row['question_id']
        previous = states.get(qid)
        if not row['correct']:
            states[qid] = {'due': stamp + timedelta(minutes=10), 'stage': 0, 'last': stamp}
        elif row.get('hints_used', 0) != 0:
            due = stamp + timedelta(days=1)
            if previous and previous['due'] > stamp: due = min(due, previous['due'])
            states[qid] = {'due': due, 'stage': 0, 'last': stamp}
        elif previous and stamp < previous['due']:
            states[qid] = {**previous, 'last': stamp}
        else:
            stage = min((previous['stage'] if previous else 0) + 1, len(INTERVAL_DAYS))
            states[qid] = {'due': stamp + timedelta(days=INTERVAL_DAYS[stage-1]), 'stage': stage, 'last': stamp}
    return states


def due_reviews(questions, history, now=None, topic=None):
    now = now or datetime.now(timezone.utc)
    schedule = review_schedule(history)
    return sorted((qid for qid, state in schedule.items()
                   if qid in questions and state['due'] <= now
                   and (topic is None or questions[qid]['topic'] == topic)),
                  key=lambda qid: (schedule[qid]['due'], qid))
