"""Standard-library HTTP adapter. Only bundled public assets can be served."""
from functools import partial
from hashlib import sha256
from hmac import compare_digest
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import re
import secrets
import threading
import time
from urllib.parse import urlsplit, unquote
from .domain import LearningEngine, ROOT, text
from .storage import Store, ConflictError
from .ai import config, analyze
from .agent import run_agent

mimetypes.add_type('application/wasm', '.wasm')
mimetypes.add_type('application/javascript', '.mjs')

class Application:
    def __init__(self, db, settings=None):
        self.engine = LearningEngine()
        self.store = Store(db)
        self.settings = settings if settings is not None else config()
        self.lock = threading.Lock()
        self.window, self.calls = time.monotonic(), 0

    def ai_enabled(self):
        return bool(self.settings.get('OPENAI_API_KEY') and len(self.settings.get('TEAM_ACCESS_CODE', '')) >= 12)

    def authorize_ai(self, supplied):
        wanted = self.settings.get('TEAM_ACCESS_CODE', '')
        return len(wanted) >= 12 and compare_digest(sha256(supplied.encode()).digest(), sha256(wanted.encode()).digest())

    def allow_call(self):
        with self.lock:
            if time.monotonic() - self.window >= 3600:
                self.window, self.calls = time.monotonic(), 0
            if self.calls >= 60:
                return False
            self.calls += 1
            return True

