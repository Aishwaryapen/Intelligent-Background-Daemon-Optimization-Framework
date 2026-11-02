import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import time
import threading

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from monitor import get_processes
from adaptive_analyzer import AdaptiveAnalyzer
from optimizer import lower_priority, restore_priority
from performance import measure_process


class ResourceOptimizerApp:

    def __init__(self, root):

        self.root = root

        # ==================================================
        # WINDOW
        # ==================================================

        self.root.title(
            "Intelligent Background Daemon Optimization Framework"
        )

        self.root.geometry("1400x900")
        self.root.minsize(1150, 750)

        # ==================================================
        # APPLICATION STATE
        # ==================================================

        self.adaptive_analyzer = AdaptiveAnalyzer(
            cpu_threshold=20,
            memory_threshold=5,
            required_checks=3
        )

        self.optimized_processes = {}

        self.process_cache = {}

        self.refresh_running = False
        self.optimization_running = False

        self.sort_column = "cpu"
        self.sort_reverse = True

        # ==================================================
        # GRAPH DATA
        # ==================================================

        self.time_data = []
        self.cpu_data = []
        self.memory_data = []

        self.start_time = time.time()

        # Prime psutil
        psutil.cpu_percent(interval=None)

        # ==================================================
        # STYLE
        # ==================================================

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Arial", 21, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Arial", 10)
        )

        style.configure(
            "Treeview",
            rowheight=28,
            font=("Arial", 9)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 9, "bold"),
            padding=6
        )

        style.configure(
            "Action.TButton",
            font=("Arial", 10, "bold"),
            padding=(15, 9)
        )

        # ==================================================
        # MAIN CONTAINER
        # ==================================================

        main = ttk.Frame(
            root,
            padding=10
        )

        main.pack(
            fill="both",
            expand=True
        )

        # ==================================================
        # TITLE
        # ==================================================

        ttk.Label(
            main,
            text="Intelligent Resource Optimizer",
            style="Title.TLabel"
        ).pack(
            pady=(0, 2)
        )

        ttk.Label(
            main,
            text=(
                "Adaptive Background Process Monitoring "
                "and Optimization"
            ),
            style="Subtitle.TLabel"
        ).pack(
            pady=(0, 10)
        )

        # ==================================================
        # SYSTEM STATUS
        # ==================================================

        stats_frame = ttk.LabelFrame(
            main,
            text="System Status",
            padding=8
        )

        stats_frame.pack(
            fill="x",
            pady=(0, 8)
        )

        self.process_label = ttk.Label(
            stats_frame,
            text="Processes: 0",
            font=("Arial", 10, "bold")
        )

        self.process_label.pack(
            side="left",
            expand=True
        )

        self.candidate_label = ttk.Label(
            stats_frame,
            text="Candidates: 0",
            font=("Arial", 10, "bold")
        )

        self.candidate_label.pack(
            side="left",
            expand=True
        )

        self.cpu_label = ttk.Label(
            stats_frame,
            text="System CPU: 0%",
            font=("Arial", 10, "bold")
        )

        self.cpu_label.pack(
            side="left",
            expand=True
        )

        self.ram_label = ttk.Label(
            stats_frame,
            text="System RAM: 0%",
            font=("Arial", 10, "bold")
        )

        self.ram_label.pack(
            side="left",
            expand=True
        )

        # ==================================================
        # SEARCH
        # ==================================================

        search_frame = ttk.Frame(main)

        search_frame.pack(
            fill="x",
            pady=(0, 7)
        )

        ttk.Label(
            search_frame,
            text="Search Process:"
        ).pack(
            side="left",
            padx=(2, 5)
        )

        self.search_var = tk.StringVar()

        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=35
        )

        self.search_entry.pack(
            side="left",
            padx=(0, 8)
        )

        self.search_var.trace_add(
            "write",
            self.on_search_changed
        )

        ttk.Button(
            search_frame,
            text="Clear Search",
            command=self.clear_search
        ).pack(
            side="left"
        )

        ttk.Label(
            search_frame,
            text="Click a column heading to sort"
        ).pack(
            side="right"
        )

        # ==================================================
        # PROCESS TABLE
        # ==================================================

        process_frame = ttk.LabelFrame(
            main,
            text="Background Process Monitor",
            padding=6
        )

        process_frame.pack(
            fill="both",
            expand=True,
            pady=(0, 8)
        )

        table_container = ttk.Frame(
            process_frame
        )

        table_container.pack(
            fill="both",
            expand=True
        )

        columns = (
            "pid",
            "process",
            "cpu",
            "memory",
            "status",
            "decision"
        )

        self.process_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # ==================================================
        # HEADINGS
        # ==================================================

        self.process_table.heading(
            "pid",
            text="PID",
            command=lambda: self.sort_table("pid")
        )

        self.process_table.heading(
            "process",
            text="PROCESS",
            command=lambda: self.sort_table("process")
        )

        self.process_table.heading(
            "cpu",
            text="CPU %",
            command=lambda: self.sort_table("cpu")
        )

        self.process_table.heading(
            "memory",
            text="MEM %",
            command=lambda: self.sort_table("memory")
        )

        self.process_table.heading(
            "status",
            text="STATUS",
            command=lambda: self.sort_table("status")
        )

        self.process_table.heading(
            "decision",
            text="ADAPTIVE DECISION",
            command=lambda: self.sort_table("decision")
        )

        # ==================================================
        # COLUMNS
        # ==================================================

        self.process_table.column(
            "pid",
            width=80,
            minwidth=70,
            anchor="center"
        )

        self.process_table.column(
            "process",
            width=280,
            minwidth=170
        )

        self.process_table.column(
            "cpu",
            width=100,
            minwidth=80,
            anchor="center"
        )

        self.process_table.column(
            "memory",
            width=100,
            minwidth=80,
            anchor="center"
        )

        self.process_table.column(
            "status",
            width=120,
            minwidth=90,
            anchor="center"
        )

        self.process_table.column(
            "decision",
            width=240,
            minwidth=180,
            anchor="center"
        )

        # ==================================================
        # SCROLLBARS
        # ==================================================

        vertical_scroll = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.process_table.yview
        )

        horizontal_scroll = ttk.Scrollbar(
            table_container,
            orient="horizontal",
            command=self.process_table.xview
        )

        self.process_table.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )

        self.process_table.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        vertical_scroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal_scroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        table_container.rowconfigure(
            0,
            weight=1
        )

        table_container.columnconfigure(
            0,
            weight=1
        )

        self.process_table.bind(
            "<<TreeviewSelect>>",
            self.on_process_selected
        )

        self.process_table.bind(
            "<MouseWheel>",
            self.mousewheel_scroll
        )

        self.process_table.bind(
            "<Up>",
            self.keyboard_selection
        )

        self.process_table.bind(
            "<Down>",
            self.keyboard_selection
        )

        # ==================================================
        # SELECTED PROCESS
        # ==================================================

        selection_frame = ttk.Frame(
            process_frame
        )

        selection_frame.pack(
            fill="x",
            pady=(6, 0)
        )

        ttk.Label(
            selection_frame,
            text="Selected Process:"
        ).pack(
            side="left"
        )

        self.selected_label = ttk.Label(
            selection_frame,
            text="None",
            font=("Arial", 10, "bold")
        )

        self.selected_label.pack(
            side="left",
            padx=6
        )

        # ==================================================
        # OPTIMIZATION CONTROLS
        # ==================================================

        action_frame = ttk.LabelFrame(
            main,
            text="Optimization Controls",
            padding=8
        )

        action_frame.pack(
            fill="x",
            pady=(0, 8)
        )

        self.refresh_button = ttk.Button(
            action_frame,
            text="⟳  Refresh",
            style="Action.TButton",
            command=self.manual_refresh
        )

        self.refresh_button.pack(
            side="left",
            padx=4
        )

        self.optimize_button = ttk.Button(
            action_frame,
            text="⚡  Optimize Selected",
            style="Action.TButton",
            command=self.optimize_selected
        )

        self.optimize_button.pack(
            side="left",
            padx=4
        )

        self.restore_button = ttk.Button(
            action_frame,
            text="↩  Restore Selected",
            style="Action.TButton",
            command=self.restore_selected
        )

        self.restore_button.pack(
            side="left",
            padx=4
        )

        ttk.Label(
            action_frame,
            text=(
                "Optimization is available only for "
                "persistent high-resource processes."
            )
        ).pack(
            side="right",
            padx=10
        )

        # ==================================================
        # BOTTOM AREA
        # ==================================================

        bottom_frame = ttk.Frame(
            main
        )

        bottom_frame.pack(
            fill="both",
            expand=True
        )

        # ==================================================
        # GRAPH
        # ==================================================

        graph_frame = ttk.LabelFrame(
            bottom_frame,
            text="Live System Resource Monitoring",
            padding=5
        )

        graph_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5)
        )

        self.figure = Figure(
            figsize=(7, 3),
            dpi=85
        )

        self.ax = self.figure.add_subplot(111)

        self.ax.set_title(
            "CPU and Memory Usage"
        )

        self.ax.set_xlabel(
            "Time (seconds)"
        )

        self.ax.set_ylabel(
            "Usage (%)"
        )

        self.ax.set_ylim(
            0,
            100
        )

        self.ax.grid(
            True,
            alpha=0.3
        )

        self.cpu_line, = self.ax.plot(
            [],
            [],
            label="CPU Usage"
        )

        self.memory_line, = self.ax.plot(
            [],
            [],
            label="Memory Usage"
        )

        self.ax.legend(
            loc="upper right"
        )

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=graph_frame
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        # ==================================================
        # PERFORMANCE PANEL
        # ==================================================

        performance_frame = ttk.LabelFrame(
            bottom_frame,
            text="Selected Process / Performance",
            padding=5
        )

        performance_frame.pack(
            side="right",
            fill="both",
            expand=False,
            padx=(5, 0)
        )

        # Give the performance panel enough horizontal space while
        # allowing its contents to scroll vertically.
        performance_frame.configure(
            width=400
        )

        performance_frame.pack_propagate(False)

        # --------------------------------------------------
        # PERFORMANCE SCROLLABLE AREA
        # --------------------------------------------------

        performance_canvas = tk.Canvas(
            performance_frame,
            highlightthickness=0,
            borderwidth=0
        )

        performance_scrollbar = ttk.Scrollbar(
            performance_frame,
            orient="vertical",
            command=performance_canvas.yview
        )

        self.performance_content = ttk.Frame(
            performance_canvas
        )

        performance_window = performance_canvas.create_window(
            (0, 0),
            window=self.performance_content,
            anchor="nw"
        )

        # The content frame is allowed to become as tall as its
        # actual contents. This is what makes vertical scrolling work.
        self.performance_content.bind(
            "<Configure>",
            lambda event: performance_canvas.configure(
                scrollregion=performance_canvas.bbox("all")
            )
        )

        # Keep the content width equal to the visible canvas width.
        # This avoids clipping the text when the window is resized.
        performance_canvas.bind(
            "<Configure>",
            lambda event: performance_canvas.itemconfigure(
                performance_window,
                width=event.width
            )
        )

        performance_canvas.configure(
            yscrollcommand=performance_scrollbar.set
        )

        performance_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        performance_scrollbar.pack(
            side="right",
            fill="y"
        )

        # Scroll when the mouse is over the panel, its text, or
        # the scrollbar area.
        def scroll_performance(event):
            if event.delta:
                performance_canvas.yview_scroll(
                    int(-event.delta / 120),
                    "units"
                )
            return "break"

        performance_canvas.bind("<MouseWheel>", scroll_performance)
        self.performance_content.bind("<MouseWheel>", scroll_performance)

        self.performance_canvas = performance_canvas

        # ==================================================
        # PERFORMANCE TEXT
        # ==================================================

        self.performance_label = tk.Label(
            self.performance_content,
            text=(
                "Select a process from the table\n\n"
                "to view CPU, memory, priority,\n"
                "adaptive decision and optimization\n"
                "information."
            ),
            font=("Arial", 10),
            justify="left",
            anchor="nw",
            wraplength=360
        )

        # IMPORTANT:
        # Do not use expand=True here. The label must keep its natural
        # height so the canvas has a real scrollable content area.
        self.performance_label.pack(
            anchor="nw",
            padx=10,
            pady=10,
            fill="x"
        )

        self.performance_label.bind(
            "<MouseWheel>",
            scroll_performance
        )

        # ==================================================
        # STATUS BAR
        # ==================================================

        self.status_bar = ttk.Label(
            main,
            text="Starting monitoring...",
            relief="sunken",
            anchor="w",
            padding=5
        )

        self.status_bar.pack(
            fill="x",
            pady=(4, 0)
        )

        # ==================================================
        # CLOSE
        # ==================================================

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

        # ==================================================
        # START MONITORING
        # ==================================================

        self.update_system_graph()

        self.start_background_refresh()

    # ======================================================
    # BACKGROUND REFRESH
    # ======================================================

    def start_background_refresh(self):

        if self.refresh_running:
            return

        self.refresh_running = True

        thread = threading.Thread(
            target=self.collect_processes_background,
            daemon=True
        )

        thread.start()

    def collect_processes_background(self):

        try:

            processes = get_processes()

            self.root.after(
                0,
                lambda: self.finish_process_refresh(
                    processes
                )
            )

        except Exception as error:

            self.root.after(
                0,
                lambda: self.refresh_failed(
                    error
                )
            )

    def finish_process_refresh(
        self,
        processes
    ):

        self.refresh_running = False

        if not self.root.winfo_exists():
            return

        try:

            active_pids = [
                process["pid"]
                for process in processes
            ]

            self.adaptive_analyzer.cleanup(
                active_pids
            )

            analyzed_processes = []

            for process in processes:

                result = self.adaptive_analyzer.analyze(
                    process
                )

                analyzed = process.copy()

                analyzed["category"] = result[
                    "category"
                ]

                analyzed["reason"] = result[
                    "reason"
                ]

                analyzed["safe_candidate"] = result[
                    "safe_candidate"
                ]

                analyzed_processes.append(
                    analyzed
                )

            self.process_cache = {
                process["pid"]: process
                for process in analyzed_processes
            }

            self.update_process_table()

            self.update_statistics()

            self.status_bar.config(
                text=(
                    f"Monitoring "
                    f"{len(analyzed_processes)} "
                    f"processes | Ready"
                )
            )

        except Exception as error:

            print(
                "GUI refresh error:",
                error
            )

        self.root.after(
            2500,
            self.start_background_refresh
        )

    def refresh_failed(
        self,
        error
    ):

        self.refresh_running = False

        self.status_bar.config(
            text=f"Monitoring error: {error}"
        )

        self.root.after(
            3000,
            self.start_background_refresh
        )

    # ======================================================
    # PROCESS TABLE
    # ======================================================

    def update_process_table(self):

        search_text = (
            self.search_var.get()
            .strip()
            .lower()
        )

        selected_pid = None

        selected = self.process_table.selection()

        if selected:

            values = self.process_table.item(
                selected[0],
                "values"
            )

            if values:

                try:
                    selected_pid = int(
                        values[0]
                    )
                except (
                    ValueError,
                    TypeError
                ):
                    selected_pid = None

        visible_processes = []

        for process in self.process_cache.values():

            if search_text:

                searchable = (
                    f"{process['pid']} "
                    f"{process['name']} "
                    f"{process['category']} "
                    f"{process['status']}"
                ).lower()

                if search_text not in searchable:
                    continue

            visible_processes.append(
                process
            )

        visible_processes.sort(
            key=lambda process:
            self.sort_value(
                process,
                self.sort_column
            ),
            reverse=self.sort_reverse
        )

        visible_pids = {
            process["pid"]
            for process in visible_processes
        }

        # Remove disappeared rows
        for item in self.process_table.get_children():

            values = self.process_table.item(
                item,
                "values"
            )

            if not values:
                continue

            try:
                pid = int(values[0])
            except (
                ValueError,
                TypeError
            ):
                continue

            if pid not in visible_pids:

                self.process_table.delete(
                    item
                )

        # Existing rows
        row_by_pid = {}

        for item in self.process_table.get_children():

            values = self.process_table.item(
                item,
                "values"
            )

            if not values:
                continue

            try:

                pid = int(values[0])

                row_by_pid[pid] = item

            except (
                ValueError,
                TypeError
            ):
                pass

        # Update / insert
        for process in visible_processes:

            pid = process["pid"]

            values = (
                pid,
                process["name"],
                f"{process['cpu']:.1f}",
                f"{process['memory']:.1f}",
                process["status"],
                process.get(
                    "category",
                    "NORMAL"
                )
            )

            tags = ()

            if process.get(
                "safe_candidate",
                False
            ):
                tags = ("candidate",)

            if pid in row_by_pid:

                self.process_table.item(
                    row_by_pid[pid],
                    values=values,
                    tags=tags
                )

            else:

                self.process_table.insert(
                    "",
                    "end",
                    values=values,
                    tags=tags
                )

        # Reorder
        pid_to_item = {}

        for item in self.process_table.get_children():

            values = self.process_table.item(
                item,
                "values"
            )

            if values:

                try:
                    pid_to_item[
                        int(values[0])
                    ] = item
                except (
                    ValueError,
                    TypeError
                ):
                    pass

        for index, process in enumerate(
            visible_processes
        ):

            item = pid_to_item.get(
                process["pid"]
            )

            if item:
                self.process_table.move(
                    item,
                    "",
                    index
                )

        # Restore selection
        if selected_pid is not None:

            item = pid_to_item.get(
                selected_pid
            )

            if item:

                self.process_table.selection_set(
                    item
                )

                self.process_table.focus(
                    item
                )

    # ======================================================
    # SORT
    # ======================================================

    def sort_table(
        self,
        column
    ):

        if self.sort_column == column:

            self.sort_reverse = (
                not self.sort_reverse
            )

        else:

            self.sort_column = column

            self.sort_reverse = (
                column in (
                    "cpu",
                    "memory"
                )
            )

        self.update_process_table()

    def sort_value(
        self,
        process,
        column
    ):

        if column == "pid":
            return process["pid"]

        if column == "process":
            return process["name"].lower()

        if column == "cpu":
            return process["cpu"]

        if column == "memory":
            return process["memory"]

        if column == "status":
            return process["status"]

        if column == "decision":
            return process.get(
                "category",
                ""
            )

        return 0

    # ======================================================
    # SEARCH
    # ======================================================

    def on_search_changed(
        self,
        *args
    ):

        self.update_process_table()

    def clear_search(self):

        self.search_var.set("")

        self.search_entry.focus_set()

    # ======================================================
    # SCROLL / KEYBOARD
    # ======================================================

    def mousewheel_scroll(
        self,
        event
    ):

        if event.delta:

            self.process_table.yview_scroll(
                int(
                    -event.delta / 120
                ),
                "units"
            )

        return "break"

    def keyboard_selection(
        self,
        event
    ):

        self.root.after(
            10,
            self.on_process_selected
        )

    # ======================================================
    # SELECTED PROCESS
    # ======================================================

    def on_process_selected(
        self,
        event=None
    ):

        process = self.get_selected_process()

        if process is None:

            self.selected_label.config(
                text="None"
            )

            return

        self.selected_label.config(
            text=(
                f"{process['name']} "
                f"(PID {process['pid']})"
            )
        )

        self.show_process_details(
            process
        )

    def get_selected_process(self):

        selected = (
            self.process_table.selection()
        )

        if not selected:
            return None

        values = self.process_table.item(
            selected[0],
            "values"
        )

        if not values:
            return None

        try:

            pid = int(values[0])

        except (
            ValueError,
            TypeError
        ):

            return None

        return self.process_cache.get(
            pid
        )

    # ======================================================
    # PERFORMANCE PANEL
    # ======================================================

    def show_process_details(
        self,
        process
    ):

        category = process.get(
            "category",
            "NORMAL"
        )

        candidate = process.get(
            "safe_candidate",
            False
        )

        optimized = (
            process["pid"]
            in self.optimized_processes
        )

        if optimized:

            optimization_status = (
                "OPTIMIZED - PRIORITY LOWERED"
            )

        else:

            optimization_status = (
                "NOT CURRENTLY OPTIMIZED"
            )

        text = (
            f"PROCESS\n"
            f"{process['name']}\n\n"

            f"PID\n"
            f"{process['pid']}\n\n"

            f"CPU USAGE\n"
            f"{process['cpu']:.1f}%\n\n"

            f"MEMORY USAGE\n"
            f"{process['memory']:.2f}%\n\n"

            f"STATUS\n"
            f"{process['status']}\n\n"

            f"ADAPTIVE DECISION\n"
            f"{category}\n\n"

            f"REASON\n"
            f"{process.get('reason', 'N/A')}\n\n"

            f"OPTIMIZATION CANDIDATE\n"
            f"{'YES' if candidate else 'NO'}\n\n"

            f"OPTIMIZATION STATUS\n"
            f"{optimization_status}"
        )

        self.performance_label.config(
            text=text
        )

        self.performance_canvas.yview_moveto(
            0
        )

    # ======================================================
    # SYSTEM STATISTICS
    # ======================================================

    def update_statistics(self):

        processes = list(
            self.process_cache.values()
        )

        candidate_count = sum(
            1
            for process in processes
            if process.get(
                "safe_candidate",
                False
            )
        )

        cpu = psutil.cpu_percent(
            interval=None
        )

        memory = (
            psutil.virtual_memory().percent
        )

        self.process_label.config(
            text=f"Processes: {len(processes)}"
        )

        self.candidate_label.config(
            text=f"Candidates: {candidate_count}"
        )

        self.cpu_label.config(
            text=f"System CPU: {cpu:.1f}%"
        )

        self.ram_label.config(
            text=f"System RAM: {memory:.1f}%"
        )

    # ======================================================
    # GRAPH
    # ======================================================

    def update_system_graph(self):

        try:

            current_time = (
                time.time()
                - self.start_time
            )

            cpu = psutil.cpu_percent(
                interval=None
            )

            memory = (
                psutil.virtual_memory().percent
            )

            self.time_data.append(
                current_time
            )

            self.cpu_data.append(
                cpu
            )

            self.memory_data.append(
                memory
            )

            if len(self.time_data) > 30:

                self.time_data = (
                    self.time_data[-30:]
                )

                self.cpu_data = (
                    self.cpu_data[-30:]
                )

                self.memory_data = (
                    self.memory_data[-30:]
                )

            self.cpu_line.set_data(
                self.time_data,
                self.cpu_data
            )

            self.memory_line.set_data(
                self.time_data,
                self.memory_data
            )

            if self.time_data:

                first = self.time_data[0]

                last = self.time_data[-1]

                if last <= first:

                    last = first + 1

                self.ax.set_xlim(
                    first,
                    last
                )

            self.canvas.draw_idle()

        except Exception as error:

            print(
                "Graph update error:",
                error
            )

        self.root.after(
            3000,
            self.update_system_graph
        )

    # ======================================================
    # MANUAL REFRESH
    # ======================================================

    def manual_refresh(self):

        if self.refresh_running:

            self.status_bar.config(
                text="Refresh already running..."
            )

            return

        self.status_bar.config(
            text="Refreshing process list..."
        )

        self.start_background_refresh()

    # ======================================================
    # OPTIMIZATION
    # ======================================================

    def optimize_selected(self):

        if self.optimization_running:

            messagebox.showinfo(
                "Optimization Busy",
                "An optimization operation is already running."
            )

            return

        process = self.get_selected_process()

        if process is None:

            messagebox.showwarning(
                "No Process Selected",
                "Please select a process first."
            )

            return

        pid = process["pid"]

        name = process["name"]

        category = process.get(
            "category",
            "NORMAL"
        )

        if category not in (
            "PERSISTENT HIGH CPU",
            "PERSISTENT HIGH MEMORY"
        ):

            messagebox.showinfo(
                "Not Ready for Optimization",
                (
                    f"{name} (PID {pid})\n\n"
                    f"Current decision:\n"
                    f"{category}\n\n"
                    "The adaptive analyzer has not "
                    "identified this process as a "
                    "persistent high-resource candidate."
                )
            )

            return

        protected = {
            "system",
            "system idle process",
            "registry",
            "smss.exe",
            "csrss.exe",
            "wininit.exe",
            "services.exe",
            "lsass.exe",
            "svchost.exe"
        }

        if name.lower() in protected:

            messagebox.showwarning(
                "Protected Process",
                (
                    f"{name} is a protected Windows "
                    "process and cannot be optimized."
                )
            )

            return

        if pid in self.optimized_processes:

            messagebox.showinfo(
                "Already Optimized",
                (
                    f"{name} (PID {pid}) is already "
                    "optimized."
                )
            )

            return

        confirmed = messagebox.askyesno(
            "Confirm Optimization",
            (
                f"Optimize {name} (PID {pid})?\n\n"
                "The process priority will be lowered "
                "temporarily.\n\n"
                "CPU usage will be measured before "
                "and after the priority change.\n\n"
                "Note: lowering priority does not "
                "guarantee lower CPU percentage."
            )
        )

        if not confirmed:
            return

        self.optimization_running = True

        self.optimize_button.config(
            state="disabled"
        )

        self.restore_button.config(
            state="disabled"
        )

        self.refresh_button.config(
            state="disabled"
        )

        self.status_bar.config(
            text=(
                f"Measuring and optimizing "
                f"{name} (PID {pid})..."
            )
        )

        thread = threading.Thread(
            target=self.optimization_worker,
            args=(pid, name),
            daemon=True
        )

        thread.start()

    def optimization_worker(
        self,
        pid,
        name
    ):

        try:

            process = psutil.Process(pid)

            before = measure_process(
                pid,
                duration=2
            )

            original_priority = lower_priority(
                pid
            )

            self.optimized_processes[pid] = {
                "name": name,
                "original_priority":
                    original_priority,
                "cpu_before":
                    before["cpu"],
                "memory_before":
                    before["memory"]
            }

            after = measure_process(
                pid,
                duration=2
            )

            current_priority = process.nice()

            cpu_change = (
                after["cpu"]
                - before["cpu"]
            )

            self.root.after(
                0,
                lambda: self.optimization_finished(
                    pid,
                    name,
                    before,
                    after,
                    original_priority,
                    current_priority,
                    cpu_change
                )
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.Error
        ) as error:

            self.root.after(
                0,
                lambda: self.optimization_failed(
                    error
                )
            )

        except Exception as error:

            self.root.after(
                0,
                lambda: self.optimization_failed(
                    error
                )
            )

    def optimization_finished(
        self,
        pid,
        name,
        before,
        after,
        original_priority,
        current_priority,
        cpu_change
    ):

        self.optimization_running = False

        self.optimize_button.config(
            state="normal"
        )

        self.restore_button.config(
            state="normal"
        )

        self.refresh_button.config(
            state="normal"
        )

        if cpu_change < 0:

            cpu_interpretation = (
                "CPU usage decreased during "
                "this measurement."
            )

        elif cpu_change > 0:

            cpu_interpretation = (
                "CPU usage increased during "
                "this measurement. The priority "
                "change was successful, but CPU "
                "reduction was not observed."
            )

        else:

            cpu_interpretation = (
                "CPU usage remained unchanged "
                "during this measurement."
            )

        text = (
            f"OPTIMIZATION RESULT\n\n"

            f"PROCESS\n"
            f"{name}\n\n"

            f"PID\n"
            f"{pid}\n\n"

            f"CPU BEFORE\n"
            f"{before['cpu']:.1f}%\n\n"

            f"CPU AFTER\n"
            f"{after['cpu']:.1f}%\n\n"

            f"CPU CHANGE\n"
            f"{cpu_change:+.1f} percentage points\n\n"

            f"MEMORY BEFORE\n"
            f"{before['memory']:.2f}%\n\n"

            f"MEMORY AFTER\n"
            f"{after['memory']:.2f}%\n\n"

            f"ORIGINAL PRIORITY\n"
            f"{original_priority}\n\n"

            f"CURRENT PRIORITY\n"
            f"{current_priority}\n\n"

            f"PRIORITY ACTION\n"
            f"Successfully lowered\n\n"

            f"CPU INTERPRETATION\n"
            f"{cpu_interpretation}\n\n"

            f"ROLLBACK STATUS\n"
            f"Available - original priority can "
            f"be restored using the Restore button."
        )

        self.performance_label.config(
            text=text
        )

        self.performance_canvas.yview_moveto(
            0
        )

        self.status_bar.config(
            text=(
                f"Priority optimization applied to "
                f"{name} (PID {pid})."
            )
        )

        messagebox.showinfo(
            "Optimization Complete",
            (
                f"{name} (PID {pid})\n\n"
                f"Priority: "
                f"{original_priority} → "
                f"{current_priority}\n\n"
                f"CPU: "
                f"{before['cpu']:.1f}% → "
                f"{after['cpu']:.1f}%\n\n"
                f"{cpu_interpretation}\n\n"
                "The process can now be restored "
                "using the Restore button."
            )
        )

    def optimization_failed(
        self,
        error
    ):

        self.optimization_running = False

        self.optimize_button.config(
            state="normal"
        )

        self.restore_button.config(
            state="normal"
        )

        self.refresh_button.config(
            state="normal"
        )

        self.status_bar.config(
            text="Optimization failed."

        )

        messagebox.showerror(
            "Optimization Failed",
            str(error)
        )

    # ======================================================
    # RESTORE
    # ======================================================

    def restore_selected(self):

        process = self.get_selected_process()

        if process is None:

            messagebox.showwarning(
                "No Process Selected",
                "Please select a process first."
            )

            return

        pid = process["pid"]

        name = process["name"]

        if pid not in self.optimized_processes:

            messagebox.showinfo(
                "Not Optimized",
                (
                    f"{name} (PID {pid}) has not "
                    "been optimized by this application."
                )
            )

            return

        original_priority = (
            self.optimized_processes[pid][
                "original_priority"
            ]
        )

        try:

            restore_priority(
                pid,
                original_priority
            )

            current_priority = (
                psutil.Process(pid).nice()
            )

            restored = (
                current_priority
                == original_priority
            )

            del self.optimized_processes[pid]

            self.performance_label.config(
                text=(
                    f"ROLLBACK RESULT\n\n"

                    f"PROCESS\n"
                    f"{name}\n\n"

                    f"PID\n"
                    f"{pid}\n\n"

                    f"ORIGINAL PRIORITY\n"
                    f"{original_priority}\n\n"

                    f"RESTORED PRIORITY\n"
                    f"{current_priority}\n\n"

                    f"ROLLBACK SUCCESS\n"
                    f"{'YES' if restored else 'NO'}\n\n"

                    f"STATUS\n"
                    f"Original process priority "
                    f"{'successfully restored.' if restored else 'could not be verified.'}"
                )
            )

            self.performance_canvas.yview_moveto(
                0
            )

            self.status_bar.config(
                text=(
                    f"{name} (PID {pid}) "
                    f"rollback completed."
                )
            )

            if restored:

                messagebox.showinfo(
                    "Rollback Complete",
                    (
                        f"{name} (PID {pid})\n\n"
                        f"Original priority: "
                        f"{original_priority}\n"
                        f"Restored priority: "
                        f"{current_priority}\n\n"
                        "Rollback successful."
                    )
                )

            else:

                messagebox.showwarning(
                    "Rollback Verification",
                    (
                        "The restore operation was "
                        "executed, but the final priority "
                        "could not be verified."
                    )
                )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.Error
        ) as error:

            messagebox.showerror(
                "Restore Failed",
                str(error)
            )

    # ======================================================
    # CLOSE
    # ======================================================

    def close_application(self):

        if self.optimization_running:

            messagebox.showwarning(
                "Operation Running",
                (
                    "An optimization operation is "
                    "still running.\n\n"
                    "Please wait for it to finish."
                )
            )

            return

        self.root.destroy()


# ==========================================================
# START APPLICATION
# ==========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ResourceOptimizerApp(
        root
    )

    root.mainloop()