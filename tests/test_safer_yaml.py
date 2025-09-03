"""
pytest-based tests for safer_yaml
"""

import re
import io

from safer_yaml import load, loads, dump, dumps


def test_no_is_string_on_loads():
    # Scalar
    assert loads("no\n") == "no"
    assert isinstance(loads("no\n"), str)

    # In a mapping
    data = loads("k: no\n")
    assert data["k"] == "no"
    assert data["k"] is not False


def test_no_roundtrip_dump_min_quotes():
    data = {"k": "no"}
    s = dumps(data)
    # Should not be quoted in YAML 1.2
    assert '"no"' not in s
    assert "'no'" not in s
    assert re.search(r"^k:\s+no\s*$", s, re.M)
    assert loads(s) == data


def test_values_with_colons_minimal_quoting_and_roundtrip():
    data = {
        "with_colon_no_space": "1:2",      # should not need quotes
        "with_colon_space": "a: b",        # must be quoted
        "url": "http://x:y",               # should not need quotes
        "plain": "value",                   # control
        "norway": "no",                     # ensure not quoted as well
    }

    s = dumps(data)

    # Ensure insertion order is preserved and quoting is minimal/required
    assert re.search(r"^with_colon_no_space:\s+1:2\s*$", s, re.M)
    assert re.search(r"^with_colon_space:\s+['\"]a: b['\"]\s*$", s, re.M)
    assert re.search(r"^url:\s+http://x:y\s*$", s, re.M)
    assert re.search(r"^plain:\s+value\s*$", s, re.M)
    assert re.search(r"^norway:\s+no\s*$", s, re.M)

    # Round-trip integrity
    assert loads(s) == data


def test_dump_and_load_file_with_string_filename(tmp_path):
    data = {
        "x": "1:2",
        "y": "a: b",
        "norway": "no",
    }
    p = tmp_path / "data.yaml"
    dump(data, str(p))
    loaded = load(str(p))
    assert loaded == data


def test_dump_and_load_file_with_pathlib_path_helper(tmp_path):
    p = tmp_path / "data_path.yaml"

    data = {"a": "1:2", "b": "a: b", "norway": "no"}
    dump(data, p)
    loaded = load(p)
    assert loaded == data


def test_on_off_yes_are_strings_on_loads():
    # YAML 1.2: "on", "off", "yes" are plain strings, not booleans
    for s in ("on", "off", "yes"):
        assert loads(s + "\n") == s
        data = loads(f"k: {s}\n")
        assert data["k"] == s
        assert isinstance(data["k"], str)


def test_values_with_hashes_minimal_quoting_and_roundtrip():
    data = {
        "with_hash_no_space": "a#b",   # should not need quotes
        "with_hash_space": "a # b",    # must be quoted (would start a comment)
        "hash_at_start": "#tag",       # must be quoted
    }
    s = dumps(data)
    assert re.search(r"^with_hash_no_space:\s+a#b\s*$", s, re.M)
    assert re.search(r"^with_hash_space:\s+['\"]a # b['\"]\s*$", s, re.M)
    assert re.search(r"^hash_at_start:\s+['\"]#tag['\"]\s*$", s, re.M)
    assert loads(s) == data


def test_dump_to_text_stream_preserves_order_and_indent():
    # When dumping to a stream, options should match file-path behavior
    data = {"outer": {"inner": "v"}, "z": 1, "a": 2}
    buf = io.StringIO()
    dump(data, buf)
    s = buf.getvalue()
    # Order should be insertion order (not sorted)
    assert s.index("outer:") < s.index("z:") < s.index("a:")
    # Indentation should be 4 spaces
    assert re.search(r"^\s{4}inner:\s+v\s*$", s, re.M)


def test_load_from_text_stream():
    s = "k: no\nlist:\n  - a\n  - b\n"
    buf = io.StringIO(s)
    data = load(buf)
    assert data == {"k": "no", "list": ["a", "b"]}


def test_dump_and_load_with_string_filename_relative(tmp_path, monkeypatch):
    # Use a relative path (exact example from the README)
    monkeypatch.chdir(tmp_path)
    data = {"a": "1:2", "b": "a: b"}
    dump(data, "myfile.yaml")
    loaded = load("myfile.yaml")
    assert loaded == data


def test_non_ascii_roundtrip_file_and_stream(tmp_path):
    # Non-ASCII characters round-trip via dumps/loads and dump/load
    data = {
        "greeting": "héllo naïve café 😀",
        "cjk": "漢字かな交じり文",
        "emoji": "🐍🚀✨",
        "accented_list": ["á", "é", "í", "ó", "ú"],
    }
    s = dumps(data)
    assert loads(s) == data

    p = tmp_path / "utf8.yaml"
    dump(data, p)
    raw = p.read_bytes()
    # Ensure the file is valid UTF-8
    decoded = raw.decode("utf-8")
    assert isinstance(decoded, str)
    loaded = load(p)
    assert loaded == data


def test_very_long_lines_no_wrap_and_required_quotes():
    # Build very long strings, including characters that force quoting
    long_plain = "x" * 10000 + "1:2" + "y" * 10000             # plain allowed (no wrap expected)
    long_colon_space = "a" * 5000 + ": " + "b" * 5000          # needs quoting due to ": "
    long_dash_space = "- " + "n" * 10000                       # needs quoting due to leading "- "

    data = {
        "plain": long_plain,
        "colon_space": long_colon_space,
        "dash_space": long_dash_space,
    }
    s = dumps(data)  # uses DEFAULT_WIDTH -> effectively no wrapping

    # No wrapping: exactly one line per entry in the mapping
    lines = s.splitlines()
    assert len(lines) == 3
    assert lines[0].startswith("plain:")
    assert lines[1].startswith("colon_space:")
    assert lines[2].startswith("dash_space:")

    # Quoting expectations: only values that require quoting should be quoted
    assert re.match(r'^plain:\s+[^\'"].*$', lines[0])
    assert re.match(r'^colon_space:\s+[\'"].*[\'"]$', lines[1])
    assert re.match(r'^dash_space:\s+[\'"].*[\'"]$', lines[2])

    # Round-trip integrity
    assert loads(s) == data
