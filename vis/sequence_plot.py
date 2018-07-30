import plotly.plotly as py
import plotly.graph_objs as go


def plotly_loadobj(df=None, instance=None, savefig=True, savefilepathandname=None, titlestr=''):
    if not savefilepathandname:
        savefig = False

    # Create a trace
    trace = go.Scatter(x=df['totalcostupperbound'],
                       y=df['objective']
                       )
    data = [trace]

    # Edit the layout
    layout = dict(title='Max Load Reduction vs. Total Cost Constraint',
                  xaxis=dict(title='Total Cost ($) Upper Bound Constraint'),
                  yaxis=dict(title='Maximal Load Reduction (%)'),
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)'
                  )

    fig = dict(data=data, layout=layout)
    # py.iplot(fig, filename='styled-line')

    if savefig:
        py.image.save_as(fig, filename=savefilepathandname, scale=5)

    return fig


def plotly_costobj(df=None, instance=None, savefig=True, savefilepathandname=None, titlestr=''):
    if not savefilepathandname:
        savefig = False
    # Create a trace
    trace = go.Scatter(x=df['tau'],
                       y=df['objective']
                       )
    data = [trace]

    # Edit the layout
    layout = dict(title='Minimal Total Cost vs. Load Constraint',
                  xaxis=dict(title='Load Reduction (%) Lower Bound Constraint'),
                  yaxis=dict(title='Minimal Total Cost ($)',
                             range=[0, 0.1]),
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  )

    fig = dict(data=data, layout=layout)
    py.iplot(fig, filename='styled-line')

    if savefig:
        py.image.save_as(fig, filename=savefilepathandname, scale=5)

    return fig
