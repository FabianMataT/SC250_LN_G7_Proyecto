from flask import Blueprint, render_template, request, redirect, url_for, session
from app.utils.file_manager import FileManager

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

@main.route('/graphics')
def about():
    return render_template('graphics/index.html')
