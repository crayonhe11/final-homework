"""Create a source-free reconstruction kit with normative data and external assets."""
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
CONTENT=['data/concepts.json','data/lessons.json','data/questions.json','data/coding_tasks.json','web/src/en.json']

def main():
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    spec=(ROOT/'SPEC.md').read_text(encoding='utf-8')
    for name in CONTENT:
        block=re.search(r'^### '+re.escape(name)+r'\n\n```json\n(.*?)\n```',spec,re.M|re.S)
        if not block or json.loads(block.group(1))!=json.loads((ROOT/name).read_text(encoding='utf-8')):
            raise ValueError('Specification content differs from '+name)
    files=[(ROOT/'SPEC.md','SPEC.md'),(ROOT/'README.md','README.md'),
           (ROOT/'scripts/verify_rebuild.py','verify_rebuild.py')]
    for folder in ['web/public/pyodide','licenses']:
        files.extend((p,p.relative_to(ROOT).as_posix()) for p in (ROOT/folder).rglob('*') if p.is_file() and not p.is_symlink())
    for name in ['ai-character.png','favicon.svg']:
        path=ROOT/'web/public'/name
        files.append((path,path.relative_to(ROOT).as_posix()))
    manifest={name:hashlib.sha256(path.read_bytes()).hexdigest() for path,name in files}
    instructions="""# 独立重建 / Independent reconstruction

中文：在空目录中让另一个 AI 阅读 SPEC.md，从规范附录恢复 JSON，使用已提供的外部运行时/图片/许可证，自行实现相同功能。不要提供原项目源码。README 是给普通使用者看的操作目标；verify_rebuild.py 是独立黑盒契约，不包含原实现。用临时数据库、禁用真实模型密钥启动重建站点，再运行 python verify_rebuild.py --url http://127.0.0.1:PORT。按 SPEC 中 AC01–AC14 做页面和模拟模型验收。记录 AI 输入、生成版本、结果与偏差。这个包不证明独立重建已完成。

English: Give an independent AI this kit in an empty directory. Restore the normative JSON appendix and implement the specified functionality using the external runtime/assets/licences. Do not supply original implementation sources. README describes ordinary user operation; verify_rebuild.py contains implementation-independent HTTP assertions. Start a fresh temporary database with real model keys disabled and run python verify_rebuild.py --url http://127.0.0.1:PORT. Complete SPEC AC01–AC14 and simulated-provider checks. Record prompts, generated revision, outcomes and discrepancies. This kit does not itself prove a successful independent reconstruction.
"""
    target=ROOT/'dist/group8_rebuild_inputs.zip'
    target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        for path,name in sorted(files,key=lambda x:x[1]):archive.write(path,name)
        archive.writestr('SHA256_MANIFEST.json',json.dumps(manifest,indent=2))
        archive.writestr('REBUILD_TASK.md',instructions)
    with zipfile.ZipFile(target) as archive:
        if archive.testzip():raise ValueError('Invalid reconstruction ZIP')
    print(target)
    print('Validated five embedded data files; no original business/UI/Worker implementation included.')
    return 0

if __name__=='__main__':raise SystemExit(main())
