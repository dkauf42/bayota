import pandas as pd


class TableLoader(object):
    def __init__(self, tableSet):
        object.__setattr__(self, "tableSet", set(tableSet))
                
    def __getattribute__(self, attr):
        if attr == "tableSet":
            raise AttributeError("instance <attr>:tableSet is not directly accessible, use <method>:getTblList instead")
        else:
            tableSet = object.__getattribute__(self, "tableSet")
            try:
                item = object.__getattribute__(self, attr)
                if attr in tableSet:
                    return item # pd.DataFrame.copy(item)
                else:
                    return item
            except AttributeError:
                if attr in tableSet:
                    raise AttributeError("use <method>:addTable to add <attr>:{:s}".format(attr))
                else:
                    raise AttributeError("invalid attribute specification")
                
    def __setattr__(self, attr, value):
        if attr == "tableSet":
            raise AttributeError("<attr>:tableSet cannot be changed")
        tableSet = object.__getattribute__(self, "tableSet")
        if attr in tableSet:
            if hasattr(self, attr):
                raise AttributeError("attribute has already been set and may not be changed")
            else:
                object.__setattr__(self, attr, value)
        else:
            raise AttributeError("invalid attribute specification")
    
    def getTblList(self):
        tableSet = object.__getattribute__(self, "tableSet")
        return sorted(list(tableSet))
        
    def addTable(self, tblName, tbl):
        if not isinstance(tbl, pd.DataFrame):
            raise TypeError("<arg>:tbl should be of type pandas.DataFrame")
        try:
            self.__setattr__(tblName, tbl)
        except AttributeError as err:
            raise err
