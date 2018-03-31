from tkinter import *
from tkinter import ttk, filedialog, messagebox
import os
import numpy as np
from threading import Thread
from multiprocessing import Process, Manager, Value
import webbrowser
import time
import math
from win32api import *
from win32gui import *
import win32con


class MainWindow:
    def __init__(self):

        self.initialization()
        self.mk_window()
        self.root.mainloop()
        os._exit(1)

    def initialization(self):

        # once initialize, all former data will be cleaned
        try:
            self.right_button_frame.destroy()
            self.data_frame.destroy()
            self.finish.destroy()
        except AttributeError:
            pass

        # initialize all class variable
        try:  # try to load the last run path
            with open(os.path.join(os.environ["temp"], "lastlocation.dna"), "r") as lastloc:
                self.last_run_path = lastloc.readline()
        except FileNotFoundError:
            self.last_run_path = ""

        # path and file names for the std and seq files
        self.std_dir_path = ""
        self.std_file_name = ""
        self.seq_files_path_list = []

        # prgress bars
        self.progress_bars_list = []
        self.progress_list = []
        self.keep_reading = False

        self.ignore_seq_header = 1

    def mk_window(self):

        # make the main window and several buttons
        self.root = Tk()
        self.root.title("DNA align")
        try:
            self.root.iconbitmap("dna\\fav.ico")
        except TclError:
            self.root.iconbitmap("fav.ico")
        except:
            pass
        self.root.resizable(0, 0)

        self.spacer_t = Frame(self.root, width=1000, height=1)
        self.spacer_t.pack(side=TOP, fill=BOTH)

        self.spacer_b = Frame(self.root, width=1000, height=25)
        self.spacer_b.pack(side=BOTTOM, fill=BOTH)

        self.main_frame = Frame(self.root, width=1000, height=600)
        self.main_frame.pack(side=TOP, fill=BOTH)

        self.top_button_frame = Frame(self.main_frame)
        self.top_button_frame.pack(side=TOP, fill=X)

        self.open_files = Button(self.top_button_frame, text='Open\nFiles', command=self.open_files_func)
        self.open_files.pack(side=LEFT, padx=12, pady=12)

    def open_files_func(self):

        self.initialization()

        # define options for opening std file
        option_std = {'filetypes': [('std file', '.txt')],
                      'initialdir': self.last_run_path,
                      'parent': self.root,
                      'title': 'Open the standard sequence txt file.',
                      'multiple': False}

        self.std_file_path = filedialog.askopenfilename(**option_std)

        if self.std_file_path:

            # read the path and file name for the std file
            self.std_dir_path, self.std_file_name = os.path.split(self.std_file_path)

            # write the std path to the last used location
            self.last_run_path = self.std_dir_path
            try:
                with open(os.path.join(os.environ["temp"], "lastlocation.dna"), "w") as lastloc:
                    lastloc.write(self.last_run_path)
            except:
                pass

            # define options for opening seq files
            option_seq = {'filetypes': [('seq file', '.seq')],
                          'initialdir': self.last_run_path,
                          'parent': self.root,
                          'title': 'Open the sequence seq files for {}'.format(os.path.splitext(self.std_file_name)[0]),
                          'multiple': True}

            # read the all file path into a list
            self.seq_files_path_list = filedialog.askopenfilename(**option_seq)

            # seq file count should be less than 10 for a performance reason
            if len(self.seq_files_path_list) > 10:
                messagebox.showerror("Open file error", "Can't deal with more than 10 seq files!")
            elif self.seq_files_path_list:
                # if the seq and std files are correctly loaded
                # print("before")
                self.data_frame = Frame(self.main_frame)
                self.data_frame.pack(side=TOP, fill=BOTH)
                self.add_std_entry()
                self.add_seq_entry()
                self.add_go()

            else:
                self.initialization()

                # print(self.std_file_name)
                # print(self.seq_files_path_list)
                # print(self.path)
        else:
            self.initialization()

    def add_std_entry(self):

        self.std_frame = Frame(self.data_frame)
        self.std_frame.pack(side=TOP, fill=BOTH)

        left_spacer = Frame(self.std_frame, width=50)
        left_spacer.pack(side=LEFT)

        right_spacer = Frame(self.std_frame, width=50)
        right_spacer.pack(side=RIGHT)

        sub1 = Frame(self.std_frame)
        sub2 = Frame(self.std_frame)

        sub1.pack(side=TOP, fill=X)
        sub2.pack(side=TOP, fill=X)

        self.std_label = Label(sub1, text="Standard DNA sequence:", fg="#555555")
        self.std_label.pack(side=LEFT)

        self.std_path = Label(sub2, text=self.std_file_name, font=("arial", "14"))
        self.std_path.pack(side=LEFT)

    def add_seq_entry(self):

        self.seq_frame = Frame(self.data_frame)
        self.seq_frame.pack(side=TOP, fill=BOTH)

        left_spacer = Frame(self.seq_frame, width=50)
        right_spacer = Frame(self.seq_frame, width=50)
        left_spacer.pack(side=LEFT)
        right_spacer.pack(side=RIGHT)

        sub1 = Frame(self.seq_frame, height=10)
        sub2 = Frame(self.seq_frame)
        sub1.pack(side=TOP, fill=X)
        sub2.pack(side=TOP, fill=X)

        seq_label = Label(sub2, text="DNA sequences to be aligned:", fg="#555555")
        seq_label.pack(side=LEFT)

        for i in range(len(self.seq_files_path_list)):
            sub3 = Frame(self.seq_frame)
            sub4 = Frame(self.seq_frame)
            sub5 = Frame(self.seq_frame, height=5)
            dir, name = os.path.split(self.seq_files_path_list[i])
            seq_dir = Label(sub3, text=dir+"\\", fg="#222222", font=("arial", "9"))
            seq_name = Label(sub3, text=name, font=("arial", "13"))
            seq_dir.pack(side=LEFT)
            seq_name.pack(side=LEFT)

            progress_bar = ttk.Progressbar(sub4, orient="horizontal", length=1000, mode="determinate")
            progress_bar["value"] = 0
            progress_bar["maximum"] = 100
            self.progress_bars_list.append(progress_bar)
            progress_bar.pack(side=TOP)

            sub3.pack(side=TOP, fill=X)
            sub4.pack(side=TOP, fill=X)
            sub5.pack(side=TOP, fill=X)

    def add_go(self):

        self.right_button_frame = Frame(self.top_button_frame)
        self.right_button_frame.pack(side=RIGHT)

        self.go_button = Button(self.right_button_frame, text="Go!", font=("arial", "14"), command=self.start_calc)
        self.go_button.pack(side=RIGHT, padx=12, pady=12)

        self.name_entry_box = Entry(self.right_button_frame, font=("arial", "12"))
        self.name_entry_box.insert(0, os.path.splitext(self.std_file_name)[0])
        self.name_entry_box.pack(side=RIGHT)
        Label(self.right_button_frame, text="Project name:", font=("arial", "12"), fg="#888888").pack(side=RIGHT)

        Label(self.right_button_frame, text=" ", font=("arial", "12"), fg="#888888").pack(side=RIGHT)
        self.ignore_header = Entry(self.right_button_frame, font=("arial", "12"), width=2)
        self.ignore_header.insert(0, self.ignore_seq_header)
        self.ignore_header.pack(side=RIGHT)
        Label(self.right_button_frame, text="Remove *.seq file header line:",
              font=("arial", "12"), fg="#888888").pack(side=RIGHT)

    def start_calc(self):
        thread = Thread(target=self._calc)
        thread.start()

    def _calc(self):

        self.project_name = self.name_entry_box.get()
        try:
            self.ignore_seq_header = int(self.ignore_header.get())
        except ValueError or TypeError:
            messagebox.showerror("Error!!!", "Please enter a valid number for *.seq file header removal!")
            return

        start = time.time()
        self.progress = []
        # print("reset progress!!!")
        for _ in self.seq_files_path_list:
            self.progress.append(0)
            # print(i)

        # print(self.project_name)
        self.right_button_frame.destroy()

        loading = Label(self.top_button_frame, text="Loading files...     ", font=("arial", "14"))
        loading.pack(side=RIGHT)
        self.clu = DNA_Cluster.create(self.std_file_path, *self.seq_files_path_list,
                                      ignore_child_header=self.ignore_seq_header)
        self.keep_reading = True
        self.read_progress()
        # print(clu)
        loading.destroy()
        aligning = Label(self.top_button_frame, text="Aligning...     ", font=("arial", "14"))
        aligning.pack(side=RIGHT)
        self.clu.align_each()
        self.clu.align_all()
        # clu.print_all()
        self.clu.generate_report()
        aligning.destroy()

        self.time = math.ceil(time.time() - start)
        print("Done in {} second.".format(str(self.time)))
        self.finished()
        w = WindowsBalloonTip("Mission Accomplished!",
                              "Alignment finished in " + str(self.time) + " second.")

        time.sleep(2)
        self.keep_reading = False

    def finished(self):
        self.finish = Label(self.top_button_frame, text="Last alignment finished in {} seconds.   "
                                                        "\nUse \"Open Files\" to start next.  ".format(str(self.time)),
                            font=("arial", "12"))
        self.finish.pack(side=RIGHT)



    def _read_progress(self):

        for i in range(len(self.progress_bars_list)):
            self.progress_bars_list[i]["value"] = self.clu.progress_list[i]
            # print("value", self.progress_bars_list[i]["value"])
            # print("progress", self.progress[i])
        time.sleep(0.1)

        if self.keep_reading:
            self._read_progress()


    def read_progress(self):
        read = Thread(target=self._read_progress)
        read.start()


