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
