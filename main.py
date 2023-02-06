import sys
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import gettext
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import font
from tkinter import ttk
import pandas as pd
from datetime import datetime
import re
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.pyplot as plt

####Global setup#######################################################################################################
lang_changed = False
root = None
file_path = ""
current_auction = pd.Series({})
current_lot = -1
current_bidder = -1
current_bid = -1

translation = gettext.translation(
    'auction', localedir='translations', languages=['en'])
translation.install()
# _ = translation.gettext


class EButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        self.bind("<Return>", lambda event: self.invoke())


def add_menu():
    global root
    _ = translation.gettext
    main_menu = Menu(root)

    btn_file = Menubutton(main_menu)
    menu_file = Menu(btn_file, tearoff=0)

    menu_file.add_command(label=_("new_file"), command=new_file)
    menu_file.add_command(label=_("save_file"), command=save_file)
    menu_file.add_command(label=_("open_file"), command=open_confirmation)

    btn_file.config(menu=menu_file)
    main_menu.add_cascade(label=_("file"), menu=menu_file)

    main_menu.add_command(label=_("mnu_auction"), command=setup_auction)
    main_menu.add_command(label=_("mnu_add_bidder"), command=setup_add_bidders)
    main_menu.add_command(label=_("mnu_add_lot"), command=setup_add_lot)
    main_menu.add_command(label=_("mnu_lang_change"), command=setup_language)
    main_menu.add_command(label=_("exit"), command=confirm_close)

    root.config(menu=main_menu)


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()
    add_menu()


def close_window(confirmed=False):
    global root
    if confirmed:
        sys.exit()


def confirm_close():
    confirmation_box(translation.gettext("close_confirm"), close_window)


def setup_main():
    global root
    global translation
    _ = translation.gettext

    if root is not None:
        root.destroy()
    root = tk.Tk()
    root.title(_("title"))
    root.geometry("500x600")

    frame = Frame(root)
    frame.pack()

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
    lbl_message = Label(popup, text=message)
    lbl_message.grid(row=0, column=1, columnspan=3)

    btn_close = EButton(popup, text=_("close"),
                        command=popup.destroy, width=10)
    btn_close.grid(row=1, column=1, columnspan=3)


def confirmation_box(message, callback1=None, callback2=None, title="Confirmation", button1="yes", button2="no", icon="::tk::icons::warning"):
    global root
    global translation
    global return_value
    global tk
    _ = translation.gettext

    return_value = False

    def set_return_value(val, callback1=None, callback2=None):
        if callback1 is not None and callback2 is not None:
            callback1(val, callback2)
        elif callback1 is not None:
            callback1(val)

    popup = tk.Toplevel()
    popup.title(title)

    lbl_image = Label(popup, image=icon)
    lbl_image.grid(row=0, column=0)
    lbl_message = Label(popup, text=message)
    lbl_message.grid(row=0, column=1, columnspan=3)

    # Get the font size and calculate the length of the message
    font_size = font.Font(font=lbl_message['font']).actual()['size']
    label_width = len(message) * font_size

    # Calculate the window width and height based on the label size
    window_width = int(label_width / 1.1)
    window_height = int(font_size * 10)

    # Set the .geometry property of the TopLevel object
    popup.geometry(f"{window_width}x{window_height}")

    btn_first = EButton(popup, text=button1,
                        command=lambda: [set_return_value(True, callback1, callback2), popup.destroy()], width=10)
    btn_first.grid(row=1, column=1)
    if button2 is not None:
        btn_second = EButton(popup, text=button2,
                             command=lambda: [set_return_value(False, callback1, callback2), popup.destroy()], width=10)
        btn_second.grid(row=1, column=2)


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
    popup.geometry("150x150")
    lbl_instruction = tk.Label(
        popup, text=translation.gettext("lang_change_instr"))
    lbl_instruction.pack()
    # new_lang = tk.StringVar()
    # rbtn_afrikaans = tk.Radiobutton(popup, text="Afrikaans", variable=new_lang, value="af", command=set_language(new_lang)).pack()
    # rbtn_english = tk.Radiobutton(popup, text="English", variable=new_lang, value="en", command=set_language(new_lang)).pack()
    btn_afrikaans = EButton(popup, text="Afrikaans",
                            command=lambda: [set_language("af")])
    btn_afrikaans.pack()
    btn_english = EButton(popup, text="English",
                          command=lambda: [set_language("en")])
    btn_english.pack()
    btn_close = EButton(popup, text=translation.gettext(
        "close"), command=popup.destroy)
    btn_close.pack()


