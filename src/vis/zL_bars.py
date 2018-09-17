import matplotlib.pyplot as plt


def zL_bars(df=None, instance=None, savefig=True, savefilepathandname=None):
    if not savefilepathandname:
        raise ValueError('Not savepath specified')

    # zL_df_filtered = merged_df.loc[abs(merged_df['zL'])>0.45,:].copy()
    keystrs = [str([x, y]) for x, y in zip(df['bmpshortname'], df['loadsource'])]
    # Make Figure
    fig = plt.figure(figsize=(10, 4))
    rects = plt.barh(y=keystrs, width=df['zL'])
    ax = plt.gca()

    ax.set_position([0.3, 0.1, 0.5, 0.8])

    if savefig:
        plt.savefig(savefilepathandname)
