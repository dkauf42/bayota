"""
RangeSlider Demo class
- Creates the window and grid bags the widgets
"""
from tkinter import *
from gui.useframes.rangeslider import RangeSlider


class RangeSliderFrame(Frame):
    __minValueLabel = None
    __maxValueLabel = None
    __rs = None

    def __init__(self, parent,
                 upperbound=1000, lowerbound=500,
                 upper=750, lower=650,
                 majortickspacing=100, minortickspacing=20,
                 snaptoticks=False):
        """ Constructor - does all the grunt work in creating the slider frame """
        Frame.__init__(self, parent)
        self.parent = parent

        self.__lowerEntryString = StringVar()
        self.__lowerBoundEntryString = StringVar()
        self.__upperEntryString = StringVar()
        self.__upperBoundEntryString = StringVar()
        self.__majorTickEntryString = StringVar()
        self.__minorTickEntryString = StringVar()

        # create the range slider widget to spec
        self.__rs = RangeSlider(self,
                                lowerBound=0, upperBound=100,
                                initialLowerBound=25, initialUpperBound=75,
                                sliderColor="yellow", sliderHighlightedColor="green",
                                barColor="lightblue",
                                caretColor="red", caretHighlightedColor="green",
                                barWidthPercent=0.85,
                                barHeightPercent=0.55,
                                canvasHeight=40)
        self.__rs.setUpperBound(upperbound)
        self.__rs.setLowerBound(lowerbound)
        self.__rs.setLower(lower)
        self.__rs.setUpper(upper)
        self.__rs.setMajorTickSpacing(majortickspacing)
        self.__rs.setMinorTickSpacing(minortickspacing)
        self.__rs.setPaintTicks(True)
        self.__rs.setSnapToTicks(snaptoticks)
        self.__rs.setFocus()

        # create the label widgets for min/max
        self.__minValueLabel = Label(self, text="Lower")
        self.__minValueEntry = Entry(self, textvariable=self.__lowerEntryString)
        self.__lowerEntryString.trace("w", self.__lowerEntry_onChange)

        self.__maxValueLabel = Label(self, text="Upper")
        self.__maxValueEntry = Entry(self, textvariable=self.__upperEntryString)
        self.__upperEntryString.trace("w", self.__upperEntry_onChange)

        self.__snapToTicksCheckVar = IntVar()
        self.__snapToTicksCheckVar.set(int(self.__rs.getSnapToTicks()))
        self.__snapToTicks = Checkbutton(self,
                                         text="Snap To Ticks",
                                         command=self.snapToTicksCheck_onClick,
                                         variable=self.__snapToTicksCheckVar,
                                         onvalue="1",
                                         offvalue="0")

        # create the reset slider and quit button
        reset_button = Button(self, text="Reset")
        reset_button.bind("<1>", self.resetButton_onClick)

        # THE GRID
        # this positions all the GUI components into their grid
        self.__minValueLabel.grid(column=1, row=0)  # , sticky=(W, E))
        self.__minValueEntry.grid(column=2, row=0)  # , sticky=(W, E))
        self.__maxValueLabel.grid(column=1, row=1)  # , sticky=(W, E))
        self.__maxValueEntry.grid(column=2, row=1)  # , sticky=(W, E))

        reset_button.grid(column=3, row=0, columnspan=1, sticky=(W, E))
        self.__snapToTicks.grid(column=3, row=1, columnspan=1, stick=(W, E))
        self.__snapToTicks.grid_remove()
        self.__rs.grid(column=0, row=0, rowspan=2, sticky=(N, S, E, W))

        # setup the grid weights
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)

        # bind our slider state change event
        self.__rs.subscribe(self.slider_changeState)
        self.slider_changeState(None)

        # bind some convenience keys
        self.bind("<Escape>", self.keyPress_Escape)

    def shutdown(self):
        """ Utility - Shutdown
            Perform any last minute shutdown/cleanup tasks
        """
        self.destroy()

    def keyPress_Escape(self, e):
        """ Event - keyPress Escape (added for developmental reasons)
            - perform shutdown whenever escape is hit
        """
        self.shutdown()

    def slider_changeState(self, e):
        """ Event - slider change state
            - Binded to the notify event of our slider controller
            - This will be called whenever the slider changes
        """
        if self.focus_displayof() != self.__minValueEntry:
            self.__minValueEntry.delete(0, END)
            self.__minValueEntry.insert(0, self.__rs.getLower())

        if self.focus_displayof() != self.__maxValueEntry:
            self.__maxValueEntry.delete(0, END)
            self.__maxValueEntry.insert(0, self.__rs.getUpper())

    def snapToTicksCheck_onClick(self, var=None):
        """ Event - Snap to ticks click
            - Reset the slider to its starting values
        """
        if var is None:
            b = self.__snapToTicksCheckVar.get()
            self.__rs.setSnapToTicks(b)
        else:
            b = var
            self.__rs.setSnapToTicks(b)
            if self.__snapToTicksCheckVar.get() is 1:
                self.__snapToTicksCheckVar.set(int(0))
                self.__rs.setSnapToTicks(0)
            elif self.__snapToTicksCheckVar.get() is 0:
                self.__snapToTicksCheckVar.set(int(1))
                self.__rs.setSnapToTicks(1)

    def __lowerEntry_onChange(self, e, a, mode):
        """ Event - on entry change events
            - these all basically do the exact same thing
        """
        try:
            f = float(self.__lowerEntryString.get())
            if f != self.__rs.getLower():
                self.__rs.setLower(f)
        except:
            None

    def __lowerBoundEntry_onChange(self, e, a, mode):
        try:
            f = float(self.__lowerBoundEntryString.get())
            if f != self.__rs.getLowerBound():
                self.__rs.setLowerBound(f)
        except:
            None

    def __upperEntry_onChange(self, e, a, mode):
        try:
            f = float(self.__upperEntryString.get())
            if f != self.__rs.getUpper():
                self.__rs.setUpper(f)
        except:
            None

    def __upperBoundEntry_onChange(self, e, a, mode):
        try:
            f = float(self.__upperBoundEntryString.get())
            if f != self.__rs.getUpperBound():
                self.__rs.setUpperBound(f)
        except:
            None

    def __minorTickEntry_onChange(self, e, a, mode):
        try:
            f = float(self.__minorTickEntryString.get())
            if f != self.__rs.getMinorTickSpacing():
                self.__rs.setMinorTickSpacing(f)
        except:
            None

    def __majorTickEntry_onChange(self, e, a, mode):
        try:
            f = float(self.__majorTickEntryString.get())
            if f != self.__rs.getMajorTickSpacing():
                self.__rs.setMajorTickSpacing(f)
        except:
            None

    def resetButton_onClick(self, e):
        """ Event - Rest button on click
            - Reset the slider to its starting or other values
        """
        #self.__rs.setLower(25)
        #self.__rs.setUpper(75)
        self.__rs.setLower(self.__rs.getLowerBound() + (self.__rs.getBoundsRange() * 0.25))
        self.__rs.setUpper(self.__rs.getLowerBound() + (self.__rs.getBoundsRange() * 0.75))
