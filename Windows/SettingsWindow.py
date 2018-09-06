from tkinter import Toplevel, StringVar
from tkinter.ttk import Frame, Label, Button
from CustomWidgets.WidgetTable import WidgetTable
from Windows import ProjectSettingsWindow

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
            pattern=[StringVar, StringVar, StringVar,
                     {'text': "Edit", 'func': self._edit_project_row,
                      'func_has_row_ctx': True}],
            widgets_pattern=[Label, Label, Label, Button],
            data_array=[self.settings_view(s) for s in self.proj_settings],
            adder_script=self._add_project_row,
            remove_script=self._remove_row)
        self.projects_table.grid(column=0, row=0)
        self.defaults_list_frame.grid(column=0, row=2, columnspan=2)
        Button(frame, text="Exit", command=self.exit).grid(row=3, column=0,
                                                           sticky='w')

    @staticmethod
    def settings_view(settings):
        # returns a condensed view version fo the project settings to be passed
        # to the WidgetTable as the intial values
        dt = settings.get('DefaultTriggers', None)
        if dt is not None:
            if dt == [[]]:
                return [settings.get('ProjectID', 'None'),
                        settings.get('ProjectTitle', 'None'),
                        '', None]
            else:
                return [settings.get('ProjectID', 'None'),
                        settings.get('ProjectTitle', 'None'),
                        ','.join([str(i[0]) for i in dt]), None]
        else:
            return ['', '']

    def _add_project_row(self):
        proj_settings = dict()
        ProjectSettingsWindow(self, proj_settings)
        if proj_settings != dict():
            if (proj_settings.get('ProjectID', '') not in
                    [d.get('ProjectID', '') for d in self.proj_settings]):
                self.proj_settings.append(proj_settings)
            return self.settings_view(proj_settings)
        else:
            raise ValueError

    def _edit_project_row(self, idx):
        curr_row = idx
        proj_settings = self.proj_settings[curr_row]
        ProjectSettingsWindow(self, proj_settings)
        self.projects_table.set_row(curr_row,
                                    self.settings_view(proj_settings))
        self.proj_settings[curr_row] = proj_settings

    def _remove_row(self, idx):
        del self.proj_settings[idx]

    def exit(self):
        self._write_settings()
        self.withdraw()
        self.update_idletasks()
        self.master.focus_set()
        self.master.file_treeview.selection_toggle(
            self.master.file_treeview.selection())
        self.destroy()

    def _write_settings(self):
        with open('proj_settings.pkl', 'wb') as settings:
            print('writing settings')
            pickle.dump(self.proj_settings, settings)