###File operations#####################################################################################################
def save_file(confirmed=True, callback=None):
    if not confirmed and callback is not None:
        callback()
    if not confirmed:
        return
    global current_auction
    global file_path

    if current_auction.empty:
        messagebox.showerror("Error", "No auction to save")
        return
    # current_auction = pd.Series({
    #     'Auction_Name': 'Auction 1',
    #     'Date': '2023-01-01',
    #     'Time': '10:00:00',
    #     'Goal': 1000,
    #     'Total': 900,
    #     'Bidder': ['Bidder 1', 'Bidder 2', 'Bidder 3', 'Bidder 4', 'Bidder 5'],
    #     'Lot': ['Lot 1', 'Lot 2', 'Lot 3'],
    #     'Winner': ['Bidder 1', 'Bidder 2', 'Bidder 3'],
    #     'Price': [100, 200, 300]
    # })

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
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[
                                             ("Excel Files", "*.xlsx"), ("All Files", "*.*")])

    # Write the result DataFrame to an Excel file
    result_df.to_excel(file_path, index=False,)

    messagebox.showinfo("Save file", "File saved successfully")
    if callback is not None:
        callback()


def open_file_dialog():
    # Open a file dialog and get the file path
    global file_path

    entered_path = filedialog.askopenfilename()

    if entered_path == '':
        raise NameError("No file selected")

    # Check if the file is an Excel file
    if not entered_path.endswith('.xlsx'):
        raise ValueError("The selected file is not an Excel file")

    try:
        # Read the file and return the result
        result_df = pd.read_excel(entered_path)
    except Exception as e:
        raise ValueError(f"An error occurred while reading the file: {e}")

    # Check if the file contains auction data
    if result_df.shape[1] != 9 or result_df.shape[0] < 1 or result_df.columns[0] != 'Auction_Name' or result_df.columns[1] != 'Date' or result_df.columns[2] != 'Time' or result_df.columns[3] != 'Goal' or result_df.columns[4] != 'Total' or result_df.columns[5] != 'Bidder' or result_df.columns[6] != 'Lot' or result_df.columns[7] != 'Winner' or result_df.columns[8] != 'Price':
        raise ValueError("The selected file does not contain auction data")

    file_path = entered_path
    return result_df


def open_confirmation():
    global current_auction
    if not current_auction.empty:
        confirmation_box(
            "Would you like to save the current auction? All unsaved changes will be lost.", callback1=save_file, callback2=open_file)
    else:
        open_file(True)


def open_file(confirmed=True):
    if not confirmed:
        return
    global current_auction
    global current_lot

    # Call the open_file_dialog function and get the result
    try:
        result_df = open_file_dialog()
    except ValueError as e:
        error_box(str(e))
        return
    except NameError as e:
        return

    # Extract the information from the DataFrame
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
        'Price': auction_lots['Price'].dropna().to_list()
    })

    if len(current_auction["Lot"]) > 0:
        i = 0
        while current_auction["Winner"][i] != "" and i < len(current_auction["Lot"])-1:
            i += 1
        current_lot = i
    else:
        current_lot = -1
    setup_auction()


