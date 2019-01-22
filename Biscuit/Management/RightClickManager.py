from tkinter import Menu, StringVar, messagebox, simpledialog, filedialog
import os.path as path
import re

from BIDSHandler import BIDSTree, Project, Subject, Session

from Biscuit.FileTypes import con_file, Folder, BIDSContainer
from Biscuit.utils.utils import create_folder, assign_bids_folder
from Biscuit.Windows.SendFilesWindow import SendFilesWindow

# pattern to match with folder names to determine if the folder is the result
# of the export process.
# This is to allow the right-click context to upload the data to the archive.
BIDS_PATTERN = re.compile("BIDS-[0-9]{4}-[0-9]{2}")


class RightClick():
    def __init__(self, parent, context):
        self.parent = parent

        # create a popup menu
        self.popup_menu = Menu(self.parent, tearoff=0)

        self.prev_selection = ()
        self.curr_selection = ()

        self.progress = StringVar()
        self.progress.set('None')

        self.context = context

#region public methods

    def popup(self, event):
        self._add_options()
        self.popup_menu.post(event.x_root, event.y_root)

    def set_current_selected(self):
        # keep track of the files selected each time a right-click occurs
        if self.prev_selection != self.curr_selection:
            # assign the previous set of selected files if they have changed
            self.prev_selection = self.curr_selection
        # now get the current set of selected files
        self.curr_selection = self.parent.file_treeview.selection()

    def undraw(self, event):
        self.popup_menu.unpost()

