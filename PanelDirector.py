import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem, QMessageBox

class PDirector(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Panel_Director.ui", self)

        self.btnIngresarMedico.clicked.connect(self.mostrarIngresoMedico)

        self.cbCesfamMedicoBuscar.currentTextChanged.connect(self.buscarMedicoPorCesfam)

        self.txtBuscarMedico.textChanged.connect(self.buscarMedicoPorTexto)

        self.btnExportarMedicoExcel.clicked.connect(self.exportarExcel)
        self.btnExportarMedicoPdf.clicked.connect(self.exportarPdf)

        self.mostrarDatosMedicos()

        self.informacion.clicked.connect(self.mostrar_info)

    def mostrar_info(self):
        self.ventana_info = uic.loadUi('info.ui') 
        self.ventana_info.show()

    def mostrarIngresoMedico(self):
        self.ventanaIngresoMedico = IngresoMedico(self) 
        
        self.ventanaIngresoMedico.show()
    
    def exportarExcel(self):
        row_count = self.tabla_medicos.rowCount()
        column_count = self.tabla_medicos.columnCount()

        data = []
        for row in range(row_count):
            row_data = []
            for column in range(column_count):
                item = self.tabla_medicos.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        df = pd.DataFrame(data, columns=["Rut", "Nombre", "Apellidos", "Telefono", "Cesfam", "Correo", "Estado"])

        df.to_excel("medicos.xlsx", index=False, engine='openpyxl')

        self.mostrarMensaje("Los datos han sido exportados a Excel correctamente.")

    def exportarPdf(self):
        row_count = self.tabla_medicos.rowCount()
        column_count = self.tabla_medicos.columnCount()

        pdf_filename = "medicos.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, height - 40, "Listado de Médicos")

       
        y_position = height - 60
        c.setFont("Helvetica", 10)

        column_names = ["Rut", "Nombre", "Apellidos", "Telefono", "Cesfam", "Usuario", "Estado"]
        x_positions = [40, 100, 200, 300, 400, 500, 600]

        for col, column_name in enumerate(column_names):
            c.drawString(x_positions[col], y_position, column_name)

        y_position -= 20
        for row in range(row_count):
            for col in range(column_count):
                item = self.tabla_medicos.item(row, col)
                c.drawString(x_positions[col], y_position, item.text() if item else "")
            y_position -= 20
            
            if y_position < 50:
                c.showPage()
                y_position = height - 40
                c.setFont("Helvetica-Bold", 16)
                c.drawString(200, height - 40, "Listado de Médicos")
                c.setFont("Helvetica", 10)
                for col, column_name in enumerate(column_names):
                    c.drawString(x_positions[col], y_position, column_name)
                y_position -= 20

        c.save()

        self.mostrarMensaje("Los datos han sido exportados a PDF correctamente.")

    def mostrarDatosMedicos(self, cesfam=None, filtro=None):
        self.tabla_medicos.setRowCount(0)
        
        conn = sqlite3.connect("caps.db")
        cursor = conn.cursor()

        if cesfam and cesfam != "Seleccionar Cesfam":
            query = '''SELECT U.Rut, U.Nombre, U.Apellidos, U.Telefono, U.Cesfam, L.Usuario, L.Estado
                       FROM Usuarios U
                       INNER JOIN Login L ON U.Rut = L.Id
                       WHERE U.Cesfam = ?'''
            cursor.execute(query, (cesfam,))
        else:
            query = '''SELECT U.Rut, U.Nombre, U.Apellidos, U.Telefono, U.Cesfam, L.Usuario, L.Estado
                       FROM Usuarios U
                       INNER JOIN Login L ON U.Rut = L.Id'''

            if filtro:
                query += ''' WHERE U.Rut LIKE ? OR U.Nombre LIKE ? OR U.Apellidos LIKE ?'''
                filtro = f"{filtro}%"  
                cursor.execute(query, (filtro, filtro, filtro))
            else:
                cursor.execute(query)
        
        rows = cursor.fetchall()
        
        for row in rows:
            row_position = self.tabla_medicos.rowCount()  
            self.tabla_medicos.insertRow(row_position)  
            
            for column, data in enumerate(row):
                self.tabla_medicos.setItem(row_position, column, QTableWidgetItem(str(data)))
        
        conn.close()

    def buscarMedicoPorCesfam(self):
        cesfam_seleccionado = self.cbCesfamMedicoBuscar.currentText()
        
        self.mostrarDatosMedicos(cesfam_seleccionado)

    def buscarMedicoPorTexto(self):
        texto_busqueda = self.txtBuscarMedico.text().strip()
        
        self.mostrarDatosMedicos(filtro=texto_busqueda)

    def mostrarMensaje(self, mensaje):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(mensaje)
        msg.setWindowTitle("Aviso")
        msg.exec()

class IngresoMedico(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("IngresoMedico.ui", self)
        
        self.btnIngresarMedico.clicked.connect(self.insertarDatos)
        self.btnCancelarIngreso.clicked.connect(self.cerrarVentana)
        
        self.parent_window = parent

    def insertarDatos(self):
        rut = self.txtRut.text().strip()  
        nombre = self.txtNombres.text().strip()  
        apellidos = self.txtApellidos.text().strip()  
        numero = self.txtNumero.text().strip()  
        correo = self.txtCorreo.text().strip()  
        
        genero = self.cbGeneroIngresar.currentText().strip()  
        cesfam = self.cbCesfamMedico.currentText().strip()  
        
        rol = "Medico"  
        estado = "activo"  
        
        if not rut or not nombre or not apellidos or not numero or not correo or genero == "Seleccionar Género" or cesfam == "Seleccionar Cesfam":
            self.mostrarMensaje("Por favor, complete todos los campos antes de continuar.")

        conn = sqlite3.connect("caps.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE Rut = ?", (rut,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            
            self.mostrarMensaje("El RUT ya está registrado en el sistema.")
        else:
            
            sql = '''INSERT INTO Usuarios (Rut, Nombre, Apellidos, Sexo, Telefono, Rol, Cesfam, Correo)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            
            cursor.execute(sql, (rut, nombre, apellidos, genero, numero, rol, cesfam, correo))
            
            conn.commit()
            
            login, password = self.generarLoginYPassword(rut, nombre, apellidos)
            
            cursor.execute("INSERT INTO Login (Id, Usuario, Password, Rol, Estado) VALUES (?, ?, ?, ?, ?)", 
                           (rut, login, password, rol, estado))
            conn.commit()
            
            self.mostrarMensaje("Los datos del medico fueron ingresados correctamente...")
        
        self.limpiarCampos()
        
        self.parent_window.mostrarDatosMedicos() 
        
        conn.close()

    def generarLoginYPassword(self, rut, nombre, apellidos):
        
        nombre_corto = nombre[:3].lower() 
        apellido1 = apellidos.split()[0].lower() 
        login = f"{nombre_corto}.{apellido1}"

        conn = sqlite3.connect("caps.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Login WHERE Usuario = ?", (login,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            apellido2 = apellidos.split()[1] if len(apellidos.split()) > 1 else ""
            login = f"{nombre_corto}.{apellido1}{apellido2[0].lower()}"
        
        rut_sin_puntos = rut.replace(".", "") 
        primer_letra_apellido = apellidos.split()[0][0].upper() 
        password = f"{primer_letra_apellido}{rut_sin_puntos}"
        
        conn.close()
        
        return login, password

    def mostrarMensaje(self, mensaje):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(mensaje)
        msg.setWindowTitle("Aviso")
        msg.exec()

    def limpiarCampos(self):
        self.txtRut.clear()
        self.txtNombres.clear()
        self.txtApellidos.clear()
        self.txtNumero.clear()
        self.txtCorreo.clear()
        self.cbGeneroIngresar.setCurrentIndex(0)  
        self.cbCesfamMedico.setCurrentIndex(0) 
    

    def cerrarVentana(self):
        self.close()

if __name__ == "__main__":
    app = QApplication([])
    ventana = PDirector()
    ventana.show() 
    app.exec()  