def new_file():
    global current_auction
    if not current_auction.empty:
        confirmation_box(
            "Would you like to save the current auction? All unsaved changes will be lost.", callback1=new_auction, callback2=save_file)
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
    _ = translation.gettext

    auction_name = None
    while True:
        auction_name = simpledialog.askstring(
            "new_auction", "Enter a new auction name", parent=root)
        if auction_name is None:
            return
        if auction_name is not None or bool(re.match("^[a-zA-Z0-9\s]+$", auction_name.strip())):
            break

    goal = None
    while True:
        goal = simpledialog.askinteger(
            "new_auction", "Enter a goal in R", parent=root)
        if goal is not None:
            break
        else:
            return

    current_auction = pd.Series({
        'Auction_Name': auction_name,
        'Date': datetime.today().strftime('%Y-%m-%d'),
        'Time': datetime.today().strftime('%H-%M-%S'),
        'Goal': goal,
        'Total': 0,
        'Bidder': [],
        'Lot': [],
        'Winner': [],
        'Price': []
    })
    current_lot = -1
    current_bidder = -1
    current_bid = -1
    setup_auction()


###Add bidder##########################################################################################################
def add_bidder(name):
    global current_auction
    global translation
    _ = translation.gettext

    if name == "":
        error_box("error_name_empty")
        return
    elif name == "Enter name":
        error_box("error_name_default")
        return
    elif name in current_auction.Bidder:
        error_box("error_name_exists")
        return

    current_auction["Bidder"].append(name)
    setup_add_bidders()


def add_multiple_bidders(base_name):
    global current_auction
    global translation
    _ = translation.gettext

    if base_name == "":
        error_box("error_name_empty")
        return
    elif base_name == "Enter name":
        error_box("error_name_default")
        return

    amount = None
    while True:
        amount = simpledialog.askinteger(
            "Multiple bidders", "Enter the amount of bidders you would like to add. They will be named \"" + base_name + " [number]\" starting from number = " + str(len(current_auction["Bidder"])+1), parent=root)
        if amount is not None:
            break
        else:
            return

    for i in range(len(current_auction["Bidder"])+1, len(current_auction["Bidder"]) + amount + 1):
        if base_name + " " + str(i) in current_auction.Bidder:
            error_box("error name: \""+base_name + " " + str(i)+"\" exists")
            return

    for i in range(len(current_auction["Bidder"])+1, len(current_auction["Bidder"]) + amount + 1):
        current_auction["Bidder"].append(base_name + " " + str(i))

    setup_add_bidders()


def setup_add_bidders():
    clear_window()
    global root
    global translation
    global current_auction
    _ = translation.gettext

    lbl_new_name = tk.Label(root, text=_("new_name")).grid(row=1, column=0)
    ent_new_name = tk.Entry(root, width=20)
    ent_new_name.insert(0, "Enter name")
    ent_new_name.grid(row=1, column=1)
    ent_new_name.focus_set()

    btn_add = EButton(root, text=_("btn_add_bidder"),
                      command=lambda: add_bidder(ent_new_name.get().trim()))
    btn_add.focus_set()
    btn_add.grid(row=2, column=0)
    btn_add_mult = EButton(root, text=_(
        "btn_add_mult_bidder"), command=lambda: add_multiple_bidders(ent_new_name.get().trim()))
    btn_add_mult.grid(row=2, column=3)

    if current_auction.empty:
        btn_add["state"] = "disabled"
        btn_add_mult["state"] = "disabled"
    else:
        lbl_current_bidders = tk.Label(root, text="Current bidders (" + (
            str(len(current_auction["Bidder"])) if not current_auction.empty else 0) + ") :")
        lbl_current_bidders.grid(row=3, column=0)
        if len(current_auction["Bidder"]) > 0:
            for i in range(len(current_auction["Bidder"])):
                lbl_current_bidders = tk.Label(
                    root, text=current_auction["Bidder"][i])
                lbl_current_bidders.grid(row=4+i, column=0)
        else:
            lbl_current_bidders = tk.Label(root, text="None")
            lbl_current_bidders.grid(row=4, column=0)


###Add lot#############################################################################################################
def add_lot(name):
    global current_auction
    global translation
    global current_lot
    _ = translation.gettext

    if name == "":
        error_box("error_name_empty")
        return
    elif name == "Enter lot":
        error_box("error_name_default")
        return
    elif name in current_auction.Lot:
        error_box("error_name_exists")
        return

    current_auction["Lot"].append(name)
    current_auction["Price"].append(0)
    current_auction["Winner"].append("")
    if current_lot < 0:
        current_lot = 0
    setup_add_lot()


