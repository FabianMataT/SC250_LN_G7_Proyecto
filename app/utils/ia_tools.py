import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import IsolationForest
from scipy.stats import zscore
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

def clustering_kmeans(data, n_clusters=3):
    model = KMeans(n_clusters=n_clusters, random_state=42)
    labels = model.fit_predict(data)
    return labels.tolist()

def clustering_dbscan(data, eps=0.5, min_samples=5):
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(data)
    return labels.tolist()

def detect_outliers_zscore(data, threshold=3):
    z_scores = np.abs(zscore(data, nan_policy='omit'))
    outliers = (z_scores > threshold)
    # devolver lista fila por fila: True si algún valor es outlier
    return outliers.any(axis=1).tolist()

def detect_outliers_iqr(data):
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    is_outlier = ((data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR)))
    return is_outlier.any(axis=1).tolist()

def detect_outliers_isolation_forest(data):
    model = IsolationForest(contamination=0.1, random_state=42)
    preds = model.fit_predict(data)
    # Isolation Forest da -1 para outliers, 1 para normales
    outliers = (preds == -1)
    return outliers.tolist()

def plot_correlation_matrix(df):
    corr = df.corr()
    plt.figure(figsize=(8,6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

def plot_boxplot(df, max_columns=10, max_rows=1000):
    numeric_cols = df.select_dtypes(include=[np.number]).columns[:max_columns]
    if len(numeric_cols) == 0:
        return None

    df_num = df[numeric_cols].dropna()
    df_sample = df_num.sample(min(len(df_num), max_rows), random_state=42)

    plt.figure(figsize=(8,6))
    sns.boxplot(data=df_sample, orient='h')
    plt.title("Diagrama de caja (todas las columnas numéricas)")

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64
