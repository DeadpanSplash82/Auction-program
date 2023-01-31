import tkinter as tk
from tkinter import *
import gettext
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.pyplot as plt

lang_changed = False
root = None
return_value = False

translation = gettext.translation(
    'auction', localedir='translations', languages=['en'])
translation.install()
# _ = translation.gettext


def add_menu():
    global root
    _ = translation.gettext
    mainmenu = Menu(root)
    mainmenu.add_command(label=_("mnu_auction"), command=setup_auction)
    mainmenu.add_command(label=_("mnu_add_bidder"), command=setup_add_bidders)
    mainmenu.add_command(label=_("mnu_add_lot"), command=setup_add_lot)
    mainmenu.add_command(label=_("mnu_lang_change"), command=setup_language)
    mainmenu.add_command(label=_("exit"), command=confirm_close)
    root.config(menu=mainmenu)


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()
    add_menu()


def close_window():
    global root
    global return_value
    if return_value:
        root.destroy()


def confirm_close():
    confirmation_box(translation.gettext("close_confirm"))


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


def confirmation_box(message, title="Confirmation"):
    global root
    global translation
    global return_value
    _ = translation.gettext

    return_value = False

    def set_return_value(val):
        global return_value
        return_value = val
        close_window()

    popup = tk.Toplevel()
    popup.title(title)
    popup.geometry("300x100")

    lbl_image = Label(popup, image="::tk::icons::warning")
    lbl_image.grid(row=0, column=0)
    lbl_message = Label(popup, text=message)
    lbl_message.grid(row=0, column=1, columnspan=3)

    btn_yes = Button(popup, text=_("yes"),
                     command=lambda:[set_return_value(True)], width=10)
    btn_yes.grid(row=1, column=1)
    btn_no = Button(popup, text=_("no"),
                    command=lambda:[set_return_value(False), popup.destroy()], width=10)
    btn_no.grid(row=1, column=2)

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
    btn_afrikaans = tk.Button(popup, text="Afrikaans",
                              command=lambda: [set_language("af")])
    btn_afrikaans.pack()
    btn_english = tk.Button(popup, text="English",
                            command=lambda: [set_language("en")])
    btn_english.pack()
    btn_close = tk.Button(popup, text=translation.gettext(
        "close"), command=popup.destroy)
    btn_close.pack()


def setup_add_bidders():
    clear_window()
    global root
    global translation
    _ = translation.gettext

    lbl_total_bidders = tk.Label(root, text=_(
        "total_bidders")).grid(row=0, column=0)
    lbl_new_name = tk.Label(root, text=_("new_name")).grid(row=2, column=0)
    ent_new_name = tk.Entry(root, width=20)
    ent_new_name.insert(0, "Enter name")
    ent_new_name.grid(row=2, column=1)

    btn_add = tk.Button(root, text=_("btn_add_bidder"))
    btn_add.focus_set()
    btn_add.grid(row=3, column=0)
    btn_add_mult = tk.Button(root, text=_(
        "btn_add_mult_bidder")).grid(row=3, column=3)


def setup_add_lot():
    clear_window()
    global root
    global translation
    _ = translation.gettext

    lbl_total_lots = tk.Label(root, text=_("total_lots")).grid(row=0, column=0)
    lbl_new_lot = tk.Label(root, text=_("new_lot")).grid(row=2, column=0)
    ent_new_lot = tk.Entry(root, width=20)
    ent_new_lot.insert(0, "Enter lot")
    ent_new_lot.grid(row=2, column=1)

    btn_add = tk.Button(root, text=_("btn_add_lot"))
    btn_add.focus_set()
    btn_add.grid(row=3, column=0)
    btn_add_mult = tk.Button(root, text=_(
        "btn_add_mult_lot")).grid(row=3, column=3)


def setup_auction():
    clear_window()
    global root
    global translation
    _ = translation.gettext

    frm_header = Frame(root, width=300, height=150)
    frm_header.pack(fill=BOTH)

    lbl_total_bidders_label = tk.Label(
        frm_header, text=_("total_bidders")).grid(row=0, column=0)
    lbl_total_bidders_value = tk.Label(
        frm_header, text="12").grid(row=0, column=1)
    lbl_total_lots_label = tk.Label(
        frm_header, text=_("total_lots")).grid(row=0, column=2)
    lbl_total_lots_value = tk.Label(
        frm_header, text="15").grid(row=0, column=3)
    lbl_end_goal_label = tk.Label(
        frm_header, text=_("end_goal")).grid(row=0, column=4)
    lbl_end_goal_value = tk.Label(
        frm_header, text="R150 000").grid(row=0, column=5)

    frm_current_info = Frame(root, width=300, height=250)
    frm_current_info.pack(fill=BOTH)

    lbl_current_lot_label = tk.Label(
        frm_current_info, text=_("current_lot")).grid(row=1, column=0)
    lbl_current_lot_value = tk.Label(
        frm_current_info, text="current_lot").grid(row=1, column=1)

    lbl_current_bid_label = tk.Label(
        frm_current_info, text=_("current_bid")).grid(row=2, column=0)
    lbl_current_bid_value = tk.Label(
        frm_current_info, text="curr_amount ").grid(row=2, column=1)
    lbl_current_bidder_label = tk.Label(
        frm_current_info, text=_("from")).grid(row=2, column=2)
    lbl_current_bidder_value = tk.Label(
        frm_current_info, text="curr_bidder").grid(row=2, column=3)

    frm_graph = Frame(root, width=300, height=250)
    frm_graph.pack(expand=False, fill=BOTH)

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

    frm_btns = Frame(root, width=300, height=100)
    frm_btns.pack(expand=True, fill=BOTH)

    btn_new_bid = tk.Button(frm_btns, text=_("btn_new_bid"))
    btn_new_bid.focus_set()
    btn_new_bid.grid(row=0, column=0)

    btn_close_lot = tk.Button(frm_btns, text=_("btn_close_lot"))
    btn_close_lot.grid(row=0, column=1)

    btn_next_lot = tk.Button(frm_btns, text=_("btn_next_lot"))
    btn_next_lot.grid(row=0, column=2)

    btn_select_lot = tk.Button(frm_btns, text=_("btn_select_lot"))
    btn_select_lot.grid(row=0, column=3)


def main():
    setup_main()
    global root
    root.mainloop()


if __name__ == '__main__':
    main()