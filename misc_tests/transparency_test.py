from tkinter import Tk, Frame, PhotoImage, Label
from tkinter import Button as tkButton
from tkinter.ttk import Style, Button

from PIL import Image, ImageTk

root = Tk()

def RBGAImage(path):
    return Image.open(path).convert("RGBA")


class main(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.master = master

        self.num = 1
        
        #icon = RBGAImage("biscuit.gif")
        self.icon = Image.open("assets/remove_row_trans.png")
        self.icon1 = self.icon.resize((51, 51), Image.LANCZOS)
        self.icon1 = ImageTk.PhotoImage(self.icon1)
        self.icon2 = self.icon.resize((51, 51))
        self.icon2 = ImageTk.PhotoImage(self.icon2)
        self.icon3 = self.icon.resize((51, 51), Image.HAMMING)
        self.icon3 = ImageTk.PhotoImage(self.icon3)
        self.icon4 = self.icon.resize((51, 51), Image.BICUBIC)
        self.icon4 = ImageTk.PhotoImage(self.icon4)
        #self.icon = PhotoImage(file="biscuit.png")
        #self.icon = self.icon.subsample(10)
        #self.delete_icon = ImageTk.PhotoImage(icon)

        Label(self.master, text="Click the biscuit ->").pack(side='left')

        self.btn1 = tkButton(self.master, bg='blue',
                             command=self.printer,
                             relief='flat',
                             highlightbackground="blue")
        self.btn1.config(image=self.icon1)
        self.btn1.pack(side='left')
        self.btn2 = tkButton(self.master, bg='blue',
                             command=self.printer,
                             relief='flat',
                             highlightbackground="blue")
        self.btn2.config(image=self.icon2)
        self.btn2.pack(side='left')
        self.btn3 = tkButton(self.master, bg='blue',
                             command=self.printer,
                             relief='flat',
                             highlightbackground="blue")
        self.btn3.config(image=self.icon3)
        self.btn3.pack(side='left')
        self.btn4 = tkButton(self.master, bg='blue',
                             command=self.printer,
                             relief='flat',
                             highlightbackground="blue")
        self.btn4.config(image=self.icon4)
        self.btn4.pack(side='left')

    def printer(self):
        print(self.num)
        self.num += 1

if __name__ == "__main__":
    app = main(root)
    app.mainloop()