class Handler(SimpleHTTPRequestHandler):
    server_version = 'PySteps/1.0'
    def __init__(self, *args, app, **kwargs):
        self.app = app
        self.cookie_out = None
        super().__init__(*args, directory=str(ROOT / 'web/static'), **kwargs)

    def log_message(self, fmt, *args):
        # Do not log reasons, source, cookies, keys or request query strings.
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'same-origin')
        self.send_header('X-Frame-Options', 'DENY')
        if self.cookie_out:
            self.send_header('Set-Cookie', self.cookie_out)
        super().end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def identity(self):
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get('Cookie', ''))
            token = cookies.get('pysteps_session')
            token = token.value if token else ''
        except Exception:
            token = ''
        if not re.fullmatch(r'[a-f0-9]{64}', token):
            token = secrets.token_hex(32)
            secure = '; Secure' if self.app.settings.get('PUBLIC_ORIGIN', '').startswith('https://') else ''
            self.cookie_out = f'pysteps_session={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=31536000{secure}'
        return sha256(token.encode()).hexdigest()

    def valid_host(self):
        try:
            host = self.headers.get('Host', '')
            public = self.app.settings.get('PUBLIC_ORIGIN', '')
            if public and host == urlsplit(public).netloc:
                return True
            parsed = urlsplit('http://' + host)
            return parsed.hostname in ['127.0.0.1', 'localhost', '::1'] and parsed.port == self.server.server_port
        except ValueError:
            return False

    def do_GET(self):
        self.cookie_out = None
        if not self.valid_host():
            return self.send_json({'error': '访问地址未配置，请设置PUBLIC_ORIGIN。'}, 403)
        path = urlsplit(self.path).path
        if path == '/api/state':
            revision, state = self.app.store.get(self.identity())
            return self.send_json(dict(revision=revision, state=state, summary=self.app.engine.summary(state)))
        if path == '/api/diagnose':
            return self.send_json(dict(configured=self.app.ai_enabled()))
        if path.startswith('/api/'):
            return self.send_json({'error': '接口不存在'}, 404)
        normalized = unquote(path)
        if any(part.startswith('.') or part == '..' for part in normalized.split('/') if part):
            return self.send_json({'error': '文件不存在'}, 404)
        candidate = Path(self.translate_path(path)).resolve()
        public = (ROOT / 'web/static').resolve()
        if not candidate.is_relative_to(public) or (candidate.is_dir() and path != '/'):
            return self.send_json({'error': '文件不存在'}, 404)
        return super().do_GET()

    def do_HEAD(self):
        if not self.valid_host():
            self.send_response(403); self.end_headers(); return
        path = Path(self.translate_path(self.path)).resolve()
        if not path.is_relative_to((ROOT / 'web/static').resolve()) or any(x.startswith('.') for x in urlsplit(self.path).path.split('/') if x):
            self.send_response(404); self.end_headers(); return
        return super().do_HEAD()

    def do_POST(self):
        self.cookie_out = None
        try:
            public = self.app.settings.get('PUBLIC_ORIGIN') or 'http://' + self.headers.get('Host', '')
            if not self.valid_host() or self.headers.get('Origin') != public:
                return self.send_json({'error': '请求来源不匹配'}, 403)
            if not self.headers.get('Content-Type', '').startswith('application/json'):
                return self.send_json({'error': '需要JSON请求'}, 415)
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > 10_000_000:
                return self.send_json({'error': '请求为空或超过10 MB'}, 413)
            self.connection.settimeout(20)
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError('请求不完整')
            body = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('非有限数字')))
            if not isinstance(body, dict):
                raise ValueError('请求格式不正确')
            engine, path = self.app.engine, urlsplit(self.path).path
            if path == '/api/state':
                revision = body.get('revision')
                if type(revision) is not int or revision < 0:
                    raise ValueError('版本号不正确')
                state = engine.validate_state(body.get('state'))
                new = self.app.store.save(self.identity(), revision, state)
                return self.send_json(dict(revision=new, summary=engine.summary(state)))
            if path == '/api/import':
                state = engine.validate_state(body.get('state'), importing=True)
                return self.send_json(dict(state=state))
            if path == '/api/recommend':
                state = engine.validate_state(body.get('state'))
                return self.send_json(dict(questions=engine.recommend(body.get('question_id'), body.get('diagnosis'), state)))
            if path == '/api/grade':
                return self.send_json(engine.grade(body.get('question_id'), body.get('choice')))
            if path == '/api/agent':
                if not self.app.ai_enabled():
                    return self.send_json({'error': 'PiPo 需要服务端配置 GLM-4.7 和团队口令。 / Configure GLM-4.7 and team access code first.'}, 503)
                if not self.app.authorize_ai(self.headers.get('X-Team-Code', '')[:1000]):
                    return self.send_json({'error': '团队AI口令不正确。 / Incorrect team access code.'}, 401)
                goal = text(body.get('goal'), 1000, '目标').strip()
                language = body.get('language', 'zh')
                history = body.get('history', [])
                if not goal or language not in ['zh', 'en'] or not isinstance(history, list) or len(history) > 8:
                    raise ValueError('Invalid agent input')
                for row in history:
                    if not isinstance(row, dict) or row.get('role') not in ['user', 'assistant']:
                        raise ValueError('Invalid history')
                    text(row.get('text'), 10000, '对话')
                state = engine.validate_state(body.get('state'))
                try:
                    result = run_agent(engine, state, goal, history, language, self.app.settings, self.app.allow_call)
                except Exception:
                    return self.send_json({'error': 'PiPo 本轮未完成，未执行页面操作。请检查模型、网络或额度后重试。 / PiPo could not finish; no page action was applied. Check model, network or quota and retry.'}, 502)
                return self.send_json(result)
            if path == '/api/diagnose':
                qid, choice = body.get('question_id'), body.get('choice')
                graded = engine.grade(qid, choice)
                reason = text(body.get('reason', ''), 1000, '理由')
                if graded['correct'] or not reason.strip():
                    return self.send_json(graded['feedback'])
                if not self.app.ai_enabled():
                    return self.send_json(dict(graded['feedback'], message='尚未配置GLM-4.7及团队口令，使用规则反馈。'))
                if not self.app.authorize_ai(self.headers.get('X-Team-Code', '')[:1000]):
                    return self.send_json({'error': '团队AI口令不正确。'}, 401)
                if not self.app.allow_call():
                    return self.send_json(dict(graded['feedback'], message='服务器本小时AI请求已达60次，使用规则反馈。'))
                language = body.get('language', 'zh')
                if language not in ['zh', 'en']:
                    raise ValueError('Invalid language')
                return self.send_json(analyze(engine, qid, choice, reason, self.app.settings, language=language))
            return self.send_json({'error': '接口不存在'}, 404)
        except ConflictError as error:
            self.send_json({'error': str(error)}, 409)
        except (ValueError, TypeError, KeyError, OverflowError):
            self.send_json({'error': '输入格式无效，请检查记录、选项及字段长度。'}, 400)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            return
        except Exception:
            self.send_json({'error': '服务暂时无法保存或处理请求，请保留备份后重试。'}, 500)

class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def create_server(host, port, db, settings=None):
    app = Application(db, settings)
    return Server((host, port), partial(Handler, app=app))
