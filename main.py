import sys
import sqlite3
import numpy as np
import pandas as pd
import warnings
from PanelDirector import PDirector
from PanelSoporte import PanelSoporte
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from contextlib import closing
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn import linear_model
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6 import uic  
from PyQt6.QtCore import QFile
warnings.simplefilter('ignore')
class Aplicacion(QMainWindow):
    def __init__(self):
        super(Aplicacion, self).__init__()

        ui_file = 'main.ui'
        try:
            self.ui = uic.loadUi(ui_file, self)  
        except Exception as e:
            print(f"Error al cargar el archivo .ui: {e}")
            sys.exit()

        self.ui.conectar.clicked.connect(self.on_conectar_click)
        

        self.setMinimumSize(600, 400)

        print("Interfaz cargada correctamente.")

    def on_conectar_click(self):
        usuario = self.ui.usuario.text() 
        password = self.ui.password.text()  
    
        resultado = self.validar_usuario(usuario, password)
    
        if resultado == "Cuenta deshabilitada":
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Icon.Warning) 
            error_message.setWindowTitle("Cuenta deshabilitada")
            error_message.setText("Tu cuenta está deshabilitada. No puedes acceder.")
            error_message.exec()
        elif resultado: 
            self.close()
            
            if resultado == "Director":
                self.abrir_panel_director()
                self.panel_director.show() 
            elif resultado == "Soporte":
                self.abrir_panel_soporte()
                self.panel_soporte.show() 
            elif resultado == "Medico":
                self.panel_medico = QMainWindow()
                uic.loadUi('Panel_Medico.ui', self.panel_medico)
                self.panel_medico.show() 
                self.panel_medico.setMinimumSize(998, 554) 
                self.panel_medico.btnPredecir.clicked.connect(self.Prediccion) 
                self.panel_medico.btnIngresarPaciente.clicked.connect(self.ingresoPaciente)
                self.panel_medico.btnExportarResultado.clicked.connect(self.exportarPDF)
                self.panel_medico.btnBuscarPacienteRegistrado.clicked.connect(self.buscar)

        else:
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Icon.Warning)  
            error_message.setWindowTitle("Error de Autenticación")
            error_message.setText("La contraseña o el usuario no son correctos")
            error_message.exec()

    def abrir_panel_director(self):
        
        self.panel_director = PDirector()  
        self.panel_director.show()

    def abrir_panel_soporte(self):
        
        self.panel_soporte = PanelSoporte() 
        self.panel_soporte.show()

    def validar_usuario(self, usuario, password):
      
        try:
            conn = sqlite3.connect('caps.db') 
            cursor = conn.cursor()

            cursor.execute("SELECT rol, estado FROM Login WHERE usuario=? AND password=?", (usuario, password))
            result = cursor.fetchone()

            conn.close()  

            if result:
                rol, estado = result 

                if estado == "activo":
                    return rol  
                else:
                    return "Cuenta deshabilitada" 

            else:
                return None  

        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
            return None

    
    def Prediccion(self):
        try:
            dataframe = pd.read_csv(r"cancer patient data sets.csv")
            dataframe.head()
            dataframe.describe()
            x = np.array(dataframe.drop('Level', axis=1))
            y = np.array(dataframe['Level'])
            scaler = preprocessing.StandardScaler().fit(x)
            x_scaled = scaler.transform(x)
            model = linear_model.LogisticRegression()
            model.fit(x_scaled,y)
            X_train,X_test,y_train,y_test=train_test_split(x_scaled,y,test_size=0.3,random_state=0)
            model = linear_model.LogisticRegression()
            model.fit(X_train,y_train) 
            rut = self.panel_medico.txtRutPacientePredecir.text()
            edad = int(self.panel_medico.txtEdadPredecir.text())
            genero = self.panel_medico.cbGeneroPredecir.currentText()
            if genero == 'Masculino':
                valor_genero = 1
            elif genero == 'Femenino':
                valor_genero = 2
            alcohol = int(self.panel_medico.txtNivelAlcohol.text())
            polvo = int(self.panel_medico.txtNivelPolvo.text())
            genetico = int(self.panel_medico.txtNivelRiesgoGen.text())
            obesidad = int(self.panel_medico.txtNivelObesidad.text())
            cigarro = int(self.panel_medico.txtNivelCigarro.text())
            pecho = int(self.panel_medico.txtNivelPecho.text())
            respirar = int(self.panel_medico.txtNivelRespirar.text())
            conn = sqlite3.connect('caps.db')
            cursor = conn.cursor()
            X_new = pd.DataFrame({'Age': [edad], 'Gender': [valor_genero], 'Alcohol use': [alcohol], 'Dust Allergy': [polvo], 'Genetic Risk': [genetico], 'Obesity': [obesidad], 'Smoking': [cigarro], 'Chest Pain': [pecho],'Shortness of Breath': [respirar]})
            X_resultado = model.predict(X_new)
            self.panel_medico.resultadoPaciente.clear()
            if alcohol <= 2 and polvo <= 2 and genetico <= 2 and obesidad <= 2 and cigarro <= 2 and pecho <= 2 and respirar <= 2:
                self.panel_medico.resultadoPaciente.insert('Posibilidad baja, debe examinarse cada 6 meses')
                cursor.execute("INSERT INTO 'main'.'Factores' ('Rut', 'Edad', 'Genero', 'Consumo_de_Alcohol', 'Alergia_al_polvo', 'Riesgo_genetico', 'Obesidad', 'Consumo_de_Cigarro', 'Dificultad_al_respirar', 'Dolor_de_pecho', 'Diagnostico') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (rut, edad, genero, alcohol, polvo, genetico, obesidad, cigarro, pecho, respirar, 'Posibilidad Baja'))
                conn.commit()
                conn.close()
            elif X_resultado == 1:
                self.panel_medico.resultadoPaciente.insert('Posibilidad baja, debe examinarse cada 6 meses')
                cursor.execute("INSERT INTO 'main'.'Factores' ('Rut', 'Edad', 'Genero', 'Consumo_de_Alcohol', 'Alergia_al_polvo', 'Riesgo_genetico', 'Obesidad', 'Consumo_de_Cigarro', 'Dificultad_al_respirar', 'Dolor_de_pecho', 'Diagnostico') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (rut, edad, genero, alcohol, polvo, genetico, obesidad, cigarro, pecho, respirar, 'Posibilidad Baja'))
                conn.commit()
                conn.close()
            elif X_resultado == 2:
                self.panel_medico.resultadoPaciente.insert('Posibilidad media, debe examinarse cada 3 meses')
                cursor.execute("INSERT INTO 'main'.'Factores' ('Rut', 'Edad', 'Genero', 'Consumo_de_Alcohol', 'Alergia_al_polvo', 'Riesgo_genetico', 'Obesidad', 'Consumo_de_Cigarro', 'Dificultad_al_respirar', 'Dolor_de_pecho', 'Diagnostico') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (rut, edad, genero, alcohol, polvo, genetico, obesidad, cigarro, pecho, respirar, 'Posibilidad Media'))
                conn.commit()
                conn.close()
            elif X_resultado == 3:
                self.panel_medico.resultadoPaciente.insert('Posibilidad alta, debe examinarse cada mes')
                cursor.execute("INSERT INTO 'main'.'Factores' ('Rut', 'Edad', 'Genero', 'Consumo_de_Alcohol', 'Alergia_al_polvo', 'Riesgo_genetico', 'Obesidad', 'Consumo_de_Cigarro', 'Dificultad_al_respirar', 'Dolor_de_pecho', 'Diagnostico') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (rut, edad, genero, alcohol, polvo, genetico, obesidad, cigarro, pecho, respirar, 'Posibilidad Alta'))
                conn.commit()
                conn.close()
        except Exception as e:
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Icon.Warning)
            error_message.setWindowTitle("Error")
            error_message.setText("Por favor llene todos los campos con valores validos")
            error_message.exec()
        
    def ingresoPaciente(self):
        try:
            rut = self.panel_medico.txtRutPaciente.text()
            nombres = self.panel_medico.txtNombrePaciente.text()
            apellidos = self.panel_medico.txtApellidosPaciente.text()
            edad = self.panel_medico.txtEdadPaciente.text()
            genero = self.panel_medico.cbGeneroPaciente.currentText()
            telefono = self.panel_medico.txtNumeroPaciente.text()
            conn = sqlite3.connect('caps.db') 
            cursor = conn.cursor()   
            cursor.execute("INSERT INTO 'main'.'Paciente' ('Rut', 'nombre', 'apellidos', 'edad', 'genero', 'telefono') VALUES (?, ?, ?, ?, ?, ?);", (rut, nombres, apellidos, edad, genero, telefono))
            conn.commit()
            conn.close()
            self.panel_medico.txtRutPacientePredecir.insert(rut)
            self.panel_medico.txtEdadPredecir.insert(edad)
        except Exception as e:
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Icon.Warning)
            error_message.setWindowTitle("Error")
            error_message.setText("Por favor llene todos los campos con valores validos")
            error_message.exec()      

    def exportarPDF(self):
            rut = self.panel_medico.txtRutPacientePredecir.text()
            edad = int(self.panel_medico.txtEdadPredecir.text())
            genero = self.panel_medico.cbGeneroPredecir.currentText()
            alcohol = int(self.panel_medico.txtNivelAlcohol.text())
            polvo = int(self.panel_medico.txtNivelPolvo.text())
            genetico = int(self.panel_medico.txtNivelRiesgoGen.text())
            obesidad = int(self.panel_medico.txtNivelObesidad.text())
            cigarro = int(self.panel_medico.txtNivelCigarro.text())
            pecho = int(self.panel_medico.txtNivelPecho.text())
            respirar = int(self.panel_medico.txtNivelRespirar.text())
            diagnostico = self.panel_medico.resultadoPaciente.text()
            c = canvas.Canvas(("report.pdf"), pagesize=A4)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 800, "Reporte")
            c.setFont("Helvetica-Bold", 9)
            c.drawString(30, 770, "Edad")
            c.drawString(30, 750, str(edad))
            c.drawString(30, 730, "RUT")
            c.drawString(30, 710, str(rut))
            c.drawString(30, 690, "Resultados")
            c.drawString(30, 670, diagnostico)
            c.drawString(67, 770, "|Genero")
            c.drawString(67, 750, genero)
            c.drawString(115, 770, "|Uso de alcohol")
            c.drawString(115, 750, str(alcohol))
            c.drawString(200, 770, "|Alergia al polvo")
            c.drawString(200, 750, str(polvo))
            c.drawString(287, 770, "|Riesgo genetico")
            c.drawString(287, 750, str(genetico))
            c.drawString(377, 770, "|Obesidad")
            c.drawString(377, 750, str(obesidad))
            c.drawString(433, 770, "|Fumador")
            c.drawString(433, 750, str(cigarro))
            c.drawString(488, 770, "|Dif. Respiración")
            c.drawString(488, 750, str(respirar))
            c.drawString(115, 730, "Dolor de Pecho")
            c.drawString(115, 710, str(pecho))
            c.save()
    
    def buscar(self):
            conn = sqlite3.connect('caps.db')
            cursor = conn.cursor()
            rut = self.panel_medico.buscarResultadoPaciente.text()
            cursor.execute("SELECT Diagnostico FROM Factores WHERE Rut=?", (rut,))
            resultado = str(cursor.fetchone())
            self.panel_medico.resultadoPaciente.clear()
            self.panel_medico.resultadoPaciente.insert(resultado)
            conn.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dial = Aplicacion()
    dial.show()
    sys.exit(app.exec())
