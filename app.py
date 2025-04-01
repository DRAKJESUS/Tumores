import os
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from processing.tumor_detector import TumorDetector
from processing.image_processor import generate_visualizations

app = Flask(__name__)

# Configuración de carpetas
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Procesamiento de imagen
            detector = TumorDetector()
            result = detector.detect_tumor(filepath)
            
            # Visualizaciones
            base_name = os.path.splitext(filename)[0]
            result_images = generate_visualizations(
                filepath, 
                app.config['RESULT_FOLDER'], 
                base_name
            )
            
            # Rutas para el frontend
            web_path = os.path.join('uploads', filename).replace('\\', '/')
            result_web_paths = [
                os.path.join('results', os.path.basename(img)).replace('\\', '/')
                for img in result_images
            ]
            
            return render_template('index.html',
                                   original_image=web_path,
                                   result_images=result_web_paths,
                                   has_tumor=result['has_tumor'])
    
    return render_template('index.html')

# Este bloque es clave para que funcione en Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
