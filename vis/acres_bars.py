import os
import matplotlib.pyplot as plt


def acres_bars(df=None, instance=None, savefig=True, savefilepathandname=None, titlestr=''):
    if not savefilepathandname:
        raise(ValueError, 'Not savepath specified')

    # ---- Make acres Figure ----
    # sorteddf_byacres = merged_df.sort_values(by='acres')
    coststrs = [str(x) for x in zip(list(df['totalannualizedcostperunit']),
                                    list(df['totalinstancecost']))]
    keystrs = [str([x, y]) for x, y in zip(df['bmpshortname'], df['loadsource'])]

    # Make Figure
    fig = plt.figure(figsize=(10, 4))
    rects = plt.barh(y=keystrs, width=df['acres'])
    ax = plt.gca()

    for rect, label in zip(rects, coststrs):
        width = rect.get_width()
        plt.text(width + 0.1, rect.get_y() + rect.get_height() / 2,
                 label,
                 ha='left', va='center')

    plt.title(titlestr)

    ax.set_position([0.3, 0.1, 0.5, 0.7])

    if savefig:
        plt.savefig(savefilepathandname)
