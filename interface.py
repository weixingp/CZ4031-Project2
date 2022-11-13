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
        """
        Display text in tooltip window
        :param text: the text to be displayed
        """
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


def create_tooltip(widget, text):
    """
    creates a ToolTip object for the widget
    :param widget: the widget to display a ToolTip
    :param text: the text to be displayed
    """
    tool_tip = ToolTip(widget)

    def enter(event):
        tool_tip.showtip(text)

    def leave(event):
        tool_tip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def draw_tree(tree: PlanNode, frame, no_annotation=False):
    """
    draws the query execution plan in a binary tree form
    :param tree: the root plan node to access the query execution plan
    :param frame: the frame to display the tree in
    :param no_annotation: boolean to display annotations for QEP but not AQP
    """
    frame_top = Frame(frame, bg="white")
    frame_top.pack(ipadx=5, fill=X)
    frame_bottom = Frame(frame, bg="white")
    frame_bottom.pack(fill=X)

    # Displays the current node
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

    create_tooltip(
        label,
        text=tooltip_text
    )

    # Displays the child nodes
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


def get_input():
    """
    gets the query execution plan from the query in the text input
    """
    global qp, query
    annotate_submit_btn.config(text="Generating...")
    query = textinput.get("1.0", END)
    try:
        qp.generate_plans(query)
        page_change()
    except Exception as ex:
        messagebox.showerror("SQL Error", ex)
        annotate_submit_btn.config(text="Annotate")


# using this to change pages first
def change():
    page_change()


def main_page(win):
    """
    displays the UI for the input page to input the sql query
    :param win: the main window to display the input page
    """
    global textinput, annotate_submit_btn

    # Display title
    frame_main_title = Frame(win, bg='#3B86A7', height=60)
    frame_main_title.pack(fill='x')
    title = Label(frame_main_title, text="SQL Query Annotator", height=2, bg="#3B86A7", fg="white", font="Inter 48")
    title.pack(fill='both')

    # Display content
    frame_main_bottom = Frame(win, bg='white', padx=10, pady=10, width=850, height=490)
    frame_main_bottom.pack(fill='x')
    frame_main_bottom.rowconfigure(0, weight=1)
    frame_main_bottom.columnconfigure(0, weight=3)
    frame_main_bottom.columnconfigure(1, weight=1)

    # Text input box to input sql query
    frame_main_left = Frame(frame_main_bottom, bg='white', padx=10, pady=10)
    frame_main_left.grid(row=0, column=0, sticky='nsew')

    subtitle = Label(frame_main_left, text="Enter Query Here:", bg="white", fg="black", font="Inter 18 bold",
                     anchor='w')
    subtitle.pack(fill='x')
    textinput = Text(frame_main_left, width=60, height=20, bg="#CCE4EB")
    textinput.pack(fill='both')
    Label(frame_main_left, text=" ", bg="white").pack()
    annotate_submit_btn = Button(frame_main_left, text="Annotate", width=10, height=1, bg="#3B86A7",
                                 fg="black", font="Inter 16", command=get_input)
    annotate_submit_btn.pack()

    # Buttons to use example SQL input
    frame_main_right = Frame(frame_main_bottom, bg='white', padx=10, pady=10)
    frame_main_right.grid(row=0, column=1, sticky='nsew')

    subtitle2 = Label(frame_main_right, text="Example SQLs:", bg="white", fg="black", font="Inter 18 bold")
    subtitle2.pack()
    Label(frame_main_right, text=" ", bg="white").pack()  # padding
    Button(frame_main_right, text=f"SQL Query 1", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 16",
           command=lambda: insert_sql(0)).pack()
    Label(frame_main_right, text=" ", bg="white").pack()  # padding
    Button(frame_main_right, text=f"SQL Query 2", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 16",
           command=lambda: insert_sql(1)).pack()
    Label(frame_main_right, text=" ", bg="white").pack()  # padding
    Button(frame_main_right, text=f"SQL Query 3", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 16",
           command=lambda: insert_sql(2)).pack()
    Label(frame_main_right, text=" ", bg="white").pack()  # padding
    Button(frame_main_right, text=f"SQL Query 4", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 16",
           command=lambda: insert_sql(3)).pack()


def insert_sql(index):
    """
    inserts sample sql query into the input box
    :param index: the index of the
    """
    assert 4 > index >= 0, "SQL index out of range"
    textinput.delete("0.0", END)
    textinput.insert("0.0", sql_list[index])


