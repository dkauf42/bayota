"""
RangeSlider Demo class
- Creates the window and grid bags the widgets
"""
import logging
from tkinter import *
'''
logging.INFO
logging.ERROR
logging.WARN
'''
LOGGING_LEVEL = logging.INFO

'''
logging global
'''
log = logging.getLogger("default")

from gui.useframes.my_rangeslider import RangeSlider

class my_rangeslider_frame(Frame):
    __width = 800
    __height = 600

    __minValueLabel = None
    __maxValueLabel = None
    __rs = None

    '''
    Constructor
    - does all the grunt work in creating the demo
    '''

    def __init__(self):
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
        self.master.geometry('%dx%d+%d+%d' %
                             (self.__width, self.__height, x, y))

        # create the range slider widget to spec
        self.__rs = RangeSlider(self.master,
                                lowerBound=0, upperBound=100,
                                initialLowerBound=25, initialUpperBound=75);
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
        # self.__minValueLabel = Label(self.master, text="Lower")
        # self.__minValueEntry = Entry(self.master, textvariable=self.__lowerEntryString)
        # self.__lowerEntryString.trace("w", self.__lowerEntry_onChange)
        #
        # self.__maxValueLabel = Label(self.master, text="Upper")
        # self.__maxValueEntry = Entry(self.master, textvariable=self.__upperEntryString)
        # self.__upperEntryString.trace("w", self.__upperEntry_onChange)
        #
        # self.__lowerBoundLabel = Label(self.master, text="LowerBound")
        # self.__lowerBoundEntry = Entry(self.master, textvariable=self.__lowerBoundEntryString)
        # self.__lowerBoundEntryString.trace("w", self.__lowerBoundEntry_onChange)
        #
        # self.__upperBoundLabel = Label(self.master, text="UpperBound")
        # self.__upperBoundEntry = Entry(self.master, textvariable=self.__upperBoundEntryString)
        # self.__upperBoundEntryString.trace("w", self.__upperBoundEntry_onChange)
        #
        # self.__majorTickSpacingLabel = Label(self.master, text="Major Tick Spacing")
        # self.__majorTickSpacingEntry = Entry(self.master, textvariable=self.__majorTickEntryString)
        # self.__majorTickEntryString.trace("w", self.__majorTickEntry_onChange)
        #
        # self.__minorTickSpacingLabel = Label(self.master, text="Minor Tick Spacing")
        # self.__minorTickSpacingEntry = Entry(self.master, textvariable=self.__minorTickEntryString)
        # self.__minorTickEntryString.trace("w", self.__minorTickEntry_onChange)

        # self.__paintTicksCheckVar = IntVar()
        # self.__paintTicksCheckVar.set(int(self.__rs.getPaintTicks()))
        # self.__paintTicksCheck = Checkbutton(self.master,
        #                                      text="Paint Ticks",
        #                                      command=self.__paintTicksCheck_onClick,
        #                                      variable=self.__paintTicksCheckVar,
        #                                      onvalue="1",
        #                                      offvalue="0")

        self.__snapToTicksCheckVar = IntVar()
        self.__snapToTicksCheckVar.set(int(self.__rs.getSnapToTicks()))
        self.__snapToTicks = Checkbutton(self.master,
                                         text="Snap To Ticks",
                                         command=self.__snapToTicksCheck_onClick,
                                         variable=self.__snapToTicksCheckVar,
                                         onvalue="1",
                                         offvalue="0")

        # create the reset slider and quit button
        resetButton = Button(self.master, text="Reset")
        resetButton.bind("<1>", self.resetButton_onClick)

        quitButton = Button(self.master, text="Quit")
        quitButton.bind("<1>", self.quitButton_onClick)

        secondRs = RangeSlider(self.master,
                               sliderColor="yellow", sliderHighlightedColor="green",
                               barColor="lightblue",
                               caretColor="red", caretHighlightedColor="green",
                               barWidthPercent=0.85, barHeightPercent=0.10)
        secondRs.setPaintTicks(True)

        # THE GRID
        # this positions all the GUI components into their grid
        # self.__minValueLabel.grid(column=1, row=0, sticky=(W, E))
        # self.__minValueEntry.grid(column=2, row=0, sticky=(W, E))
        # self.__maxValueLabel.grid(column=1, row=1, sticky=(W, E))
        # self.__maxValueEntry.grid(column=2, row=1, sticky=(W, E))
        # self.__lowerBoundLabel.grid(column=1, row=2, sticky=(W, E))
        # self.__lowerBoundEntry.grid(column=2, row=2, sticky=(W, E))
        # self.__upperBoundLabel.grid(column=1, row=3, sticky=(W, E))
        # self.__upperBoundEntry.grid(column=2, row=3, sticky=(W, E))
        # self.__majorTickSpacingLabel.grid(column=1, row=4, sticky=(W, E))
        # self.__majorTickSpacingEntry.grid(column=2, row=4, sticky=(W, E))
        # self.__minorTickSpacingLabel.grid(column=1, row=5, sticky=(W, E))
        # self.__minorTickSpacingEntry.grid(column=2, row=5, sticky=(W, E))
        # self.__paintTicksCheck.grid(column=1, row=6, columnspan=2, stick=(W, E))
        self.__snapToTicks.grid(column=1, row=7, columnspan=2, stick=(W, E))
        resetButton.grid(column=1, row=8, columnspan=2, sticky=(W, E))
        quitButton.grid(column=1, row=9, columnspan=2, sticky=(W, E))
        self.__rs.grid(column=0, row=0, rowspan=10, sticky=(N, S, E, W))
        secondRs.grid(column=0, row=10, columnspan=3, sticky=(W, E))

        # setup the grid weights
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.master.rowconfigure(2, weight=1)
        self.master.rowconfigure(3, weight=1)
        self.master.rowconfigure(4, weight=1)
        self.master.rowconfigure(5, weight=1)
        self.master.rowconfigure(6, weight=1)
        self.master.rowconfigure(7, weight=1)
        self.master.rowconfigure(8, weight=1)
        self.master.rowconfigure(9, weight=1)
        self.master.rowconfigure(10, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=0)
        self.master.columnconfigure(2, weight=0)

        # bind our slider state change event
        #self.__rs.subscribe(self.slider_changeState)
        #self.slider_changeState(None)

        # bind some convenience keys
        self.master.bind("<Escape>", self.keyPress_Escape)

    '''
    Utility - Shutdown
    Perform any last minute shutdown tasks
    '''
    def shutdown(self):
        # perform any cleanup
        log.info("Quitting...")
        self.master.destroy()

    '''
    Event - keyPress Escape
    - perform shutdown whenever escape is hit
    - added for developmental reasons
    '''
    def keyPress_Escape(self, e):
        self.shutdown()

    '''
    Event - slider change state
    - Binded to the notify event of our slider controller
    - This will be called whenever the slider changes
    '''
    # def slider_changeState(self, e):
    #     if (self.focus_displayof() != self.__minValueEntry):
    #         self.__minValueEntry.delete(0, END)
    #         self.__minValueEntry.insert(0, self.__rs.getLower())
    #
    #     if (self.focus_displayof() != self.__maxValueEntry):
    #         self.__maxValueEntry.delete(0, END)
    #         self.__maxValueEntry.insert(0, self.__rs.getUpper())
    #
    #     if (self.focus_displayof() != self.__lowerBoundEntry):
    #         self.__lowerBoundEntry.delete(0, END)
    #         self.__lowerBoundEntry.insert(0, self.__rs.getLowerBound())
    #
    #     if (self.focus_displayof() != self.__upperBoundEntry):
    #         self.__upperBoundEntry.delete(0, END)
    #         self.__upperBoundEntry.insert(0, self.__rs.getUpperBound())
    #
    #     if (self.focus_displayof() != self.__majorTickSpacingEntry):
    #         self.__majorTickSpacingEntry.delete(0, END)
    #         self.__majorTickSpacingEntry.insert(0, self.__rs.getMajorTickSpacing())
    #
    #     if (self.focus_displayof() != self.__minorTickSpacingEntry):
    #         self.__minorTickSpacingEntry.delete(0, END)
    #         self.__minorTickSpacingEntry.insert(0, self.__rs.getMinorTickSpacing())

    # ''' Event - Rest button on click
    # - Reset the slider to its starting values
    # '''
    # def __paintTicksCheck_onClick(self):
    #     b = self.__paintTicksCheckVar.get()
    #     self.__rs.setPaintTicks(b)

    ''' Event - Snap to ticks click
    - Reset the slider to its starting values
    '''
    def __snapToTicksCheck_onClick(self):
        b = self.__snapToTicksCheckVar.get()
        self.__rs.setSnapToTicks(b)

    ''' Event - on entry change events
    - these all basically do the exact same thing
    '''
    def __lowerEntry_onChange(self, e, a, mode):
        try:
            f = float(self.__lowerEntryString.get())
            if (f != self.__rs.getLower()):
                self.__rs.setLower(f)
        except:
            None

    def __lowerBoundEntry_onChange(self, e, a, mode):
        try:
            f = float(self.__lowerBoundEntryString.get())
            if (f != self.__rs.getLowerBound()):
                self.__rs.setLowerBound(f)
        except:
            None

    def __upperEntry_onChange(self, e, a, mode):
        try:
            f = float(self.__upperEntryString.get())
            if (f != self.__rs.getUpper()):
                self.__rs.setUpper(f)
        except:
            None

    def __upperBoundEntry_onChange(self, e, a, mode):
        try:
            f = float(self.__upperBoundEntryString.get())
            if (f != self.__rs.getUpperBound()):
                self.__rs.setUpperBound(f)
        except:
            None

    def __minorTickEntry_onChange(self, e, a, mode):
        try:
            f = float(self.__minorTickEntryString.get())
            if (f != self.__rs.getMinorTickSpacing()):
                self.__rs.setMinorTickSpacing(f)
        except:
            None

    def __majorTickEntry_onChange(self, e, a, mode):
        try:
            f = float(self.__majorTickEntryString.get())
            if (f != self.__rs.getMajorTickSpacing()):
                self.__rs.setMajorTickSpacing(f)
        except:
            None

    ''' Event - Rest button on click
    - Reset the slider to its starting values
    '''
    def resetButton_onClick(self, e):
        log.debug("Reseting Slider...")
        self.__rs.setLower(25)
        self.__rs.setUpper(75)

    ''' Event - quit on click
    - Perform shutdown on quit
    '''
    def quitButton_onClick(self, e):
        self.shutdown()

