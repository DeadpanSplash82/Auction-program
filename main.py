import sys
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import font
from tkinter import ttk
from ttkthemes import ThemedTk
import gettext
import pandas as pd
from datetime import datetime
import re
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as backend_tkagg
import numpy as np
import random
import math
import ast

####Global setup#######################################################################################################
RED   = "\033[1;31m"
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
BACKGROUND = "#F2F2F2"
lang_changed = False
root = None
file_path = ""
current_auction = pd.Series({}, dtype=object)
current_run = pd.Series({}, dtype=object)
bidder_map = {}
colors = []
current_lot = -1
current_bidder = -1
current_bid = -1

#TODO test with exe file (pyinstaller)
#TODO add descriptive comments
#TODO reorganize translation files

translation = gettext.translation(
    'auction', localedir='translations', languages=['en'])
translation.install()
# _ = translation.gettext


class EButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        try:
            self.bind("<Return>", lambda event: self.invoke())
        except Exception:
            pass
    
    def configure(self, **kwargs):
        if 'background' in kwargs:
            self.config(bg=kwargs['background'])
        else:
            tk.Button.configure(self, **kwargs)


def add_menu():
    global root
    _ = translation.gettext

    main_menu = Menu(root, font=("Tahoma", 12))

    btn_file = Menubutton(main_menu)
    menu_file = Menu(btn_file, tearoff=0)

    menu_file.add_command(label=_("new_file"), command=new_file, font=("Tahoma", 12))
    menu_file.add_command(label=_("save_file"), command=save_file, font=("Tahoma", 12))
    menu_file.add_command(label=_("open_file"), command=open_confirmation, font=("Tahoma", 12))

    btn_file.config(menu=menu_file)
    main_menu.add_cascade(label=_("file"), menu=menu_file)

    main_menu.add_command(label=_("mnu_auction"), command=setup_auction, font=("Tahoma", 12))
    main_menu.add_command(label=_("mnu_add_bidder"), command=setup_add_bidders, font=("Tahoma", 12))
    main_menu.add_command(label=_("mnu_add_lot"), command=setup_add_lot, font=("Tahoma", 12))
    main_menu.add_command(label=_("mnu_lang_change"), command=setup_language, font=("Tahoma", 12))
    main_menu.add_command(label=_("exit"), command=confirm_close, font=("Tahoma", 12))

    root.config(menu=main_menu)


def clear_window():
    global root
    for widget in root.winfo_children():
        widget.destroy()
    add_menu()


def close_window(confirmed=False):
    global root
    if confirmed:
        sys.exit()


def confirm_close():
    confirmation_box(translation.gettext("close_confirm"), close_window)


def set_bg_color(parent, color=None):
    if color is None:
        color = parent.cget("bg")
    for child in parent.winfo_children():
        if not isinstance(child, EButton):
            child.configure(background=color)
            set_bg_color(child, color)


def setup_main():
    global root
    global translation
    _ = translation.gettext

    if root is not None:
        root.destroy()
    root = ThemedTk(themebg=True)
    root.set_theme("scidmint")
    root.title(_("title"))
    root.geometry("700x800")
    style = ttk.Style(root)
    root.option_add("*Menu.font", ("Tahoma", 12))
    style.configure('.', font=("Tahoma", 12))
    root.style = style
    root.protocol("WM_DELETE_WINDOW", confirm_close)

    for i in range(4):
        root.grid_columnconfigure(i, weight=1)


    add_menu()
    setup_auction()


def error_box(message, title="Error"):
    global root
    global translation
    _ = translation.gettext

    popup = tk.Toplevel()
    popup.title(title)
    popup.geometry("300x100")

    lbl_image = Label(popup, image="::tk::icons::error")
    lbl_image.grid(row=0, column=0)
    lbl_message = Label(popup, text=message, font=("Tahoma", 12))
    lbl_message.grid(row=0, column=1, columnspan=3)

    btn_close = EButton(popup, text=_("close"),
                        command=popup.destroy, width=10, font=("Tahoma", 12))
    btn_close.grid(row=1, column=1, columnspan=3)
    btn_close.focus_set()


def generate_color():
    global bidder_map
    r = random.randint(0, 255) / 255
    g = random.randint(0, 255) / 255
    b = random.randint(0, 255) / 255
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    if brightness > 200:
        return generate_color()

    color = (r, g, b)
    for existing_color in bidder_map.values():
        difference = math.sqrt((existing_color[0] - color[0])**2 + (
            existing_color[1] - color[1])**2 + (existing_color[2] - color[2])**2)
        if difference < 0.1:
            return generate_color()

    return color


