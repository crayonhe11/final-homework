import copy
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from edu.bank import load_bank, validate_bank
from edu.engine import next_practice, learning_summary, progress, recommend
from edu.scheduler import review_schedule, due_reviews
from edu.storage import Store

NOW = datetime(2026, 9, 30, 12, tzinfo=timezone.utc)


def attempt(qid='range_end_1', correct=1, hints=0, stamp=NOW):
    return {'question_id':qid, 'correct':correct, 'hints_used':hints, 'created_at':stamp.isoformat()}


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.questions, self.concepts = load_bank()

    def test_wrong_due_in_ten_minutes(self):
        rows = [attempt(correct=0)]
        self.assertEqual(due_reviews(self.questions, rows, NOW + timedelta(minutes=9)), [])
        self.assertEqual(due_reviews(self.questions, rows, NOW + timedelta(minutes=10)), ['range_end_1'])

    def test_due_correct_advances_interval(self):
        rows = [attempt(), attempt(stamp=NOW + timedelta(days=1))]
        state = review_schedule(rows)['range_end_1']
        self.assertEqual(state['stage'], 2)
        self.assertEqual(state['due'], NOW + timedelta(days=4))

    def test_early_repetition_does_not_push_due(self):
        rows = [attempt()] + [attempt(stamp=NOW + timedelta(minutes=i)) for i in range(1,10)]
        self.assertEqual(review_schedule(rows)['range_end_1']['due'], NOW + timedelta(days=1))
        self.assertEqual(review_schedule(rows)['range_end_1']['stage'], 1)

    def test_hinted_or_unknown_not_independent(self):
        for hints in (1,2,None):
            rows = [attempt(), attempt('range_end_2', hints=hints)]
            result = next(r for r in progress(self.questions, rows, self.concepts) if r['concept']=='range_end')
            self.assertEqual(result['state'], '需独立作答验证')
            self.assertEqual(review_schedule(rows)['range_end_2']['stage'], 0)

    def test_hinted_due_review_reschedules_without_promotion(self):
        rows = [attempt(), attempt(hints=1, stamp=NOW+timedelta(days=1))]
        state = review_schedule(rows)['range_end_1']
        self.assertEqual(state['due'], NOW+timedelta(days=2))
        self.assertEqual(state['stage'], 0)

    def test_lapse_resets_interval(self):
        rows = [attempt(), attempt(stamp=NOW+timedelta(days=1)), attempt(correct=0,stamp=NOW+timedelta(days=4))]
        state = review_schedule(rows)['range_end_1']
        self.assertEqual(state['stage'], 0)
        self.assertEqual(state['due'], NOW + timedelta(days=4,minutes=10))

    def test_interval_capped(self):
        rows = [attempt()]
        for _ in range(9): rows.append(attempt(stamp=review_schedule(rows)['range_end_1']['due']))
        state = review_schedule(rows)['range_end_1']
        self.assertEqual(state['stage'], 5)
        self.assertEqual(state['due'] - state['last'], timedelta(days=30))

    def test_bad_legacy_time_and_unknown_question(self):
        rows = [attempt('deleted',correct=0,stamp=NOW-timedelta(days=1))]
        rows += [{'question_id':'range_end_1','correct':1,'created_at':'bad date'}]
        self.assertEqual(due_reviews(self.questions, rows, NOW), [])
        self.assertEqual(learning_summary(self.questions, rows, NOW)['archived'], 1)
        progress(self.questions, rows, self.concepts)  # Missing archived question must not crash.

    def test_naive_legacy_timestamp_treated_as_utc(self):
        row = attempt(); row['created_at'] = '2026-09-30T12:00:00'
        self.assertEqual(review_schedule([row])['range_end_1']['due'],NOW+timedelta(days=1))

    def test_due_before_unrelated_new_question(self):
        rows = [attempt('accumulate_1',correct=0,stamp=NOW-timedelta(hours=1))]
        item = next_practice('循环',self.questions,rows,self.concepts,NOW)
        self.assertEqual(item['question']['id'],'accumulate_1')
        self.assertIn('到期',item['reason'])

    def test_immediate_same_concept_before_due(self):
        rows = [attempt('accumulate_1',correct=0,stamp=NOW-timedelta(hours=1))]
        recs = recommend(self.questions['range_end_1'],self.questions,rows,now=NOW)
        self.assertEqual(recs[0]['question']['id'],'range_end_2')
        self.assertEqual(recs[1]['question']['id'],'accumulate_1')

    def test_learning_order_and_soft_prerequisites(self):
        first = next_practice('循环',self.questions,[],self.concepts,NOW)
        self.assertEqual(first['question']['id'],'range_end_1')
        rows=[attempt(),attempt('range_end_2')]
        second = next_practice('循环',self.questions,rows,self.concepts,NOW)
        self.assertEqual(second['question']['id'],'range_step_1')
        # 没有基础题可做时仍允许学习，不把前置关系变成硬锁。
        subset={'while_check_1':self.questions['while_check_1']}
        item=next_practice('循环',subset,[],self.concepts,NOW)
        self.assertIn('建议先巩固',item['reason'])

    def test_first_accuracy_not_inflated_by_repeats(self):
        rows=[attempt(correct=0)] + [attempt() for _ in range(5)]
        stats=learning_summary(self.questions,rows,NOW)
        self.assertEqual(stats['first_correct'],0)
        self.assertEqual(stats['unique'],1)
        self.assertEqual(stats['correct'],5)

    def test_legacy_database_migration_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'old.sqlite3'
            with sqlite3.connect(path) as conn:
                conn.execute('CREATE TABLE attempts (id INTEGER PRIMARY KEY,question_id TEXT,choice TEXT,reason TEXT,correct INTEGER,diagnosis TEXT,ai_json TEXT,created_at TEXT)')
                conn.execute('INSERT INTO attempts VALUES (1,?,?,?,?,?,?,?)',('range_end_1','B','原理由',0,'range_end','{}',NOW.isoformat()))
            conn.close()
            Store(path); store=Store(path)
            rows=store.history()
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]['reason'],'原理由')
            self.assertIsNone(rows[0]['hints_used'])
            store.save('range_end_2','B','',{'correct':True,'concept':None},{},hints_used=2)
            self.assertEqual(store.history()[1]['hints_used'],2)

    def test_invalid_question_content_rejected(self):
        for mutate in (
            lambda qs: qs[0].update(explanation=''),
            lambda qs: qs[0].update(difficulty=True),
            lambda qs: qs[0].update(hints=[]),
            lambda qs: qs[0].update(topic='未知主题'),
            lambda qs: qs[0]['options'].update(B=qs[0]['options']['A']),
            lambda qs: qs.append(copy.deepcopy(qs[0])),
        ):
            qs=copy.deepcopy(list(self.questions.values())); mutate(qs)
            with self.assertRaises(ValueError): validate_bank(qs,self.concepts)

    def test_prerequisite_cycle_rejected(self):
        concepts=copy.deepcopy(self.concepts)
        concepts['boundary']['prerequisites']=['branches']
        with self.assertRaisesRegex(ValueError,'循环依赖'):
            validate_bank(list(self.questions.values()),concepts)

    def test_unknown_prerequisite_rejected(self):
        concepts=copy.deepcopy(self.concepts)
        concepts['boundary']['prerequisites']=['nonexistent']
        with self.assertRaisesRegex(ValueError,'未知前置'):
            validate_bank(list(self.questions.values()),concepts)

if __name__ == '__main__': unittest.main()
