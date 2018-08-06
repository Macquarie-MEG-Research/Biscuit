from tkinter import Toplevel, StringVar, PhotoImage
from tkinter.ttk import Frame, Label, Button, Separator, Style
from CustomWidgets.WidgetTable import WidgetTable
from Windows.ProjectSettingsWindow import ProjectSettingsWindow

import pickle

""" A lot of the code here will be overhauled at some point once we have the
code set up to handle writing the readme file with general project settings.
"""


class SettingsWindow(Toplevel):
    def __init__(self, master, settings, proj_settings):
        print(proj_settings, 'ps')
        self.master = master
        Toplevel.__init__(self, self.master)
        self.withdraw()
        if master.winfo_viewable():
            self.transient(master)

        self.title('Project Settings')

        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.deiconify()
        self.focus_set()

        self.settings = settings
        self.proj_settings = proj_settings

        self.delete_icon = PhotoImage(file="assets/remove_row.png")

        self.t_style = Style()
        self.t_style.configure('Transp.TButton', borderwidth=0, relief='flat',
                               padding=0)

        self._create_widgets()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def _create_widgets(self):
        frame = Frame(self)
        frame.grid()
        Label(frame, text="Project defaults").grid(column=0, row=0)
        self.defaults_list_frame = Frame(frame, borderwidth=2,
                                         relief='ridge')
        self.projects_table = WidgetTable(
            self.defaults_list_frame,
            headings=["Project ID", "Project Title", "Default Triggers",
                      "      "],
            row_vars=[StringVar, StringVar, StringVar,
                      ("Edit", self._edit_project_row)],
            entry_types=[Label, Label, Label, Button],
            data_array=[self.settings_view(s) for s in self.proj_settings],
            adder_script=self._add_project_row)
        self.projects_table.grid(column=0, row=0)
        self.defaults_list_frame.grid(column=0, row=2, columnspan=2)

    @staticmethod
    def settings_view(settings):
        # returns a condensed view version fo the project settings to be passed
        # to the WidgetTable as the intial values
        dt = settings.get('DefaultTriggers', [[]])
        return [settings.get('ProjectID', 'None'),
                settings.get('ProjectTitle', 'None'),
                ','.join([str(i[0]) for i in dt]), None]

    def _add_project_row(self):
        proj_settings = dict()
        # this will need to be made to block...
        ProjectSettingsWindow(self, proj_settings)
        if proj_settings != dict():
            if (proj_settings.get('ProjectID', '') not in
                    [d.get('ProjectID', '') for d in self.proj_settings]):
                self.proj_settings.append(proj_settings)
            return self.settings_view(proj_settings)
        else:
            raise ValueError

    def _edit_project_row(self):
        curr_row = self.projects_table.curr_row()
        proj_settings = self.proj_settings[curr_row]
        ProjectSettingsWindow(self, proj_settings)
        self.projects_table.set_row(curr_row,
                                    self.settings_view(proj_settings))
        self.proj_settings[curr_row] = proj_settings

    def _add_defaults_row(self, data):
        """
            Adds a new row to the view.
            data is a dictionary with keys 'ID' and 'triggers'
        """
        frame = self.defaults_list_frame
        rows = frame.grid_size()[1]
        Label(self.defaults_list_frame,
              text=data.get('ID', '')).grid(column=0, row=rows)
        Separator(self.defaults_list_frame,
                  orient='vertical').grid(column=1, row=0, rowspan=rows + 1,
                                          sticky='ns')
        Label(self.defaults_list_frame,
              text=data.get('triggers', '')).grid(column=2, row=rows)
        Separator(self.defaults_list_frame,
                  orient='vertical').grid(column=3, row=0, rowspan=rows + 1,
                                          sticky='ns')
        Label(self.defaults_list_frame,
              text=data.get('descriptions', '')).grid(column=4, row=rows)

    def exit(self):
        self._write_settings()
        self.withdraw()
        self.update_idletasks()
        self.master.focus_set()
        self.destroy()

    def _write_settings(self):
        with open('proj_settings.pkl', 'wb') as settings:
            pickle.dump(self.proj_settings, settings)