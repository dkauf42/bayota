"""
Main
"""
import logging

from gui.useframes.myrangesliderframe2 import MyRangeSliderFrame2
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


def main():
    # configure the logger
    global log
    log.setLevel(LOGGING_LEVEL)
    handler = logging.StreamHandler()
    logformat = logging.Formatter("%(levelname)s " +
                                  "%(asctime)s " +
                                  "%(filename)s:%(funcName)s(line:%(lineno)d)" +
                                  "\n\t%(message)s")
    handler.setFormatter(logformat)
    log.addHandler(handler)

    # initialize the demo
    MyRangeSliderFrame2().mainloop()


'''
Entry Point
'''
if __name__ == "__main__":
    main()