def add_multiple_lots(base_name):
    global current_auction
    global translation
    global current_lot
    _ = translation.gettext

    if base_name == "":
        error_box("error_name_empty")
        return
    elif base_name == "Enter lot":
        error_box("error_name_default")
        return

    amount = None
    while True:
        amount = simpledialog.askinteger(
            "Multiple lots", "Enter the amount of lots you would like to add. They will be named \"" + base_name + " [number]\" starting from number = " + str(len(current_auction["Lot"])+1), parent=root)
        if amount is not None:
            break
        else:
            return

    for i in range(len(current_auction["Lot"])+1, len(current_auction["Lot"]) + amount + 1):
        if base_name + " " + str(i) in current_auction.Lot:
            error_box("error name: \""+base_name + " " + str(i)+"\" exists")
            return

    for i in range(len(current_auction["Lot"])+1, len(current_auction["Lot"]) + amount + 1):
        current_auction["Lot"].append(base_name + " " + str(i))
        current_auction["Price"].append(0)
        current_auction["Winner"].append("")

    if current_lot < 0:
        current_lot = 0
    setup_add_lot()


def setup_add_lot():
    clear_window()
    global root
    global translation
    _ = translation.gettext

    lbl_new_lot = tk.Label(root, text=_("new_lot")).grid(row=1, column=0)
    ent_new_lot = tk.Entry(root, width=20)
    ent_new_lot.insert(0, "Enter lot")
    ent_new_lot.grid(row=1, column=1)
    ent_new_lot.focus_set()

    btn_add = EButton(root, text=_("btn_add_lot"),
                      command=lambda: add_lot(ent_new_lot.get().trim()))
    btn_add.focus_set()
    btn_add.grid(row=2, column=0)
    btn_add_mult = EButton(root, text=_(
        "btn_add_mult_lot"), command=lambda: add_multiple_lots(ent_new_lot.get().trim()))
    btn_add_mult.grid(row=2, column=3)

    if current_auction.empty:
        btn_add["state"] = "disabled"
        btn_add_mult["state"] = "disabled"
    else:
        lbl_current_lots = tk.Label(root, text="Current lots (" + (
            str(len(current_auction["Lot"])) if not current_auction.empty else 0) + ") :")
        lbl_current_lots.grid(row=3, column=0)
        if len(current_auction["Lot"]) > 0:
            for i in range(len(current_auction["Lot"])):
                lbl_current_lots = tk.Label(
                    root, text=current_auction["Lot"][i])
                lbl_current_lots.grid(row=4+i, column=0)
        else:
            lbl_current_lots = tk.Label(root, text="None")
            lbl_current_lots.grid(row=4, column=0)


###Auction#############################################################################################################
def add_bid(amount, bidder):
    global current_auction
    global translation
    global current_bidder
    global current_lot
    global current_bid
    _ = translation.gettext

    try:
        float(amount)
    except ValueError:
        error_box("error_amount_not_number")
        return
    if amount == "":
        error_box("error_amount_empty")
        return
    elif float(amount) <= 0:
        error_box("error_amount_negative")
        return
    elif bidder == "Pick a Bidder":
        error_box("error_bidder_default")
        return
    elif bidder == -1:
        error_box("error_bidder_empty")
        return
    elif bidder == "":
        error_box("error_bidder_default")
        return
    elif current_lot < 0:
        error_box("error_no_lot_selected")
        return
    elif current_lot >= len(current_auction["Lot"]):
        error_box("error_lot_out_of_range")
        return
    elif float(amount) <= current_bid:
        error_box("error_bid_too_low")
        return

    current_bidder = bidder
    current_bid = float(amount)
    setup_auction()


