import json

import filewatch


def make_files(folder):
    (folder / "a.txt").write_text("hello")
    (folder / "b.txt").write_text("world")
    sub = folder / "sub"
    sub.mkdir()
    (sub / "c.txt").write_text("nested")


def test_hash_is_deterministic(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello")
    assert filewatch.hash_file(f) == filewatch.hash_file(f)


def test_snapshot_includes_subfolders(tmp_path):
    make_files(tmp_path)
    snap = filewatch.build_snapshot(tmp_path)
    assert set(snap) == {"a.txt", "b.txt", "sub/c.txt"}


def test_no_changes_on_unchanged_folder(tmp_path):
    make_files(tmp_path)
    snap = filewatch.build_snapshot(tmp_path)
    assert filewatch.compare(snap, filewatch.build_snapshot(tmp_path)) == ([], [], [])


def test_detects_added_file(tmp_path):
    make_files(tmp_path)
    old = filewatch.build_snapshot(tmp_path)
    (tmp_path / "new.txt").write_text("new")
    added, modified, deleted = filewatch.compare(old, filewatch.build_snapshot(tmp_path))
    assert (added, modified, deleted) == (["new.txt"], [], [])


def test_detects_modified_file(tmp_path):
    make_files(tmp_path)
    old = filewatch.build_snapshot(tmp_path)
    (tmp_path / "a.txt").write_text("hellO")
    added, modified, deleted = filewatch.compare(old, filewatch.build_snapshot(tmp_path))
    assert (added, modified, deleted) == ([], ["a.txt"], [])


def test_detects_deleted_file(tmp_path):
    make_files(tmp_path)
    old = filewatch.build_snapshot(tmp_path)
    (tmp_path / "sub" / "c.txt").unlink()
    added, modified, deleted = filewatch.compare(old, filewatch.build_snapshot(tmp_path))
    assert (added, modified, deleted) == ([], [], ["sub/c.txt"])


def test_baseline_roundtrip(tmp_path):
    make_files(tmp_path)
    snap = filewatch.build_snapshot(tmp_path)
    baseline = tmp_path.parent / "baseline_test.json"
    filewatch.save_baseline(snap, baseline)
    assert filewatch.load_baseline(baseline) == snap
    assert json.loads(baseline.read_text()) == snap