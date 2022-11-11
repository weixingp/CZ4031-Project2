from functools import partial
from tkinter import *
from tkinter import messagebox

from node import PlanNode
from preprocessing import QueryPlanner
from sample_sql import sql_list


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
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="white", relief=SOLID, borderwidth=1,
                      font=("tahoma", "12", "normal"))
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


def draw_tree(tree: PlanNode, frame, no_annotation=False):
    frame_top = Frame(frame, bg="white")
    frame_top.pack(ipadx=5, fill=X)
    frame_bottom = Frame(frame, bg="white")
    frame_bottom.pack(fill=X)

    if len(tree.type) > 12:
        width = 13
    else:
        width = 10
    label = Label(frame_top, text=tree.type, fg="black", bg="white", relief=SOLID, borderwidth=1, width=width)
    label.pack()

    # Process tooltip content
    extra_annotation = qp.extra_annotation.get(tree.type, None)

    if no_annotation:
        tooltip_text = f"Cost: {tree.cost}"
    else:
        tooltip_text = f"Cost: {tree.cost}\n\n{tree.get_formatted_annotations()}"
        if extra_annotation:
            # add line break if more than 70 characters
            if len(extra_annotation) >= 70:
                last_space_before = extra_annotation[:70].rindex(' ')
                extra_annotation = extra_annotation[:last_space_before] + '\n' + extra_annotation[
                                                                                 last_space_before + 1:]
            tooltip_text += f"\n{extra_annotation}"

    CreateToolTip(
        label,
        text=tooltip_text
    )
    # left = tree[1] != [""]
    # right = tree[2] != [""]
    if len(tree.children) > 0:
        Label(frame_top, text="|", bg="white").pack()
        frame_arrow = Frame(frame_top, bg="white")
        frame_arrow.pack(expand=True, fill=X)
        frame_arrow.grid_columnconfigure(0, weight=1)
        frame_arrow.grid_columnconfigure(1, weight=3)
        frame_arrow.grid_columnconfigure(2, weight=1)
        frame_arrow.grid_rowconfigure(0, weight=1)

        if len(tree.children) == 2:
            Label(frame_arrow, text=" ", bg="white").grid(row=0, column=0, sticky="ew")
            Canvas(frame_arrow, height=2, width=20, bg='black').grid(row=0, column=1, sticky="ew")
            Label(frame_arrow, text=" ", bg="white").grid(row=0, column=2, sticky="ew")

            frame_left = Frame(frame_bottom, bg="white")
            frame_left.pack(side=LEFT, anchor=N, expand=True)
            draw_tree(tree.children[0], frame_left, no_annotation)

            frame_right = Frame(frame_bottom, bg="white")
            frame_right.pack(side=LEFT, anchor=N, expand=True)
            draw_tree(tree.children[1], frame_right, no_annotation)
        else:
            Label(frame_arrow, text="|", bg="white").pack()

            frame_left = Frame(frame_bottom, bg="white")
            frame_left.pack(side=LEFT, anchor=N, expand=True)
            draw_tree(tree.children[0], frame_left, no_annotation)


def getinput():
    global qp, query
    annotate_submit_btn.config(text="Generating...")
    query = textinput.get("1.0", END)
    try:
        qp.generate_plans(query)
        pagechange()
    except Exception as ex:
        messagebox.showerror("SQL Error", ex)
        annotate_submit_btn.config(text="Annotate")


# using this to change pages first
def change():
    pagechange()


def mainpage(root):
    global textinput, annotate_submit_btn
    title = Label(root, text="SQL Query Annotator", height=2, bg="#3B86A7", fg="white", font="Inter 48")
    title.place(anchor=CENTER, relx=0.5, rely=0.12)
    title.grid(row=0, column=0, columnspan=5, sticky='ew')
    subtitle = Label(root, text="Enter Query Here:", bg="white", fg="black", font="Inter 18 bold")
    subtitle.place(x=80, y=140)

    textinput = Text(width=60, height=20, bg="#CCE4EB")
    textinput.place(x=80, y=180)

    annotate_submit_btn = Button(root, text="Annotate", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 16",
                                 command=getinput)
    annotate_submit_btn.place(x=80, y=480)

    # Example SQL input

    subtitle2 = Label(root, text="Example SQLs:", bg="white", fg="black", font="Inter 18 bold")
    subtitle2.place(x=550, y=140)

    sql1_btn = Button(root, text=f"SQL Query 1", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 16",
                      command=lambda: insert_sql(0))
    sql1_btn.place(x=550, y=180 + 40 * 0)

    sql2_btn = Button(root, text=f"SQL Query 2", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 16",
                      command=lambda: insert_sql(1))
    sql2_btn.place(x=550, y=180 + 40 * 1)

    sql3_btn = Button(root, text=f"SQL Query 3", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 16",
                      command=lambda: insert_sql(2))
    sql3_btn.place(x=550, y=180 + 40 * 2)

    sql4_btn = Button(root, text=f"SQL Query 4", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 16",
                      command=lambda: insert_sql(3))
    sql4_btn.place(x=550, y=180 + 40 * 3)


