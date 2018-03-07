"""
RangeSlider Demo class
- Creates the window and grid bags the widgets
"""
import logging
from tkinter import *
from gui.useframes.my_rangeslider import RangeSlider
'''
logging.INFO
logging.ERROR
logging.WARN
'''
LOGGING_LEVEL = logging.INFO

''' logging global '''
log = logging.getLogger("default")


class MyRangeSliderFrame2(Frame):
    __width = 800
    __height = 300

    __minValueLabel = None
    __maxValueLabel = None
    __rs = None

    def __init__(self):
        """ Constructor - does all the grunt work in creating the slider frame """
        Frame.__init__(self)
        self.master.title("Range Slider Demo")

        self.__lowerEntryString = StringVar()
        self.__lowerBoundEntryString = StringVar()
        self.__upperEntryString = StringVar()
        self.__upperBoundEntryString = StringVar()
        self.__majorTickEntryString = StringVar()
        self.__minorTickEntryString = StringVar()

        # center the window
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        x = (ws / 2) - (self.__width / 2)
        y = (hs / 2) - (self.__height / 2)

        # geometry = wxh+x+y
        self.master.geometry('%dx%d+%d+%d' % (self.__width, self.__height, x, y))

        # create the range slider widget to spec
        self.__rs = RangeSlider(self.master,
                                lowerBound=0, upperBound=100,
                                initialLowerBound=25, initialUpperBound=75,
                                sliderColor="yellow", sliderHighlightedColor="green",
                                barColor="lightblue",
                                caretColor="red", caretHighlightedColor="green",
                                barWidthPercent=0.85, barHeightPercent=0.05)
        self.__rs.setUpperBound(1000)
        self.__rs.setLowerBound(500)
        self.__rs.setLower(650)
        self.__rs.setUpper(750)
        self.__rs.setMajorTickSpacing(100)
        self.__rs.setMinorTickSpacing(20)
        self.__rs.setPaintTicks(True)
        self.__rs.setSnapToTicks(False)
        self.__rs.setFocus()

        # create the label widgets for min/max
        self.__minValueLabel = Label(self.master, text="Lower")
        self.__minValueEntry = Entry(self.master, textvariable=self.__lowerEntryString)
        self.__lowerEntryString.trace("w", self.__lowerEntry_onChange)

        self.__maxValueLabel = Label(self.master, text="Upper")
        self.__maxValueEntry = Entry(self.master, textvariable=self.__upperEntryString)
        self.__upperEntryString.trace("w", self.__upperEntry_onChange)

        self.__snapToTicksCheckVar = IntVar()
        self.__snapToTicksCheckVar.set(int(self.__rs.getSnapToTicks()))
        self.__snapToTicks = Checkbutton(self.master,
                                         text="Snap To Ticks",
                                         command=self.__snapToTicksCheck_onClick,
                                         variable=self.__snapToTicksCheckVar,
                                         onvalue="1",
                                         offvalue="0")

        # create the reset slider and quit button
        reset_button = Button(self.master, text="Reset")
        reset_button.bind("<1>", self.resetButton_onClick)

        # THE GRID
        # this positions all the GUI components into their grid
        self.__minValueLabel.grid(column=1, row=0, sticky=(W, E))
        self.__minValueEntry.grid(column=2, row=0, sticky=(W, E))
        self.__maxValueLabel.grid(column=1, row=1, sticky=(W, E))
        self.__maxValueEntry.grid(column=2, row=1, sticky=(W, E))

        self.__snapToTicks.grid(column=1, row=2, columnspan=2, stick=(W, E))
        reset_button.grid(column=1, row=3, columnspan=2, sticky=(W, E))
        self.__rs.grid(column=0, row=0, rowspan=10, sticky=(N, S, E, W))

        # setup the grid weights
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.master.rowconfigure(2, weight=1)
        self.master.rowconfigure(3, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=0)
        self.master.columnconfigure(2, weight=0)

        # bind our slider state change event
        self.__rs.subscribe(self.slider_changeState)
        self.slider_changeState(None)

        # bind some convenience keys
        self.master.bind("<Escape>", self.keyPress_Escape)

    def shutdown(self):
        """ Utility - Shutdown
            Perform any last minute shutdown tasks
        """
        # perform any cleanup
        log.info("Quitting...")
        self.master.destroy()

    def keyPress_Escape(self, e):
        """ Event - keyPress Escape
            - perform shutdown whenever escape is hit
            - added for developmental reasons
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

    def __snapToTicksCheck_onClick(self):
        """ Event - Snap to ticks click
            - Reset the slider to its starting values
        """
        b = self.__snapToTicksCheckVar.get()
        self.__rs.setSnapToTicks(b)

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
            - Reset the slider to its starting values
        """
        log.debug("Reseting Slider...")
        self.__rs.setLower(25)
        self.__rs.setUpper(75)
