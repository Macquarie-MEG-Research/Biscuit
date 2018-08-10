from os.path import join, splitext
from mne.io import read_raw_kit

from tkinter import *
from tkinter import filedialog

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from numpy import dot, append, asarray

from ToBIDS import process_folder

from mne.viz.utils import _plot_sensors

from timeit import default_timer as timer

root = Tk()

class GUI(Frame):
    def __init__(self, master):
        self.master = master
        Frame.__init__(self, self.master)

        self.createWidgets()

    def createWidgets(self):
        # frame with buttons
        button_frame = Frame(self.master)
        open_button = Button(button_frame, text="OPEN", command=self.open)
        open_button.pack(side=LEFT)
        self.apply_button = Button(button_frame, text="APPLY", command=self.apply, state=DISABLED)
        self.apply_button.pack(side = LEFT)
        self.view_button = Button(button_frame, text="VIEW", command=self.view, state=DISABLED)
        self.view_button.pack(side=LEFT)
        quit_button = Button(button_frame, text="QUIT", command=self.quit)
        quit_button.pack(side=LEFT)
        button_frame.pack()

    def allow_presses(self):
        self.apply_button.config(state = NORMAL)
        self.view_button.config(state = NORMAL)

    def open(self):
        self.path_name = filedialog.askdirectory(title="Specify folder containing MEG files")
        #self.path_name = "C:\\Users\\MQ20184158\\Documents\\MEG data\\rs_test_data_for_matt"
        #path_name = "C:\\Users\\msval\\Desktop\\rs_test_data_for_matt"

        files, valid = process_folder(self.path_name, validate = True)

        self.MEG_data = dict()

        if valid:
            for prefix in files:
                # these will each be separate things
                pre_files = files[prefix]
                t1 = timer()
                # loading in the data takes ~ 0.5s
                self.MEG_data[prefix] = (read_raw_kit(pre_files['.con'][0].path,
                                                      mrk = pre_files['.mrk'][0].path,
                                                      elp = pre_files['.elp'][0].path,
                                                      hsp = pre_files['.hsp'][0].path))
                t2 = timer()
                print(t2 - t1, 'time')
            print("Files loaded fine.")
            # let the view and apply buttons be press-able
            self.allow_presses()
            for prefix in files:
                print(self.MEG_data[prefix].info)
        else:
            print("Invalid folder selected!")

    def view(self):
        # original data:
        for prefix in self.MEG_data:
            t = self.MEG_data[prefix].info['dev_head_t']
            trans = t['trans']
            orig_data = asarray([ch['loc'][:3] for ch in self.MEG_data[prefix].info['chs']])
            orig_names = ['MEG {0}'.format(str(i).zfill(3)) for i in range(1, 161)]
            new_data = asarray([dot(trans, append(ch['loc'][:3], [0])) for ch in self.MEG_data[prefix].info['chs']])
            new_names = ['MEG new {0}'.format(str(i).zfill(3)) for i in range(1, 161)]

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(orig_data[:, 0], orig_data[:, 1], orig_data[:, 2], c='red')      # original
            ax.scatter(new_data[:, 0], new_data[:, 1], new_data[:, 2], c='blue')        # transformed

            plt.show()

    def apply(self):
        #print(MEG_data.info)

        for prefix in self.MEG_data:
            t = self.MEG_data[prefix].info['dev_head_t']
            trans = t['trans']
            #print(trans)

            #print(dot(t['trans'], array([0,0,1,0])))        # this gives us the transformed coordinate basis
            with open(join(self.path_name, '{0}_output.txt'.format(prefix)), 'w') as out_file:
                out_file.writelines(['Channel Name', '\t', 'x', '\t', 'y', '\t', 'z', '\n'])
                for channel in self.MEG_data[prefix].info['chs']:
                    new_pos = dot(trans, append(channel['loc'][:3], [0]))
                    out_file.writelines([channel['ch_name'], '\t', str(new_pos[0]), '\t', str(new_pos[1]), '\t', str(new_pos[2]), '\n'])

            # output the original points for comparison:
            with open(join(self.path_name, '{0}_output_original.txt'.format(prefix)), 'w') as out_file:
                out_file.writelines(['Channel Name', '\t', 'x', '\t', 'y', '\t', 'z', '\n'])
                for channel in self.MEG_data[prefix].info['chs']:
                    b = channel['loc'][:3]
                    out_file.writelines([channel['ch_name'], '\t', str(b[0]), '\t', str(b[1]), '\t', str(b[2]), '\n'])

    def quit(self):
        self.master.destroy()

app = GUI(master=root)
app.mainloop()