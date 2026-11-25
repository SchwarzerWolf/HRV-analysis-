from pathlib import Path
from shutil import copytree
from subprocess import run
from sys import executable

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "hrv" / "data"


def test_course_example(tmp_path: Path) -> None:
    copytree(DATA, tmp_path / "hrv" / "data")
    output = tmp_path / "output"
    output.mkdir()
    result = run(
        [executable, str(PROJECT / "hrv" / "hrv_analysis.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout.splitlines() == (DATA / "expected_output.txt").read_text().splitlines()
    reference = PROJECT / "tests" / "fixtures" / "expected_summary.csv"
    assert (output / "hrv_summary.csv").read_text() == reference.read_text()
    plot_types = ("hist", "acf", "scatter", "rhythmogram", "pulsogram", "spectrum")
    expected_names = {
        f"hrv_{plot}_{subject.stem}.png"
        for subject in DATA.glob("subject_*.csv")
        for plot in plot_types
    }
    assert {path.name for path in output.glob("*.png")} == expected_names
    for name in expected_names:
        with (output / name).open("rb") as stream:
            assert stream.read(8) == b"\x89PNG\r\n\x1a\n"


def test_invalid_subject_does_not_stop_the_batch(tmp_path: Path) -> None:
    data = tmp_path / "hrv" / "data"
    data.mkdir(parents=True)
    (data / "subject_01.csv").write_text("200\n250\n")
    (data / "subject_02.csv").write_text("invalid\n")
    (data / "subject_03.csv").write_text("800\n850\n900\n")
    result = run(
        [executable, str(PROJECT / "hrv" / "hrv_analysis.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "После фильтрации нужно хотя бы два интервала" in result.stdout
    assert "Не удалось прочитать файл ./hrv/data/subject_02.csv" in result.stdout
    summary = (tmp_path / "output" / "hrv_summary.csv").read_text().splitlines()
    assert len(summary) == 2
    assert summary[1].startswith("subject_03,850.0,50.0,50.0,")
