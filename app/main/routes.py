import shutil
from flask import flash, render_template, redirect, request, session, url_for, abort, jsonify, current_app, send_from_directory
from app.main import bp
from app.extensions import db
from app.models import DocxFile, EduPlan, YamlDocument
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests
from functools import wraps
import os
import subprocess
from werkzeug.utils import secure_filename
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('main.index_page'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
def index_page():
    """Главная страница"""
    client_id = current_app.config['CLIENT_ID']
    return render_template('index.html', client_id=client_id)

@bp.route('/login/', methods=['POST'])
def login():
    """Вход пользователя в систему"""
    # Защита от CSRF
    cookie_token = request.cookies.get('g_csrf_token')
    if not cookie_token:
        return abort(400, 'No CSRF token in Cookie.')
    post_token = request.form.get('g_csrf_token')
    if not post_token:
        return abort(400, 'No CSRF token in post body.')
    if cookie_token != post_token:
        return abort(400, 'Failed to verify double submit cookie.')

    # Проверка токена
    token = request.form.get('credential')
    if not token:
        return abort(400, 'No ID token.')
    req = requests.Request()
    client_id = current_app.config['CLIENT_ID']
    try:
        payload = id_token.verify_oauth2_token(token, req, client_id)
    except GoogleAuthError:
        return abort(401, 'ID token verification error.')

    # Проверим что пользователь зарегистрирован
    email = payload['email']
    if email not in current_app.config['USERS']:
        return abort(403, 'User is not authorized.')

    session['user'] = {
        'email': email,
        'id': payload['sub'],
        'name': payload['name'],
    }
    return redirect(url_for('main.index_page'))

@bp.route('/logout/')
def logout():
    """Выход пользователя из системы"""
    session.pop('user', None)
    return redirect(url_for('main.index_page'))

@bp.route('/edu_plan/')
@login_required
def edu_plan_list():
    """Список учебных планов"""
    edu_plans = EduPlan.query.order_by(EduPlan.code).all()
    return render_template('edu_plan_list.html', edu_plans=edu_plans)

@bp.route('/edu_plan_load/', methods=['GET', 'POST'])
@login_required
def edu_plan_load():
    """Загрузка учебного плана"""
    if request.method == 'POST':
        plan = request.files['plan']
        EduPlan.load(plan.filename, plan.stream.read()) # type: ignore
        return redirect(url_for('main.edu_plan_list'))
    return render_template('edu_plan_load.html')

@bp.route('/edu_plan/download/<path:filename>')
@login_required
def edu_plan_download(filename):
    """Скачивание учебного плана"""
    directory = os.path.join(current_app.root_path, 'edu_plans')
    return send_from_directory(directory, filename, as_attachment=True)

@bp.route('/api/yaml/')
@login_required
def yaml_list():
    """Список YAML документов"""
    docs = YamlDocument.query.all()
    return jsonify([{
        'id': doc.id,
        'name': doc.name
    } for doc in docs])

@bp.route('/api/yaml/<int:doc_id>', methods=['GET'])
@login_required
def yaml_get(doc_id):
    """Получение YAML документа"""
    doc = YamlDocument.query.get_or_404(doc_id)
    return jsonify({
        'id': doc.id,
        'name': doc.name,
        'content': doc.content
    })

@bp.route('/api/yaml/save', methods=['POST'])
@login_required
def yaml_save():
    """Сохранение YAML документа"""
    if not request.is_json:
        return abort(400, 'Content-Type must be application/json')
    
    data = request.get_json()
    if not data or 'content' not in data or 'name' not in data:
        return abort(400, 'Name and content are required')

    if not YamlDocument.validate_yaml(data['content']):
        return abort(400, 'Invalid YAML content')

    try:
        if 'id' in data and data['id']:
            doc = YamlDocument.query.get(data['id'])
            if not doc:
                return abort(404, 'Document not found')
            doc.name = data['name']
            doc.content = data['content']
        else:
            doc = YamlDocument(name=data['name'], content=data['content']) # type: ignore
            db.session.add(doc)

        db.session.commit()
        return jsonify({'id': doc.id, 'name': doc.name})
    except Exception as e:
        db.session.rollback()
        return abort(500, str(e))

@bp.route('/api/yaml/delete/<int:doc_id>', methods=['DELETE'])
@login_required
def yaml_delete(doc_id):
    """Удаление YAML документа"""
    doc = YamlDocument.query.get_or_404(doc_id)
    try:
        db.session.delete(doc)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return abort(500, str(e))
    
    
@bp.route('/docx/')
@login_required
def docx_list():
    """Список сгенерированных DOCX файлов"""
    docx_files = DocxFile.query.order_by(DocxFile.created_at.desc()).all()
    edu_plans = EduPlan.query.all()
    yaml_docs = YamlDocument.query.all()
    return render_template('docx_list.html', 
                         docx_files=docx_files,
                         edu_plans=edu_plans,
                         yaml_docs=yaml_docs)

@bp.route('/docx/generate', methods=['POST'])
@login_required
def docx_generate():
    """Генерация DOCX файла"""
    try:
        edu_plan_id = request.form.get('edu_plan_id')
        yaml_doc_id = request.form.get('yaml_doc_id')
        
        if not edu_plan_id or not yaml_doc_id:
            flash('Выберите учебный план и YAML файл', 'error')
            return redirect(url_for('main.docx_list'))
            
        edu_plan = EduPlan.query.get_or_404(edu_plan_id)
        yaml_doc = YamlDocument.query.get_or_404(yaml_doc_id)
        
     
        scripts_dir = os.path.join(current_app.root_path, 'scripts', 'glowing-enigma')
        temp_dir = os.path.join(current_app.root_path, 'temp')
        docx_dir = os.path.join(current_app.root_path, 'docx_files')
        
      
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(docx_dir, exist_ok=True)
        
    
        plx_path = os.path.join(current_app.root_path, 'edu_plans', edu_plan.file)
        yaml_path = os.path.join(temp_dir, f"{yaml_doc.id}.yaml")
        output_filename = f"rpd_{edu_plan.code}_{yaml_doc.name}.docx"
        output_path = os.path.join(docx_dir, output_filename)
        

        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_doc.content)
        

        env = os.environ.copy()
        env['PYTHONPATH'] = scripts_dir + os.pathsep + env.get('PYTHONPATH', '')
        
  
        script_path = os.path.join(scripts_dir, 'get_rpd.py')
        
        current_app.logger.info(f"Executing script with:")
        current_app.logger.info(f"Script path: {script_path}")
        current_app.logger.info(f"PLX path: {plx_path}")
        current_app.logger.info(f"YAML path: {yaml_path}")
        current_app.logger.info(f"Working directory: {scripts_dir}")
        
        result = subprocess.run(
            ['python', script_path, plx_path, yaml_path],
            capture_output=True,
            text=True,
            env=env,
            cwd=scripts_dir
        )
        
        current_app.logger.info(f"Script output:")
        current_app.logger.info(f"STDOUT: {result.stdout}")
        current_app.logger.info(f"STDERR: {result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f"Ошибка выполнения скрипта: {result.stderr}")
        

        generated_file = os.path.join(temp_dir, f"{yaml_doc.id}.docx")
        if not os.path.exists(generated_file):
            raise Exception(f"Файл {generated_file} не был создан скриптом")
            
        shutil.move(generated_file, output_path)
        
        docx_file = DocxFile(
            name=output_filename, # type: ignore
            file_path=output_filename, # type: ignore
            edu_plan_id=edu_plan.pk,# type: ignore
            yaml_doc_id=yaml_doc.id # type: ignore
        )
        db.session.add(docx_file)
        db.session.commit()
        
        flash('Файл успешно сгенерирован', 'success')
        return redirect(url_for('main.docx_list'))
        
    except Exception as e:
        current_app.logger.error(f"Error occurred: {str(e)}")
        flash(f'Ошибка при генерации файла: {str(e)}', 'error')
        return redirect(url_for('main.docx_list'))
    finally:
        if os.path.exists(yaml_path):
            os.remove(yaml_path)
            
@bp.route('/docx/download/<int:file_id>')
@login_required
def docx_download(file_id):
    """Скачивание DOCX файла"""
    docx_file = DocxFile.query.get_or_404(file_id)
    directory = os.path.join(current_app.root_path, 'docx_files')
    return send_from_directory(directory, docx_file.file_path, as_attachment=True)

@bp.route('/docx/delete/<int:file_id>', methods=['POST'])
@login_required
def docx_delete(file_id):
    """Удаление DOCX файла"""
    docx_file = DocxFile.query.get_or_404(file_id)
    try:
        # Удаление файла с диска
        file_path = os.path.join(current_app.root_path, 'docx_files', docx_file.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Удаление записи из базы данных
        db.session.delete(docx_file)
        db.session.commit()

        flash('Файл успешно удалён', 'success')
        return redirect(url_for('main.docx_list'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting DOCX file: {str(e)}")
        flash(f'Ошибка при удалении файла: {str(e)}', 'error')
        return redirect(url_for('main.docx_list'))