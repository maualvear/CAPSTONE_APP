import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem, QMessageBox

class PanelSoporte(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("Panel_Soporte.ui", self)

        self.conn = sqlite3.connect('caps.db')
        self.cursor = self.conn.cursor()

        self.btnIngresarDirector.clicked.connect(self.ingresar_director)
        self.btnEditarDirector.clicked.connect(self.editar_director)
        self.btnBorrarDirector.clicked.connect(self.borrar_director)

        self.mostrar_usuarios()

        self.tabla_director.cellClicked.connect(self.seleccionar_fila)

        self.informacion.clicked.connect(self.mostrar_info)

    def mostrar_info(self):
        self.ventana_info = uic.loadUi('info.ui') 
        self.ventana_info.show()

    def seleccionar_fila(self, row, column):
        rut = self.tabla_director.item(row, 0).text()
        nombre = self.tabla_director.item(row, 1).text()
        apellidos = self.tabla_director.item(row, 2).text()
        sexo = self.tabla_director.item(row, 3).text()
        telefono = self.tabla_director.item(row, 4).text()
        cesfam = self.tabla_director.item(row, 5).text()
        usuario = self.tabla_director.item(row, 6).text()
        estado = self.tabla_director.item(row, 7).text()

        self.txtRutDirector.setText(rut)
        self.txtNombreDirector.setText(nombre)
        self.txtApellidosDirector.setText(apellidos)
        self.txtNumeroDirector.setText(telefono)
        self.cbCesfamDirector.setCurrentText(cesfam)
        self.cbEstadoDirector.setCurrentText(estado)
        self.cbGenero.setCurrentText(sexo)

        self.usuario_actual = usuario

    def ingresar_director(self):
        rut = self.txtRutDirector.text()
        nombre = self.txtNombreDirector.text()
        apellidos = self.txtApellidosDirector.text()
        genero = self.cbGenero.currentText()  
        telefono = self.txtNumeroDirector.text()
        cesfam = self.cbCesfamDirector.currentText()
        estado = self.cbEstadoDirector.currentText()

        if not nombre or not apellidos:
            QMessageBox.warning(self, "Error", "El nombre y los apellidos son obligatorios.")
            return

        sexo = genero if genero != "Seleccionar Género" else "" 
        correo = ""  

        self.cursor.execute("SELECT * FROM Usuarios WHERE Rut = ?", (rut,))
        if self.cursor.fetchone(): 
            QMessageBox.warning(self, "Error", "El director ya está registrado con este RUT.")
            
            self.limpiar_campos()
            return

        query_usuarios = '''INSERT INTO Usuarios (Rut, Nombre, Apellidos, Sexo, Telefono, Rol, Cesfam, Correo)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        self.cursor.execute(query_usuarios, (rut, nombre, apellidos, sexo, telefono, estado, cesfam, correo))
        self.conn.commit()

        usuario = self.generar_usuario(nombre, apellidos)
        contrasena = self.generar_contrasena(rut, apellidos)

        query_login = '''INSERT INTO Login (Id, Usuario, Password, Rol, Estado)
                         VALUES (?, ?, ?, ?, ?)'''
        self.cursor.execute(query_login, (rut, usuario, contrasena, "Director", "activo"))
        self.conn.commit()

        self.mostrar_usuarios()

        QMessageBox.information(self, "Éxito", "El director y usuario se han ingresado correctamente.")

        self.limpiar_campos()

    def generar_usuario(self, nombre, apellidos):
        nombre_usuario = nombre.lower()[:3]  
        apellido_usuario = apellidos.lower().split()[0]  
        return f"{nombre_usuario}.{apellido_usuario}"

    def generar_contrasena(self, rut, apellidos):
        primer_apellido = apellidos.split()[0] 
        rut_sin_puntos = rut.replace(".", "").replace("-", "") 
        return f"{primer_apellido[0].upper()}{rut_sin_puntos}"

    def editar_director(self):
        rut = self.txtRutDirector.text()
        nombre = self.txtNombreDirector.text()
        apellidos = self.txtApellidosDirector.text()
        genero = self.cbGenero.currentText()  
        telefono = self.txtNumeroDirector.text()
        cesfam = self.cbCesfamDirector.currentText()
        estado = self.cbEstadoDirector.currentText()

        if not nombre or not apellidos:
            QMessageBox.warning(self, "Error", "El nombre y los apellidos son obligatorios.")
            return

        sexo = genero if genero != "Seleccionar Género" else ""  
        correo = ""  

        query_usuarios = '''UPDATE Usuarios
                            SET Nombre = ?, Apellidos = ?, Sexo = ?, Telefono = ?, Cesfam = ?, Rol = ?, Correo = ?
                            WHERE Rut = ?'''
        self.cursor.execute(query_usuarios, (nombre, apellidos, sexo, telefono, cesfam, estado, correo, rut))
        self.conn.commit()

        usuario = self.generar_usuario(nombre, apellidos)
        contrasena = self.generar_contrasena(rut, apellidos)

        query_login = '''UPDATE Login
                         SET Usuario = ?, Password = ?, Estado = ?
                         WHERE Id = ?'''
        self.cursor.execute(query_login, (usuario, contrasena, estado, rut))
        self.conn.commit()

        QMessageBox.information(self, "Éxito", "Los datos del director han sido actualizados correctamente.")

        self.mostrar_usuarios()

        self.limpiar_campos()

    def borrar_director(self):
        rut = self.txtRutDirector.text()

        self.cursor.execute("DELETE FROM Login WHERE Id = ?", (rut,))
        self.conn.commit()

        self.cursor.execute("DELETE FROM Usuarios WHERE Rut = ?", (rut,))
        self.conn.commit()

        QMessageBox.information(self, "Éxito", "El director ha sido borrado correctamente.")

        self.mostrar_usuarios()

        self.limpiar_campos()

    def mostrar_usuarios(self):
        self.tabla_director.setRowCount(0)

        self.cursor.execute("""
            SELECT 
                U.Rut, 
                U.Nombre, 
                U.Apellidos, 
                U.Sexo, 
                U.Telefono, 
                U.Cesfam, 
                L.Usuario, 
                L.Estado
            FROM 
                Usuarios U
            JOIN 
                Login L ON U.Rut = L.Id;  
        """)
        usuarios = self.cursor.fetchall()

        
        for row in usuarios:
            row_position = self.tabla_director.rowCount()
            self.tabla_director.insertRow(row_position)

            self.tabla_director.setItem(row_position, 0, QTableWidgetItem(str(row[0])))  
            self.tabla_director.setItem(row_position, 1, QTableWidgetItem(str(row[1])))  
            self.tabla_director.setItem(row_position, 2, QTableWidgetItem(str(row[2])))  
            self.tabla_director.setItem(row_position, 3, QTableWidgetItem(str(row[3])))  
            self.tabla_director.setItem(row_position, 4, QTableWidgetItem(str(row[4])))  
            self.tabla_director.setItem(row_position, 5, QTableWidgetItem(str(row[5])))  
            self.tabla_director.setItem(row_position, 6, QTableWidgetItem(str(row[6])))  
            self.tabla_director.setItem(row_position, 7, QTableWidgetItem(str(row[7])))  

    def limpiar_campos(self):
        self.txtRutDirector.clear()
        self.txtNombreDirector.clear()
        self.txtApellidosDirector.clear()
        self.txtNumeroDirector.clear()
        self.cbGenero.setCurrentIndex(0)  
        self.cbCesfamDirector.setCurrentIndex(0)
        self.cbEstadoDirector.setCurrentIndex(0)

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PanelSoporte()
    window.show()
    sys.exit(app.exec())
