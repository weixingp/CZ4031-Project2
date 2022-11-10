from tkinter import *

def getinput():
    global output, query
    query = textinput.get("1.0", END) 
    output = processQuery(query)
    if output:
        pagechange()
    # else:
    #     messagebox.showerror("Error", "Invalid Input!\nInput SQL query")

#using this to change pages first
def change():
    pagechange()

def mainpage(root):

    title = Label(root, text="SQL Query Annotator", height=1, width=25, bg="#3B86A7", fg="white", font="Inter 48")
    title.place(anchor=CENTER, relx=0.5, rely=0.12)


    subtitle = Label(root, text="Enter Query Here:", bg="white", fg="black", font="Inter 18 bold")
    subtitle.place(x=80,y=120)

    textinput = Text(width=60, height=15, bg="#CCE4EB")
    textinput.place(x=180,y=160)


    input_button = Button(root, text = "Annotate", width=10, height=1, bg="#3B86A7", fg="white", font="Inter 16", command=change)
    input_button.place(x=532,y=420)

def outputpage(root):
    title = Label(root, text="Query Annotation", width=25, bg="#3B86A7", fg="white", font="Inter 48")
    title.place(anchor=CENTER, relx=0.5, rely=0.12)

    home_button = Button(root, text = "Back", width=5, height=1, bg="#3B86A7", fg="white", font="Inter 16", command=change)
    home_button.place(x=25,y=35)

def pagechange():
    global page_num, root
    for widget in root.winfo_children():
        widget.destroy()
    if page_num == 1:
        outputpage(root)
        page_num = 2
    else:
        mainpage(root)
        page_num = 1

page_num = 1

root = Tk()
root.geometry("850x500")
root.resizable(False, False)
root.title("CZ4031 Database System Principles GUI")
root.configure(background="white")
mainpage(root)
root.mainloop()