def output_page(win, plan_root: PlanNode, no_annotation=False):
    """
    displays the UI for the annotations of query execution plan
    :param win: the main window to display the annotations of query execution plan
    :param plan_root: the root plan node to access the query execution plan
    :param no_annotation: boolean to display annotations for QEP but not AQP
    """

    # Display title
    frame_output_title = Frame(win, bg='#3B86A7', height=60, padx=40)
    frame_output_title.pack(fill='x')
    home_button = Button(frame_output_title, text="Back", width=5, height=1, bg="#3B86A7", fg="black", font="Inter 16",
                         command=change)
    home_button.pack(side=LEFT)
    title = Label(frame_output_title, text="Query Annotation", height=2, bg="#3B86A7", fg="white", font="Inter 48")
    title.pack(side=LEFT, fill='x', expand=1)
    Label(frame_output_title, text="Back", width=5, height=1, bg="#3B86A7", fg="#3B86A7",
          font="Inter 16").pack(side=LEFT)  # padding

    # Display content
    frame_output_content = Frame(win, bg="white", height=490, width=850, padx=0, pady=0)
    frame_output_content.pack(fill='x')
    frame_output_content.rowconfigure(0, weight=1)
    frame_output_content.columnconfigure(0, weight=3)
    frame_output_content.columnconfigure(1, weight=1)

    # Display annotation frame
    frame_output = Frame(frame_output_content, bg="white", height=320, width=850, padx=0, pady=0)
    frame_output.pack(fill='x')

    canvas = Canvas(frame_output, bg="white", height=320, width=830)
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
    Label(scrollable_frame, text="", bg="white").pack()

    plan_cost_title = Label(frame_output, text=f"Plan cost: {plan_root.cost}", bg="white", fg="black",
                            font="Inter 18 bold")
    plan_cost_title.place(x=20, y=20)

    # Display bottom frame
    frame_output_bottom = Frame(frame_output_content, bg="white", height=170, width=850, padx=0, pady=0)
    frame_output_bottom.pack(fill='x')

    original_query_box = Text(frame_output_bottom, width=60, height=10, bg="#CCE4EB")
    original_query_box.pack(side=LEFT)
    original_query_box.insert("1.0", query)

    frame_output_bottom_aqp = Frame(frame_output_bottom, bg="white", width=200, padx=20)
    frame_output_bottom_aqp.pack(side=LEFT, fill='both')

    frame_output_bottom_qep = Frame(frame_output_bottom, bg="white")
    frame_output_bottom_qep.pack(side=LEFT, fill='both', expand=1)

    alt_plan_label = Label(frame_output_bottom_aqp, text=f"Alt Plans:", bg="white", fg="black", font="Inter 16",
                           anchor='w')
    alt_plan_label.pack()
    alt_plans_buttons(frame_output_bottom_aqp, frame_output_bottom_qep)


def refresh_output_page(win, plan_root: PlanNode, no_annotation=False):
    """
    switches UI to display the alternate plan
    :param win: the main window to display the annotations of query execution plan
    :param plan_root: the root plan node to access the alternate plan
    :param no_annotation: boolean to display annotations for QEP but not AQP
    """
    for widget in win.winfo_children():
        widget.destroy()
    output_page(win, plan_root, no_annotation)


def alt_plans_buttons(frame_aqp, frame_qep):
    """
    displays buttons to switch between different query plans
    :param frame_aqp: the frame in which to display the alternate query plan buttons
    :param frame_qep: the frame in which to display the query execution plan button
    """
    org_btn = Button(frame_qep, text=f"Original Plan", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 14",
                     command=partial(refresh_output_page, root, qp.qep, False))
    org_btn.place(relx=0.5, rely=0.5, anchor=CENTER)
    keep = []
    for key, node in qp.aqp.items():
        plan1_btn = Button(frame_aqp, text=f"No {key}", width=10, height=1, bg="#3B86A7", fg="black", font="Inter 14",
                           command=partial(refresh_output_page, root, node, True))
        plan1_btn.pack()
        keep.append(plan1_btn)


def connect_db_form():
    """
    displays the login form to connect to DB
    """
    global top
    top = Toplevel(root)
    top.geometry("400x250")

    def disable_event():
        pass

    top.title("Connect to PostgresSQL Database")
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

    submit_button = Button(
        top,
        text="Login",
        bg='blue',
        command=lambda: login_db([x.get() for x in entry_list])
    )
    submit_button.place(x=175, y=(len(fields) + 1) * y_padding, width=55)


def login_db(credentials: list):
    """
    to attempt login to connect to DB
    """
    global qp, is_logged_in
    try:
        qp = QueryPlanner(*credentials)
        is_logged_in = True
        top.destroy()
        top.update()
        main_page(root)
    except Exception as ex:
        top.attributes('-topmost', 'false')
        messagebox.showerror("Unable to connect to DB", ex)
        top.attributes('-topmost', 'true')


def page_change():
    """
    to switch between the input query page and output annotation page
    """
    global page_num, root
    for widget in root.winfo_children():
        widget.destroy()

    if page_num == 1:
        output_page(root, qp.qep)
        page_num = 2
    else:
        main_page(root)
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
center(root)
connect_db_form()
root.mainloop()