def confirmation_box(message, callback1=None, callback2=None, title="confirmation", button1="yes", button2="no", icon="::tk::icons::warning"):
    global root
    global translation
    global return_value
    global ttk
    _ = translation.gettext

    return_value = False

    def set_return_value(val, callback1=None, callback2=None):
        if callback1 is not None and callback2 is not None:
            callback1(val, callback2)
        elif callback1 is not None:
            callback1(val)

    popup = tk.Toplevel()
    popup.title(_(title))

    lbl_image = Label(popup, image=icon)
    lbl_image.grid(row=0, column=0)
    lbl_message = Label(popup, text=message, font=("Tahoma", 12))
    lbl_message.grid(row=0, column=1, columnspan=3)

    # Get the font size and calculate the length of the message
    font_size = font.Font(font=lbl_message['font']).actual()['size']
    label_width = len(message) * font_size

    # Calculate the window width and height based on the label size
    window_width = int(label_width / 1.1)
    window_height = int(font_size * 10)

    # Set the .geometry property of the TopLevel object
    popup.geometry(f"{window_width}x{window_height}")

    btn_first = EButton(popup, text=_(button1),
                        command=lambda: [set_return_value(True, callback1, callback2), popup.destroy()], width=10, font=("Tahoma", 12))
    btn_first.grid(row=1, column=1)
    btn_first.focus_set()
    if button2 is not None:
        btn_second = EButton(popup, text=_(button2),
                             command=lambda: [set_return_value(False, callback1, callback2), popup.destroy()], width=10, font=("Tahoma", 12))
        btn_second.grid(row=1, column=2)
    


def setup_bidder_color():
    global bidder_map
    global colors
    global translation
    _ = translation.gettext

    for bidder in current_auction["Bidder"]:
        if bidder_map.get(bidder) is None:
            bidder_map[bidder] = generate_color()

    colors = np.array([bidder_map[b] for b in current_auction["Bidder"]])


###Language settings##################################################################################################
def set_language(input_lang):
    global translation
    if input_lang == "en":
        lang = 'en'
    else:
        lang = 'af'
    translation = gettext.translation(
        'auction', localedir='translations', languages=[lang])
    translation.install()
    setup_main()


def setup_language():
    popup = tk.Toplevel()
    popup.title(translation.gettext("title"))
    popup.geometry("200x150")
    lbl_instruction = ttk.Label(
        popup, text=translation.gettext("lang_change_instr"), font=("Tahoma", 12))
    lbl_instruction.pack()
    btn_afrikaans = EButton(popup, text="Afrikaans",
                            command=lambda: [set_language("af")], font=("Tahoma", 12))
    btn_afrikaans.pack()
    btn_english = EButton(popup, text="English",
                          command=lambda: [set_language("en")], font=("Tahoma", 12))
    btn_english.pack()
    btn_close = EButton(popup, text=translation.gettext(
        "close"), command=popup.destroy, font=("Tahoma", 12))
    btn_close.pack()

    set_bg_color(popup, "#f0f0f0")


###File operations#####################################################################################################
def save_file(confirmed=True, callback=None):
    if not confirmed and callback is not None:
        callback()
    if not confirmed:
        return
    global current_auction
    global file_path
    global translation
    _ = translation.gettext

    if current_auction.empty:
        messagebox.showerror(_("error"), _("err_no_auction"))
        return
    #TODO make sure current lot is closed before saving

    # Create a new DataFrame with the arrays for Lot, Bidder, and Price as columns
    bidder_df = pd.DataFrame({'Bidder': current_auction['Bidder']})
    lot_df = pd.DataFrame({'Lot': current_auction['Lot']})
    winner_df = pd.DataFrame({'Winner': current_auction['Winner']})
    price_df = pd.DataFrame({'Price': current_auction['Price']})

    # Concatenate the DataFrames for Lot, Bidder, and Price along axis 1
    auction_df = pd.concat([bidder_df, lot_df, winner_df, price_df], axis=1)

    info_df = pd.DataFrame({
        'Auction_Name': [current_auction['Auction_Name']],
        'Date': [current_auction['Date']],
        'Time': [current_auction['Time']],
        'Goal': [current_auction['Goal']],
        'Total': [current_auction['Total']]
    })
    # Concatenate the DataFrames for the auction information and the bids along axis 0
    result_df = pd.concat([info_df, auction_df], axis=0)

    if file_path == '':
        file_path = filedialog.asksaveasfilename(initialfile=current_auction["Auction_Name"].upper() + " " + str(current_auction["Date"]) + ".xlsx", defaultextension=".xlsx", filetypes=[
            ("Excel Files", "*.xlsx"), ("All Files", "*.*")])

    # Write the result DataFrame to an Excel file
    result_df.to_excel(file_path, index=False, sheet_name='Auction')
    with pd.ExcelWriter(file_path, mode='a', engine='openpyxl') as writer:
        for run in current_auction['Runs']:
            run.to_excel(writer, index=False,
                        sheet_name=run["Lot"])

    messagebox.showinfo(_("save_header"), _("save_success"))
    if callback is not None:
        callback()


