import datetime as dt
import gzip
import json
import os
import pathlib
import re
import shutil
import tempfile
import unicodedata
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent
def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))

def build(src, dest):
    buckets = {}
    for name, source, prefix in [('film','movies','movie'), ('serie','tv','tv_series')]:
        extra = {x['tmdb_id']: x for x in json.loads((src / (source+'.json')).read_text())['items']}
        count = 0
        with (dest / (name+'.json')).open('w') as out:
            out.write('[')
            def emit(row):
                nonlocal count
                out.write((',' if count else '') + compact(row))
                count += 1
                title = row.get('title') or row.get('original_title') or row.get('original_name')
                groups = {}
                for alias in {title,row.get('original_title'),row.get('original_name')} - {None,''}:
                    norm = ''.join(c for c in unicodedata.normalize('NFKD',alias.lower()) if not unicodedata.combining(c))
                    norm = ' '.join(re.findall(r'[^\W_]+',norm))
                    for key in {norm,re.sub(r"^(the|a|an|il|lo|la|i|gli|le|l|un|una) ", "",norm)}:
                        if key:
                            groups.setdefault(key[:2],set()).add(norm)
                for bucket, aliases in groups.items():
                    buckets.setdefault(bucket,[]).append([title,row['id'],name,row.get('year'),round(row.get('popularity') or 0,2),sorted(aliases)])
            with gzip.open(src / (prefix+'.gz'),'rt') as lines:
                for line in lines:
                    row = json.loads(line)
                    row.update(extra.pop(row['id'],{}))
                    emit(row)
            for ident,row in extra.items():
                emit(dict(row,id=ident))
            out.write(']')
        print(name,count,flush=True)
    index = dest/'indice'
    index.mkdir()
    # Group rare prefixes into a bounded number of portable files.
    grouped = {}
    for key,rows in buckets.items():
        code = sum(ord(c)*(i+1) for i,c in enumerate(key)) % 512
        grouped.setdefault(code,{})[key] = rows
    for code, data in grouped.items():
        (index/f'{code}.js').write_text('receive('+str(code)+','+compact(data).replace('<','\\u003c')+');')

def write_seasons(src,dest):
    items=json.loads((src/'tv.json').read_text())['items']
    mapping={r['tmdb_id']: sorted([[s['n'],s['episodes']] for s in r.get('seasons',[]) if (s.get('n') or 0)>0 and (s.get('episodes') or 0)>0]) for r in items}
    (dest/'stagioni.js').write_text('const seasonsById='+compact(mapping)+';')

def refresh():
    with tempfile.TemporaryDirectory() as tmp:
        src = pathlib.Path(tmp)
        for name in ['movies','tv']:
            urllib.request.urlretrieve(f'https://raw.githubusercontent.com/scageto/CasaFlix/main/data/{name}.json',src/(name+'.json'))
        for offset in range(3):
            day = dt.datetime.now(dt.timezone.utc).date()-dt.timedelta(days=offset)
            try:
                for prefix in ['movie','tv_series']:
                    urllib.request.urlretrieve(f'https://files.tmdb.org/p/exports/{prefix}_ids_{day:%m_%d_%Y}.json.gz',src/(prefix+'.gz'))
                break
            except OSError:
                if offset==2: raise
        dest=src/'site'
        dest.mkdir()
        build(src,dest)
        write_seasons(src,dest)
        shutil.copy(ROOT/'index.html',dest)
        shutil.copytree(dest,ROOT/'public',dirs_exist_ok=True)
if __name__=='__main__':
    refresh()
