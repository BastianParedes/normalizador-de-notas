from os import makedirs, listdir, remove
from sys import modules
from statistics import stdev
from tkinter import *
from tkinter import ttk

#Genera el curso vacío con el que se inicia el programa
makedirs("Cursos", exist_ok=True)
file = open("./Cursos/.txt", "w", encoding="utf-8")
file.write("")
file.close()

estudiantes_creados = []

frame_base = Tk()
if "logo.ico" in listdir("./Cursos"):
    frame_base.iconbitmap("Cursos/logo.ico")
frame_base.title("Normalizador de notas")
frame_base.state("zoomed")

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    def config(self, **kargs):
        self.canvas.config(**kargs)


#FRAME BASE=================================================================================================================
#FRAME IZQUIERDO============================================================================================================
frame_izquierdo = Frame(frame_base)
frame_izquierdo.pack(side="left", fill="y")
frame_izquierdo.config(bg="light grey")
frame_izquierdo.grid_columnconfigure(0, minsize=300)
frame_izquierdo.grid_columnconfigure(1, minsize=100)

class Label_Entry:
    def __init__(self, label="", valor_inicial="", fila=0):
        self.variable = StringVar(value=valor_inicial)
        self.variable.trace("w", self.quitar_letras)
        self.Label = Label(frame_izquierdo, text=label, font=("Helvetica", 12), bg="light grey")
        self.Label.grid(row=fila, column=0, sticky=W, padx=10, pady=5)

        self.Entry = Entry(frame_izquierdo, textvariable=self.variable, width=5, font=("Helvetica", 12))
        self.Entry.grid(row=fila, column=1, padx=5, pady=5)

    def quitar_letras(self, tipo, vacío, modo):
        #Quita lo no numérico
        contenido = ""
        for letra_numero in self.variable.get():
            try:
                letra_numero = int(letra_numero)
                contenido += str(letra_numero)
            except:
                pass
        self.variable.set(contenido)
        #Quita los ceros extras
        for numero in self.variable.get():
            if numero=="0" and len(self.variable.get())>1:
                self.variable.set(self.variable.get()[1:])
            else:
                break

    def valor(self):
        if self.variable.get()=="":
            return 0
        else:
            return int(self.variable.get())

nota_minima = Label_Entry("Nota mínima", 20, 0)
nota_maxima = Label_Entry("Nota máxima", 70, 1)
nota_aprobacion = Label_Entry("Nota de aprobación", 40, 2)
porcentaje_exigencia = Label_Entry("Porcentaje de exigencia", 60, 3)
puntaje_maximo = Label_Entry("Puntaje máximo", 30, 4)



