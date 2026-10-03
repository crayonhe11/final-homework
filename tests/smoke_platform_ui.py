"""平台外观结构与导航检查，使用临时数据库。"""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from edu.ui import App
from edu.theme import ACCENT

with tempfile.TemporaryDirectory() as folder:
    app=App(Path(folder)/'platform.sqlite3')
    try:
        app.update()
        assert len(app.nav_buttons)==4
        assert [v.get() for v in app.course.metric_vars]==['0 / 15','0 / 30','0']
        for index,button in enumerate(app.nav_buttons):
            button.invoke();app.update()
            assert app.tabs.index(app.tabs.select())==index
            assert button.cget('fg')==ACCENT
        app.load_question('range_step_2');app.update()
        assert app.feedback.winfo_rootx()>app.code.winfo_rootx()+app.code.winfo_width()
        assert app.feedback.winfo_rootx()+app.feedback.winfo_width() <= app.winfo_rootx()+app.winfo_width()
        app.geometry('900x740');app.return_to_map();app.update()
        assert app.course.map_scroll.winfo_viewable()
        assert app.course.map.yview()[1]<1  # 窄屏改列后可滚动访问后续章节。
        app.course.map.yview_moveto(1);app.update()
        assert app.course.map.yview()[0]>0
        app.course.map.yview_moveto(0)
        print('Platform layout passed: sidebar, live metrics, two-column practice, responsive scrollable curriculum.')
    finally:
        app.destroy()
