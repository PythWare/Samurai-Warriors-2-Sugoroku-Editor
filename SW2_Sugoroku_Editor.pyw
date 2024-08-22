import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

file1 = "SW2.iso"
sug_folders = ["icons", "SW2_Sugoroku", "Backup_Mod_Disabling"]
file_list = ["Sugoroku.SW2D", "Sugoroku.SW2R", ".SMOD"]
prop_offset = 0x64351F0 # offset to sugoroku properties
large_map = 80
small_map = 56
class TheCheck:
    @staticmethod
    def validate_numeric_input(new_value):
        return new_value == "" or (new_value.replace(".", "", 1).isdigit() and '.' not in new_value and float(new_value) >= 0)
def rem(files1, files2):
    filepath1 = os.path.join(sug_folders[1], files1)
    if os.path.isfile(filepath1):
        os.remove(filepath1)
    filepath2 = os.path.join(sug_folders[1], files2)
    if os.path.isfile(filepath2):
        os.remove(filepath2)
class SugorokuEditor(TheCheck):
    def __init__(self, root):
        self.root = root
        self.root.title("Samurai Warriors 2 Sugoroku Editor")
        self.root.iconbitmap(os.path.join(sug_folders[0], "icon1.ico"))
        self.root.minsize(1000, 700)
        self.root.resizable(False, False)
        self.modname = tk.StringVar()
        self.cost = tk.IntVar() # 2 bytes
        self.type = tk.IntVar() # 1 byte
        self.name = tk.IntVar() # 1 bytes
        self.xcord = tk.IntVar() # 2 bytes
        self.ycord = tk.IntVar() # 2 bytes
        self.prop_create()
        self.ref_create()
        self.gui_labels()
        self.gui_entries()
        self.gui_misc()
    def gui_labels(self):
        tk.Label(self.root, text="Property X Coordinate").place(x=60, y=100)
        tk.Label(self.root, text="Property Y Coordinate").place(x=60, y=180)
        tk.Label(self.root, text="Property Value").place(x=280, y=100)
        tk.Label(self.root, text="Property Type").place(x=280, y=180)
        tk.Label(self.root, text="Property Name ").place(x=500, y=100)
        tk.Label(self.root, text=f"This Editor allows modding Sugoroku mode \nand making custom maps. More features \nwill be added.").place(x=230, y=10)
    def gui_entries(self):
        tk.Entry(self.root, textvariable=self.xcord, validate="key", validatecommand=(self.root.register(self.validate_numeric_input), "%P")).place(x=60, y=140)
        tk.Entry(self.root, textvariable=self.ycord, validate="key", validatecommand=(self.root.register(self.validate_numeric_input), "%P")).place(x=60, y=220)
        tk.Entry(self.root, textvariable=self.cost, validate="key", validatecommand=(self.root.register(self.validate_numeric_input), "%P")).place(x=280, y=140)
        tk.Entry(self.root, textvariable=self.type, validate="key", validatecommand=(self.root.register(self.validate_numeric_input), "%P")).place(x=280, y=220)
        tk.Entry(self.root, textvariable=self.name, validate="key", validatecommand=(self.root.register(self.validate_numeric_input), "%P")).place(x=500, y=140)
    def gui_misc(self):
        self.selected_slot = tk.IntVar(self.root)
        self.selected_slot.set(0)  # Default value
        self.slot_combobox = ttk.Combobox(self.root, textvariable=self.selected_slot, values=list(range(137)))
        self.slot_combobox.bind("<<ComboboxSelected>>", self.slot_selected)
        self.slot_combobox.place(x=600, y=10)
        tk.Label(self.root, text="Property to mod").place(x=480, y=10)
        self.status_label = tk.Label(self.root, text="", fg="green")
        self.status_label.place(x=480, y=200)
        tk.Button(self.root, text = "Create Mod", command=self.create_sugo_mod, height = 3, width = 20).place(x=800,y=300)
        mm1 = tk.Entry(self.root, textvariable = self.modname).place(x=800,y=260)
        mm2 = tk.Label(self.root, text = f"Enter a mod name").place(x=800,y=230)
        self.mod_manager = tk.Button(self.root, text = "SW2 Mod Manager", command = self.mod_manager, height = 3, width = 25)
        self.mod_manager.place(x=800, y=10)
        tk.Button(self.root, text="Submit values to .SW2D file", command= self.submit_change, height = 3, width = 25).place(x=30, y=10)
    def slot_selected(self, event=None): # update display data
        selected_slot_value = self.selected_slot.get()
        self.property_search(selected_slot_value)
        
    def prop_create(self): # make the .SW2D file to store 14 byte property slot data
        with open(file1, "rb") as f1: # the main file to obtain references from
            with open(os.path.join(sug_folders[1], file_list[0]), "ab") as f2:
                f1.seek(prop_offset) # seek each offset within each list
                for j in range(0, 137): # read 14 chunks of data
                    sdata = f1.read(14)
                    f2.write(sdata)
                f2.write(prop_offset.to_bytes(4, "little"))
        self.check_backup1()
    def ref_create(self): # make the .SW2R file store offsets for each slot in the .SW2D file
        with open(os.path.join(sug_folders[1], file_list[0]), "rb") as f_data:  # Open the .SW2D file for reading
            with open(os.path.join(sug_folders[1], file_list[1]), "ab") as f_ref:  # Open the corresponding .SW2R file for writing
                offset = 0  # Initialize offset counter
                while True:
                    data_chunk = f_data.read(14)  # Read a 14-byte chunk from .data file
                    if not data_chunk:  # Break loop if end of file is reached
                        break
                    f_ref.write(offset.to_bytes(8, "little"))  # Write the offset to the .ref file
                    offset += 14  # Move offset to the next chunk
        self.check_backup2()
    def submit_change(self):
        try:
            col = [self.xcord.get().to_bytes(2, "little"), self.ycord.get().to_bytes(2, "little"), self.cost.get().to_bytes(2, "little"), self.type.get().to_bytes(1, "little"),
                   self.unk1, self.name.get().to_bytes(1, "little"), self.unk2]
            
            sugo_slot = self.selected_slot.get()
            with open(os.path.join(sug_folders[1], file_list[1]), "rb") as r1: # for obtaining the offset for a property slot from the .SW2R file
                uservalue = sugo_slot * 8
                r1.seek(uservalue)
                getoffset = int.from_bytes(r1.read(8), "little")
                with open(os.path.join(sug_folders[1], file_list[0]), "r+b") as f1: # for updating the property slot with the current values from col list
                    f1.seek(getoffset)
                    for b in col:
                        f1.write(b)                       
            self.status_label.config(text=f"Values submitted successfully.", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", fg="red")
            
    def create_sugo_mod(self): # for creating a mod file with custom extension
        sep = "." # to be used for correcting possible user filenames that have their own extension
        try:
            usermodname = self.modname.get().split(sep, 1)[0] + file_list[2] # Create modname with the user entered name and .SMOD extension
            with open(os.path.join(sug_folders[1], file_list[0]), "rb") as r1:
                data = r1.read()
                with open(usermodname, "wb") as w1:
                    w1.write(data)
            self.status_label.config(text=f"Mod file '{usermodname}' created successfully.", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Error creating mod file '{usermodname}': {str(e)}", fg="red")
    def property_search(self, selected_slot): # search the data for property data
        new_select = os.path.join(sug_folders[1], file_list[1])
        new_read = os.path.join(sug_folders[1], file_list[0]) # .SW2D file
        with open(new_select, "rb") as r1: # .ref file
            useroffset = selected_slot
            uservalue = selected_slot * 8
            r1.seek(uservalue)
            getoffset = int.from_bytes(r1.read(8), "little")
            with open(new_read, "rb") as f1: # .SW2D file
                f1.seek(getoffset)
                slotoffset = f1.tell()
                propxcord = int.from_bytes(f1.read(2), "little")
                propycord = int.from_bytes(f1.read(2), "little")
                propcost = int.from_bytes(f1.read(2), "little")
                proptype = int.from_bytes(f1.read(1), "little")
                self.unk1 = f1.read(4)
                propname = int.from_bytes(f1.read(1), "little")
                self.unk2 = f1.read(2)

                self.xcord.set(propxcord)
                self.ycord.set(propycord)
                self.cost.set(propcost)
                self.type.set(proptype)
                self.name.set(propname)

    def check_backup1(self): # Create backups of the .SW2D file
        try_file = os.path.join(sug_folders[1], file_list[0])
        backup_file = os.path.join(sug_folders[2], file_list[0])
        if not os.path.exists(backup_file):
            shutil.copy(try_file, backup_file)
        else:
            pass
    def check_backup2(self): # create backups of .SW2R file
        otry_file = os.path.join(sug_folders[1], file_list[1])
        obackup_file = os.path.join(sug_folders[2], file_list[1])
        if not os.path.exists(obackup_file):
            shutil.copy(otry_file, obackup_file)
        else:
            pass
    def mod_manager(self):
        manager = SW2Manager(self.root)

class SW2Manager: # mod manager for Sugoroku mods
    def __init__(self, root):
        self.root = tk.Toplevel()
        self.root.title("Sugoroku Mod Manager")
        self.root.iconbitmap(os.path.join(sug_folders[0], "icon2.ico"))
        self.root.minsize(400, 400)
        self.root.resizable(False, False)
        self.mod_status = tk.Label(self.root, text="", fg="green")
        self.mod_status.place(x=10, y=170)
        tk.Button(self.root, text="Enable Mod", command=self.ask_open_file, height=10, width=50).place(x=10, y=10) # button for enabling mods
        tk.Button(self.root, text="Disable Mod", command=self.ask_open_ofile, height=10, width=50).place(x=10, y=210) # button for disabling mods
    def ask_open_file(self): # This is for enabling the user selected mod
        file_path = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select mod file",
            filetypes=(
                ("Supported Files", "*.SMOD;"),
            ))
        try:
            if file_path:
                check_size1 = os.path.getsize(file_path)
                offset_size1 = check_size1 - 4
                # Apply the mod to the iso file
                with open(file1, "r+b") as f1: # open iso file for reading and writing
                    with open(file_path, "rb") as f2: # open the mod file for reading
                        f2.seek(offset_size1)
                        offset = int.from_bytes(f2.read(4), "little")
                        f1.seek(offset) # seek the offset in the iso file
                        f2.seek(0)
                        sdata = f2.read(offset_size1) # read the mod file's data
                        f1.write(sdata) # write the mod file's data to the iso file
                self.mod_status.config(text=f"Mod file '{os.path.basename(file_path)}' enabled successfully.", fg="green")
        except Exception as e:
            self.mod_status.config(text=f"Error: {str(e)}", fg="red")
    def ask_open_ofile(self): # For disabling mods
        file_path = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select mod file",
            filetypes=(
                ("Supported Files", "*.SW2D;"),
            ))
        try:
            if file_path:
                check_size2 = os.path.getsize(file_path)
                offset_size2 = check_size2 - 4
                # apply the disabling file to the iso file
                with open(file1, "r+b") as f1: # open the iso file for reading and writing
                    with open(file_path, "rb") as f2: # open the mod disabling file
                        f2.seek(offset_size2)
                        offset = int.from_bytes(f2.read(4), "little")
                        f1.seek(offset) # seek offset for Sugoroku data in the iso file
                        f2.seek(0)
                        sdata = f2.read(offset_size2) # read the data for disabling Sugoroku mods
                        f1.write(sdata) # write the data
                self.mod_status.config(text=f"The mod that used the '{os.path.basename(file_path)}' template was disabled.", fg="green")
        except Exception as e:
            self.mod_status.config(text=f"Error: {str(e)}", fg="red")
            
def runner():
    root = tk.Tk()
    sw2 = SugorokuEditor(root)
    root.mainloop()
if __name__ == "__main__":
    rem(file_list[0], file_list[1])
    for folds in sug_folders:
        os.makedirs(folds, exist_ok = True)
    runner()
