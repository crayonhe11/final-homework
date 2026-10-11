"""仅使用模拟模型，验证讲解、推荐与下一题衔接；不产生API用量。"""
import sys,time,tempfile,json
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from edu.ui import App

def wait(app):
    deadline=time.monotonic()+5
    while app.pending and time.monotonic()<deadline: app.update();time.sleep(.02)
    assert not app.pending

with tempfile.TemporaryDirectory() as d,patch('edu.ai.ai_config',return_value={'EDU_AI_PROVIDER':'kimi','MOONSHOT_API_KEY':'fake'}):
    app=App(Path(d)/'db')
    try:
        app.update();assert not app.ai_enabled.get()
        app.load_question('range_end_2');app.ai_enabled.set(True);app.reason.insert('1.0','不包含5，我点错了');app.choice.set('A')
        result={'status':'ok','concept':'unknown','quote':'点错了','message':'测试模拟结果',
                'feedback':{'status':'ok','explanation':'你的文字说明终点不包含；仅凭这次误选不足以判断概念误区。',
                            'hint':'换一个终点再验证。','knowledge_quote':app.current['explanation']}}
        with patch.object(app.ai,'analyze',return_value=result): app.submit_btn.invoke();wait(app)
        app.update();assert 'AI个性化讲解' in app.feedback.get('1.0','end')
        assert app.next_recommendation['strategy']=='neutral_verification'
        next_id=app.next_recommendation['question']['id'];app.submit_btn.invoke();app.update();assert app.current['id']==next_id
        assert 'AI证据不足' in app.feedback.get('1.0','end')
        assert json.loads(app.store.history()[0]['ai_json'])['feedback']['status']=='ok'
        app.course.select_lesson('__intro__');app.course.start_selected();app.course.start_selected();app.update()
        assert app.course_concept=='boundary'
        app.choice.set(next(k for k in app.current['options'] if k!=app.current['answer']));app.reason.insert('1.0','我点错了')
        with patch.object(app.ai,'analyze',return_value=result): app.submit_btn.invoke();wait(app)
        app.update();assert app.course_concept=='boundary';assert not app.course.states['boundary']['passed']
        extras=[b for b in app.recs.winfo_children() if '课外验证' in b.cget('text')];assert len(extras)==1
        app.geometry('900x740');app.update();assert app.submit_btn.winfo_rooty()+app.submit_btn.winfo_height()<app.winfo_rooty()+app.winfo_height()
        extras[0].invoke();app.update();assert app.course_concept is None
        print('AI UI passed: generated explanation, neutral recommendation, next-button routing, saved feedback, course-safe supplementary practice.')
    finally: app.destroy()
