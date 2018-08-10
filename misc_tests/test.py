from tkinter import *

def createBox(window):
    list_ = ['CARGA', 'MAQUINA', 'SOLTAR']
    for i in range(3):
        mybox = LabelFrame(window, padx=5, pady=4)
        mybox.grid(row=i, column=0)
        createWindow(mybox, list_[i], i)

def createWindow(box, lt_actual, i):
    canvas = Canvas(box, borderwidth=0)
    frame = Frame(canvas)
    vsb = Scrollbar(box, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set, width=1200, heigh=80)       

    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((4,4), window=frame, anchor="nw", tags="frame")

    # be sure that we call OnFrameConfigure on the right canvas
    frame.bind("<Configure>", lambda event, canvas=canvas: OnFrameConfigure(canvas))

    fillWindow(lt_actual, frame)

def fillWindow(lt_ver, frame):
    piezas = ['time: 39.41597 BT: 3025.5923', 'time: 21.637377 BT: 3025.5923', 'time: 52.185192 BT: 3025.5923', 'time: 57.804752 BT: 3025.5923', 'time: 47.700306 BT: 3025.5923', 'time: 21.1827 BT: 3025.5923', 'time: 35.244156 BT: 3025.5923', 'time: 47.26321 BT: 3025.5923']
    fechaentrada = ['26-02-2014', '26-02-2014', '26-02-2014', '26-02-2014', '26-02-2014', '26-02-2014', '26-02-2014', '21-02-2014']
    fechasalida = ['26-02-2014', '26-02-2014', '26-02-2014', '26-02-2014', '26-02-2014', '26-02-2014', '26-02-2014', '21-02-2014']
    horacomienzo = ['12:00', '12:39', '01:00', '01:52', '02:49', '03:36', '03:57', '12:00']
    horafinal = ['12:39', '01:00', '01:52', '02:49', '03:36', '03:57', '04:32', '12:47']
    ide = [0, 1, 2, 3, 4, 5, 6, 7]

    idpieza_w1 = Label(frame, text = "Id", width=20, font="bold")
    idpieza_w1.grid(row=0, column=0)
    pieza_w1 = Label(frame, text = "Pieza", width=20, font="bold")
    pieza_w1.grid(row=0, column=1)
    fechainiciopromo_w1 = Label(frame, text = "Dia inicio " + str(lt_ver), width=20, font="bold")
    fechainiciopromo_w1.grid(row=0, column=2)
    horainiciopromo_w1 = Label(frame, text = "Hora inicio "  + str(lt_ver), width=20, font="bold")
    horainiciopromo_w1.grid(row=0, column=3)
    fechafinalpromo_w1 = Label(frame, text = "Dia fin carga "  + str(lt_ver), width=20, font="bold")
    fechafinalpromo_w1.grid(row=0, column=4)
    horafinalpromo_w1 = Label(frame, text = "Hora final carga "  + str(lt_ver), width=20, font="bold")
    horafinalpromo_w1.grid(row=0, column=5)

    for i in range(len(piezas)):
        idtextos_w1 = Label(frame, text=str(ide[i]))
        idtextos_w1.grid(row=i+1, column=0)
        textos_w1 = Label(frame, text=str(piezas[i]))
        textos_w1.grid(row=i+1, column=1)
        fechainiciogrid_w1 = Label(frame, text=str(fechaentrada[i]))
        fechainiciogrid_w1.grid(row=i+1, column=2)
        horainiciogrid_w1 = Label(frame, text=str(horacomienzo[i]))
        horainiciogrid_w1.grid(row=i+1, column=3)
        fechafinalgrid_w1 = Label(frame, text=str(fechasalida[i]))
        fechafinalgrid_w1.grid(row=i+1, column=4)
        horafinalgrid_w1 = Label(frame, text=str(horafinal[i]))
        horafinalgrid_w1.grid(row=i+1, column=5)

def OnFrameConfigure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))


tk = Tk()

createBox(tk)

tk.mainloop()