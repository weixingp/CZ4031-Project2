from tkinter import *

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 30
        y = y + cy + self.widget.winfo_rooty() +20
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                         background="white", relief=SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def CreateToolTip(widget, text):

    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

def drawTree(tree, frame):
    frame_top = Frame(frame, bg="white")
    frame_top.pack(ipadx=5, fill=X)
    frame_bottom = Frame(frame, bg="white")
    frame_bottom.pack(fill=X)
    label = Label(frame_top, text=tree[0], fg="black", bg="white", relief=SOLID, borderwidth=1, width=8)
    label.pack()
    CreateToolTip(label, text = tree[0] + '\nThis is how tip looks like.')
    left = tree[1] != [""]
    right = tree[2] != [""]
    if left or right:
        Label(frame_top, text="|", bg="white").pack()
        frame_arrow = Frame(frame_top, bg="white")
        frame_arrow.pack(expand=True, fill=X)
        frame_arrow.grid_columnconfigure(0, weight = 1)
        frame_arrow.grid_columnconfigure(1, weight = 3)
        frame_arrow.grid_columnconfigure(2, weight = 1)
        frame_arrow.grid_rowconfigure(0, weight = 1)

        if left and right:
            Label(frame_arrow, text=" ", bg="white").grid(row = 0, column = 0, sticky = "ew")
            Canvas(frame_arrow, height=2, width=20, bg='black').grid(row = 0, column = 1, sticky = "ew")
            Label(frame_arrow, text=" ", bg="white").grid(row = 0, column = 2, sticky = "ew")
        else:
            Label(frame_arrow, text="|", bg="white").pack()

        if left:
            frame_left = Frame(frame_bottom, bg="white")
            frame_left.pack(side=LEFT, anchor=N, expand=True)
            drawTree(tree[1], frame_left)
        if right:
            frame_right = Frame(frame_bottom, bg="white")
            frame_right.pack(side=LEFT, anchor=N, expand=True)
            drawTree(tree[2], frame_right)

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

    frame_output = Frame(root, bg="white", height=400, width=850, padx=0, pady=0)
    frame_output.place(x=0, y=100)

    canvas = Canvas(frame_output, bg="white", height=380, width=830)
    vsb = Scrollbar(frame_output, orient="vertical", command=canvas.yview)
    hsb = Scrollbar(frame_output, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    scrollable_frame = Frame(canvas, bg="white")
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((415, 190), window=scrollable_frame, anchor="center")

    # TODO modify code to get actual tree
    tree = ["a", ["b", ["c",
                        ["f", ["h", ["i", [""], [""]], ["j", ["m", [""], [""]], ["n", [""], [""]]]], [""]],
                        ["g", [""], [""]]], ["d", ["e", ["k", [""], [""]], ["l", [""], [""]]], [""]]], [""]]
    Label(scrollable_frame, text="", bg="white").pack()
    drawTree(tree, scrollable_frame)
    Label(scrollable_frame, text="", bg="white").pack()

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