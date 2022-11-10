from tkinter import *

def click():
    entered_text = textinput.get()


def page1(root):

    title = Label(root, text="       SQL Query Annotator       ", bg="#3B86A7", fg="white", font="Inter 48", )
    title.place(anchor=CENTER, relx=0.5, rely=0.12)


    subtitle = Label(root, text="Enter Query Here:", bg="white", fg="black", font="Inter 18 bold")
    subtitle.place(x=80,y=120)

    textinput = Text(width=60, height=15, bg="#CCE4EB")
    textinput.place(x=180,y=160)


    input_button = Button(root, text = "Annotate", width=10, height=1, bg="#3B86A7", fg="white", font="Inter 16", command=click)
    input_button.place(x=532,y=420)



# Label(window, text="\nOutput:", bg="white", fg="black", font="none 12 bold") .grid(row=4, column=0,sticky=W)
# output = Text(window, width=75, height=6, wrap=WORD, background="white")
# output.grid(row=5, column=0, columnspan=2, sticky=W)

def pagechange():
    global page_num, root
    for widget in root.winfo_children():
        widget.destroy()
    if page_num == 1:
        page2(root)
        page_num = 2
    else:
        page1(root)
        page_num = 1

page_num = 1

root = Tk()
root.geometry("850x500")
root.resizable(False, False)
root.title("CZ4031 Database System Principles GUI")
root.configure(background="white")
page1(root)
root.mainloop()