#region private methods

    def _add_options(self):
        # a context dependent function to only add options that are applicable
        # to the current situation.
        # first, remove any currently visible entries in the menu so we can
        # draw only the ones required by the current context
        self.popup_menu.delete(0, self.popup_menu.index("end"))
        # now, draw the manu elements required depending on context
        if self.parent.treeview_select_mode == "NORMAL":
            """
            if ("FOLDER" not in self.context and
                    self.context != set()):
                self.popup_menu.add_command(label="Create Folder",
                                            command=self._create_folder)
            """
            # add an option to associate the file as extra data to be included
            # in the bids output
            self.popup_menu.add_command(label="Add to BIDS output",
                                        command=self._add_to_bids)
            if ('.CON' in self.context or '.MRK' in self.context):
                self.popup_menu.add_command(label="Associate",
                                            command=self._associate_mrk)
            else:
                pass
                #self.popup_menu.add_command(label="Convert to BIDS",
                # command=self._folder_to_bids)
        elif self.parent.treeview_select_mode.startswith("ASSOCIATE"):
            self.popup_menu.add_command(label="Associate",
                                        command=self._associate_mrk)

        # give the option to associate one or more mrk files with all con files
        if (".MRK" in self.context and
                not self.parent.treeview_select_mode.startswith("ASSOCIATE")):
            self.popup_menu.add_command(
                label="Associate with all",
                command=lambda: self._associate_mrk(all_=True))
        # Add an option mark all selected .con files as junk
        if ".CON" in self.context and not self.context.is_mixed:
            self.popup_menu.add_command(label="Ignore files",
                                        command=self._ignore_cons)
            self.popup_menu.add_command(label="Include files",
                                        command=self._include_cons)
        if len(self.curr_selection) == 1:
            fname = self.parent.file_treeview.get_text(self.curr_selection[0])
            fpath = self.parent.file_treeview.get_filepath(
                self.curr_selection[0])
            # the selected object
            selected_obj = self.parent.preloaded_data[self.curr_selection[0]]
            # if the folder is a BIDS folder allow it to be uploaded to the
            # archive
            if BIDS_PATTERN.match(fname):
                self.popup_menu.add_command(
                    label="Upload to archive",
                    command=lambda: self._upload(selected_obj))
            # allow any folder to be sent to another location using the
            # BIDSMERGE functionality
            if isinstance(selected_obj,
                          (BIDSTree, Project, Subject, Session)):
                self.popup_menu.add_command(
                    label="Send to...",
                    command=lambda: self._send_to(selected_obj))
            if path.isdir(fpath):
                if isinstance(self.parent.preloaded_data.get(
                        self.curr_selection[0], None), Folder):
                    self.popup_menu.add_command(
                        label="Assign as BIDS folder",
                        command=self._toggle_bids_folder)

    def _add_to_bids(self):
        """Add the selected file(s) to the list of files to be retained across
        BIDS conversion.
        """
        sids = self.curr_selection
        parent_obj = None
        for sid in sids:
            parent = self.parent.file_treeview.parent(sid)
            fpath = self.parent.file_treeview.get_filepath(sid)
            parent_obj = self.parent.preloaded_data.get(parent, None)
            if isinstance(parent_obj, BIDSContainer):
                parent_obj.extra_files.append(fpath)

    # TODO: clean this up
    def _associate_mrk(self, all_=False):
        """
        Allow the user to select an .mrk file if a .con file has been
        selected (or vice-versa) and associate the mrk file with the con file.
        """
        con_files = []
        if all_ and self.parent.treeview_select_mode == "NORMAL":
            mrk_files = [self.parent.preloaded_data[sid] for sid in
                         self.curr_selection]
            # get the parent folder and then find all .con file children
            parent = self.parent.file_treeview.parent(mrk_files[0].ID)
            container = self.parent.preloaded_data[parent]
            for con in container.contained_files['.con']:
                con.hpi = mrk_files
                con.validate()
        else:
            if self.parent.treeview_select_mode == "NORMAL":
                # initialise the association process
                if '.MRK' in self.context and not self.context.is_mixed:
                    if self.context.group_size > 2:
                        messagebox.showerror(
                            "Error", ("Too many .mrk files selected. You may "
                                      "only select up to two .mrk files to be "
                                      "associated with any .con file"))
                        return
                    else:
                        if self.parent.settings.get(
                                'SHOW_ASSOC_MESSAGE', True):
                            messagebox.showinfo(
                                "Select",
                                ("Please select the .con file(s) "
                                 "associated with this file.\nOnce you "
                                 "have selected all required files, "
                                 "right click and press 'associate' "
                                 "again"))
                        self.parent.set_treeview_mode("ASSOCIATE-CON")
                elif '.CON' in self.context and not self.context.is_mixed:
                    if self.parent.settings.get(
                            'SHOW_ASSOC_MESSAGE', True):
                        messagebox.showinfo(
                            "Select",
                            ("Please select the .mrk file(s) associated "
                             "with this file.\nOnce you have selected "
                             "all required files, right click and press "
                             "'associate' again"))
                    self.parent.set_treeview_mode("ASSOCIATE-MRK")
                else:
                    messagebox.showerror("Error", "Invalid file selection")
            elif self.parent.treeview_select_mode.startswith("ASSOCIATE"):
                # complete the association process
                cont = None
                if self.parent.treeview_select_mode == "ASSOCIATE-CON":
                    # in this case expect the user to have selected one or
                    # more .mrk files
                    if ".CON" in self.context and not self.context.is_mixed:
                        # make sure that the .con and .mrk files are in the
                        # same folder
                        pid = self.parent.file_treeview.parent(
                            self.curr_selection[0])
                        for id_ in self.prev_selection + self.curr_selection:
                            if id_ not in self.parent.file_treeview.get_children(pid):  # noqa
                                cont = messagebox.askretrycancel(
                                    "Error",
                                    ("You have selected .con and .mrk file(s) "
                                     "in different folders. Please select the "
                                     "correct file or press 'cancel' to stop "
                                     "associating."))
                                if cont is False:
                                    self.parent.set_treeview_mode("NORMAL")
                                    return
                                else:
                                    return
                        # the previously selected files will be .mrk files:
                        mrk_files = [self.parent.preloaded_data[sid] for sid in
                                     self.prev_selection]
                        con_files = [self.parent.preloaded_data[sid] for sid in
                                     self.curr_selection]
                    else:
                        cont = messagebox.askretrycancel(
                            "Error", ("The files you selected are not valid.\n"
                                      "Would you like to select the correct "
                                      ".con files, or cancel?"))
                elif self.parent.treeview_select_mode == "ASSOCIATE-MRK":
                    # in this case expect the user to have selected one or more
                    #  .mrk files
                    if ".MRK" in self.context and not self.context.is_mixed:
                        # make sure that the .con and .mrk files are in the
                        # same folder
                        if self.context.group_size > 2:
                            # make sure no more than 2 mrk files selected
                            messagebox.showerror(
                                "Error", ("Too many .mrk files selected. You "
                                          "may only select up to two .mrk "
                                          "files to be associated with any "
                                          ".con file"))
                            return
                        pid = self.parent.file_treeview.parent(
                            self.curr_selection[0])
                        for id_ in self.prev_selection + self.curr_selection:
                            if id_ not in self.parent.file_treeview.get_children(pid):  # noqa
                                cont = messagebox.askretrycancel(
                                    "Error",
                                    ("You have selected .con and .mrk file(s) "
                                     "in different folders. Please select the "
                                     "correct file or press 'cancel' to stop "
                                     "associating."))
                                if cont is False:
                                    self.parent.set_treeview_mode("NORMAL")
                                    return
                                else:
                                    return
                        # the previously selected files will be .con files:
                        con_files = [self.parent.preloaded_data[sid] for sid in
                                     self.prev_selection]
                        mrk_files = [self.parent.preloaded_data[sid] for sid in
                                     self.curr_selection]
                    else:
                        cont = messagebox.askretrycancel(
                            "Error", ("The files you selected are not valid.\n"
                                      "Would you like to select the correct "
                                      ".mrk files, or cancel?"))

                # now associate the mrk files with the con files:
                if cont is None:
                    for cf in con_files:
                        cf.hpi = mrk_files
                        cf.validate()
                    # check if the con file is the currently selected file
                    if self.parent.treeview_select_mode == "ASSOCIATE-CON":
                        # if so, redraw the info panel and call the mrk
                        # association function so GUI is updated
                        self.parent.info_notebook.determine_tabs()
                        self.parent._highlight_associated_mrks(None)
                    self.parent.set_treeview_mode("NORMAL")
                if cont is False:
                    self.parent.set_treeview_mode("NORMAL")

    def _create_folder(self):
        """
        Create a folder at the currently open level. Clicking on a folder and
        selecting "create folder" will create a sibling folder, not child
        folder (not sure which to do?)
        """
        # get the current root depth
        if self.context != set():        # maybe??
            dir_ = path.dirname(
                self.parent.file_treeview.get_filepath(self.curr_selection[0]))
        else:
            dir_ = self.parent.settings['DATA_PATH']
        # ask the user for the folder name:
        folder_name = simpledialog.askstring("Folder Name",
                                             "Enter a folder Name:",
                                             parent=self.parent)
        # we will need to make sure the folder doesn't already exist at the
        # selected level
        if folder_name is not None:
            # create the folder
            full_path = path.join(dir_, folder_name)
            _, exists_already = create_folder(full_path)
            if not exists_already:
                try:
                    parent = self.parent.file_treeview.parent(
                        self.parent.selected_files[0])
                except IndexError:
                    # we have clicked outside the tree. Set the parent as the
                    # root
                    parent = ''
                self.parent.file_treeview.ordered_insert(
                    parent, values=['', str(full_path)], text=folder_name,
                    open=False)
                print('folder created!!')
            else:
                print('Folder already exists!')

    def _ignore_cons(self):
        """
        Set all selected con files to have 'Is Junk' as True
        """
        for sid in self.curr_selection:
            con = self.parent.preloaded_data.get(sid, None)
            if con is not None:
                if isinstance(con, con_file):
                    con.is_junk.set(True)
                    con.validate()

    def _include_cons(self):
        """
        Set all selected con files to have 'Is Junk' as False
        """
        for sid in self.curr_selection:
            con = self.parent.preloaded_data.get(sid, None)
            if con is not None:
                if isinstance(con, con_file):
                    con.is_junk.set(False)
                    con.validate()

    def _send_to(self, src_obj):
        """Send the selected object to another selected location."""
        dst = filedialog.askdirectory(title="Select BIDS folder")
        if dst != '':
            SendFilesWindow(self.parent, src_obj, dst, opt_verify=True)

    def _toggle_bids_folder(self):
        """Assign the selected folder as a BIDS-formatted folder.

        This will attempt to load the selected folder into a
        BIDSController.Project object. If this isn't possible an error will be
        raised stating this.
        """
        sid = self.curr_selection[0]
        fpath = self.parent.file_treeview.get_filepath(sid)

        bids_folder = assign_bids_folder(fpath, self.parent.file_treeview,
                                         self.parent.preloaded_data)
        if bids_folder is not None:
            # Only needed if the current selection is the same thing that has
            # been right-clicked.
            self.parent.info_notebook.data = [bids_folder]

    def _upload(self, src_obj):
        """Upload the selected object to the MEG_RAW archive."""
        dst = self.parent.settings.get("ARCHIVE_PATH", None)
        if dst is not None:
            SendFilesWindow(self.parent, src_obj, dst, set_copied=True)
