import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from analysis.signals import autocorrelation, fractal_indices, ratio, resample, spectrum, time_axis
from analysis.intervals import HISTOGRAM_EDGES, REFERENCE_MODE_MS, IntervalSeries, time_metrics

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
    raw_data = pd.DataFrame(series.values)
    print("Среднее значение: ", np.round(metrics.mean, 2))
    print("Среднеквадратическое отклонение SDNN: ", np.round(metrics.sdnn, 2))
    print("Коэффициент вариации: ", np.round(metrics.variation_percent, 2), "%")
    print("среднеквадратическая разностная характеристика RMSSD: ", np.round(metrics.rmssd, 2))
    plt.figure(figsize=(20, 8))
    plt.hist(series.values, bins=HISTOGRAM_EDGES)
    plt.savefig("output/hrv_hist_" + f[-14:-4] + ".png")
    plt.close()
    print("Амплитуда моды: ", np.round(metrics.mode_amplitude, 4))
    print("Мода: ", REFERENCE_MODE_MS)
    print("Вариационный размах: ", metrics.occupied_range)
    print("Индекс напряжения регуляторных систем: ", np.round(metrics.stress, 2))

    fig, ax = plt.subplots(1, figsize=(60, 30))
    acf = autocorrelation(series.values)
    ax.stem(range(acf.size), acf)
    plt.savefig("output/hrv_acf_" + f[-14:-4] + ".png")
    plt.close()
    print("Автокорреляция, сдвиг 1: ", np.round(acf[1], 2))

    x_data = raw_data.iloc[:299]
    y_data = raw_data.iloc[1:300]

    plt.figure(figsize=(20, 8))
    plt.xlim(400, 1300)
    plt.ylim(400, 1300)
    plt.scatter(x_data, y_data)

    x1 = range(400, 1300, 1)
    y1 = range(400, 1300, 1)
    plt.plot(x1, y1)

    ax = plt.gca()

    center = np.array([975, 975])

    ellipse = Ellipse(
        xy=center, width=300, height=110, edgecolor="r", fc="None", ls="solid", lw=3, angle=45
    )

    ax.add_patch(ellipse)
    plt.savefig("output/hrv_scatter_" + f[-14:-4] + ".png")
    plt.close()

    y = raw_data[0]

    x = time_axis(series.values)

    plt.figure(figsize=(20, 8))
    plt.scatter(x, y)
    plt.plot(x, y)
    plt.title("Кардиоритмограмма")
    plt.savefig("output/hrv_rhythmogram_" + f[-14:-4] + ".png")
    plt.close()

    xnew, ynew = resample(x, series.values)

    plt.figure(figsize=(20, 8))
    plt.plot(xnew, ynew)
    plt.scatter(xnew, ynew)
    plt.title("Пульсограмма")
    plt.savefig("output/hrv_pulsogram_" + f[-14:-4] + ".png")
    plt.close()

    bands = spectrum(series.values)
    plt.figure(figsize=(20, 8))
    plt.plot(bands.frequencies, bands.plot_power)
    plt.savefig("output/hrv_spectrum_" + f[-14:-4] + ".png")
    plt.close()

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
