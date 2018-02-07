import tkinter as tk
import Pmw
import warnings
from collections import OrderedDict


class DualBox(tk.Frame):
    def __init__(self, parent, list_items):
        """Two side-by-side listboxes are created with which items can be moved from one to the other"""
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # The input list is checked for duplicate values.
        if len(list_items) > len(set(list_items)):
            warnings.warn("DualBox: duplicates are present in list. Removing duplicates...")
            list_items = list(OrderedDict.fromkeys(list_items))  # remove duplicates

        # Left-hand side Listbox
        self.listBox = Pmw.ScrolledListBox(self, items=list_items,
                                           listbox_height=5,
                                           vscrollmode="static",
                                           listbox_selectmode=tk.EXTENDED,
                                           dblclickcommand=self.add_item)
        self.listBox.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

        # Buttons
        self.buttonframe = tk.Frame(self)
        self.buttonframe.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
        # Copy Button
        self.copyButton = tk.Button(self.buttonframe, text=">>>", command=self.add_item)
        self.copyButton.grid(row=0, column=0, sticky='we')
        # Remove Button
        self.removeButton = tk.Button(self.buttonframe, text="<<<", command=self.remove_item)
        self.removeButton.grid(row=1, column=0, sticky='we')
        # Clear Button
        self.clearButton = tk.Button(self.buttonframe, text="clear", command=self.clear_all_items)
        self.clearButton.grid(row=2, column=0, sticky='we')

        # Right-hand side Listbox
        self.chosen = Pmw.ScrolledListBox(self, items='',
                                          listbox_height=5,
                                          vscrollmode="static",
                                          listbox_selectmode=tk.EXTENDED,
                                           dblclickcommand=self.remove_item)
        self.chosen.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

    def get_selection(self):
        return list(self.chosen.get(0, tk.END))

    def add_item(self):
        original_chosen_items = self.chosen.get(0, tk.END)
        selected = self.listBox.getcurselection()
        selected_minus_duplicates = []
        if selected:
            for item in selected:
                if item not in original_chosen_items:
                    selected_minus_duplicates.append(item)
            self.chosen.get(0, tk.END)
            self.chosen.setlist(original_chosen_items + tuple(selected_minus_duplicates))

    def remove_item(self):
        original_chosen_items = self.chosen.get(0, tk.END)
        selected = self.chosen.getcurselection()
        original_minus_selected = []
        if selected:
            for item in original_chosen_items:
                if item not in selected:
                    original_minus_selected.append(item)
            self.chosen.setlist(original_minus_selected)

    def clear_all_items(self):
        self.chosen.clear()