def open_file_dialog():
    # Open a file dialog and get the file path
    global file_path
    global translation
    _ = translation.gettext

    entered_path = filedialog.askopenfilename()

    if entered_path == '':
        raise NameError(_("err_no_file"))

    # Check if the file is an Excel file
    if not entered_path.endswith('.xlsx'):
        raise ValueError(_("err_wrong_format"))

    try:
        # Read the file and return the result
        xl = pd.read_excel(entered_path, sheet_name=None)
    except Exception as e:
        raise ValueError(_("err_reading") + f": {e}")

    if 'Auction' not in xl.keys():
        raise ValueError(_("err_no_auction_data"))
    result_df = xl['Auction']

    # Check if the file contains auction data
    if result_df.shape[1] != 9 or result_df.shape[0] < 1 or result_df.columns[0] != 'Auction_Name' or result_df.columns[1] != 'Date' or result_df.columns[2] != 'Time' or result_df.columns[3] != 'Goal' or result_df.columns[4] != 'Total' or result_df.columns[5] != 'Bidder' or result_df.columns[6] != 'Lot' or result_df.columns[7] != 'Winner' or result_df.columns[8] != 'Price':
        raise ValueError(_("err_no_auction_data"))

    file_path = entered_path
    return xl


def open_confirmation():
    global current_auction
    if not current_auction.empty:
        confirmation_box(
            "save_confirmation", callback1=save_file, callback2=open_file)
    else:
        open_file(True)


def open_file(confirmed=True):
    if not confirmed:
        return
    global current_auction
    global current_lot
    global current_run
    global file_path
    global translation
    _ = translation.gettext

    # Call the open_file_dialog function and get the result
    try:
        xl = open_file_dialog()
    except ValueError as e:
        error_box(str(e))
        return
    except NameError as e:
        return

    # Extract the information from the DataFrame
    result_df = xl['Auction']
    auction_info = result_df.iloc[0, :]
    auction_bidders = result_df.iloc[1:, [5]]
    auction_lots = result_df.iloc[1:, 6:]

    # Create a Series with the auction information
    current_auction = pd.Series({
        'Auction_Name': auction_info['Auction_Name'],
        'Date': auction_info['Date'],
        'Time': auction_info['Time'],
        'Goal': auction_info['Goal'],
        'Total': auction_info['Total'],
        'Bidder': auction_bidders['Bidder'].dropna().to_list(),
        'Lot': auction_lots['Lot'].dropna().to_list(),
        'Winner': auction_lots['Winner'].fillna('').to_list(),
        'Price': auction_lots['Price'].dropna().to_list(),
        'Runs': []
    })

    # Read each sheet into a DataFrame and add it to the `current_auction["Runs"]` list
    with pd.ExcelFile(file_path) as xls:
        sheets = xls.sheet_names
        for sheet in sheets:
            if sheet == 'Auction':
                continue
            try:
                df = pd.read_excel(xls, sheet_name=sheet)
            except Exception as e:
                 error_box(_("err_reading") + f": {e}")
                 return
            run = pd.Series({}, dtype=object)
            run["Lot"] = sheet
            run["Bidder"] = ast.literal_eval(df.values[1][0])
            run["Bid"] = ast.literal_eval(df.values[2][0])
            current_auction["Runs"].append(run)
    
    setup_bidder_color()

    if len(current_auction["Lot"]) > 0:
        i = 0
        while current_auction["Winner"][i] != "" and i < len(current_auction["Lot"])-1:
            i += 1
        current_lot = i
        current_run = current_auction["Runs"][i]
    else:
        current_lot = -1
        current_run = pd.Series({}, dtype=object)
    setup_auction()


def new_file():
    global current_auction
    global translation
    _ = translation.gettext
    if not current_auction.empty:
        confirmation_box(
            _("save_confirmation"), callback1=new_auction, callback2=save_file)
    else:
        new_auction(True)


