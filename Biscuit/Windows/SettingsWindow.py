from tkinter import Toplevel, StringVar
from tkinter.ttk import Frame, Label, Button
import os.path as path
import pickle
from platform import system as os_name

from Biscuit.CustomWidgets.WidgetTable import WidgetTable
from Biscuit.Windows import ProjectSettingsWindow
from Biscuit.utils.constants import OSCONST


class SettingsWindow(Toplevel):
    """
    The popup window that lists all the different project defaults.
    New defaults can be added for each project and are added to the
    WidgetTable
    """
    def __init__(self, master, settings, proj_settings):
        self.master = master
        Toplevel.__init__(self, self.master)
        self.withdraw()
        if master.winfo_viewable():
            self.transient(master)

        self.title('Project Settings')

        self.proj_settings_file = path.join(OSCONST.USRDIR,
                                            'proj_settings.pkl')

        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.settings = settings
        self.proj_settings = proj_settings

        self._create_widgets()

        self.deiconify()
        self.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def _create_widgets(self):
        frame = Frame(self)
        frame.grid(sticky='nsew')

        Label(frame, text="Project defaults").grid(column=0, row=0,
                                                   columnspan=2)
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
        self.projects_table.grid(column=0, row=0, sticky='nsew')
        self.defaults_list_frame.grid(column=0, row=1, columnspan=2,
                                      sticky='nsew')
        Button(frame, text="Save and Exit",
               command=self.save_and_exit).grid(row=2, column=0, sticky='se')
        Button(frame, text="Cancel",
               command=self.exit).grid(row=2, column=1, sticky='sw')

        self.defaults_list_frame.grid_rowconfigure(0, weight=1)
        self.defaults_list_frame.grid_columnconfigure(0, weight=1)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    @staticmethod
    def settings_view(settings):
        # TODO: make this much nicer...
        # returns a condensed view version of the project settings to be passed
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
            return ['', '', '', None]

    def _add_project_row(self):
        proj_settings = dict()
        if os_name() == 'Windows':
            ProjectSettingsWindow(self.master, proj_settings)
        else:
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
        # TODO: figure out why there is this weird asymmetry...
        if os_name() == 'Windows':
            ProjectSettingsWindow(self.master, proj_settings)
        else:
            ProjectSettingsWindow(self, proj_settings)
        self.projects_table.set_row(curr_row,
                                    self.settings_view(proj_settings))
        self.proj_settings[curr_row] = proj_settings

    def _remove_row(self, idx):
        del self.proj_settings[idx]

    def save_and_exit(self):
        self._write_settings()
        self.exit()

    def exit(self):
        # TODO: popup window notifying that any unsaved changes will be lost?
        self.withdraw()
        self.update_idletasks()
        self.master.focus_set()
        self.destroy()

    def _write_settings(self):
        with open(self.proj_settings_file, 'wb') as settings:
            print('writing settings')
            pickle.dump(self.proj_settings, settings)
