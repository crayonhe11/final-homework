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
        print('GUI smoke passed: wrong → recommendation → correct → history → progress; layout fits.')
    finally:
        app.destroy()
