"""Allowlist packager: never includes local credentials or learner records."""
import argparse
from pathlib import Path
import re
import zipfile
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--group',default='N');args=parser.parse_args()
    if not re.fullmatch(r'(N|[0-9]{1,3})',args.group):parser.error('组号须为1至3位数字；暂未确定可用N')
    allowed_files=['main.py','打开网页版.html','README.md','SPEC.md','config.example.json','Dockerfile','.dockerignore','.gitignore']
    allowed_dirs=['backend','data','tests','scripts','submission','licenses','.github']
    paths=[ROOT/f for f in allowed_files]+[f for d in allowed_dirs for f in (ROOT/d).rglob('*')]
    for d in ['src','public','static']:
        paths.extend((ROOT/'web'/d).rglob('*'))
    paths.extend(ROOT/'web'/f for f in ['package.json','package-lock.json','tsconfig.json','build.mjs'])
    destination=ROOT/'dist'/f'group{args.group}_project.zip';destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(paths)):
            rel=path.relative_to(ROOT)
            if not path.is_file() or path.is_symlink() or '__pycache__' in rel.parts or path.suffix in ['.pyc','.sqlite3','.db'] or path.name.startswith('.env') or path.name in ['config.local.json','api_config.json','.DS_Store']:continue
            arc=str(Path(f'group{args.group}_project')/rel)
            if rel.as_posix()=='submission/groupN_presentation.pptx':arc=arc.replace('groupN_presentation',f'group{args.group}_presentation')
            archive.write(path,arc)
    print(destination)
    if args.group=='N':print('N为占位组号，提交前请用真实组号重新打包。')

if __name__=='__main__':main()
