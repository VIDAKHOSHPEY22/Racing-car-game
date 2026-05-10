import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler


adres = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
veri = pd.read_csv(adres, sep=";")

print("Soru 1 - Ilk 5 satir")
print(veri.head())
print()

print("Soru 1 - Ornek ve ozellik sayisi")
print(f"Ornek sayisi: {veri.shape[0]}")
print(f"Ozellik sayisi: {veri.shape[1]}")
print()

print("Soru 2 - Ozet istatistikler")
print(veri.describe())
print()

print("Soru 2 - Eksik degerler")
print(veri.isnull().sum())
print()

veri.hist(figsize=(16, 12), bins=20)
plt.tight_layout()
plt.savefig("histogramlar.png", dpi=150)
plt.close()

print("Soru 2 - Histogramlar kaydedildi: histogramlar.png")
print()


def kalite_etiketi(puan):
    if 3 <= puan <= 5:
        return "low"
    if puan == 6:
        return "medium"
    return "high"


veri["quality_label"] = veri["quality"].apply(kalite_etiketi)
veri["quality_label"] = veri["quality_label"].astype("category")

print("Soru 3 - quality_label sinif dagilimi")
print(veri["quality_label"].value_counts())
print()

x = veri.drop(["quality", "quality_label"], axis=1)
y = veri["quality_label"].cat.codes
etiketler = list(veri["quality_label"].cat.categories)

print("Soru 4 - Kodlanmis sinif dagilimi")
print(y.value_counts().sort_index())
print()
print("Soru 4 - Etiket karsiliklari")
for i, ad in enumerate(etiketler):
    print(f"{i}: {ad}")
print()

x_egitim, x_test, y_egitim, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42, stratify=y
)

print("Soru 5 - Train test split tamamlandi")
print(f"Egitim veri boyutu: {x_egitim.shape}")
print(f"Test veri boyutu: {x_test.shape}")
print()

olcek = StandardScaler()
x_egitim_olcekli = olcek.fit_transform(x_egitim)
x_test_olcekli = olcek.transform(x_test)

print("Soru 6 - StandardScaler uygulandi")
print(f"Olceklenmis egitim veri boyutu: {x_egitim_olcekli.shape}")
print(f"Olceklenmis test veri boyutu: {x_test_olcekli.shape}")
print()

pca = PCA(n_components=2)
x_egitim_pca = pca.fit_transform(x_egitim_olcekli)
x_test_pca = pca.transform(x_test_olcekli)

print("Soru 7 - PCA aciklanan varyans orani")
print(pca.explained_variance_ratio_)
print()

pca_df = pd.DataFrame(x_egitim_pca, columns=["bilesen1", "bilesen2"])
pca_df["sinif"] = y_egitim.map(dict(enumerate(etiketler)))

plt.figure(figsize=(10, 7))
sns.scatterplot(data=pca_df, x="bilesen1", y="bilesen2", hue="sinif")
plt.tight_layout()
plt.savefig("pca_dagilim.png", dpi=150)
plt.close()

print("Soru 7 - PCA grafigi kaydedildi: pca_dagilim.png")
print()

modeller = {
    "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
    "KNN": KNeighborsClassifier(n_neighbors=5),
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
}

sonuclar = {}

print("Soru 8 ve Soru 9 - Model sonuclari")
for ad, model in modeller.items():
    model.fit(x_egitim_pca, y_egitim)
    tahmin = model.predict(x_test_pca)
    skor = accuracy_score(y_test, tahmin)
    sonuclar[ad] = skor

    print(f"Model: {ad}")
    print(f"Accuracy: {skor:.4f}")
    print("Confusion matrix")
    print(confusion_matrix(y_test, tahmin))
    print("Classification report")
    print(classification_report(y_test, tahmin, target_names=etiketler))
    print("-" * 60)

en_iyi = max(sonuclar, key=sonuclar.get)

print("Soru 8 - En iyi model")
print(f"{en_iyi} -> {sonuclar[en_iyi]:.4f}")
print()
print("Dosyalar kaydedildi: histogramlar.png, pca_dagilim.png")