def new_bid():
    global current_auction
    global translation
    global current_bidder
    global current_lot
    global current_bid
    _ = translation.gettext

    popup = tk.Toplevel()
    popup.title("Add bid")
    popup.geometry("300x200")
    popup.resizable(False, False)

    lbl_bidder = tk.Label(
        popup, text="Select a bidder from the list below").grid(row=0, column=0)
    cmb_bidders = ttk.Combobox(
        popup, values=current_auction["Bidder"], state="readonly")
    cmb_bidders.set("Pick a Bidder")
    cmb_bidders.grid(row=1, column=0)
    cmb_bidders.focus_set()

    lbl_bid = tk.Label(popup, text="Enter the bid amount:").grid(
        row=2, column=0)
    ent_bid = tk.Entry(popup, width=20)
    ent_bid.insert(0, "0")
    ent_bid.grid(row=3, column=0)

    btn_add = EButton(popup, text="Add bid", command=lambda: add_bid(
        ent_bid.get(), cmb_bidders.current()))
    btn_add.grid(row=4, column=0)


def next_lot():
    global current_auction
    global translation
    global current_lot
    _ = translation.gettext

    if current_lot < 0:
        return

    i = current_lot+1
    while i < len(current_auction["Lot"]):
        if current_auction["Winner"][i % len(current_auction["Lot"])] == "":
            current_lot = i
            break
        i += 1
    setup_auction()


def close_lot():
    global current_auction
    global translation
    global current_lot
    global current_bid
    global current_bidder
    _ = translation.gettext

    if current_lot < 0:
        error_box("error_no_lot_selected")
        return
    elif current_lot >= len(current_auction["Lot"]):
        error_box("error_lot_out_of_range")
        return
    elif current_bidder < 0:
        error_box("error_no_bidder_selected")
        return
    elif current_bidder >= len(current_auction["Bidder"]):
        error_box("error_bidder_out_of_range")
        return
    elif current_bid < 0:
        error_box("error_no_bid_selected")
        return

    current_auction["Price"][current_lot] = current_bid
    current_auction["Winner"][current_lot] = current_auction["Bidder"][current_bidder]
    current_auction["Total"] += current_bid
    current_bid = -1
    current_bidder = -1
    setup_auction()


def change_lot(index):
    global current_auction
    global translation
    global current_lot
    _ = translation.gettext

    if index < 0:
        error_box("error_no_lot_selected")
        return
    elif index >= len(current_auction["Lot"]):
        error_box("error_lot_out_of_range")
        return

    current_lot = index
    setup_auction()


def select_lot():
    global current_auction
    global translation
    global current_lot
    _ = translation.gettext

    popup = tk.Toplevel()
    popup.title("Select Lot")
    popup.geometry("300x200")
    popup.resizable(False, False)

    vals = current_auction["Lot"].copy()
    for i in range(len(vals)):
        if current_auction["Price"][i] > 0:
            vals[i] = vals[i] + " (closed)"

    lbl_lot = tk.Label(popup, text="Select a lot from the list below").grid(
        row=0, column=0)
    cmb_lots = ttk.Combobox(popup, values=vals, state="readonly")
    cmb_lots.set("Pick a Lot")
    cmb_lots.grid(row=1, column=0)
    cmb_lots.focus_set()

    btn_select = EButton(popup, text="Select",
                         command=lambda: change_lot(cmb_lots.current()))
    btn_select.grid(row=2, column=0)


