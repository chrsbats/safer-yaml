# safer-yaml

A tiny wrapper around PyYAML and yamlcore that provides a consistent, JSON-like API for YAML 1.2.

Why
- Consistent API: mirrors Python’s json module: load, loads, dump, dumps.
- YAML 1.2 semantics: avoids the classic “Norway problem” and treats on/off/yes/no as plain strings unless explicitly boolean.
- Simple file/stream handling: accepts path-like objects and text streams, with UTF-8 file I/O by default.
- Minimal quoting and stable ordering: outputs human-friendly YAML with minimal necessary quotes and preserves insertion order.

Install
```bash
pip install safer-yaml
```

Quick start
```python
from safer_yaml import load, loads, dump, dumps

# YAML 1.2 semantics (not YAML 1.1)
assert loads("no\n") == "no"        # not False
assert loads("on\n") == "on"        # not True

# Dump to a string
s = dumps({"k": "no"})
print(s)  # k: no
```

Dump and load using a string filename
```python
from safer_yaml import load, dump

dump({"a": "1:2", "b": "a: b"}, "myfile.yaml")
data = load("myfile.yaml")
assert data == {"a": "1:2", "b": "a: b"}
```

Use pathlib.Path too
```python
from pathlib import Path
from safer_yaml import load, dump

p = Path("data.yaml")
dump({"a": "1:2", "b": "a: b"}, p)
data = load(p)
assert data == {"a": "1:2", "b": "a: b"}
```

Work with text streams
```python
import io
from safer_yaml import dump

buf = io.StringIO()
dump({"outer": {"inner": "v"}}, buf)
print(buf.getvalue())
```

Control formatting (width and indent)
```python
from safer_yaml import dumps
from safer_yaml.safer_yaml import DEFAULT_WIDTH, DEFAULT_INDENT

# Use defaults (no wrapping, indent=4)
print(dumps({"k": ["a", "b", "c"]}))

# Set your own
yaml_text = dumps({"nested": {"x": 1}}, width=80, indent=2)
print(yaml_text)
```

API by example
- loads
```python
loads("k: v\n")            # -> {"k": "v"}
```

- load
```python
load("config.yaml")        # path-like (opened UTF-8)
```

- dumps
```python
dumps({"k": "v"})          # -> "k: v\n"
dumps({"k": "v"}, width=80, indent=2)
```

- dump
```python
dump({"k": "v"}, "out.yaml")
with open("out.yaml", "r", encoding="utf-8") as f:
    assert f.read().strip() == "k: v"
```

Defaults and constants
- DEFAULT_WIDTH = 1_000_000 (effectively disables wrapping)
- DEFAULT_INDENT = 4

If you need the constants:
```python
from safer_yaml.safer_yaml import DEFAULT_WIDTH, DEFAULT_INDENT
```

Behavior and notes
- YAML 1.2 booleans: true/false are booleans; yes/no/on/off are strings by default.
- Minimal quoting: values are quoted only when required (e.g., "a: b", "#tag").
- Insertion order is preserved; keys are not sorted (sort_keys=False).
- Paths are handled cross-platform using os.fspath and PathLike.
- Uses yamlcore’s CCoreLoader/CCoreDumper for correctness and performance with YAML 1.2.

Compatibility
- Python: 3.8+
- Platforms: cross-platform (Windows, macOS, Linux)

License
MIT — see LICENSE.

Links
- PyPI: https://pypi.org/project/safer-yaml/ (planned)
- Source: https://github.com/chrsbats/safer-yaml