class boton_calcular_notas:
    def __init__(self):
        self.boton = Button(frame_izquierdo, text="Calcular notas", font=("Helvetica", 12), command=self.calcular_notas, bg="light green", relief=GROOVE)
        self.boton.grid(columnspan=2, pady=15)

    def calcular_notas(self):
        global estudiantes_creados
        lista_notas_tradicionales = []
        lista_notas_normalizadas = []

        #Agrega 0 a las notas y puntaje si están vacios
        nota_minima.Entry.insert(0, 0)
        nota_maxima.Entry.insert(0, 0)
        nota_aprobacion.Entry.insert(0, 0)
        porcentaje_exigencia.Entry.insert(0, 0)
        puntaje_maximo.Entry.insert(0, 0)

        #Detiene el cálculo si no están las condiciones propicias
        if not actualizar_mensaje()==True:
            return None


        #Obtiene y calcula notas, puntajes y porcentajes
        nota_media = (nota_minima.valor() + nota_maxima.valor())/2
        desviacion_estandar = int((nota_maxima.valor()-nota_media)/3)
        cantidad_de_estudiantes = len(estudiantes_creados)

        #Notas sin normalizar y pone 0 si no hay número en el puntaje
        for estudiante in estudiantes_creados:
            estudiante.Entry_puntaje.insert(0, "0")
            if estudiante.puntaje() <= porcentaje_exigencia.valor()*puntaje_maximo.valor()/100:
                nota = int(100*(nota_aprobacion.valor()-nota_minima.valor())/(porcentaje_exigencia.valor()*puntaje_maximo.valor())*estudiante.puntaje()+nota_minima.valor())
            else:
                nota = int((nota_maxima.valor()-nota_aprobacion.valor())/(puntaje_maximo.valor()-porcentaje_exigencia.valor()*puntaje_maximo.valor()/100)*(estudiante.puntaje()-puntaje_maximo.valor())+nota_maxima.valor())
            estudiante.Label_nota_sin_normalizar.config(text=nota)
            lista_notas_tradicionales.append(nota)

        
        #Calcula y establece la media y desviación estandar de las notas tracicionales
        media_tradicional.actualizar(sum(lista_notas_tradicionales)/len(lista_notas_tradicionales))
        if len(estudiantes_creados)==1:
            desviacion_estandar_tradicional.actualizar(0)
        else:
            desviacion_estandar_tradicional.actualizar(stdev(lista_notas_tradicionales))


        #Notas normalizadas
        #Colecta los puntajes y los junta en una lista
        lista_puntajes_correjidos = []
        for estudiante in estudiantes_creados:
            lista_puntajes_correjidos.append(estudiante.puntaje())
        #En un diccionrio las claves serán el puntaje obtenible y el valor la frecuencia absoluta acumulada
        diccionario_puntaje_notas = {}
        for puntaje_obtenible in range(0, puntaje_maximo.valor()+1):
            diccionario_puntaje_notas[puntaje_obtenible] = lista_puntajes_correjidos.count(puntaje_obtenible)
            if puntaje_obtenible!=0:
                diccionario_puntaje_notas[puntaje_obtenible] = (diccionario_puntaje_notas[puntaje_obtenible] + diccionario_puntaje_notas[puntaje_obtenible-1])
        #Transforma la frecuencia absoluta acumulada a frecuencia relativa acumulada
        for puntaje_obtenible in diccionario_puntaje_notas:
            diccionario_puntaje_notas[puntaje_obtenible] = diccionario_puntaje_notas[puntaje_obtenible]/cantidad_de_estudiantes
        
        #Transforma las frecuencias relativas acumuladas en desviaciones estandar (Z)
        for puntaje_obtenible in diccionario_puntaje_notas:
            diccionario_provisional = {}
            for Fra in diccionario_Fr_Z:
                diccionario_provisional[abs(Fra-diccionario_puntaje_notas[puntaje_obtenible])] = diccionario_Fr_Z[Fra]
            diccionario_puntaje_notas[puntaje_obtenible] = diccionario_provisional[min(diccionario_provisional)]
        
        #Cambia los label de las notas normalizadas
        for estudiante in estudiantes_creados:
            if estudiante.puntaje()==0:
                nota = nota_minima.valor()
            elif estudiante.puntaje()==puntaje_maximo.valor():
                nota = nota_maxima.valor()
            else:
                nota = int(nota_media+desviacion_estandar*diccionario_puntaje_notas[estudiante.puntaje()])
            estudiante.Label_nota_normalizada.config(text=nota)
            lista_notas_normalizadas.append(nota)
        #Calcula y establece la media y desviación estandar de las notas tracicionales
        media_normalizada.actualizar(sum(lista_notas_normalizadas)/len(lista_notas_normalizadas))
        if len(estudiantes_creados)==1:
            desviacion_estandar_normalizada.actualizar(0)
        else:
            desviacion_estandar_normalizada.actualizar(stdev(lista_notas_normalizadas))

        # media+desvi_estan*Z
boton_calculo_notas = boton_calcular_notas()


class medida:
    def __init__(self, label, decimales, fila):
        self.Label = Label(frame_izquierdo, text=label, font=("Helvetica", 12), bg="light grey")
        self.Label.grid(row=fila, column=0, sticky=W, padx=10, pady=5)

        self.Label_valor = Label(frame_izquierdo, text="Sin calcular", font=("Helvetica", 12), bg="light grey")
        self.Label_valor.grid(row=fila, column=1)
        self.decimales = decimales
    def actualizar(self, valor):
        self.Label_valor.config(text=str(round(valor,self.decimales)).replace(".",","))

media_tradicional = medida("Media tradicional", 1, 6)
media_normalizada = medida("Media normalizada", 1, 7)
desviacion_estandar_tradicional = medida("Desviación estándar tradicional", 2, 8)
desviacion_estandar_normalizada = medida("Desviación estándar normalizada", 2, 9)





class boton_agregar_estudiante:
    def __init__(self):
        self.boton = Button(frame_izquierdo, text="Agregar estudiante", font=("Helvetica", 12), command=self.agregar_estudiante, bg="SteelBlue2")
        self.boton.grid(columnspan=2, pady=5)
    def agregar_estudiante(self):
        global estudiantes_creados
        for alumno in estudiantes_creados:
            alumno.Label_nota_normalizada.config(text="Sin calcular")
        estudiantes_creados.append(Estudiante())

        #Reinicia las medias y desviacioens estándar
        media_tradicional.Label_valor.config(text="Sin calcular")
        media_normalizada.Label_valor.config(text="Sin calcular")
        desviacion_estandar_tradicional.Label_valor.config(text="Sin calcular")
        desviacion_estandar_normalizada.Label_valor.config(text="Sin calcular")
boton_agregado_estudiante = boton_agregar_estudiante()


