from importlib.resources import path
from werkzeug.utils import secure_filename
from flask import Blueprint, request, render_template, url_for, send_from_directory, send_file, flash
import os
from geodb import app
import pandas as pd
import numpy as np
from re import split
from geodb import georreferenciador
from geodb.forms import GeorreferenciarForm, GeorreferenciarFormGoogle


df_veredas= pd.read_excel("./geodb//files/df_veredas1.xlsx") 
df_poblados=pd.read_excel('./geodb//files/df_poblados1.xlsx')
df_departamentos=pd.read_excel('./geodb//files/df_departamentos.xlsx')
extension = set(['csv'])

def csv_validation(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in extension

def csv_filename(filename):
    return filename.rsplit(".", 1)[0]

files=[]



georreferenciar = Blueprint('georreferenciar', __name__)

@georreferenciar.route('/georreferenciar/upload', methods=['GET','POST'])
def georreferenciar_upload():
    
    georreferenciar_form = GeorreferenciarForm()
    georreferenciar_form_google = GeorreferenciarFormGoogle()

    if request.method == "POST":

        
        filename_pandas = request.form.get('filename_pandas')
        if filename_pandas:
            
            df_usuario = pd.read_csv(f'./geodb//files/uploads/{filename_pandas}')
            df_usuario_2= pd.read_csv(f'./geodb//files/uploads/{filename_pandas}')
            df_salida = pd.read_csv(f'./geodb//files/uploads/{filename_pandas}')
            
            #Preparación de datos
            df_usuario = georreferenciador.process_string_db(df_usuario=df_usuario)
            df_usuario = georreferenciador.del_names(df_usuario)
            df_usuario = georreferenciador.delete_spaces_db(df_usuario)
            
            
            #Georreferenciación
            df = georreferenciador.georreferenciar(df_usuario, df_veredas, df_poblados, df_departamentos)
            df_salida = georreferenciador.merge_df_salida(df_salida, df)
            
            m = georreferenciador.create_map()
            m = georreferenciador.map_pandas(df, df_usuario_2, m)
            
            mapa = m.save(f"./geodb//templates/mapa.html")
            mapa_filename = csv_filename(filename_pandas)
            mapa_route = f"/georreferenciar/mapa/{mapa_filename}"

            final_filename = f"final_{filename_pandas}"
            df_salida.to_csv(os.path.join(app.config["UPLOAD_FOLDER"], final_filename))

            return render_template('georreferenciar.html', mapa_route = mapa_route, files =  files, filename=final_filename, georreferenciar_form = georreferenciar_form, georreferenciar_form_google = georreferenciar_form_google) #df_salida.to_html()

        filename_google = request.form.get('filename_google')
        if filename_google:
            df_usuario = pd.read_csv(f'./geodb//files/uploads/{filename_google}')
            df_usuario = georreferenciador.georreferenciar_google(df_usuario)
            return df_usuario.to_html()

        if "user_file" not in request.files:
            flash("No se ha subido ningún archivo", category='danger')
            return render_template(
            'georreferenciar.html', files =  files, georreferenciar_form = georreferenciar_form, georreferenciar_form_google = georreferenciar_form_google
            ) 
        f = request.files['user_file']
        if f.filename == '':
            flash("No se ha seleccionado ningún archivo", category='danger')
            return render_template(
            'georreferenciar.html', files =  files, filename = filename_pandas, georreferenciar_form = georreferenciar_form, georreferenciar_form_google = georreferenciar_form_google
            )
        if f and csv_validation(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            files.append(f.filename)
            del f
            print(files)
            

        else:
            flash("El archivo debe tener la extension .csv", category='danger')
        
        return render_template(
            'georreferenciar.html', files =  files, georreferenciar_form = georreferenciar_form, georreferenciar_form_google = georreferenciar_form_google
            )

        
    


    
    return render_template('georreferenciar.html', files =  files, georreferenciar_form = georreferenciar_form, georreferenciar_form_google = georreferenciar_form_google)

@georreferenciar.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], path= filename, as_attachment = True)

@georreferenciar.route('/georreferenciar/mapa')
def show_map():
        return render_template("mapa.html")

