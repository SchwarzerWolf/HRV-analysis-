from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis.intervals import REFERENCE_MODE_MS, IntervalSeries, time_metrics
from analysis.plots import save_plots
from analysis.signals import autocorrelation, fractal_indices, ratio, spectrum

files = [
    "./hrv/data/subject_01.csv",
    "./hrv/data/subject_02.csv",
    "./hrv/data/subject_03.csv",
    "./hrv/data/subject_04.csv",
]

names = []
means = []
sdnns = []
rmssds = []
stress = []
lfhf = []
hurst = []
states = []

plt.switch_backend("Agg")

for f in files:
    print("=====", f, "=====")
    try:
        raw = pd.read_csv(f, header=None)[0]
    except:
        print("Не удалось прочитать файл", f)
        continue
    print("Прочитано интервалов: ", raw.size)

    series = IntervalSeries.from_raw(raw.to_numpy(dtype=float))
    print("Удалено выбросов: ", series.outliers)
    print("Удалено экстрасистол: ", series.abrupt_changes)
    metrics = time_metrics(series.values)
    print("Среднее значение: ", np.round(metrics.mean, 2))
    print("Среднеквадратическое отклонение SDNN: ", np.round(metrics.sdnn, 2))
    print("Коэффициент вариации: ", np.round(metrics.variation_percent, 2), "%")
    print("среднеквадратическая разностная характеристика RMSSD: ", np.round(metrics.rmssd, 2))
    print("Амплитуда моды: ", np.round(metrics.mode_amplitude, 4))
    print("Мода: ", REFERENCE_MODE_MS)
    print("Вариационный размах: ", metrics.occupied_range)
    print("Индекс напряжения регуляторных систем: ", np.round(metrics.stress, 2))

    acf = autocorrelation(series.values)
    print("Автокорреляция, сдвиг 1: ", np.round(acf[1], 2))

    bands = spectrum(series.values)
    save_plots(Path("output"), Path(f).stem, series.values, acf, bands)
    print(np.round(bands.total, 2))

    print("Высокочастотный диапазон: ", np.round(ratio(bands.hf, bands.total), 2))
    print("Низкочастотный диапазон: ", np.round(ratio(bands.lf, bands.total), 2))
    print("Очень низкочастотный диапазон: ", np.round(ratio(bands.vlf, bands.total), 2))
    print("Ультра низкочастотный компонент: ", np.round(ratio(bands.ulf, bands.total), 2))

    print("Индекс централизации: ", np.round(ratio(bands.vlf + bands.lf, bands.hf), 2))
    print("Индекс вагосимпатического взаимодействия: ", np.round(ratio(bands.lf, bands.hf), 2))
    print("Индекс активации подкорковых нервных центров: ", np.round(ratio(bands.lf, bands.vlf), 2))

    herstIndex, fluctuation = fractal_indices(series.values)
    print("Индекс Херста: ", np.round(herstIndex, 2))


    print("Показатель флуктуации a", np.round(fluctuation, 2))

    state = metrics.state
    print("Состояние: ", state)

    names.append(f[-14:-4])
    means.append(np.round(metrics.mean, 2))
    sdnns.append(np.round(metrics.sdnn, 2))
    rmssds.append(np.round(metrics.rmssd, 2))
    stress.append(np.round(metrics.stress, 2))
    lfhf.append(np.round(ratio(bands.lf, bands.hf), 2))
    hurst.append(np.round(herstIndex, 2))
    states.append(state)

summary = pd.DataFrame(
    {
        "subject": names,
        "mean": means,
        "sdnn": sdnns,
        "rmssd": rmssds,
        "stress_index": stress,
        "lf_hf": lfhf,
        "hurst": hurst,
        "state": states,
    }
)
summary.to_csv("output/hrv_summary.csv", index=False)
print("=====  Сводка  =====")
print(summary.to_string())