def insert_sql(index):
    assert 4 > index >= 0, "SQL index out of range"
    # textinput.delete(0, END)
    textinput.delete("0.0", END)
    textinput.insert("0.0", sql_list[index])


def outputpage(root, plan_root: PlanNode, no_annotation=False):
    title = Label(root, text="Query Annotation", bg="#3B86A7", fg="white", font="Inter 48", height=2)
    title.place(anchor=CENTER, relx=0.5, rely=0.12)
    title.grid(row=0, column=0, columnspan=5, sticky='ew')

    home_button = Button(root, text="Back", width=5, height=1, bg="#3B86A7", fg="black", font="Inter 16",
                         command=change)
    home_button.place(x=25, y=35)

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
    Label(scrollable_frame, text="", bg="white").pack()
    canvas.create_window((415, 250), window=scrollable_frame, anchor="n")
    draw_tree(plan_root, scrollable_frame, no_annotation)

    plan_cost_title = Label(root, text=f"Plan cost: {plan_root.cost}", bg="white", fg="black", font="Inter 18 bold")
    plan_cost_title.place(x=20, y=120)

    Label(scrollable_frame, text="", bg="white").pack()

    # bottom page
    original_query_box = Text(width=60, height=10, bg="#CCE4EB")
    original_query_box.place(x=30, y=505)
    original_query_box.insert("1.0", query)

    plan_cost_title = Label(root, text=f"Alt Plans:", bg="white", fg="black", font="Inter 16")
    plan_cost_title.place(x=480, y=505)
    alt_plans_btns()


def refreshOutputpage(root, plan_root: PlanNode, no_annotation=False):
    for widget in root.winfo_children():
        widget.destroy()
    outputpage(root, plan_root, no_annotation)


def alt_plans_btns():
    org_btn = Button(root, text=f"Original Plan", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 14",
                     command=partial(refreshOutputpage, root, qp.qep, False))
    org_btn.place(x=700, y=505)
    keep = []
    i = 0
    top_padding = 0
    right_padding = 0
    for key, node in qp.aqp.items():
        plan1_btn = Button(root, text=f"No {key}", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 14",
                           command=partial(refreshOutputpage, root, node, True))
        plan1_btn.place(x=480 + right_padding, y=540 + top_padding)
        keep.append(plan1_btn)
        i += 1
        top_padding += 40
        if i >= 2:
            top_padding = 0
            right_padding += 150


def connect_db_form():
    global top
    top = Toplevel(root)
    top.geometry("400x250")

    def disable_event():
        pass

    top.title("Connect to PostresSQL Database")
    top.protocol("WM_DELETE_WINDOW", disable_event)
    top.protocol("WM_MINIMIZE_WINDOW", disable_event)
    # top.overrideredirect(True)
    top.attributes('-topmost', 'true')
    center(top)
    fields = [
        "Host",
        "Port",
        "DB Name",
        "Username",
        "Password"
    ]

    entry_list = []
    y_padding = 30
    for index, item in enumerate(fields):
        row = Label(top, text=f"{item}: ", )
        row.place(x=100, y=20 + y_padding * index)

        entry = Entry(top, width=35)
        entry.place(x=200, y=20 + y_padding * index, width=100)

        # insert default value
        if item == "Host":
            entry.insert(0, "127.0.0.1")
        elif item == "Port":
            entry.insert(0, "5432")

        entry_list.append(entry)

    submitbtn = Button(
        top,
        text="Login",
        bg='blue',
        command=lambda: login_db([x.get() for x in entry_list])
    )
    submitbtn.place(x=175, y=(len(fields) + 1) * y_padding, width=55)


def login_db(credentials: list):
    global qp, is_logged_in
    try:
        qp = QueryPlanner(*credentials)
        is_logged_in = True
        top.destroy()
        top.update()
        mainpage(root)
    except Exception as ex:
        top.attributes('-topmost', 'false')
        messagebox.showerror("Unable to connect to DB", ex)
        top.attributes('-topmost', 'true')


def pagechange():
    global page_num, root
    for widget in root.winfo_children():
        widget.destroy()

    if page_num == 1:
        outputpage(root, qp.qep)
        page_num = 2
    else:
        mainpage(root)
        page_num = 1


def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


page_num = 1

is_logged_in = False
root = Tk()
root.geometry("850x650")
root.resizable(False, False)
root.title("CZ4031 Database System Principles GUI")
root.configure(background="white")
root.columnconfigure(0, weight=1)
center(root)
connect_db_form()
root.mainloop()
