import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from edu.bank import load_bank
from edu.curriculum import INTRO_ID, course_states, load_lessons, lesson_question
from edu.storage import Store


class CurriculumTests(unittest.TestCase):
    def setUp(self):
        self.questions,self.concepts=load_bank()
        self.lessons=load_lessons(self.concepts)
        self.reads={INTRO_ID:'read'}
        self.rows=[]

    def states(self):
        return course_states(self.questions,self.concepts,self.rows,self.reads)

    def complete(self,cid,hints=0):
        self.reads[cid]='read'
        for q in self.questions.values():
            if q['concept']==cid:
                self.rows.append({'question_id':q['id'],'course_concept':cid,'correct':1,'hints_used':hints})

    def test_every_lesson_example_output(self):
        self.assertEqual(len(self.lessons),15)
        for cid,lesson in self.lessons.items():
            with self.subTest(concept=cid):
                result=subprocess.run([sys.executable,'-I','-c',lesson['example_code']],capture_output=True,text=True,check=True,timeout=2)
                self.assertEqual(result.stdout.rstrip('\n'),lesson['example_output'])
                for q in self.questions.values():
                    if q['concept']==cid: self.assertNotEqual(q['code'],lesson['example_code'])

    def test_intro_required(self):
        self.reads={}
        self.assertTrue(all(s['locked'] for s in self.states().values()))
        self.reads[INTRO_ID]='read'
        self.assertFalse(self.states()['boundary']['locked'])
        self.assertTrue(self.states()['branches']['locked'])
        self.assertTrue(self.states()['range_end']['locked'])

    def test_reading_alone_does_not_pass(self):
        self.reads['boundary']='read'
        state=self.states()['boundary']
        self.assertEqual(state['status'],'学习中')
        self.assertFalse(state['passed'])

    def test_same_question_twice_does_not_pass(self):
        self.reads['boundary']='read'
        self.rows=[{'question_id':'boundary_1','course_concept':'boundary','correct':1,'hints_used':0}]*2
        self.assertFalse(self.states()['boundary']['passed'])
        self.assertEqual(lesson_question('boundary',self.questions,self.states()['boundary'])['id'],'boundary_2')

    def test_hints_require_independent_retry(self):
        self.complete('boundary',hints=1)
        self.assertFalse(self.states()['boundary']['passed'])
        self.complete('boundary')
        self.assertTrue(self.states()['boundary']['passed'])
        self.assertFalse(self.states()['branches']['locked'])

    def test_free_practice_cannot_award_course(self):
        self.complete('boundary')
        for row in self.rows: row['course_concept']=None
        self.assertFalse(self.states()['boundary']['passed'])
        self.assertTrue(self.states()['branches']['locked'])

    def test_locked_attempts_are_not_counted_retroactively(self):
        self.complete('branches')
        self.complete('boundary')
        self.assertFalse(self.states()['branches']['passed'])
        self.assertEqual(self.states()['branches']['solved'],0)

    def test_latest_wrong_before_pass_invalidates_that_question(self):
        self.reads['boundary']='read'
        self.rows=[{'question_id':'boundary_1','course_concept':'boundary','correct':1,'hints_used':0},
                   {'question_id':'boundary_1','course_concept':'boundary','correct':0,'hints_used':0},
                   {'question_id':'boundary_2','course_concept':'boundary','correct':1,'hints_used':0}]
        self.assertFalse(self.states()['boundary']['passed'])
        self.assertEqual(self.states()['boundary']['solved'],1)

    def test_all_chapters_unlock_without_deadlock(self):
        for cid in sorted(self.concepts,key=lambda c:self.concepts[c]['order']):
            self.assertFalse(self.states()[cid]['locked'],cid)
            self.complete(cid)
            self.assertTrue(self.states()[cid]['passed'],cid)
        self.assertTrue(all(s['passed'] for s in self.states().values()))

    def test_later_review_error_does_not_relock(self):
        self.complete('boundary')
        self.rows.append({'question_id':'boundary_1','course_concept':'boundary','correct':0,'hints_used':0})
        self.assertTrue(self.states()['boundary']['passed'])
        self.assertFalse(self.states()['branches']['locked'])

    def test_course_state_survives_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'learning.sqlite3'
            store=Store(path)
            store.mark_lesson_read(INTRO_ID);store.mark_lesson_read('boundary')
            store.mark_lesson_read('boundary')
            for qid in ('boundary_1','boundary_2'):
                store.save(qid,self.questions[qid]['answer'],'',{'correct':True,'concept':None},{},course_concept='boundary')
            restarted=Store(path)
            states=course_states(self.questions,self.concepts,restarted.history(),restarted.lesson_reads())
            self.assertTrue(states['boundary']['passed'])
            self.assertEqual(len(restarted.lesson_reads()),2)

if __name__=='__main__': unittest.main()
