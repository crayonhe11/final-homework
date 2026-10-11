import sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from edu.ui import App
with tempfile.TemporaryDirectory() as d:
    app=App(Path(d)/'db')
    try:
        app.update();app.open_coding('循环');app.update();lab=app.coding
        assert lab.current_id=='robot_coins'
        source=lab.tasks[lab.current_id]['solution']
        lab.editor.delete('1.0','end');lab.editor.insert('1.0',source);lab.save_draft()
        app.open_coding('条件判断');app.open_coding('循环');app.update()
        assert lab.editor.get('1.0','end-1c')==source
        lab.run('submit');deadline=time.monotonic()+8
        while lab.running and time.monotonic()<deadline: app.update();time.sleep(.02)
        assert not lab.running
        assert app.store.code_history()[-1]['passed'], lab.result.get('1.0','end')
        assert len(app.store.history())==0
        app.open_coding('全部章节');app.update();assert len(lab.tree.get_children())==3
        app.navigate(3);app.update();assert app.charts.canvas.find_all()
        app.geometry('900x740');app.open_coding('函数与返回值');app.update()
        assert lab.submit_button.winfo_viewable()
        assert lab.submit_button.winfo_rooty()+lab.submit_button.winfo_height()<app.winfo_rooty()+app.winfo_height()
        print('Coding UI passed: chapter entry, drafts, actual submission, grouped overview, charts, small window.')
    finally: app.destroy()