def new_auction(confirmed=False, callback=None):
    if (confirmed and callback is not None):
        callback()
    global current_auction
    global translation
    global current_lot
    global current_bidder
    global current_bid
    global current_run
    _ = translation.gettext

    auction_name = None
    while True:
        auction_name = simpledialog.askstring(
            _("new_auction"), _("new_auction_name"), parent=root)
        if auction_name is None:
            return
        if bool(re.match("^[a-zA-Z0-9\s]+$", auction_name.strip())):
            break

    goal = None
    while True:
        goal = simpledialog.askfloat(
            _("new_auction"), _("new_auction_goal"), parent=root)
        if goal is not None:
            if goal > 0:
                break
        else:
            return

    current_auction = pd.Series({
        'Auction_Name': auction_name,
        'Date': datetime.today().strftime('%Y-%m-%d'),
        'Time': datetime.today().strftime('%H-%M-%S'),
        'Goal': round(goal,2),
        'Total': 0,
        'Bidder': [],
        'Lot': [],
        'Winner': [],
        'Price': [],
        'Runs': []
    })
    current_lot = -1
    current_bidder = -1
    current_bid = -1
    current_run = pd.Series({}, dtype=object)
    setup_auction()


###Add bidder##########################################################################################################
def add_bidder(name):
    global current_auction
    global translation
    global bidder_map, colors
    _ = translation.gettext

    name.strip()
    if name == "":
        error_box(_("err_name_empty"))
        return
    elif name == _("enter_name"):
        error_box(_("err_name_default"))
        return
    elif name in current_auction.Bidder:
        error_box(_("error_name_exists"))
        return

    current_auction["Bidder"].append(name)

    setup_bidder_color()

    setup_add_bidders()


def add_multiple_bidders(base_name):
    global current_auction
    global translation
    global bidder_map, colors
    _ = translation.gettext

    base_name.strip()
    if base_name == "":
        error_box(_("err_name_empty"))
        return
    elif base_name == _("enter_name"):
        error_box(_("err_name_default"))
        return

    amount = None
    while True:
        amount = simpledialog.askinteger(
            _("mult_bidders_header"), _("mult_bidders_instr1") + base_name + _("mult_bidders_instr2") + str(len(current_auction["Bidder"])+1), parent=root)
        if amount is not None:
            break
        else:
            return

    for i in range(len(current_auction["Bidder"])+1, len(current_auction["Bidder"]) + amount + 1):
        if base_name + " " + str(i) in current_auction.Bidder:
            error_box(_("err_name_exists1")+base_name +
                      " " + str(i)+_("err_name_exists2"))
            return

    for i in range(len(current_auction["Bidder"])+1, len(current_auction["Bidder"]) + amount + 1):
        current_auction["Bidder"].append(base_name + " " + str(i))
        setup_bidder_color()

    setup_add_bidders()


def setup_add_bidders():
    clear_window()
    global root
    global translation
    global current_auction
    global colors
    _ = translation.gettext

    #TODO ensure all grid commands are separate
    lbl_new_name = ttk.Label(root, text=_("new_name"), font=("Tahoma", 12)).grid(row=1, column=0)
    ent_new_name = ttk.Entry(root, width=20, font=("Tahoma", 12))
    ent_new_name.insert(0, _("enter_name"))
    ent_new_name.grid(row=1, column=1)
    ent_new_name.focus_set()

    btn_add = EButton(root, text=_("btn_add_bidder"),
                      command=lambda: add_bidder(ent_new_name.get()), font=("Tahoma", 12))
    btn_add.focus_set()
    btn_add.grid(row=2, column=0)
    btn_add_mult = EButton(root, text=_(
        "btn_add_mult_bidder"), command=lambda: add_multiple_bidders(ent_new_name.get()), font=("Tahoma", 12))
    btn_add_mult.grid(row=2, column=1)

    if current_auction.empty:
        btn_add.configure(state="disabled")
        btn_add_mult.configure(state="disabled")
    else:
        lbl_current_bidders = ttk.Label(root, text=_("curr_bidders") + " (" + (
            str(len(current_auction["Bidder"])) if not current_auction.empty else 0) + ") :", font=("Tahoma", 12))
        lbl_current_bidders.grid(row=3, column=0)
        col = 0
        if len(current_auction["Bidder"]) > 0:
            colors = np.array([bidder_map[bidder]
                                    for bidder in current_auction["Bidder"]])
            for i in range(len(current_auction["Bidder"])):
                if i % 30 == 0 and i != 0:
                    col += 1
                rgb = [int(round(x * 255)) for x in colors[i]]
                fcolor = "#{:02x}{:02x}{:02x}".format(*rgb)
                brightness = (0.2126 * colors[i][0]) + (0.7152 * colors[i][1]) + (0.0722 * colors[i][2])
                if brightness < 0.5:
                    bcolor = BACKGROUND
                else:
                    bcolor = "black"
                lbl_current_bidders = ttk.Label(
                    root, text=current_auction["Bidder"][i], font=("Tahoma", 10), foreground=fcolor, background=bcolor)
                lbl_current_bidders.grid(row=4+(i%30), column=col)
        else:
            lbl_current_bidders = ttk.Label(root, text=_("none"), font=("Tahoma", 10))
            lbl_current_bidders.grid(row=4, column=col)
        colors = []

