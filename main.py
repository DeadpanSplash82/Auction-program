import tkinter as tk
import gettext

lang_changed = False
root = None

translation = gettext.translation(
        'auction', localedir='translations', languages=['en'])
translation.install()
# _ = translation.gettext

def setup_window():
    global root
    global translation
    if root is not None:
        root.destroy()
    root = tk.Tk()
    root.title("Auction program")
    root.geometry("400x400")

    btn_language = tk.Button(root, text="Change language", command=ask_language)
    btn_language.pack()

    lbl_test = tk.Label(root, text=translation.gettext("test_str"))
    lbl_test.pack()


def set_language(input_lang):
    global translation
    if input_lang == "en":
        lang = 'en'
    else:
        lang = 'af'
    translation = gettext.translation(
        'auction', localedir='translations', languages=[lang])
    translation.install()
    setup_window()


def ask_language():
    popup = tk.Toplevel()
    popup.title("Please select a language")
    btn_afrikaans = tk.Button(popup, text="Afrikaans", command=lambda:[set_language("af")])
    btn_afrikaans.pack()
    btn_english = tk.Button(popup, text="English", command=lambda:[set_language("en")])
    btn_english.pack()
    btn_close = tk.Button(popup, text="Close", command=popup.destroy)
    btn_close.pack()


def main():
    setup_window() 
    global root 

    root.mainloop()


if __name__ == '__main__':
    main()
