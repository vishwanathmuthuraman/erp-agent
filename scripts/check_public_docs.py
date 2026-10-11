"""Validate the public documentation package; does not execute the proposed application."""
from pathlib import Path
from urllib.parse import urlparse, unquote
import json, re, subprocess, sys, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
raw = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '--cached', '--others', '--exclude-standard', '-z'])
paths = sorted({ROOT / p for p in raw.decode().split('\0') if p and (ROOT / p).is_file()})
counts = {'json_files': 0, 'relative_links': 0, 'svg_files': 0}
errors = []
for path in paths:
    if path.suffix == '.json':
        try: json.loads(path.read_text()); counts['json_files'] += 1
        except Exception as exc: errors.append(f'{path.relative_to(ROOT)}: {exc}')
    if path.suffix == '.md':
        content = path.read_text()
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', content):
            target = target.strip().split(' "')[0].strip('<>')
            parsed = urlparse(target)
            if parsed.scheme or not parsed.path or target.startswith('//'): continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(ROOT) or not destination.exists():
                errors.append(f'{path.relative_to(ROOT)}: missing or external local target {target}')
            counts['relative_links'] += 1
    if path.suffix == '.svg':
        try:
            tree = ET.fromstring(path.read_text())
            assert tree.tag.endswith('svg')
            for node in tree.iter():
                assert not node.tag.endswith('script')
                for key, value in node.attrib.items():
                    assert not key.lower().startswith('on')
                    if key.endswith('href'): assert not value.startswith(('http:', 'https:', 'file:'))
            counts['svg_files'] += 1
        except Exception as exc: errors.append(f'{path.relative_to(ROOT)}: unsafe or invalid SVG {exc}')
if errors:
    print('\n'.join(errors), file=sys.stderr); raise SystemExit(1)
print(json.dumps({'status': 'passed', 'check': 'public_documentation_integrity', **counts,
                  'application_executed': False, 'benchmark_executed': False}, indent=2))
