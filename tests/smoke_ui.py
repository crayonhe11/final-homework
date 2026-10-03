"""需要桌面会话：python3 tests/smoke_ui.py。只写临时数据库。"""
import sys
import tempfile
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from edu.ui import App

with tempfile.TemporaryDirectory() as temp:
    app=App(Path(temp)/'test.sqlite3')
    try:
        app.update()
        app.load_question('range_end_1'); app.choice.set('B')
        app.reason.insert('1.0','我以为包含终点4。'); app.submit()
        until=time.monotonic()+5
        while app.pending and time.monotonic()<until:
            app.update(); time.sleep(.02)
        assert not app.pending
        assert len(app.store.history())==1
        assert '可能涉及' in app.feedback.get('1.0','end')
        app.submit(); assert len(app.store.history())==1
        assert len(app.recs.winfo_children())==2
        app.recs.winfo_children()[0].invoke(); app.update()
        assert app.current['id']=='range_end_2'
        app.choice.set('B'); app.submit()
        until=time.monotonic()+5
        while app.pending and time.monotonic()<until:
            app.update(); time.sleep(.02)
        assert len(app.store.history())==2
        app.tabs.select(app.review); app.update()
        assert len(app.records.get_children())==1
        app.records.selection_set(app.records.get_children()[0]); app.show_record()
        assert '我以为包含终点4' in app.record_detail.get('1.0','end')
        app.only_wrong.set(False); app.refresh(); assert len(app.records.get_children())==2
        app.tabs.select(app.stats); app.update()
        assert len(app.progress_table.get_children())==15
        app.tabs.select(app.practice); app.update()
        assert app.recs.winfo_y()+app.recs.winfo_height()<=app.practice.winfo_height()
        app.load_question('boundary_1')
        app.show_hint(); app.show_hint(); app.show_hint()
        assert app.hints_used == 2
        assert app.hint_btn.instate(['disabled'])
        app.choice.set(app.current['answer']); app.submit()
        until=time.monotonic()+5
        while app.pending and time.monotonic()<until:
            app.update(); time.sleep(.02)
        assert app.store.history()[-1]['hints_used'] == 2
        assert '需独立作答验证' in app.feedback.get('1.0','end')
        with app.store.connect() as conn:
            conn.execute("UPDATE attempts SET created_at='2020-01-01T00:00:00+00:00' WHERE question_id='boundary_1'")
        app.tabs.select(app.stats); app.refresh(); app.update()
        assert '到期' in app.summary.get()
        app.start_due_review(); app.update()
        assert app.current['id']=='boundary_1'
        assert app.hints_used==0
        # 旧题被删除后仍能浏览、导出其记录，不导致进度页异常。
        app.store.save('archived_question','A','保留旧记录',{'correct':False,'concept':None},{})
        app.refresh(); app.tabs.select(app.review); app.update()
        app.records.selection_set(str(app.store.history()[-1]['id'])); app.show_record()
        assert '题目已不在当前题库' in app.record_detail.get('1.0','end')
        print('Hints, due review, and archived history passed.')
        print('GUI smoke passed: wrong → recommendation → correct → history → progress; layout fits.')
    finally:
        app.destroy()
