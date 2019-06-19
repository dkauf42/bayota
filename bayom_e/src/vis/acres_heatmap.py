import seaborn as sns
import matplotlib.pyplot as plt


def heatmap_loadobj(df=None, savefig=True, savefilepathandname=None, xname='totalcostupperbound'):
    if not savefilepathandname:
        savefig=False

    fig = plt.figure(figsize=(10, 12))
    ax = sns.heatmap(df[df.columns.difference([xname, 'range', 'objective'])].transpose(),
                     cmap='viridis',
                     cbar_kws={'label': 'acres'},
                     xticklabels=list('%s\n(%.1f)' % ("${0:,.0f}".format(x), y)
                                      for x, y in
                                      zip(df[xname], round(df['objective'], 1))
                                      )
                     )
    plt.xlabel("totalcostupperbound (max % load reduction achieved)")
    plt.tight_layout()

    if savefig:
        plt.savefig(savefilepathandname, bbox_inches='tight')


def heatmap_costobj(df=None, figsize=(10, 20), savefig=True, savefilepathandname=None, xname='tau'):
    if not savefilepathandname:
        savefig=False

    fig = plt.figure(figsize=figsize)
    ax = sns.heatmap(df[df.columns.difference([xname, 'range', 'objective'])].T,
                     cmap='viridis',
                     cbar_kws={'label': 'acres'},
                     xticklabels=list('%d\n(%s)' % (x, "${0:,.0f}".format(y))
                                      for x, y in
                                      zip(df[xname], round(df['objective'], 1))
                                      )
                     )
    plt.xlabel("loadreductionlowerbound (min total cost achieved)")
    # plt.tight_layout()
    if savefig:
        plt.savefig(savefilepathandname, bbox_inches='tight')