###Add lot#############################################################################################################
def add_lot(name):
    global current_auction
    global translation
    global current_lot
    global current_run
    _ = translation.gettext

    name.strip()
    if name == "":
        error_box(_("err_name_empty"))
        return
    elif name == _("enter_lot"):
        error_box(_("err_name_default"))
        return
    elif name in current_auction.Lot:
        error_box(_("err_name_exists"))
        return

    current_auction["Lot"].append(name)
    current_auction["Price"].append(0)
    current_auction["Winner"].append("")
    current_auction["Runs"].append(pd.Series({"Lot": name, "Bidder": [], "Bid": []}))
    if current_lot < 0:
        current_lot = 0
        current_run = current_auction["Runs"][current_lot]
    setup_add_lot()


def add_multiple_lots(base_name):
    global current_auction
    global translation
    global current_lot
    global current_run
    _ = translation.gettext

    base_name.strip()
    if base_name == "":
        error_box(_("err_name_empty"))
        return
    elif base_name == _("enter_lot"):
        error_box(_("err_name_default"))
        return

    amount = None
    while True:
        amount = simpledialog.askinteger(
            _("mult_lots_header"), _("mult_lots_instr1") + base_name + _("mult_lots_instr2") + str(len(current_auction["Lot"])+1), parent=root)
        if amount is not None:
            break
        else:
            return

    for i in range(len(current_auction["Lot"])+1, len(current_auction["Lot"]) + amount + 1):
        if base_name + " " + str(i) in current_auction.Lot:
            error_box(_("err_name_exists1") + base_name +
                      " " + str(i)+_("err_name_exists2"))
            return

    for i in range(len(current_auction["Lot"])+1, len(current_auction["Lot"]) + amount + 1):
        current_auction["Lot"].append(base_name + " " + str(i))
        current_auction["Price"].append(0)
        current_auction["Winner"].append("")
        current_auction["Runs"].append(pd.Series({"Lot": base_name + " " + str(i), "Bidder": [], "Bid": []}))

    if current_lot < 0:
        current_lot = 0
        current_run = current_auction["Runs"][current_lot]
    setup_add_lot()


def setup_add_lot():
    clear_window()
    global root
    global translation
    _ = translation.gettext

    lbl_new_lot = ttk.Label(root, text=_("new_lot"), font=("Tahoma", 12)).grid(row=1, column=0)
    ent_new_lot = ttk.Entry(root, width=20, font=("Tahoma", 12))
    ent_new_lot.insert(0, _("enter_lot"))
    ent_new_lot.grid(row=1, column=1)
    ent_new_lot.focus_set()

    btn_add = EButton(root, text=_("btn_add_lot"),
                      command=lambda: add_lot(ent_new_lot.get()), font=("Tahoma", 12))
    btn_add.focus_set()
    btn_add.grid(row=2, column=0)
    btn_add_mult = EButton(root, text=_(
        "btn_add_mult_lot"), command=lambda: add_multiple_lots(ent_new_lot.get()), font=("Tahoma", 12))
    btn_add_mult.grid(row=2, column=1)

    if current_auction.empty:
        btn_add.configure(state="disabled")
        btn_add_mult.configure(state="disabled")
    else:
        lbl_current_lots = ttk.Label(root, text=_("curr_lots") + " (" + (
            str(len(current_auction["Lot"])) if not current_auction.empty else 0) + ") :", font=("Tahoma", 12))
        lbl_current_lots.grid(row=3, column=0)
        if len(current_auction["Lot"]) > 0:
            col = 0 
            for i in range(len(current_auction["Lot"])):
                if i % 30 == 0 and i != 0:
                    col += 1
                lbl_current_lots = ttk.Label(
                    root, text=current_auction["Lot"][i], font=("Tahoma", 10))
                lbl_current_lots.grid(row=4+(i%30), column=col)
        else:
            lbl_current_lots = ttk.Label(root, text=_("none"), font=("Tahoma", 10))
            lbl_current_lots.grid(row=4, column=0)


###Auction#############################################################################################################
def add_bid(amount, bidder):
    global current_auction
    global translation
    global current_bidder
    global current_lot
    global current_bid
    global current_run
    _ = translation.gettext

    #TODO make sure user doesn't already hold the highest bid
    try:
        float(amount)
    except ValueError:
        error_box(_("err_nan"))
        return
    if amount == "":
        error_box(_("err_no_amount"))
        return
    elif float(amount) <= 0:
        error_box(_("err_neg_amount"))
        return
    elif bidder == _("select_bidder"):
        error_box(_("err_no_bidder"))
        return
    elif bidder == -1:
        error_box(_("err_no_bidder"))
        return
    elif bidder == "":
        error_box(_("err_no_bidder"))
        return
    elif current_lot < 0:
        error_box(_("err_no_lot"))
        return
    elif current_lot >= len(current_auction["Lot"]):
        error_box(_("err_lot_out_of_range"))
        return
    elif float(amount) <= current_bid:
        error_box(_("err_bid_too_low"))
        return

    current_bidder = bidder
    current_bid = float(amount)
    current_run["Bidder"].append(current_bidder)
    current_run["Bid"].append(current_bid)
    setup_auction()