def setup_auction():
    clear_window()
    global root
    global translation
    global current_auction
    global current_bidder
    global current_lot
    global current_bid
    _ = translation.gettext

    frm_header = Frame(root, width=300, height=150)
    lbl_total_bidders_label = tk.Label(
        frm_header, text=_("total_bidders")).grid(row=0, column=0)
    lbl_total_bidders_value = tk.Label(
        frm_header, text=len(current_auction["Bidder"]) if not current_auction.empty else "0").grid(row=0, column=1)
    lbl_total_lots_label = tk.Label(
        frm_header, text=_("total_lots")).grid(row=0, column=2)
    lbl_total_lots_value = tk.Label(
        frm_header, text=len(current_auction["Lot"]) if not current_auction.empty else "0").grid(row=0, column=3)
    lbl_end_goal_label = tk.Label(
        frm_header, text=_("end_goal")).grid(row=0, column=4)
    lbl_end_goal_value = tk.Label(
        frm_header, text=("R" + str(current_auction["Goal"])) if not current_auction.empty else "R0").grid(row=0, column=5)

    frm_current_info = Frame(root, width=300, height=250)

    lbl_current_lot_label = tk.Label(frm_current_info, text="current lot " + (("(" + str(
        current_lot+1) + "/" + str(len(current_auction["Lot"])) + ")") if not current_auction.empty else "") + ":")
    lbl_current_lot_label.grid(row=1, column=0)
    lbl_current_lot_value = tk.Label(
        frm_current_info, text=current_auction["Lot"][current_lot] if current_lot != -1 else "None").grid(row=1, column=1)

    lbl_current_bid_label = tk.Label(
        frm_current_info, text=_("current_bid")).grid(row=2, column=0)
    lbl_current_bid_value = tk.Label(
        frm_current_info, text=("R " + str(current_bid)) if current_bid > 0 else "None").grid(row=2, column=1)
    lbl_current_bidder_label = tk.Label(
        frm_current_info, text=_("from")).grid(row=2, column=2)
    lbl_current_bidder_value = tk.Label(
        frm_current_info, text=current_auction["Bidder"][current_bidder] if current_bidder != -1 else "none").grid(row=2, column=3)

    frm_graph = Frame(root, width=300, height=250)

    canvas = Canvas(frm_graph, bg='white', width=300, height=300)

    coordinates = 20, 50, 210, 230
    arc = canvas.create_arc(coordinates, start=0, extent=250, fill="blue")
    arc = canvas.create_arc(coordinates, start=250, extent=50, fill="red")
    arc = canvas.create_arc(coordinates, start=300, extent=60, fill="yellow")

    canvas.pack(expand=True, fill=BOTH)

    # create figure and axis for the graph
    # figure = plt.figure()
    # axis = figure.add_subplot(111)

    # plot some data on the axis
    # x_data = [1, 2, 3, 4, 5]
    # y_data = [2, 4, 6, 8, 10]
    # axis.plot(x_data, y_data)

    # create a FigureCanvasTkAgg to display the graph in the Tkinter window
    # canvas = FigureCanvasTkAgg(figure, master=frm_graph)
    # canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    lbl_no_auction = tk.Label(
        root, text="Please open an auction file or create a new one.")

    frm_btns = Frame(root, width=300, height=100)

    btn_new_bid = EButton(frm_btns, text=_("btn_new_bid"), command=new_bid)
    # btn_new_bid.focus_set()
    btn_new_bid.grid(row=0, column=0)
    if current_lot == -1 or current_auction["Winner"][current_lot] != "":
        btn_new_bid.config(state="disabled")
    else:
        btn_new_bid.focus_set()

    btn_close_lot = EButton(frm_btns, text=_(
        "btn_close_lot"), command=close_lot)
    btn_close_lot.grid(row=0, column=1)
    if current_lot == -1 or current_bid <= 0:
        btn_close_lot.config(state="disabled")

    btn_next_lot = EButton(frm_btns, text=_("btn_next_lot"), command=next_lot)
    btn_next_lot.grid(row=0, column=2)
    if current_lot == -1 or current_lot == len(current_auction["Lot"]) - 1:
        btn_next_lot.config(state="disabled")
    else:
        btn_next_lot.focus_set()

    btn_select_lot = EButton(frm_btns, text=_(
        "btn_select_lot"), command=select_lot)
    btn_select_lot.grid(row=0, column=3)
    if current_auction.empty or len(current_auction["Lot"]) == 0:
        btn_select_lot.config(state="disabled")

    if not current_auction.empty:
        frm_header.pack(fill=BOTH)
        frm_current_info.pack(fill=BOTH)
        frm_graph.pack(expand=False, fill=BOTH)
        frm_btns.pack(expand=True, fill=BOTH)
    else:
        lbl_no_auction.pack()


###Main program##########################################################################################################
def main():
    setup_main()
    global root
    root.mainloop()


if __name__ == '__main__':
    main()
