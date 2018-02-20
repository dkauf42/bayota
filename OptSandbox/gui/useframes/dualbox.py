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
                                           dblclickcommand=self.add_item_to_chosen)
        self.listBox.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

        # Buttons
        self.buttonframe = tk.Frame(self)
        self.buttonframe.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
        # Copy Button
        self.copyButton = tk.Button(self.buttonframe, text=">>>", command=self.add_item_to_chosen)
        self.copyButton.grid(row=0, column=0, sticky='we')
        # Remove Button
        self.removeButton = tk.Button(self.buttonframe, text="<<<", command=self.remove_item_from_chosen)
        self.removeButton.grid(row=1, column=0, sticky='we')
        # Clear Button
        self.clearButton = tk.Button(self.buttonframe, text="clear", command=self.clear_all_chosen_items)
        self.clearButton.grid(row=2, column=0, sticky='we')

        # Right-hand side Listbox
        self.chosen = Pmw.ScrolledListBox(self, items='',
                                          listbox_height=5,
                                          vscrollmode="static",
                                          listbox_selectmode=tk.EXTENDED,
                                          dblclickcommand=self.remove_item_from_chosen)
        self.chosen.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

    def set_new_left_side_items(self, items):
        if not isinstance(items, list):
            raise TypeError('"items" argument must be a <list>')
        self.clear_all_chosen_items()
        list_items = sorted(items, key=str.lower)  # list is alphabetized
        self.listBox.setlist(list_items)

    def get_selection(self):
        return list(self.chosen.get(0, tk.END))

    def add_item_to_chosen(self):
        original_chosen_items = self.chosen.get(0, tk.END)
        selected = self.listBox.getcurselection()
        selected_minus_duplicates = []
        if selected:
            for item in selected:
                if item not in original_chosen_items:
                    selected_minus_duplicates.append(item)
            self.chosen.setlist(original_chosen_items + tuple(selected_minus_duplicates))

            # ..and remove from left-side box
            original_unselected_items = self.listBox.get()
            unselected_minus_selected = []
            for item in original_unselected_items:
                if item not in selected_minus_duplicates:
                    unselected_minus_selected.append(item)
            self.listBox.setlist(unselected_minus_selected)

    def remove_item_from_chosen(self):
        original_chosen_items = self.chosen.get(0, tk.END)
        selected = self.chosen.getcurselection()
        original_minus_selected = []
        selected_to_remove = []
        if selected:
            for item in original_chosen_items:
                if item not in selected:
                    original_minus_selected.append(item)
                else:
                    selected_to_remove.append(item)
            self.chosen.setlist(original_minus_selected)

            # ..and add to left-side box
            original_unselected_items = self.listBox.get()
            list_items = sorted(original_unselected_items + tuple(selected_to_remove), key=str.lower)
            self.listBox.setlist(list_items)

    def clear_all_chosen_items(self):
        original_unselected_items = self.listBox.get()
        original_chosen_items = self.chosen.get(0, tk.END)
        self.chosen.clear()

        # ..and add to left-side box
        list_items = sorted(original_unselected_items + original_chosen_items, key=str.lower)
        self.listBox.setlist(list_items)