def new_bid():
    global current_auction
    global translation
    global current_bidder
    global current_lot
    global current_bid
    _ = translation.gettext

    popup = tk.Toplevel()
    popup.title(_("add_bid"))
    popup.geometry("300x200")
    popup.resizable(False, False)

    lbl_bidder = ttk.Label(
        popup, text=_("select_bidder_from_list"), background=BACKGROUND).grid(row=0, column=0)
    cmb_bidders = ttk.Combobox(
        popup, values=current_auction["Bidder"], state="readonly")
    cmb_bidders.set(_("select_bidder"))
    cmb_bidders.grid(row=1, column=0)
    cmb_bidders.focus_set()

    lbl_bid = ttk.Label(popup, text=_("enter_bid_amount") + ":", font=("Tahoma", 12), background=BACKGROUND).grid(
        row=2, column=0)
    ent_bid = ttk.Entry(popup, width=20, font=("Tahoma", 12), background=BACKGROUND)
    ent_bid.insert(0, "0")
    ent_bid.grid(row=3, column=0)

    btn_add = EButton(popup, text=_("add_bid"), command=lambda: add_bid(
        ent_bid.get(), cmb_bidders.current()))
    btn_add.grid(row=4, column=0)

def has_next_lot():
    global current_auction
    global translation
    global current_lot
    _ = translation.gettext

    if current_lot < 0 and current_auction.empty:
        return False
    i = current_lot+1
    while i < len(current_auction["Lot"]):
        if current_auction["Winner"][i % len(current_auction["Lot"])] == "":
            return True
        i += 1
    return False


def next_lot():
    global current_auction
    global translation
    global current_lot
    global current_run
    _ = translation.gettext

    if current_lot < 0:
        return
    i = current_lot+1
    while i < len(current_auction["Lot"]):
        if current_auction["Winner"][i % len(current_auction["Lot"])] == "":
            current_lot = i
            break
        i += 1
    current_run = current_auction["Runs"][current_lot]
    setup_auction()


def close_lot():
    global current_auction
    global translation
    global current_lot
    global current_bid
    global current_bidder
    global current_run
    _ = translation.gettext

    if current_lot < 0:
        error_box(_("err_no_lot"))
        return
    elif current_lot >= len(current_auction["Lot"]):
        error_box(_("err_lot_out_of_range"))
        return
    elif current_bidder < 0:
        error_box(_("err_no_bidder"))
        return
    elif current_bidder >= len(current_auction["Bidder"]):
        error_box(_("err_bidder_out_of_range"))
        return
    elif current_bid < 0:
        error_box(_("err_no_bid"))
        return

    current_auction["Price"][current_lot] = current_bid
    current_auction["Winner"][current_lot] = current_auction["Bidder"][current_bidder]
    current_auction["Total"] += current_bid
    current_auction["Runs"][current_lot] = current_run
    current_bid = -1
    current_bidder = -1
    setup_auction()


def change_lot(index):
    global current_auction
    global translation
    global current_lot
    global current_run
    _ = translation.gettext

    if index < 0:
        error_box(_("err_no_lot"))
        return
    elif index >= len(current_auction["Lot"]):
        error_box(_("err_lot_out_of_range"))
        return

    current_lot = index
    current_run = current_auction["Runs"][current_lot]
    setup_auction()


def select_lot():
    global current_auction
    global translation
    global current_lot
    _ = translation.gettext

    popup = tk.Toplevel()
    popup.title(_("select_lot"))
    popup.geometry("250x150")
    popup.resizable(False, False)

    vals = current_auction["Lot"].copy()
    for i in range(len(vals)):
        if current_auction["Price"][i] > 0:
            vals[i] = vals[i] + " (" + _("closed") + ")"

    lbl_lot = ttk.Label(popup, text=_("select_lot_from_list"), font=("Tahoma", 12)).grid(
        row=0, column=0)
    cmb_lots = ttk.Combobox(popup, values=vals, state="readonly", font=("Tahoma", 12)   )
    cmb_lots.set(_("pick_lot"))
    cmb_lots.grid(row=1, column=0)
    cmb_lots.focus_set()

    btn_select = EButton(popup, text=_("select"),
                         command=lambda: change_lot(cmb_lots.current()), font=("Tahoma", 12))
    btn_select.grid(row=2, column=0)


