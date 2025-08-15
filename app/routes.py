from flask import Blueprint, render_template, request, redirect, url_for, session
from app.utils.file_manager import FileManager
from app.utils import ia_tools
import numpy as np
import pandas as pd

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def home():
    FileManager.init_session(session)
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            FileManager.add_file(session, file)
            session['uploadSuccess'] = 'True'
        else:
            session['uploadSuccess'] = 'False'
    files = FileManager.get_files(session)
    return render_template('home/index.html', files=files)


@main.route('/delete/<file_id>', methods=['POST'])
def delete_file(file_id):
    FileManager.delete_file(session, file_id)
    return redirect(url_for('main.home'))

@main.route('/scatter', methods=['POST'])
def scatter():
    from flask import jsonify
    import io, base64
    import matplotlib.pyplot as plt

    file_id = request.form.get("file_id")
    files = FileManager.get_files(session)
    file_info = next((f for f in files if f["id"] == file_id), None)

    if not file_info:
        return jsonify({"error": "Archivo no encontrado"}), 400

    filepath = file_info["path"]
    df = pd.read_csv(filepath) if filepath.endswith(".csv") else pd.read_excel(filepath)

    x_col = request.form.get("x_column")
    y_col = request.form.get("y_column")

    if x_col not in df.columns or y_col not in df.columns:
        return jsonify({"error": "Columnas inválidas"}), 400

    plt.figure(figsize=(6,4))
    plt.scatter(df[x_col], df[y_col], c='blue', alpha=0.6)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f"Diagrama de dispersión {x_col} vs {y_col}")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    scatter_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    return jsonify({"scatter_plot": scatter_base64})

@main.route('/graphics', methods=['GET', 'POST'])
def graphics():
    files = FileManager.get_files(session)
    resultados = []

    if 'graphics_results' not in session:
        session['graphics_results'] = {}

    for f in files:
        file_id = f['id']

        # Revisar si ya tenemos resultados cacheados
        if file_id in session['graphics_results']:
            resultados.append(session['graphics_results'][file_id])
            continue

        # Leer archivo
        try:
            if f['name'].endswith('.csv'):
                df = pd.read_csv(f['path'])
            elif f['name'].endswith(('.xls', '.xlsx')):
                df = pd.read_excel(f['path'])
            else:
                continue
        except Exception as e:
            print(f"Error leyendo {f['name']}: {e}")
            continue

        # Columnas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:10]  # solo primeras 10 columnas
        if len(numeric_cols) == 0:
            print(f"No hay columnas numéricas en {f['name']}")
            continue

        df_num = df[numeric_cols].dropna()

        # Muestreo de filas si dataset es grande
        df_sample = df_num.sample(min(len(df_num), 1000), random_state=42)

        # Ejecutar análisis
        try:
            kmeans_labels = ia_tools.clustering_kmeans(df_sample)
        except Exception as e:
            print(f"KMeans error en {f['name']}: {e}")
            kmeans_labels = []

        try:
            dbscan_labels = ia_tools.clustering_dbscan(df_sample)
        except Exception as e:
            print(f"DBSCAN error en {f['name']}: {e}")
            dbscan_labels = []

        try:
            zscore_outliers = ia_tools.detect_outliers_zscore(df_sample)
        except Exception as e:
            print(f"Z-score error en {f['name']}: {e}")
            zscore_outliers = []

        try:
            iqr_outliers = ia_tools.detect_outliers_iqr(df_sample)
        except Exception as e:
            print(f"IQR error en {f['name']}: {e}")
            iqr_outliers = []

        try:
            iso_outliers = ia_tools.detect_outliers_isolation_forest(df_sample)
        except Exception as e:
            print(f"Isolation Forest error en {f['name']}: {e}")
            iso_outliers = []

        try:
            heatmap_img = ia_tools.plot_correlation_matrix(df_sample)
        except Exception as e:
            print(f"Heatmap error en {f['name']}: {e}")
            heatmap_img = None
            
        try:
            boxplot_img = ia_tools.plot_boxplot(df)
        except Exception as e:
            print(f"Boxplot error en {f['name']}: {e}")
            boxplot_img = None

        resultado = {
            "file_id": file_id,
            "filename": f['name'],
            "analisis": {
                "numeric_columns": numeric_cols.tolist()
            },
            "clustering_kmeans_labels": kmeans_labels,
            "clustering_dbscan_labels": dbscan_labels,
            "status_zscore": zscore_outliers,
            "status_iqr": iqr_outliers,
            "status_iso": iso_outliers,
            "plot_img": heatmap_img,
            "boxplot_img": boxplot_img
        }

        resultados.append(resultado)
        session['graphics_results'][file_id] = resultado  # cachear

    session.modified = True
    return render_template('graphics/index.html', resultados=resultados)