from flask import Blueprint, render_template, request, redirect, url_for, session
from app.utils.file_manager import FileManager
from app.utils import ia_tools
import pandas as pd

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def home():
    FileManager.init_session(session)
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            FileManager.add_file(session, file)
    files = FileManager.get_files(session)
    return render_template('home/index.html', files=files)

@main.route('/delete/<file_id>', methods=['POST'])
def delete_file(file_id):
    FileManager.delete_file(session, file_id)
    return redirect(url_for('main.home'))

@main.route('/graphics', methods=['GET', 'POST'])
def graphics():
    plot_img = None
    clustering_kmeans_labels = []
    clustering_dbscan_labels = []
    outliers_zscore = []
    outliers_iqr = []
    outliers_iso = []
    status_zscore = []
    status_iqr = []
    status_iso = []

    if request.method == 'POST':
        uploaded_file = request.files.get('datafile')
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            numeric_df = df.select_dtypes(include='number')

            # Clustering
            clustering_kmeans_labels = ia_tools.clustering_kmeans(numeric_df, n_clusters=3)
            clustering_dbscan_labels = ia_tools.clustering_dbscan(numeric_df)

            # Outliers detectados
            outliers_zscore = ia_tools.detect_outliers_zscore(numeric_df)
            outliers_iqr = ia_tools.detect_outliers_iqr(numeric_df)
            outliers_iso = ia_tools.detect_outliers_isolation_forest(numeric_df)

            # Convertir booleanos a "Normal" / "Outlier"
            status_zscore = ["Outlier" if val else "Normal" for val in outliers_zscore]
            status_iqr = ["Outlier" if val else "Normal" for val in outliers_iqr]
            status_iso = ["Outlier" if val else "Normal" for val in outliers_iso]

            # Heatmap correlación
            plot_img = ia_tools.plot_correlation_matrix(numeric_df)

    return render_template('graphics/index.html',
                           plot_img=plot_img,
                           clustering_kmeans_labels=clustering_kmeans_labels,
                           clustering_dbscan_labels=clustering_dbscan_labels,
                           status_zscore=status_zscore,
                           status_iqr=status_iqr,
                           status_iso=status_iso)
