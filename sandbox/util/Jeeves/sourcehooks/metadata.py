from sandbox.util.Jeeves.sourcehooks.sourcehooks import SourceHook


class Metadata(SourceHook):
    def __init__(self, sourcedata=None):
        """ Metadata Methods """
        SourceHook.__init__(self, sourcedata=sourcedata)

    # Methods to get metadata options
    def base_year_names(self):
        return ['640', '1642', '1812', '1918']

    def base_condition_names(self):
        return ['BaseCondition0001', 'BaseCondition0002', 'BaseCondition0003', 'BaseCondition0004']

    def wastewaterdata_names(self):
        return ['WasteWater0001', 'WasteWater0002', 'WasteWater0003', 'WasteWater0004']

    def costprofile_names(self):
        return ['CostProfile0001', 'CostProfile0002', 'CostProfile0003', 'CostProfile0004']