class nombre_del_curso:
    def __init__(self, nombre=""):
        self.Label = Label(frame_izquierdo, text="Guardar curso con el nombre:", font=("Helvetica", 12), bg="light grey")
        self.Label.grid(sticky=W, padx=10, pady=5)
        self.variable = StringVar(value=nombre)
        self.variable.trace("w", self.quitar_simbolos)
        self.Entry = Entry(frame_izquierdo, textvariable=self.variable, width=25, font=("Helvetica", 12))
        self.Entry.grid(columnspan=2, padx=5, pady=5)
    def quitar_simbolos(self, tipo, vacío, modo):
        self.variable.set(self.variable.get().replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","").replace(".",""))
nombre_curso = nombre_del_curso()


class boton_guardar_curso:
    def __init__(self):
        self.boton = Button(frame_izquierdo, text="Guardar curso", font=("Helvetica", 12), command=self.guardar_curso, bg="gold2")
        self.boton.grid(columnspan=2, pady=5)
    def guardar_curso(self):
        global estudiantes_creados
        lista = ""
        for alumno in estudiantes_creados:
            lista += alumno.Entry_nombre.get()+"\n"
        lista = lista[:-1]

        file = open(f"./Cursos/{nombre_curso.variable.get()}.txt", "w", encoding="utf-8")
        file.write(lista)
        file.close()
        lista = listdir("Cursos")
        try:
            lista.remove("__pycache__")
        except:
            pass
        try:
            lista.remove("logo.ico")
        except:
            pass
        lista[lista.index(".txt")]=""
        for curso in lista:
            lista[lista.index(curso)] = curso[:-4]
        cursos_guardados.lista['values'] = lista
        cursos_guardados.variable.set(nombre_curso.variable.get())
boton_guardado_curso = boton_guardar_curso()


class lista_de_cursos:
    def __init__(self):
        self.Label = Label(frame_izquierdo, text="Cargar curso:", font=("Helvetica", 12), bg="light grey")
        self.Label.grid(sticky=W, padx=10, pady=5)
        self.variable = StringVar(value="")

        self.lista = ttk.Combobox(frame_izquierdo, textvariable=self.variable, state="readonly", font=("Helvetica", 12))
        lista_de_cursos = listdir("Cursos")
        try:
            lista_de_cursos.remove("__pycache__")
        except:
            pass
        try:
            lista_de_cursos.remove("logo.ico")
        except:
            pass
        for curso in lista_de_cursos:
            lista_de_cursos[lista_de_cursos.index(curso)] = curso[:-4]
        self.lista["values"] = lista_de_cursos
        self.lista.set("")
        self.lista.grid(columnspan=2, padx=5, pady=5)

        self.variable.trace("w", self.cargar_curso)

    def cargar_curso(self, *args):
        #Esta parte de arriba detiene la carga si el nombre guardado es igual al nombre que se está mostrando en la lista. Esto es para evitar que se cargue un curso al momento de guardarlo
        if self.variable.get()==nombre_curso.variable.get():
            return True
        #Quita los estudiantes creados
        global estudiantes_creados
        for alumno in estudiantes_creados:
            alumno.boton_eliminar.grid_forget()
            alumno.Label_numero.grid_forget()
            alumno.Entry_nombre.grid_forget()
            alumno.Entry_puntaje.grid_forget()
            alumno.Label_nota_sin_normalizar.grid_forget()
            alumno.Label_nota_normalizada.grid_forget()
        estudiantes_creados = []
        #Pone en el Entry nombre del curso el nombre del curso que se está cargando
        nombre_curso.variable.set(self.variable.get())
        #Lee el archivo txt
        archivo_txt = open(f"./Cursos/{self.variable.get()}.txt")
        contenido = archivo_txt.read().split("\n")
        archivo_txt.close()
        #Crea los estudiantes obtenidos del archivo. No crea nada si no hay nada en el archivo
        if not (len(contenido)==1 and contenido[0]==''):
            for nombre in contenido:
                estudiantes_creados.append(Estudiante(nombre))

        #Reinicia las medias y desviaciones estándar
        media_tradicional.Label_valor.config(text="Sin calcular")
        media_normalizada.Label_valor.config(text="Sin calcular")
        desviacion_estandar_tradicional.Label_valor.config(text="Sin calcular")
        desviacion_estandar_normalizada.Label_valor.config(text="Sin calcular")
cursos_guardados = lista_de_cursos()


class boton_borrar_curso:
    def __init__(self):
        self.boton = Button(frame_izquierdo, text="Borrar curso", font=("Helvetica", 12), command=self.borrar_curso, bg="tomato")
        self.boton.grid(columnspan=2, pady=5)
    def borrar_curso(self):
        global estudiantes_creados
        if not nombre_curso.variable.get()=="":
            remove(f"Cursos/{nombre_curso.variable.get()}.txt")
            lista = listdir("Cursos")
            try:
                lista.remove("__pycache__")
            except:
                pass
            try:
                lista.remove("logo.ico")
            except:
                pass
            lista[lista.index(".txt")]=""
            for curso in lista:
                lista[lista.index(curso)] = curso[:-4]
            cursos_guardados.lista['values'] = lista
            cursos_guardados.variable.set("")
boton_borrado_curso = boton_borrar_curso()




#FRAME IZQUIERDO============================================================================================================
#FRAME SUPERIOR=============================================================================================================
frame_superior = Frame(frame_base, bg="tomato", height=100)
frame_superior.pack(side="top", fill="x")


mensaje_al_usuario = Label(frame_superior, text="Este mensaje se actualiza cada vez que se intenta calcular las notas.\nAgrega estudiantes o carga un curso ya creado.", font=("Helvetica", 15), bg="tomato")
mensaje_al_usuario.pack(pady=25)

def actualizar_mensaje(*args):
    global estudiantes_creados
    lista_de_puntajes = [0]
    for estudiante in estudiantes_creados:
        lista_de_puntajes.append(estudiante.puntaje())
    while "" in lista_de_puntajes:
        lista_de_puntajes.remove("")
    if len(estudiantes_creados)==0:
        mensaje_al_usuario.config(text="Este mensaje se actualiza cada vez que se intenta calcular las notas.\nAgrega estudiantes o carga un curso ya creado.")
        frame_superior.configure(bg="tomato")
        mensaje_al_usuario.configure(bg="tomato")
    elif not nota_minima.valor() < nota_maxima.valor():
        mensaje_al_usuario.config(text="Este mensaje se actualiza cada vez que se intenta calcular las notas.\nLa nota mínima debe ser menor que la nota máxima.")
        frame_superior.configure(bg="tomato")
        mensaje_al_usuario.configure(bg="tomato")
    elif not nota_minima.valor() < nota_aprobacion.valor():
        mensaje_al_usuario.config(text="Este mensaje se actualiza cada vez que se intenta calcular las notas.\nLa nota de aprobación debe ser mayor que la nota mínima.")
        frame_superior.configure(bg="tomato")
        mensaje_al_usuario.configure(bg="tomato")
    elif not nota_aprobacion.valor() < nota_maxima.valor():
        mensaje_al_usuario.config(text="Este mensaje se actualiza cada vez que se intenta calcular las notas.\nLa nota de aprobación debe ser menor que la nota máxima.")
        frame_superior.configure(bg="tomato")
        mensaje_al_usuario.configure(bg="tomato")
    elif not max(lista_de_puntajes) <= puntaje_maximo.valor():
        mensaje_al_usuario.config(text="Este mensaje se actualiza cada vez que se intenta calcular las notas.\nEl puntaje de uno o más estudiantes es mayor que el puntaje máximo.")
        frame_superior.configure(bg="tomato")
        mensaje_al_usuario.configure(bg="tomato")
    else:
        mensaje_al_usuario.config(text="Este mensaje se actualiza cada vez que se intenta calcular las notas.\nSe calcularon las notas exitosamente.")
        frame_superior.configure(bg="light green")
        mensaje_al_usuario.configure(bg="light green")
        return True

    



#FRAME SUPERIOR=============================================================================================================
#FRAME ESTUDIANTES==========================================================================================================

frame_estudiantes = ScrollableFrame(frame_base)

frame_estudiantes.pack(side="left", fill="both", expand=True)

class label_informacion:
    def __init__(self, columna, label):
        self.Label = Label(frame_estudiantes.scrollable_frame, text=label, font=("Helvetica", 12), background="grey", fg="white")
        self.Label.grid(sticky=N, row=0, column=columna)

nombre_estudiante = label_informacion(0, "Botones")
numero_estudiante = label_informacion(1, "Número del\nestudiante")
nombre_estudiante = label_informacion(2, "Nombre del estudiante")
puntaje_estudiante = label_informacion(3, "Puntaje")
nota_tradicional_estudiante = label_informacion(4, "Nota\ntradicional")
nota_normalizada_estudiante = label_informacion(5, "Nota\nnormalizada")

frame_estudiantes.scrollable_frame.grid_columnconfigure(0, minsize=150)
frame_estudiantes.scrollable_frame.grid_columnconfigure(1, minsize=100)
frame_estudiantes.scrollable_frame.grid_columnconfigure(2, minsize=350)
frame_estudiantes.scrollable_frame.grid_columnconfigure(3, minsize=100)
frame_estudiantes.scrollable_frame.grid_columnconfigure(4, minsize=120)
frame_estudiantes.scrollable_frame.grid_columnconfigure(5, minsize=120)

class Estudiante:
    def __init__(self, nombre=""):
        # El estudiante se agrega a la lista de los que se están mostrando
        global estudiantes_creados

        #Asigna número a estudiante en base a su número de creación. Tengo que sumar 1, de otro modo se borran los label del frame de abajo
        self.fila = len(estudiantes_creados)+1

        #Btón para eliminarlo de los que se están mostrando
        self.boton_eliminar = Button(frame_estudiantes.scrollable_frame, text="Quitar estudiante", command=self.eliminar, font=("Helvetica", 12))
        self.boton_eliminar.grid(row=self.fila, column=0, pady=3)

        # Label número de estudiante
        self.Label_numero = Label(frame_estudiantes.scrollable_frame, text=self.fila, font=("Helvetica", 12))
        self.Label_numero.grid(row=self.fila, column=1, pady=3)

        # Caja del nombre
        self.Entry_nombre = Entry(frame_estudiantes.scrollable_frame, width=35, font=("Helvetica", 12))
        self.Entry_nombre.insert(END, nombre)
        self.Entry_nombre.grid(row=self.fila, column=2, pady=3)

        # Variable de la caja del puntaje
        self.variable = StringVar(value=0)
        self.variable.trace("w", self.quitar_letras)

        # Caja del puntaje
        self.Entry_puntaje = Entry(frame_estudiantes.scrollable_frame, textvariable=self.variable ,width=5, font=("Helvetica", 12))
        self.Entry_puntaje.grid(row=self.fila, column=3, pady=3)

        # Nota sin normalizar
        self.Label_nota_sin_normalizar = Label(frame_estudiantes.scrollable_frame, text="Sin calcular", font=("Helvetica", 12))
        self.Label_nota_sin_normalizar.grid(row=self.fila, column=4, pady=3)

        # Nota normalizada
        self.Label_nota_normalizada = Label(frame_estudiantes.scrollable_frame, text="Sin calcular", font=("Helvetica", 12))
        self.Label_nota_normalizada.grid(row=self.fila, column=5, pady=3)



    def quitar_letras(self, tipo, vacío, modo):
        #Quita lo no numérico
        contenido = ""
        for letra_numero in self.variable.get():
            try:
                letra_numero = int(letra_numero)
                contenido += str(letra_numero)
            except:
                pass
        self.variable.set(contenido)
        #Quita los ceros extras
        for numero in self.variable.get():
            if numero=="0" and len(self.variable.get())>1:
                self.variable.set(self.variable.get()[1:])
            else:
                break

    def actualizar_posicion(self, nueva_fila):
        self.fila=nueva_fila
        self.boton_eliminar.grid(row=nueva_fila, column=0, pady=3)
        self.Label_numero.grid(row=nueva_fila, column=1, pady=3)
        self.Entry_nombre.grid(row=nueva_fila, column=2, pady=3)
        self.Entry_puntaje.grid(row=nueva_fila, column=3, pady=3)
        self.Label_nota_sin_normalizar.grid(row=nueva_fila, column=4, pady=3)
        self.Label_nota_normalizada.grid(row=nueva_fila, column=5, pady=3)
        self.Label_numero.config(text=nueva_fila)

    def eliminar(self, *args):
        global estudiantes_creados
        estudiantes_creados.remove(self)
        posicion = 1
        for alumno in estudiantes_creados:
            alumno.actualizar_posicion(posicion)
            alumno.Label_nota_normalizada.config(text="Sin calcular")
            posicion += 1
        self.boton_eliminar.grid_forget()
        self.Label_numero.grid_forget()
        self.Entry_nombre.grid_forget()
        self.Entry_puntaje.grid_forget()
        self.Label_nota_sin_normalizar.grid_forget()
        self.Label_nota_normalizada.grid_forget()

        #Reinicia las medias y desviacioens estándar
        media_tradicional.Label_valor.config(text="Sin calcular")
        media_normalizada.Label_valor.config(text="Sin calcular")
        desviacion_estandar_tradicional.Label_valor.config(text="Sin calcular")
        desviacion_estandar_normalizada.Label_valor.config(text="Sin calcular")
        

    def puntaje(self):
        return int(self.variable.get())

    def __eq__(self, other):
        return self.fila==other.fila




diccionario_Fr_Z = {
0.001:  -3.09,
0.00104:  -3.08,
0.00107:  -3.07,
0.00111:  -3.06,
0.00114:  -3.05,
0.00118:  -3.04,
0.00122:  -3.03,
0.00126:  -3.02,
0.00131:  -3.01,
0.00135:  -3.0,
0.0014:  -2.99,
0.0015:  -2.97,
0.0016:  -2.95,
0.0017:  -2.93,
0.0018:  -2.92,
0.0019:  -2.9,
0.002:  -2.88,
0.0021:  -2.87,
0.0022:  -2.85,
0.0023:  -2.84,
0.0024:  -2.82,
0.0025:  -2.81,
0.0026:  -2.8,
0.0027:  -2.78,
0.0028:  -2.77,
0.0029:  -2.76,
0.003:  -2.75,
0.0031:  -2.74,
0.0032:  -2.73,
0.0033:  -2.72,
0.0034:  -2.71,
0.0035:  -2.7,
0.0036:  -2.69,
0.0037:  -2.68,
0.0038:  -2.67,
0.0039:  -2.66,
0.004:  -2.65,
0.0041:  -2.64,
0.0043:  -2.63,
0.0044:  -2.62,
0.0045:  -2.61,
0.0047:  -2.6,
0.0048:  -2.59,
0.0049:  -2.58,
0.0051:  -2.57,
0.0052:  -2.56,
0.0054:  -2.55,
0.0055:  -2.54,
0.0057:  -2.53,
0.0059:  -2.52,
0.006:  -2.51,
0.0062:  -2.5,
0.0064:  -2.49,
0.0066:  -2.48,
0.0068:  -2.47,
0.0069:  -2.46,
0.0071:  -2.45,
0.0073:  -2.44,
0.0075:  -2.43,
0.0078:  -2.42,
0.008:  -2.41,
0.0082:  -2.4,
0.0084:  -2.39,
0.0087:  -2.38,
0.0089:  -2.37,
0.0091:  -2.36,
0.0094:  -2.35,
0.0096:  -2.34,
0.0099:  -2.33,
0.0102:  -2.32,
0.0104:  -2.31,
0.0107:  -2.3,
0.011:  -2.29,
0.0113:  -2.28,
0.0116:  -2.27,
0.0119:  -2.26,
0.0122:  -2.25,
0.0125:  -2.24,
0.0129:  -2.23,
0.0132:  -2.22,
0.0136:  -2.21,
0.0139:  -2.2,
0.0143:  -2.19,
0.0146:  -2.18,
0.015:  -2.17,
0.0154:  -2.16,
0.0158:  -2.15,
0.0162:  -2.14,
0.0166:  -2.13,
0.017:  -2.12,
0.0174:  -2.11,
0.0179:  -2.1,
0.0183:  -2.09,
0.0188:  -2.08,
0.0192:  -2.07,
0.0197:  -2.06,
0.0202:  -2.05,
0.0207:  -2.04,
0.0212:  -2.03,
0.0217:  -2.02,
0.0222:  -2.01,
0.0228:  -2.0,
0.0233:  -1.99,
0.0239:  -1.98,
0.0244:  -1.97,
0.025:  -1.96,
0.0256:  -1.95,
0.0262:  -1.94,
0.0268:  -1.93,
0.0274:  -1.92,
0.0281:  -1.91,
0.0287:  -1.9,
0.0294:  -1.89,
0.0301:  -1.88,
0.0307:  -1.87,
0.0314:  -1.86,
0.0322:  -1.85,
0.0329:  -1.84,
0.0336:  -1.83,
0.0344:  -1.82,
0.0351:  -1.81,
0.0359:  -1.8,
0.0367:  -1.79,
0.0375:  -1.78,
0.0384:  -1.77,
0.0392:  -1.76,
0.0401:  -1.75,
0.0409:  -1.74,
0.0418:  -1.73,
0.0427:  -1.72,
0.0436:  -1.71,
0.0446:  -1.7,
0.0455:  -1.69,
0.0465:  -1.68,
0.0475:  -1.67,
0.0485:  -1.66,
0.0495:  -1.65,
0.0505:  -1.64,
0.0516:  -1.63,
0.0526:  -1.62,
0.0537:  -1.61,
0.0548:  -1.6,
0.0559:  -1.59,
0.0571:  -1.58,
0.0582:  -1.57,
0.0594:  -1.56,
0.0606:  -1.55,
0.0618:  -1.54,
0.063:  -1.53,
0.0643:  -1.52,
0.0655:  -1.51,
0.0668:  -1.5,
0.0681:  -1.49,
0.0694:  -1.48,
0.0708:  -1.47,
0.0721:  -1.46,
0.0735:  -1.45,
0.0749:  -1.44,
0.0764:  -1.43,
0.0778:  -1.42,
0.0793:  -1.41,
0.0808:  -1.4,
0.0823:  -1.39,
0.0838:  -1.38,
0.0853:  -1.37,
0.0869:  -1.36,
0.0885:  -1.35,
0.0901:  -1.34,
0.0918:  -1.33,
0.0934:  -1.32,
0.0951:  -1.31,
0.0968:  -1.3,
0.0985:  -1.29,
0.1003:  -1.28,
0.102:  -1.27,
0.1038:  -1.26,
0.1056:  -1.25,
0.1075:  -1.24,
0.1093:  -1.23,
0.1112:  -1.22,
0.1131:  -1.21,
0.1151:  -1.2,
0.117:  -1.19,
0.119:  -1.18,
0.121:  -1.17,
0.123:  -1.16,
0.1251:  -1.15,
0.1271:  -1.14,
0.1292:  -1.13,
0.1314:  -1.12,
0.1335:  -1.11,
0.1357:  -1.1,
0.1379:  -1.09,
0.1401:  -1.08,
0.1423:  -1.07,
0.1446:  -1.06,
0.1469:  -1.05,
0.1492:  -1.04,
0.1515:  -1.03,
0.1539:  -1.02,
0.1562:  -1.01,
0.1587:  -1.0,
0.1611:  -0.99,
0.1635:  -0.98,
0.166:  -0.97,
0.1685:  -0.96,
0.1711:  -0.95,
0.1736:  -0.94,
0.1762:  -0.93,
0.1788:  -0.92,
0.1814:  -0.91,
0.1841:  -0.9,
0.1867:  -0.89,
0.1894:  -0.88,
0.1922:  -0.87,
0.1949:  -0.86,
0.1977:  -0.85,
0.2005:  -0.84,
0.2033:  -0.83,
0.2061:  -0.82,
0.209:  -0.81,
0.2119:  -0.8,
0.2148:  -0.79,
0.2177:  -0.78,
0.2206:  -0.77,
0.2236:  -0.76,
0.2266:  -0.75,
0.2296:  -0.74,
0.2327:  -0.73,
0.2358:  -0.72,
0.2389:  -0.71,
0.242:  -0.7,
0.2451:  -0.69,
0.2483:  -0.68,
0.2514:  -0.67,
0.2546:  -0.66,
0.2578:  -0.65,
0.2611:  -0.64,
0.2643:  -0.63,
0.2676:  -0.62,
0.2709:  -0.61,
0.2743:  -0.6,
0.2776:  -0.59,
0.281:  -0.58,
0.2843:  -0.57,
0.2877:  -0.56,
0.2912:  -0.55,
0.2946:  -0.54,
0.2981:  -0.53,
0.3015:  -0.52,
0.305:  -0.51,
0.3085:  -0.5,
0.3121:  -0.49,
0.3156:  -0.48,
0.3192:  -0.47,
0.3228:  -0.46,
0.3264:  -0.45,
0.33:  -0.44,
0.3336:  -0.43,
0.3372:  -0.42,
0.3409:  -0.41,
0.3446:  -0.4,
0.3483:  -0.39,
0.352:  -0.38,
0.3557:  -0.37,
0.3594:  -0.36,
0.3632:  -0.35,
0.3669:  -0.34,
0.3707:  -0.33,
0.3745:  -0.32,
0.3783:  -0.31,
0.3821:  -0.3,
0.3859:  -0.29,
0.3897:  -0.28,
0.3936:  -0.27,
0.3974:  -0.26,
0.4013:  -0.25,
0.4052:  -0.24,
0.409:  -0.23,
0.4129:  -0.22,
0.4168:  -0.21,
0.4207:  -0.2,
0.4247:  -0.19,
0.4286:  -0.18,
0.4325:  -0.17,
0.4364:  -0.16,
0.4404:  -0.15,
0.4443:  -0.14,
0.4483:  -0.13,
0.4522:  -0.12,
0.4562:  -0.11,
0.4602:  -0.1,
0.4641:  -0.09,
0.4681:  -0.08,
0.4721:  -0.07,
0.4761:  -0.06,
0.4801:  -0.05,
0.484:  -0.04,
0.488:  -0.03,
0.492:  -0.02,
0.496:  -0.01,
0.5:  0,
0.504:  0.01,
0.508:  0.02,
0.512:  0.03,
0.516:  0.04,
0.5199:  0.05,
0.5239:  0.06,
0.5279:  0.07,
0.5319:  0.08,
0.5359:  0.09,
0.5398:  0.1,
0.5438:  0.11,
0.5478:  0.12,
0.5517:  0.13,
0.5557:  0.14,
0.5596:  0.15,
0.5636:  0.16,
0.5675:  0.17,
0.5714:  0.18,
0.5753:  0.19,
0.5793:  0.2,
0.5832:  0.21,
0.5871:  0.22,
0.591:  0.23,
0.5948:  0.24,
0.5987:  0.25,
0.6026:  0.26,
0.6064:  0.27,
0.6103:  0.28,
0.6141:  0.29,
0.6179:  0.3,
0.6217:  0.31,
0.6255:  0.32,
0.6293:  0.33,
0.6331:  0.34,
0.6368:  0.35,
0.6406:  0.36,
0.6443:  0.37,
0.648:  0.38,
0.6517:  0.39,
0.6554:  0.4,
0.6591:  0.41,
0.6628:  0.42,
0.6664:  0.43,
0.67:  0.44,
0.6736:  0.45,
0.6772:  0.46,
0.6808:  0.47,
0.6844:  0.48,
0.6879:  0.49,
0.6915:  0.5,
0.695:  0.51,
0.6985:  0.52,
0.7019:  0.53,
0.7054:  0.54,
0.7088:  0.55,
0.7123:  0.56,
0.7157:  0.57,
0.719:  0.58,
0.7224:  0.59,
0.7257:  0.6,
0.7291:  0.61,
0.7324:  0.62,
0.7357:  0.63,
0.7389:  0.64,
0.7422:  0.65,
0.7454:  0.66,
0.7486:  0.67,
0.7517:  0.68,
0.7549:  0.69,
0.758:  0.7,
0.7611:  0.71,
0.7642:  0.72,
0.7673:  0.73,
0.7704:  0.74,
0.7734:  0.75,
0.7764:  0.76,
0.7794:  0.77,
0.7823:  0.78,
0.7852:  0.79,
0.7881:  0.8,
0.791:  0.81,
0.7939:  0.82,
0.7967:  0.83,
0.7995:  0.84,
0.8023:  0.85,
0.8051:  0.86,
0.8078:  0.87,
0.8106:  0.88,
0.8133:  0.89,
0.8159:  0.9,
0.8186:  0.91,
0.8212:  0.92,
0.8238:  0.93,
0.8264:  0.94,
0.8289:  0.95,
0.8315:  0.96,
0.834:  0.97,
0.8365:  0.98,
0.8389:  0.99,
0.8413:  1.0,
0.8438:  1.01,
0.8461:  1.02,
0.8485:  1.03,
0.8508:  1.04,
0.8531:  1.05,
0.8554:  1.06,
0.8577:  1.07,
0.8599:  1.08,
0.8621:  1.09,
0.8643:  1.1,
0.8665:  1.11,
0.8686:  1.12,
0.8708:  1.13,
0.8729:  1.14,
0.8749:  1.15,
0.877:  1.16,
0.879:  1.17,
0.881:  1.18,
0.883:  1.19,
0.8849:  1.2,
0.8869:  1.21,
0.8888:  1.22,
0.8907:  1.23,
0.8925:  1.24,
0.8944:  1.25,
0.8962:  1.26,
0.898:  1.27,
0.8997:  1.28,
0.9015:  1.29,
0.9032:  1.3,
0.9049:  1.31,
0.9066:  1.32,
0.9082:  1.33,
0.9099:  1.34,
0.9115:  1.35,
0.9131:  1.36,
0.9147:  1.37,
0.9162:  1.38,
0.9177:  1.39,
0.9192:  1.4,
0.9207:  1.41,
0.9222:  1.42,
0.9236:  1.43,
0.9251:  1.44,
0.9265:  1.45,
0.9279:  1.46,
0.9292:  1.47,
0.9306:  1.48,
0.9319:  1.49,
0.9332:  1.5,
0.9345:  1.51,
0.9357:  1.52,
0.937:  1.53,
0.9382:  1.54,
0.9394:  1.55,
0.9406:  1.56,
0.9418:  1.57,
0.9429:  1.58,
0.9441:  1.59,
0.9452:  1.6,
0.9463:  1.61,
0.9474:  1.62,
0.9484:  1.63,
0.9495:  1.64,
0.9505:  1.65,
0.9515:  1.66,
0.9525:  1.67,
0.9535:  1.68,
0.9545:  1.69,
0.9554:  1.7,
0.9564:  1.71,
0.9573:  1.72,
0.9582:  1.73,
0.9591:  1.74,
0.9599:  1.75,
0.9608:  1.76,
0.9616:  1.77,
0.9625:  1.78,
0.9633:  1.79,
0.9641:  1.8,
0.9649:  1.81,
0.9656:  1.82,
0.9664:  1.83,
0.9671:  1.84,
0.9678:  1.85,
0.9686:  1.86,
0.9693:  1.87,
0.9699:  1.88,
0.9706:  1.89,
0.9713:  1.9,
0.9719:  1.91,
0.9726:  1.92,
0.9732:  1.93,
0.9738:  1.94,
0.9744:  1.95,
0.9750:  1.96,
0.9756:  1.97,
0.9761:  1.98,
0.9767:  1.99,
0.9772:  2.0,
0.9778:  2.01,
0.9783:  2.02,
0.9788:  2.03,
0.9793:  2.04,
0.9798:  2.05,
0.9803:  2.06,
0.9808:  2.07,
0.9812:  2.08,
0.9817:  2.09,
0.9821:  2.1,
0.9826:  2.11,
0.9830:  2.12,
0.9834:  2.13,
0.9838:  2.14,
0.9842:  2.15,
0.9846:  2.16,
0.9850:  2.17,
0.9854:  2.18,
0.9857:  2.19,
0.9861:  2.2,
0.9864:  2.21,
0.9868:  2.22,
0.9871:  2.23,
0.9875:  2.24,
0.9878:  2.25,
0.9881:  2.26,
0.9884:  2.27,
0.9887:  2.28,
0.9890:  2.29,
0.9893:  2.3,
0.9896:  2.31,
0.9898:  2.32,
0.9901:  2.33,
0.9904:  2.34,
0.9906:  2.35,
0.9909:  2.36,
0.9911:  2.37,
0.9913:  2.38,
0.9916:  2.39,
0.9918:  2.4,
0.9920:  2.41,
0.9922:  2.42,
0.9925:  2.43,
0.9927:  2.44,
0.9929:  2.45,
0.9931:  2.46,
0.9932:  2.47,
0.9934:  2.48,
0.9936:  2.49,
0.9938:  2.5,
0.9940:  2.51,
0.9941:  2.52,
0.9943:  2.53,
0.9945:  2.54,
0.9946:  2.55,
0.9948:  2.56,
0.9949:  2.57,
0.9951:  2.58,
0.9952:  2.59,
0.9953:  2.6,
0.9955:  2.61,
0.9956:  2.62,
0.9957:  2.63,
0.9959:  2.64,
0.9960:  2.65,
0.9961:  2.66,
0.9962:  2.67,
0.9963:  2.68,
0.9964:  2.69,
0.9965:  2.7,
0.9966:  2.71,
0.9967:  2.72,
0.9968:  2.73,
0.9969:  2.74,
0.9970:  2.75,
0.9971:  2.76,
0.9972:  2.77,
0.9973:  2.78,
0.9974:  2.79,
0.9974:  2.8,
0.9975:  2.81,
0.9976:  2.82,
0.9977:  2.83,
0.9977:  2.84,
0.9978:  2.85,
0.9979:  2.86,
0.9979:  2.87,
0.9980:  2.88,
0.9981:  2.89,
0.9981:  2.9,
0.9982:  2.91,
0.9982:  2.92,
0.9983:  2.93,
0.9984:  2.94,
0.9984:  2.95,
0.9985:  2.96,
0.9985:  2.97,
0.9986:  2.98,
0.9986:  2.99,
0.99865:  3.0,
0.99869: 3.01,
0.99874: 3.02,
0.99878: 3.03,
0.99882: 3.04,
0.99886: 3.05,
0.99889: 3.06,
0.99893: 3.07,
0.99896: 3.08,
0.99900: 3.09
}

frame_base.mainloop()

