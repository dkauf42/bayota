from sandbox.__init__ import get_outputdir

writedir = get_outputdir()


class Examples:
    def __init__(self, name=''):
        """Define example scenarios for testing/prototyping the decision spaces, scenarios, and optimization
        """
        self.load(name)

    def load(self, name):
        if name == 'adamscounty':
            self.name = 'TestOne'
            self.description = 'TestOneDescription'
            self.baseyear = '1995'
            self.basecondname = 'Example_BaseCond2'
            self.wastewatername = 'Example_WW1'
            self.costprofilename = 'Example_CostProfile1'
            self.geoscalename = 'County'
            self.geoareanames = ['Adams, PA']

        elif name == 'adams_and_annearundel':
            self.name = 'TestOne'
            self.description = 'TestOneDescription'
            self.baseyear = '1995'
            self.basecondname = 'Example_BaseCond2'
            self.wastewatername = 'Example_WW1'
            self.costprofilename = 'Example_CostProfile1'
            self.geoscalename = 'County'
            self.geoareanames = ['Adams, PA', 'Anne Arundel, MD']

        elif name == 'adams_annearundel_and_york':
            self.name = 'TestOne'
            self.description = 'TestOneDescription'
            self.baseyear = '1995'
            self.basecondname = 'Example_BaseCond2'
            self.wastewatername = 'Example_WW1'
            self.costprofilename = 'Example_CostProfile1'
            self.geoscalename = 'County'
            self.geoareanames = ['Adams, PA', 'York, PA', 'Anne Arundel, MD']

        else:
            if not name:
                raise ValueError('example name not supplied')
            raise ValueError('example name "%s" unrecognized' % name)
