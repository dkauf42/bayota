import plotly.plotly as py
import plotly.graph_objs as go


def plotly_loadobj(df=None, savefig=True, savefilepathandname=None,
                   xname='totalcostupperbound',
                   title='Max Load Reduction vs. Total Cost Constraint',
                   xlabel='Total Cost ($) Upper Bound Constraint',
                   ylabel='Maximal Load Reduction (%)'):
    if not savefilepathandname:
        savefig = False

    # Create a trace
    trace = go.Scatter(x=df[xname],
                       y=df['objective']
                       )
    data = [trace]

    # Edit the layout
    layout = dict(title=title,
                  xaxis=dict(title=xlabel,
                             tickformat='.0f'),
                  yaxis=dict(title=ylabel,
                             tickformat='.2f'),
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)'
                  )

    fig = dict(data=data, layout=layout)
    # py.iplot(fig, filename='styled-line')

    if savefig:
        py.image.save_as(fig, filename=savefilepathandname, scale=5)

    return fig


def plotly_costobj(df=None, savefig=True, savefilepathandname=None,
                   xname='theta',
                   title='Minimal Total Cost vs. Load Constraint',
                   xlabel='Load Reduction (%) Lower Bound Constraint',
                   ylabel='Minimal Total Cost ($)'):
    if not savefilepathandname:
        savefig = False

    df_feasib = df.loc[df['feasible'] == True, :]
    df_infeas = df.loc[df['feasible'] == False, :]

    # Create a trace
    trace_feasible = go.Scatter(x=df_feasib[xname],
                                y=df_feasib['objective'],
                                mode='lines+markers',
                                line=dict(
                                    color='rgb(31, 119, 180)',
                                    width=4,)
                                )

    trace_infeasible = go.Scatter(x=df_infeas[xname],
                                  y=df_infeas['objective'],
                                  mode='markers',
                                  line=dict(
                                      color='rgb(249, 120, 80)',
                                      width=4,)
                                  )

    data = [trace_feasible, trace_infeasible]

    # Edit the layout
    layout = dict(title=title,
                  xaxis=dict(title=xlabel,
                             tickformat='.2f'),
                  yaxis=dict(title=ylabel,
                             tickformat='.2f'),
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  )

    fig = dict(data=data, layout=layout)
    py.iplot(fig, filename='styled-line')

    if savefig:
        py.image.save_as(fig, filename=savefilepathandname, scale=5)

    return fig

