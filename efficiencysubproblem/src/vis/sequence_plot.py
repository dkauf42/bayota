import matplotlib.pyplot as plt
plt.switch_backend('agg')
from matplotlib import rcParams


def plotlib_costobj(df=None, savefig=True, savefilepathandname=None,
                    xname='tau',
                    title='Minimal Total Cost vs. Load Constraint',
                    xlabel='Load Reduction (%) Lower Bound Constraint',
                    ylabel='Minimal Total Cost ($)',
                    secondaryxticklabels=None,
                    showplot=True):
    if not savefilepathandname:
        savefig = False

    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['MS Reference Sans Serif']
    rcParams['font.weight'] = 'normal'
    rcParams['font.size'] = 12

    df_feasib = df.loc[df['feasible'] == True, :]
    df_infeas = df.loc[df['feasible'] == False, :]

    fig, ax = plt.subplots()
    for ii, data in enumerate([df_feasib, df_infeas]):
        if ii == 0:
            ax.plot(data[xname],
                    data['objective'],
                    color=[31/255, 119/255, 180/255],
                    linestyle='-',
                    linewidth=3,
                    marker='o',
                    label='feasible solutions',
                    alpha=1.)
        else:
            ax.plot(data[xname],
                    data['objective'],
                    color=[249/255, 120/255, 80/255],
                    linestyle='None',
                    marker='o',
                    label='infeasible solutions',
                    alpha=0.7)

    ax.grid(color=[200/255, 200/255, 200/255],
            alpha=0.4, linestyle='-', linewidth=1)

    ax.set_xticks(df[xname])
    ax.set_xticklabels(df[xname])
    plt.yticks(rotation=45)

    # Hide the right and top spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.set_ylabel(ylabel, rotation=90)
    ax.set_xlabel(xlabel)
    ax.set_title(title)

    ax.legend(frameon=False, loc='upper left', ncol=1)

    if secondaryxticklabels is not None:
        ax2 = ax.twiny()
        axTicks = ax.get_xticks()
        ax2Ticks = axTicks

        def tick_function(X):
            return ["%.1f" % z for z in X]

        ax2.set_xticks(ax2Ticks)
        ax2.set_xbound(ax.get_xbound())

        ax2.set_xticklabels(tick_function(secondaryxticklabels))
        ax2.tick_params(axis='x', which='major', labelsize=9)

        # Add some extra space for the second axis at the bottom
        plt.subplots_adjust(bottom=0.05)
        # ax.xaxis.labelpad = 30

        # Move twinned axis ticks and label from top to bottom
        ax2.xaxis.set_ticks_position("bottom")
        ax2.xaxis.set_label_position("bottom")
        # Offset the twin axis below the host
        ax2.spines["bottom"].set_position(("axes", -0.2))
        # Turn on the frame for the twin axis, but then hide all
        # but the bottom spine
        ax2.set_frame_on(True)
        ax2.patch.set_visible(False)
        for k, sp in ax2.spines.items():
            sp.set_visible(False)
        ax2.spines["bottom"].set_visible(True)

        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    if showplot:
        plt.show()
    else:
        plt.draw()
    if savefig:
        fig.savefig(savefilepathandname, dpi=300,
                    bbox_inches='tight', transparent=True)

    return fig


def plotlib_loadreductionobj(df=None, savefig=True, savefilepathandname=None,
                    xname='totalcostupperbound',
                    title='Max Load Reduction vs. Total Cost Constraint',
                    xlabel='Total Cost ($) Upper Bound Constraint',
                    ylabel='Maximal Load Reduction (%)',
                    secondaryxticklabels=None,
                    showplot=True):
    if not savefilepathandname:
        savefig = False

    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['MS Reference Sans Serif']
    rcParams['font.weight'] = 'normal'
    rcParams['font.size'] = 12

    df_feasib = df.loc[df['feasible'] == True, :]
    df_infeas = df.loc[df['feasible'] == False, :]

    fig, ax = plt.subplots()
    for ii, data in enumerate([df_feasib, df_infeas]):
        if ii == 0:
            ax.plot(data[xname],
                    data['objective'],
                    color=[31/255, 119/255, 180/255],
                    linestyle='-',
                    linewidth=3,
                    marker='o',
                    label='feasible solutions',
                    alpha=1.)
        else:
            ax.plot(data[xname],
                    data['objective'],
                    color=[249/255, 120/255, 80/255],
                    linestyle='None',
                    marker='o',
                    label='infeasible solutions',
                    alpha=0.7)

    ax.grid(color=[200/255, 200/255, 200/255],
            alpha=0.4, linestyle='-', linewidth=1)

    ax.set_xticks(df[xname])
    ax.set_xticklabels(df[xname])
    plt.yticks(rotation=45)

    # Hide the right and top spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.set_ylabel(ylabel, rotation=90)
    ax.set_xlabel(xlabel)
    ax.set_title(title)

    ax.legend(frameon=False, loc='upper left', ncol=1)

    if secondaryxticklabels is not None:
        ax2 = ax.twiny()
        axTicks = ax.get_xticks()
        ax2Ticks = axTicks

        def tick_function(X):
            return ["%.1f" % z for z in X]

        ax2.set_xticks(ax2Ticks)
        ax2.set_xbound(ax.get_xbound())

        ax2.set_xticklabels(tick_function(secondaryxticklabels))
        ax2.tick_params(axis='x', which='major', labelsize=9)

        # Add some extra space for the second axis at the bottom
        plt.subplots_adjust(bottom=0.05)
        # ax.xaxis.labelpad = 30

        # Move twinned axis ticks and label from top to bottom
        ax2.xaxis.set_ticks_position("bottom")
        ax2.xaxis.set_label_position("bottom")
        # Offset the twin axis below the host
        ax2.spines["bottom"].set_position(("axes", -0.2))
        # Turn on the frame for the twin axis, but then hide all
        # but the bottom spine
        ax2.set_frame_on(True)
        ax2.patch.set_visible(False)
        for k, sp in ax2.spines.items():
            sp.set_visible(False)
        ax2.spines["bottom"].set_visible(True)

        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    if showplot:
        plt.show()
    else:
        plt.draw()
    if savefig:
        fig.savefig(savefilepathandname, dpi=300,
                    bbox_inches='tight', transparent=True)

    return fig