def setup_auction():
    clear_window()
    global root
    global translation
    global current_auction
    global current_bidder
    global current_lot
    global current_bid
    global current_run
    global bidder_map, colors
    _ = translation.gettext

    bidder_names = []
    # bidder_colors = []
    if not current_run.empty:
        if current_run["Bid"] and current_run["Bidder"]:
            for index in current_run["Bidder"]:
                bidder_names.append(current_auction["Bidder"][index])
                # bidder_colors.append(colors[index])

            colors = np.array([bidder_map[current_auction["Bidder"][bidder]]
                                for bidder in current_run["Bidder"]])

    frm_header = Frame(root, width=300, height=150)
    for i in range(6):
        frm_header.grid_columnconfigure(i, weight=1)
    for i in range(1):
        frm_header.grid_rowconfigure(i, weight=1)

    lbl_total_bidders_label = ttk.Label(
        frm_header, text=_("total_bidders"), font=("Tahoma", 12), background=BACKGROUND)
    lbl_total_bidders_label.grid(row=0, column=0, sticky=E)
    lbl_total_bidders_value = ttk.Label(
        frm_header, text=len(current_auction["Bidder"]) if not current_auction.empty else "0", font=("Tahoma", 12, "bold"), padding=(0,0,10,0), justify=tk.LEFT, background=BACKGROUND)
    lbl_total_bidders_value.grid(row=0, column=1, sticky=W)
    lbl_total_lots_label = ttk.Label(
        frm_header, text=_("total_lots"), font=("Tahoma", 12), background=BACKGROUND)
    lbl_total_lots_label.grid(row=0, column=2, sticky=E)
    lbl_total_lots_value = ttk.Label(
        frm_header, text=len(current_auction["Lot"]) if not current_auction.empty else "0", font=("Tahoma", 12, "bold"), padding=(0,0,10,0), justify=tk.LEFT, background=BACKGROUND)
    lbl_total_lots_value.grid(row=0, column=3, sticky=W)
    lbl_end_goal_label = ttk.Label(
        frm_header, text=_("total_made") + ("(" + "{:.2%}".format(current_auction["Total"]/current_auction["Goal"]) + _("of_end_goal") +")") if not current_auction.empty else "", font=("Tahoma", 12), background=BACKGROUND)
    lbl_end_goal_label.grid(row=0, column=4, sticky=E)
    lbl_end_goal_value = ttk.Label(
        frm_header, text=("R{:,.2f}".format(current_auction["Total"])).replace(",", " ") if not current_auction.empty else "R0", font=("Tahoma", 12, "bold"), padding=(0,0,10,0), justify=tk.LEFT, background=BACKGROUND)
    lbl_end_goal_value.grid(row=0, column=5, sticky=W)

    frm_current_info = Frame(root, width=300, height=250)
    for i in range(6):
        frm_current_info.grid_columnconfigure(i, weight=1)
    for i in range(3):
        frm_current_info.grid_rowconfigure(i, weight=1)

    lbl_current_lot_label = ttk.Label(frm_current_info, text=_("current_lot") + " " + (("(" + str(
        current_lot+1) + "/" + str(len(current_auction["Lot"])) + ")") if not current_auction.empty else "") + ":", font=("Tahoma", 12), background=BACKGROUND)
    lbl_current_lot_label.grid(row=1, column=0, sticky=E)
    lbl_current_lot_value = ttk.Label(
        frm_current_info, text=current_auction["Lot"][current_lot] if current_lot != -1 else _("none"), font=("Tahoma", 12, "bold"), padding=(0,0,10,0), justify=tk.LEFT, background=BACKGROUND)
    lbl_current_lot_value.grid(row=1, column=1, sticky=W)

    lbl_current_bid_label = ttk.Label(
        frm_current_info, text=(_("current_bid") if current_auction.empty or current_auction["Winner"][current_lot] == "" else _("final_amount")), font=("Tahoma", 12), justify=tk.LEFT, background=BACKGROUND)
    lbl_current_bid_label.grid(row=2, column=0, sticky=E)
    lbl_current_bid_value = ttk.Label(
        frm_current_info, text=(("R{:,.2f}".format(current_bid).replace(",", " ") if current_bid > 0 else _("none")) if current_auction.empty or current_auction["Winner"][current_lot] == "" else "R{:,.2f}".format(current_auction["Price"][current_lot]).replace(",", " ")), font=("Tahoma", 12, "bold"), padding=(0,0,10,0), justify=tk.LEFT, background=BACKGROUND)
    lbl_current_bid_value.grid(row=2, column=1, sticky=W)
    lbl_current_bidder_label = ttk.Label(
        frm_current_info, text=_("from"), font=("Tahoma", 12), background=BACKGROUND)
    lbl_current_bidder_label.grid(row=2, column=2, sticky=E)

    if current_bidder != -1:
        rgb = [int(round(x * 255)) for x in colors[len(colors)-1]]
        fcolor = "#{:02x}{:02x}{:02x}".format(*rgb)
        brightness = (0.2126 * colors[len(colors)-1][0]) + (0.7152 * colors[len(colors)-1][1]) + (0.0722 * colors[len(colors)-1][2])
        if brightness < 0.5:
            bcolor = BACKGROUND
        else:
            bcolor = "black"
    elif not current_auction.empty and current_auction["Winner"][current_lot] != "":
        bidder_index = len(colors)-1
        rgb = [int(round(x * 255)) for x in colors[bidder_index]]
        fcolor = "#{:02x}{:02x}{:02x}".format(*rgb)
        brightness = (0.2126 * colors[bidder_index][0]) + (0.7152 * colors[bidder_index][1]) + (0.0722 * colors[bidder_index][2])
        if brightness < 0.5:
            bcolor = BACKGROUND
        else:
            bcolor = "black"
    else:
        fcolor = "black"
        bcolor = BACKGROUND
    lbl_current_bidder_value = ttk.Label(
        frm_current_info, text=((current_auction["Bidder"][current_bidder] if current_bidder != -1 else _("none")) if current_auction.empty or current_auction["Winner"][current_lot] == "" else current_auction["Winner"][current_lot]), font=("Tahoma", 12, "bold"), padding=(0,0,10,0), justify=tk.LEFT, foreground=fcolor, background=bcolor)
    lbl_current_bidder_value.grid(row=2, column=3, sticky=W)

    frm_graph = Frame(root, width=300, height=250)
    frm_graph.configure(background=root.cget("bg"))

    if not current_run.empty:
        # create the figure and axis objects
        fig, ax = plt.subplots()
        if current_run["Bid"] and current_run["Bidder"]:
            x = range(len(current_run["Bid"]))
            y = current_run["Bid"]

            sc = ax.scatter(x, y, c=colors)
            ax.plot(x, y, '-o', color='black', linewidth=0.25, markersize=0)

        ax.set_xlabel("")
        ax.set_ylabel("Price" + " (R)")
        ax.set_xticks([])

        
        # embed the Matplotlib figure in the tkinter frame
        canvas = backend_tkagg.FigureCanvasTkAgg(fig, master=frm_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    lbl_no_auction = ttk.Label(
        root, text=_("err_no_current_auction"), font=("Tahoma", 16), foreground="red")

    frm_btns = Frame(root, width=300, height=100)
    frm_btns.configure(background=root.cget("bg"))
    for i in range(4):
        frm_btns.grid_columnconfigure(i, weight=1)

    btn_new_bid = EButton(frm_btns, text=_("btn_new_bid"), command=new_bid, font=("Tahoma", 12), width=15)
    btn_new_bid.grid(row=0, column=0, sticky="we")
    if current_lot == -1 or current_auction["Winner"][current_lot] != "":
        btn_new_bid.config(state="disabled")
    else:
        btn_new_bid.focus_set()

    btn_close_lot = EButton(frm_btns, text=_(
        "btn_close_lot"), command=close_lot, font=("Tahoma", 12), width=15)
    btn_close_lot.grid(row=0, column=1, sticky="we")
    if current_lot == -1 or current_bid <= 0:
        btn_close_lot.config(state="disabled")

    btn_next_lot = EButton(frm_btns, text=_("btn_next_lot"), command=next_lot, font=("Tahoma", 12), width=15)
    btn_next_lot.grid(row=0, column=2, sticky="we")
    if not has_next_lot() or (len(current_run["Bid"]) > 0 and current_bid != -1):
        btn_next_lot.config(state="disabled")
    else:
        btn_next_lot.focus_set()

    btn_select_lot = EButton(frm_btns, text=_(
        "select_lot"), command=select_lot, font=("Tahoma", 12), width=15)
    btn_select_lot.grid(row=0, column=3, sticky="we")
    if current_auction.empty or len(current_auction["Lot"]) == 0 or (len(current_run["Bid"]) > 0 and current_bid != -1):
        btn_select_lot.config(state="disabled")

    if not current_auction.empty:
        frm_header.pack(fill=BOTH)
        frm_current_info.pack(fill=BOTH)
        frm_graph.pack(expand=False, fill=BOTH)
        frm_btns.pack(expand=True, fill=BOTH)
    else:
        lbl_no_auction.pack()
    
    # set_bg_color(root)


###Main program##########################################################################################################
def main():
    setup_main()
    global root
    root.mainloop()


if __name__ == '__main__':
    main()