class DNA:
    def __init__(self):
        self.path = ""
        self.name = ""
        self.dna_string = ""

    def __getitem__(self, key):
        return self.dna_string[key]

    def __len__(self):
        return len(self.dna_string)

    def __str__(self):
        return self.name + ":\n" + self.dna_string + "\n"

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    @classmethod
    def from_string(cls, name, string):
        dna = cls()
        dna.name = name
        dna.dna_string = string
        return dna

    @classmethod
    def from_file(cls, path, ignore_header=0):
        # print(time.time())
        dna = cls()
        dna.path = path
        print(path)
        dna.name = os.path.splitext(os.path.basename(dna.path))[0]
        # print(time.time())
        with open(dna.path, "r") as dna_file:
            file_lines = dna_file.readlines()
            for line in file_lines[ignore_header:]:
                dna.dna_string += line
            dna.dna_string = dna.dna_string.replace(" ", "").replace("\r", "").replace("\n", "").upper()
        # print(time.time())
        # print("done!!!")
        return dna

    def reverse_complement(self):
        s = self.dna_string.upper()
        self.dna_string = s.replace("A", "t").replace("T", "a").replace("C", "g").replace("G", "c").upper()[::-1]


class Seq(DNA):
    pass


class Std(DNA):
    pass


class DNA_Pair:
    def __init__(self):
        # static data:
        self.parent_path = ""
        self.child_path = ""

        self.parent_name = ""
        self.child_name = ""

        self.parent_dna_string = ""
        self.child_dna_string = ""

        self.reverse_complement_status = False

        # alignment data:
        self.alignment_tried = 0
        self.alignment_score = 0
        self.alignment_failed = None
        self.alignment_threshold = 0.6  # high = strict fit, low = loose fit
        self.aligning_progress = Value("i", 0)

        # alignment result:
        self.result = Manager().dict()
        self.parent_dna_string_aligned = ""
        self.child_dna_string_aligned = ""
        self.aligned = False
        self.align_result_marker = []

    def __str__(self):
        print_string = self.parent_name + ":\n" \
                       + self.parent_dna_string + "\n" \
                       + self.child_name + ":\n" \
                       + self.child_dna_string + "\n\n"
        return print_string

    def print_result(self):
        print(self.parent_name + ":\n"
              + self.parent_dna_string_aligned + "\n"
              + self.child_name + ":\n"
              + self.child_dna_string_aligned + "\n"
              + "".join(self.align_result_marker))

    def get_result(self):
        return [self.parent_name,
                self.parent_dna_string_aligned,
                self.child_name,
                self.child_dna_string_aligned,
                self.align_result_marker]

    @classmethod
    def create(cls, parent, child):
        # print(time.time(), "sssss")
        pair = cls()
        # print(time.time(), "obj created")
        pair.parent_path = parent.path
        pair.child_path = child.path
        # print(time.time(), "path")
        pair.parent_name = parent.name
        pair.child_name = child.name
        # print(time.time(), "name")
        pair.parent_dna_string = parent.dna_string
        pair.child_dna_string = child.dna_string
        # print(time.time(), "string")
        return pair

    @classmethod
    def create_empty(cls):
        pair = cls()
        return pair

    def load_data(self, parent, child):
        self.parent_path = parent.path
        self.child_path = child.path
        # print(time.time(), "path")
        self.parent_name = parent.name
        self.child_name = child.name
        # print(time.time(), "name")
        self.parent_dna_string = parent.dna_string
        self.child_dna_string = child.dna_string


    def reverse_complement(self):
        self.child_dna_string = self.child_dna_string.upper().replace("A", "t").replace("T", "a")
        self.child_dna_string = self.child_dna_string.replace("C", "g").replace("G", "c").upper()[::-1]
        self.reverse_complement_status = not self.reverse_complement_status
        if self.reverse_complement_status:
            self.child_name += "_rc"
            self.result["self.child_name"] = self.child_name
            print(self.result["self.child_name"])
        elif self.child_name[-3:] == "_rc":
            self.child_name = self.child_name[:-3]
            self.result["self.child_name"] = self.child_name
        self.align_result_marker = []

    def align(self):
        # self.monitor_progress()
        self.result["self.child_name"] = self.child_name
        parent = self.parent_dna_string
        child = self.child_dna_string
        self.aligning_progress.value = 0

        match_award = 5
        mismatch_penalty = -1
        gap_penalty_v = -2
        gap_penalty_h = -6

        len_parent = len(parent) + 1
        len_child = len(child) + 1

        score_matrix = np.zeros([len_parent, len_child], dtype=int)
        direction_matrix = np.zeros([len_parent, len_child], dtype=int)

        for i in range(1, len_parent):
            self.aligning_progress.value = int(i / len_parent * 95)
            # print(self.aligning_progress.value)
            for j in range(1, len_child):
                # i for row/vertical_move, j for col/horizontal_move
                if parent[i - 1] == child[j - 1]:
                    match_or_not = match_award
                else:
                    match_or_not = mismatch_penalty

                diagonal_direction = score_matrix[i - 1][j - 1] + match_or_not
                vertical_direction = score_matrix[i - 1][j] + gap_penalty_v
                horizontal_direction = score_matrix[i][j - 1] + gap_penalty_h

                max_of_the_three = max(diagonal_direction, vertical_direction, horizontal_direction)
                score_matrix[i][j] = max_of_the_three

                if max_of_the_three == diagonal_direction:
                    direction_matrix[i][j] = 1
                elif max_of_the_three == vertical_direction:
                    direction_matrix[i][j] = 2
                elif max_of_the_three == horizontal_direction:
                    direction_matrix[i][j] = 4

        # print(score_matrix)
        # print(direction_matrix)
        # assert False

        # with open("1_score.csv", "wb") as f1:
        #     np.savetxt(f1, score_matrix, delimiter=",", fmt="%i")
        # with open("2_direction.csv", "wb") as f2:
        #     np.savetxt(f2, direction_matrix, delimiter=",", fmt="%i")

        max_position = [np.argmax(score_matrix) // len_child, np.argmax(score_matrix) % len_child]
        position_row, position_col = max_position
        # print(score_matrix)
        # print(np.argmax(score_matrix))
        # print(max_position)
        # assert False
        aligned = ["", ""]
        aligned[0] += parent[position_row:][::-1]
        aligned[1] += child[position_col:][::-1]
        for _ in range(position_row + len_child - 1 - position_col, len_parent - 1):
            aligned[1] = " " + aligned[1]

        while position_col > 0 and position_row > 0:

            if direction_matrix[position_row][position_col] == 1:
                position_row -= 1
                position_col -= 1
                aligned[0] += parent[position_row]
                aligned[1] += child[position_col]

            elif direction_matrix[position_row][position_col] == 2:
                position_row -= 1
                aligned[0] += parent[position_row]
                aligned[1] += "-"

            elif direction_matrix[position_row][position_col] == 4:
                position_col -= 1
                aligned[0] += "-"
                aligned[1] += child[position_col]
                # print(position_row, position_col)
                # print(aligned[0], aligned[1], sep="\n")

        # print(aligned[0],aligned[1],sep="\n")
        # assert False
        self.aligning_progress.value = 98
        row_left = parent[:position_row]
        col_left = child[:position_col]

        aligned[0] += row_left[::-1]
        aligned[1] += col_left[::-1]

        if len(row_left) > len(col_left):
            i = 1
        else:
            i = 0

        for _ in range(abs(len(row_left) - len(col_left))):
            aligned[i] += " "

        aligned[0] = aligned[0][::-1]
        aligned[1] = aligned[1][::-1]

        # print(aligned[0], aligned[1], sep="\n")
        # time.sleep(0.2)
        # assert False

        alignment_score = 0
        for i in range(len(aligned[0])):
            if aligned[0][i].upper() == "-":
                alignment_score += -12
            elif aligned[1][i].upper() == "-":
                alignment_score += -4
            elif aligned[0][i].upper() == "N" or aligned[1][i].upper() == "N" or aligned[1][i].upper() == " ":
                alignment_score += 0
            elif aligned[0][i] == aligned[1][i]:
                alignment_score += 2
            else:
                alignment_score += -1

        self.alignment_tried += 1

        if alignment_score < int(len(child) * self.alignment_threshold):  # if poor alignment:

            if self.alignment_tried < 2:  # not tried after reverse complement:
                self.alignment_score = alignment_score
                self.parent_dna_string_aligned = aligned[0]
                self.child_dna_string_aligned = aligned[1]
                # do the rc and try it again:
                self.reverse_complement()
                self.align()
            elif alignment_score > self.alignment_score:  # if second time is better:
                self.alignment_score = alignment_score
                self.parent_dna_string_aligned = aligned[0]
                self.child_dna_string_aligned = aligned[1]
            else:  # if already tried, but the first time is better:
                print(self.child_name, "Waterman: poor alignment or can not be aligned!!")
                self.alignment_failed = True
                self.child_name = self.child_name[:-3]
                self.result["self.child_name"] = self.child_name

        else:  # if alignment is good:
            self.alignment_score = alignment_score
            self.parent_dna_string_aligned = aligned[0]
            self.child_dna_string_aligned = aligned[1]

        self.aligning_progress.value = 100
        self.result["self.parent_dna_string_aligned"] = self.parent_dna_string_aligned
        self.result["self.child_dna_string_aligned"] = self.child_dna_string_aligned

    def get_progress(self, timer=0.5):
        while self.aligning_progress.value < 99:
            print("get progress:", self.aligning_progress.value)
            time.sleep(timer)
        return self.aligning_progress.value

    def return_progress(self):
        return self.aligning_progress.value

    def monitor_progress(self):
        monitor = Thread(target=self.get_progress)
        monitor.start()

    # =================== data finalize: ===================
    def update_result(self):
        self.parent_dna_string_aligned = self.result["self.parent_dna_string_aligned"]
        self.child_dna_string_aligned = self.result["self.child_dna_string_aligned"]
        self.child_name = self.result["self.child_name"]
        self.align_result_marker = []
        for _ in range(len(self.parent_dna_string_aligned)):
            self.align_result_marker.append("")

        for i in range(len(self.parent_dna_string_aligned)):
            if self.parent_dna_string_aligned[i] == self.child_dna_string_aligned[i] \
                    and self.parent_dna_string_aligned[i] not in [" ", "-"] \
                    and self.child_dna_string_aligned[i] not in [" ", "-"]:
                self.align_result_marker[i] = "*"
            else:
                self.align_result_marker[i] = " "


class DNA_Cluster:
    def __init__(self):
        self.cluster_name = ""
        self.dna_pairs_list = []

        self.dna_parent_string = ""
        self.dna_parent_marker = []
        self.dna_parent_string_list = []
        self.dna_child_string_list = []
        self.dna_child_marker_list = []
        self.dna_child_name_list = []
        self.dir = ""
        self.progress_list = []

    def __str__(self):
        return str(len(self.dna_pairs_list)) + " pairs in the cluster:\n"

    @classmethod
    def create(cls, std_path, *child_path_list, ignore_child_header=1):
        cluster = cls()
        cluster.dna_pairs_list = []
        parent = Std.from_file(std_path, 0)
        cluster.dir = os.path.dirname(std_path)
        cluster.cluster_name = parent.name
        cluster.dna_parent_string = parent.dna_string
        cluster.progress_list = [0 for _ in range(len(child_path_list))]

        for path in child_path_list:
            # print(time.time(), "start")
            child = Seq.from_file(path, ignore_child_header)
            # print(time.time(), "seq created")
            pair = DNA_Pair.create(parent, child)
            # print(time.time(), "pair created")
            cluster.dna_pairs_list.append(pair)
            # print(time.time(), "fin")

        return cluster

    @classmethod
    def create_empty(cls, std_path, *child_path_list, ignore_child_header=1):
        cluster = cls()
        cluster.dna_pairs_list = []
        for _ in child_path_list:
            pair = DNA_Pair.create_empty()
            cluster.dna_pairs_list.append(pair)
        return cluster

    def load_data(self, std_path, *child_path_list, ignore_child_header=1):
        parent = Std.from_file(std_path, 0)
        self.dir = os.path.dirname(std_path)
        self.cluster_name = parent.name
        self.dna_parent_string = parent.dna_string
        self.progress_list = [0 for _ in range(len(child_path_list))]

        for i in range(len(self.dna_pairs_list)):
            path = child_path_list[i]
            pair = self.dna_pairs_list[i]
            # print(time.time(), "start")
            child = Seq.from_file(path, ignore_child_header)
            # print(time.time(), "seq created")
            pair.load_data(parent, child)
            # print(time.time(), "pair created")
            # print(time.time(), "fin")


    def align_each(self):

        thread = Thread(target=self.update_progress)
        thread.start()

        process = []
        for pair in self.dna_pairs_list:
            process.append(Process(target=pair.align))
            # print(pair)
            # pair.align()
        for x in process:
            x.start()
        for x in process:
            x.join()
        for pair in self.dna_pairs_list:
            pair.update_result()

    def update_progress(self):
        loop = True
        while loop:
            time.sleep(0.1)
            for i in range(len(self.dna_pairs_list)):
                self.progress_list[i] = self.dna_pairs_list[i].return_progress()
                # print(self.progress_list)
            if sum(self.progress_list) >= len(self.dna_pairs_list) * 100:
                loop = False

    def align_all(self):
        pair_count = len(self.dna_pairs_list)
        for pair in self.dna_pairs_list:
            self.dna_child_string_list.append(pair.child_dna_string_aligned)
            self.dna_child_marker_list.append(pair.align_result_marker)
            self.dna_child_name_list.append(pair.child_name)
            self.dna_parent_string_list.append(pair.parent_dna_string_aligned)

        # in case that the child is longer than parent on the left:
        for i in range(int(len(self.dna_parent_string_list[0]) / 2)):
            for j in range(pair_count):
                if self.dna_parent_string_list[j][i] == " ":
                    for k in range(pair_count):
                        if k != j and self.dna_parent_string_list[k][i] != " ":
                            self.dna_parent_string_list[k] = " " + self.dna_parent_string_list[k]
                            self.dna_child_string_list[k] = " " + self.dna_child_string_list[k]
                            self.dna_child_marker_list[k] = [" "] + self.dna_child_marker_list[k]

        j = 0
        while j < len(self.dna_parent_string_list[0]):
            try:
                for i in range(pair_count):
                    if self.dna_parent_string_list[i][j] == "-":
                        for k in range(pair_count):
                            if self.dna_parent_string_list[k][j] == "-":
                                pass
                            elif self.dna_child_string_list[k][j] == " ":
                                self.dna_parent_string_list[k] = self.dna_parent_string_list[k][:j] + "-" \
                                                                 + self.dna_parent_string_list[k][j:]
                                self.dna_child_string_list[k] = self.dna_child_string_list[k][:j] + " " \
                                                                + self.dna_child_string_list[k][j:]
                                self.dna_child_marker_list[k] = self.dna_child_marker_list[k][:j] + [" "] \
                                                                + self.dna_child_marker_list[k][j:]
                            else:
                                self.dna_parent_string_list[k] = self.dna_parent_string_list[k][:j] + "-" \
                                                                 + self.dna_parent_string_list[k][j:]
                                self.dna_child_string_list[k] = self.dna_child_string_list[k][:j] + "-" \
                                                                + self.dna_child_string_list[k][j:]
                                self.dna_child_marker_list[k] = self.dna_child_marker_list[k][:j] + [" "] \
                                                                + self.dna_child_marker_list[k][j:]
            except:
                pass
            j += 1

        self.dna_parent_marker = []
        self.dna_parent_string = self.dna_parent_string_list[0]
        j = 0
        while j < len(self.dna_parent_string):
            try:
                for i in range(pair_count):
                    if self.dna_child_marker_list[i][j] == "*":
                        self.dna_parent_marker.append(str(i))
                        break
                else:
                    self.dna_parent_marker.append(" ")
                j += 1
            except IndexError:
                break

    def print_all(self):
        print("".join(self.dna_parent_marker))
        print(self.dna_parent_string)
        for i in range(len(self.dna_pairs_list)):
            # print(self.dna_parent_string_list[i])
            print(self.dna_child_name_list[i])
            print(self.dna_child_string_list[i])
            print("".join(self.dna_child_marker_list[i]))

    def print_each(self):
        for pair in self.dna_pairs_list:
            pair.print_result()

    def generate_report(self):
        file_name = self.cluster_name

        def color_a_string(string_a, marker, single_color=True, color_index=-1, red_mismatch=False):
            """
            color_type = 1: by default, only color match with green
            color_type = 0: used for lower left bock, color based on the child ones
            """
            color_dict = {-1: "green_bg",
                          0: "color_0_bg",
                          1: "color_1_bg",
                          2: "color_2_bg",
                          3: "color_3_bg",
                          4: "color_4_bg",
                          5: "color_5_bg",
                          6: "color_6_bg",
                          7: "color_7_bg",
                          8: "color_8_bg",
                          9: "color_9_bg",
                          10: "color_10_bg",
                          11: "color_11_bg",
                          12: "color_12_bg",
                          13: "color_13_bg",
                          14: "color_14_bg",
                          15: "color_15_bg"}

            ans = ""
            i = 0
            j = 0
            while i - 1 < len(marker) and j - 1 < len(marker):
                if j < len(marker) and marker[i] == marker[j]:
                    pass
                else:
                    string = string_a[i:j]
                    i = j
                    if marker[i - 1] == " ":
                        if not red_mismatch == 0 and string_a[i - 1] != "-" and string_a[i - 1] != " ":
                            ans += "<span class=\"red_bg\">" + string + "</span>"
                        else:
                            ans += "<span class=\"white_bg\">" + string + "</span>"
                    else:
                        if single_color:
                            color = color_index
                        else:
                            color = int(marker[i - 1])
                        ans += "<span class=\"" + color_dict[color] + "\">" + string + "</span>"
                j += 1

            # print(ans)
            return ans

        html_head = """<html>\n    <head>\n        <title>""" + self.cluster_name + """</title>

        <!-- CSS -->
        <style>
            body {
                font-family: "Courier New", Lucida Console;
                font-size: 1em;
            }

            #top_alignment {
                border: 1px dashed green;
                margin-right: 75px;
                margin-left: 75px;
                margin-top: 10px;
                margin-bottom: 35px;
                width: 90%;
                float: left;
            }

            #seq_names {
                float: left;
                margin-right: 5px;
                text-align: right;
                white-space: nowrap;
            }

            #seqs {
                border: none;
                overflow: scroll;
                white-space: nowrap;
            }

            #bottom_alignment {
                margin-right: 75px;
                margin-left: 75px;
                margin-top: 10px;
                margin-bottom: 335px;
                width: 90%;
                float: left;
            }

            #std_seq {
                border: 1px dashed green;
                float: left;
                margin-right: 5px;
                width: 42%;
                word-wrap: break-word; 
                text-align: right
                overflow: auto;
            }

            #children_seq {
                border: 1px dashed green;
                width: 55%;
                word-wrap: break-word; 
                overflow: auto;
                float: right;
            }

            .blue {
                color: #00f;
            }

            .green_bg {
                color: #000000;
                background-color: rgb(200,255,200);
            }

            .white_bg {
                color: #000000;
                background-color: rgb(255,255,255);
            }

            .red_bg {
                color: #000000;
                background-color: rgb(255,200,200);
            }

            .color_0_bg {
                color: #000000;
                background-color: #99FF99;
            }

            .color_1_bg {
                color: #000000;
                background-color: #99CCFF;
            }

            .color_2_bg {
                color: #000000;
                background-color: #9999FF;
            }

            .color_3_bg {
                color: #000000;
                background-color: #FFCC99;
            }

            .color_4_bg {
                color: #000000;
                background-color: #FF7F90;
            }

            .color_5_bg {
                color: #000000;
                background-color: #FF00FF;
            }

            .color_6_bg {
                color: #000000;
                background-color: #FFFF00;
            }

            .color_7_bg {
                color: #000000;
                background-color: #FF6347
            }

            .color_8_bg {
                color: #000000;
                background-color: #FF1493
            }

            .color_9_bg {
                color: #000000;
                background-color: #ADFF2F; 
            }

            .color_10_bg {
                color: #000000;
                background-color: #FAFAD2; 
            }

            .color_11_bg {
                color: #000000;
                background-color: #20B2AA; 
            }

            .color_12_bg {
                color: #000000;
                background-color: #7CFC00;
            }

            .color_13_bg {
                color: #000000;
                background-color: #DA70D6;
            }

            .color_14_bg {
                color: #000000;
                background-color: #EE82EE;
            }

            .color_15_bg {
                color: #000000;
                background-color: #BAA1E2
            }



        </style>
    </head>
    <body>
    <!-- HTML -->
        <h2 style="margin-left: 75px;">
"""
        # page_title
        html_body_1 = """</h2>
        <span style="margin-left: 75px;">alignment result:</span>

        <div id="top_alignment">
            <div id="seq_names">"""
        # seq names<br>
        html_body_2 = """</div>\n            <div id="seqs">"""

        std_single_color = color_a_string(self.dna_parent_string.replace(" ", "Z"), self.dna_parent_marker,
                                          red_mismatch=True).replace("Z", "&nbsp;")
        child_list = []  # child_list = [[name1, string1],[name2,string2]]
        for i in range(len(self.dna_child_string_list)):
            child_string = color_a_string(self.dna_child_string_list[i].replace(" ", "Z"),
                                          self.dna_child_marker_list[i], color_index=i).replace("Z", "&nbsp;")
            child_list.append([self.dna_child_name_list[i], child_string])

        html_body_3 = """</div>
        </div>


        <div id="bottom_alignment">
            <div id="std_seq">"""

        std_multi_color = color_a_string(self.dna_parent_string.replace(" ", "Z"), self.dna_parent_marker,
                                         single_color=False).replace("Z", "")
        html_body_4 = """</div>\n            <div id="children_seq">"""
        # child seq name<br>child seq
        html_body_5_end = """</div>\n        </div>\n    </body>\n</html>"""

        with open(os.path.join(self.dir, file_name + "_result.html"), "w") as html_result:
            html_result.write(html_head)
            html_result.write(file_name)

            html_result.write(html_body_1)

            html_result.write(self.cluster_name + ">" + "<br>")
            for child in child_list:
                html_result.write(child[0] + ">" + "<br>")

            html_result.write(html_body_2)

            html_result.write(std_single_color + "<br>")
            for child in child_list:
                html_result.write(child[1] + "<br>")
            html_result.write(html_body_3)

            html_result.write(std_multi_color)

            html_result.write(html_body_4)
            for child in child_list:
                html_result.write(child[0] + "<br>")
                html_result.write(child[1].replace("&nbsp;", "") + "<br>" + "<br>")

            html_result.write(html_body_5_end)
            webbrowser.open(os.path.join(self.dir, file_name + "_result.html"))


class WindowsBalloonTip:
    def __init__(self, title, msg):
        message_map = {
            win32con.WM_DESTROY: self.OnDestroy,
        }
        # Register the Window class.
        wc = WNDCLASS()
        hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar"
        wc.lpfnWndProc = message_map  # could also specify a wndproc.
        classAtom = RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow(classAtom, "Taskbar", style, 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0,
                                 0, hinst, None)
        UpdateWindow(self.hwnd)
        iconPathName = os.path.abspath(os.path.join(sys.path[0], "balloontip.ico"))
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
            hicon = LoadImage(hinst, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
            hicon = LoadIcon(0, win32con.IDI_APPLICATION)
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, hicon, "tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY,
                         (self.hwnd, 0, NIF_INFO, win32con.WM_USER + 20, hicon, "Balloon  tooltip", msg, 200, title))
        # self.show_balloon(title, msg)
        time.sleep(10)
        DestroyWindow(self.hwnd)
        UnregisterClass(classAtom, hinst)

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)  # Terminate the app.


if __name__ == '__main__':
    a = MainWindow()


# a = Std.from_file("D:\\OneDrive\\Shared\\Lab\\VBS\\ads_std.txt")
# b = Seq.from_file("D:\\OneDrive\\Shared\\Lab\\VBS\\ADS3_ADS-REV_W33398_1.seq", 1)
#
# pair = DNA_Pair.create(a, b)
#
# pair.monitor_progress()
# pair.align()
# pair.update_result()
#
#
# pair.print_result()
#
#
#
#
#
#




























