import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def purpleair(tmp_path, monkeypatch):
    # purpleair reads .env from the working directory on import
    (tmp_path / '.env').write_text('READ_KEY=test-read\nWRITE_KEY=test-write\n\n')
    monkeypatch.chdir(tmp_path)
    sys.modules.pop('purpleair', None)
    import purpleair
    return purpleair
