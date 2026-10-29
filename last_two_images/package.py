"""Package the Kaggle input without duplicate ZIP entries or Python caches."""
from pathlib import Path
import json
import shutil
import zipfile

here = Path(__file__).resolve().parent
package = here / 'kaggle'
shutil.copyfile(here / 'README.md', package / 'README.md')
with zipfile.ZipFile(here / 'last_two_kaggle.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(package.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            archive.write(path, path.relative_to(package).as_posix())
    for name in ('review.html', 'validation.json'):
        archive.write(here / name, name)
    for path in sorted((here / 'review').glob('*.json')):
        archive.write(path, 'review/' + path.name)
with zipfile.ZipFile(here / 'last_two_kaggle.zip') as archive:
    assert archive.testzip() is None
    names = archive.namelist()
    assert len(names) == len(set(names))
    assert 'annotations/18592.json' not in names
    assert 'annotations/model_reviews/55431.json' not in names
    assert 'annotations/source_mismatches/18592.json' in names
    assert len(json.loads(archive.read('inscription_content.json'))) == 9
print('Verified:', here / 'last_two_kaggle.zip')
