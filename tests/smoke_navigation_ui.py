"""验证真实鼠标双击事件与课程/练习往返，不修改用户数据库。"""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from edu.ui import App

with tempfile.TemporaryDirectory() as folder:
    app=App(Path(folder)/'navigation.sqlite3')
    try:
        app.update()
        assert app.course.page=='map'
        assert not app.course.lesson.winfo_viewable()
        canvas=app.course.map
        coords=canvas.bbox(canvas.find_withtag('border_range_step')[0])
        x,y=int(coords[0]+20),int(coords[1]+20)
        canvas.event_generate('<ButtonPress-1>',x=x,y=y,time=1000)
        canvas.event_generate('<ButtonRelease-1>',x=x,y=y,time=1020)
        app.update()
        assert app.course.page=='map'  # 单击只选中。
        assert app.course.selected=='range_step'
        canvas.event_generate('<ButtonPress-1>',x=x,y=y,time=1100)
        canvas.event_generate('<ButtonRelease-1>',x=x,y=y,time=1120)
        app.update()
        assert app.course.page=='detail'
        assert app.course.heading.get()=='range 的步长'
        assert app.course.start_button.instate(['disabled'])  # 锁定课仍可预览。
        assert app.course.free_button.instate(['!disabled'])
        assert app.course.sections.index('end')==3
        app.course.free_button.invoke();app.update()
        assert app.tabs.select()==str(app.practice)
        assert app.current['concept']=='range_step'
        assert app.course_concept is None
        assert app.store.lesson_reads()=={}  # 自由练习不伪造已读或解锁。
        app.open_current_lesson();app.update()
        assert app.tabs.select()==str(app.course)
        assert app.course.selected=='range_step'
        assert app.course.page=='detail'
        app.return_to_map();app.update()
        assert app.course.page=='map'
        app.course.resume();app.update()
        assert app.course.selected=='__intro__'
        app.course.start_selected();app.update()
        assert app.course.selected=='boundary'
        app.course.start_selected();app.update()
        assert app.current['concept']=='boundary' and app.course_concept=='boundary'
        app.return_to_map();app.geometry('900x740');app.update()
        assert app.course.map.winfo_height()>150
        assert app.course.map_scroll.winfo_viewable()
        app.course.select_lesson('range_step');app.update()
        assert app.course.start_button.winfo_rooty()+app.course.start_button.winfo_height()<=app.winfo_rooty()+app.winfo_height()
        print('Navigation passed: actual double-click → lesson detail → exact concept practice → lesson → map; guided mode and minimum layout preserved.')
    finally:
        app.destroy()
