from docstr_md.python import PySoup, compile_md
from docstr_md.src_href import Github

import os

src_href = Github('https://github.com/dsbowen/dash-fcast/blob/master')

path = 'dash_fcast/table.py'
soup = PySoup(path=path, parser='sklearn', src_href=src_href)
table_cls = soup.objects[-1]
table_cls.rm_methods('to_plotly_json')
compile_md(soup, compiler='sklearn', outfile='docs_md/table.md')

dist_path = 'dash_fcast/distributions'
outfile_path = 'docs_md/dist'

path = os.path.join(dist_path, '__init__.py')
soup = PySoup(path=path, parser='sklearn', src_href=src_href)
outfile = os.path.join(outfile_path, 'utils.md')
compile_md(soup, compiler='sklearn', outfile=outfile)

dist_files = ('moments', 'table')

for f in dist_files:
    path = os.path.join(dist_path, f+'.py')
    soup = PySoup(path=path, parser='sklearn', src_href=src_href)
    soup.import_path = dist_path
    for obj in soup.objects:
        try:
            obj.rm_methods('to_plotly_json')
        except:
            pass
    outfile = os.path.join(outfile_path, f+'.md')
    compile_md(soup, compiler='sklearn', outfile=outfile)