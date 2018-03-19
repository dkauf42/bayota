import pyodbc

server = 'SQL2D'
database = 'master'
username = 'dkaufman'
driver = '{SQL Server Native Client 11.0}'
port = '1433'

cnn = pyodbc.connect('Driver=' + driver +
                     ';Server=' + server +
                     ';Database=' + database +
                     ';Trusted_Connection=yes')

#  cnn = pyodbc.connect('DRIVER=' + driver +
#                      ';SERVER=' + server +
#                      ';PORT=' + port +
#                      ';DATABASE=' + database +
#                      ';UID=' + username +
#                      ';PWD=' + password)
# cnn = pyodbc.connect(driver='{SQL Server}',
#                      server=server,
#                      database=database,
#                      user=username,
#                      password=password)
cursor = cnn.cursor()
cursor.execute('SELECT COUNT(ScenarioBuilderV3MetaData')
