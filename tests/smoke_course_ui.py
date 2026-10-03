"""桌面课程完整流程；所有数据使用临时数据库。"""
import sys
import tempfile
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from edu.ui import App


def submit_and_wait(app,hint=False):
    if hint: app.show_hint()
    app.choice.set(app.current['answer']);app.submit()
    until=time.monotonic()+5
    while app.pending and time.monotonic()<until:
        app.update();time.sleep(.02)
    assert not app.pending

with tempfile.TemporaryDirectory() as folder:
    app=App(Path(folder)/'course.sqlite3')
    try:
        app.update()
        assert app.tabs.select()==str(app.course)
        assert app.current is None
        assert len(app.course.map.find_all())>=45
        app.course.select_lesson('range_end')
        assert app.course.start_button.instate(['disabled'])
        assert '概念讲解' in app.course.lesson.get('1.0','end')
        app.course.select_lesson('__intro__');app.course.start_selected();app.update()
        assert app.course.selected=='boundary'
        assert app.current is None  # 先看第一课，不直接跳进测验。
        app.course.start_selected();app.update()
        assert app.course_concept=='boundary'
        submit_and_wait(app,hint=True)
        assert not app.course.states['boundary']['passed']
        app.continue_course();submit_and_wait(app)
        app.continue_course();submit_and_wait(app)
        assert app.course.states['boundary']['passed']
        app.continue_course();app.update()
        assert app.tabs.select()==str(app.course)
        assert app.course.selected=='branches'
        assert not app.course.states['branches']['locked']
        assert app.course.states['range_end']['locked']
        assert app.store.history()[0]['hints_used']==1
        assert all(r['course_concept']=='boundary' for r in app.store.history())
        app.geometry('900x740');app.update()
        assert app.course.start_button.winfo_rooty()+app.course.start_button.winfo_height() <= app.winfo_rooty()+app.winfo_height()
        print('Course GUI passed: map → intro → lesson → hinted retry → two independent answers → unlock next lesson; minimum-window layout fits.')
    finally:
        app.destroy()
