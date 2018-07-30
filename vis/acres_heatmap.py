import seaborn as sns
import matplotlib.pyplot as plt


def loadobj(df=None, instance=None, savefig=True, savefilepathandname=None, titlestr=''):
    if not savefilepathandname:
        savefig=False

    fig = plt.figure(figsize=(10, 12))
    ax = sns.heatmap(df[df.columns.difference(['totalcostupperbound', 'range', 'objective'])].transpose(),
                     cmap='viridis',
                     cbar_kws={'label': 'acres'},
                     xticklabels=list('%s\n(%.1f)' % ("${0:,.0f}".format(x), y)
                                      for x, y in
                                      zip(df['totalcostupperbound'], round(df['objective'], 1))
                                      )
                     )
    plt.xlabel("totalcostupperbound (max % load reduction achieved)")

    if savefig:
        plt.savefig(savefilepathandname)


def heatmap_costobj(df=None, instance=None, savefig=True, savefilepathandname=None, titlestr=''):
    if not savefilepathandname:
        savefig=False

    fig = plt.figure(figsize=(10, 12))
    ax = sns.heatmap(df[df.columns.difference(['tau', 'range', 'objective'])].T,
                     cmap='viridis',
                     cbar_kws={'label': 'acres'},
                     xticklabels=list('%d\n(%s)' % (x, "${0:,.0f}".format(y))
                                      for x, y in
                                      zip(df['tau'], round(df['objective'], 1))
                                      )
                     )
    plt.xlabel("loadreductionlowerbound (min total cost achieved)")

    if savefig:
        plt.savefig(savefilepathandname)
