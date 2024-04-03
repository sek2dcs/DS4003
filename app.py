# importing packages 
from dash import Dash, dcc, html, Input, Output, callback  
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd 
import numpy as np
import dash_bootstrap_components as dbc

# reading in data 
data = pd.read_csv("https://github.com/sek2dcs/DS4003/blob/main/data.csv")

# initializing app  -- using minty boostrap theme 
app = Dash(__name__, external_stylesheets = [dbc.themes.MINTY])
server = app.server

# building app 
app.layout = html.Div([
    html.H1(children = "GHG Facility Emissions"),  # title
    html.Div([
        dcc.Tabs(id = 'tabs-on-top', value = 'tab-1', children = [  # tabs for the app
            dcc.Tab(label = 'Facility Industry Type', value = 'tab-1', children = [ # first tab 
                dcc.Dropdown(   # putting multi-select dropdown in for graph I will make 
                    options = [{'label': State, 'value': State} for State in data.State.unique()],  # user will be able to select every state in the dataset 
                    id = 'multi-dd-state', 
                    multi = True, 
                    value = 'VA'
                )
            ]),
            dcc.Tab(label = 'Facility Emissions', value = 'tab-2'), # second tab... 
            dcc.Tab(label = 'Emissions Map', value = 'tab-3', children = [  # graph for assignment
                dcc.RadioItems(  # radio button in the tab
                    options = [  # labels and values going by the diff emission type columns plus the total emissions 
                        {'label': 'Total reported emissions', 'value': 'Total reported emissions'},
                        {'label': 'CO2 emissions', 'value': 'CO2 emissions'},
                        {'label': 'Methane (CH4) emissions', 'value': 'Methane (CH4) emissions'},
                        {'label': 'Nitrous Oxide (N2O) emissions', 'value': 'Nitrous Oxide (N2O) emissions'},
                        {'label': 'SF6 emissions', 'value': 'SF6 emissions'}
                    ],
                    value = 'Total reported emissions', # default button 
                    id = 'map-radio-button',
                    inline = True # to be horizontal 
                ),
                dcc.Graph(id = 'bubble-map')  # graph in the tab
            ]),
            dcc.Tab(label = 'About', value='tab-4') # fourth tab 
        ])
    ])
])

# defining callback to update bubble map 
@app.callback(
    Output('bubble-map', 'figure'),
    Input('map-radio-button', 'value')
)
def update_bubble_map(selected_emissions):   

# converting emissions values to numeric just in case 
    data[selected_emissions] = pd.to_numeric(data[selected_emissions], errors = 'coerce')

# filtering out any NAs
    data_filtered = data.dropna(subset = [selected_emissions, 'Latitude', 'Longitude'])

# getting scale for bubbles 
    scale = 5000

# colors for the quartiles 
    colors = ["royalblue", "crimson", "lightseagreen", "orange", "yellowgreen"]

# calculating quartiles for the emissions to get the limits for a discrete legend 
    quartiles = np.percentile(data_filtered[selected_emissions], [25, 50, 75])
    
# limits for legend from the quartiles 
    limits = [(0, quartiles[0]), (quartiles[0], quartiles[1]), (quartiles[1], quartiles[2]),
              (quartiles[2], data_filtered[selected_emissions].max())]
    
# defining categories for legend 
    num_categories = len(limits)
    
# defining bin edges to make a discrete lengend at the end 
    bin_edges = np.linspace(data_filtered[selected_emissions].min(), data_filtered[selected_emissions].max(), num_categories + 1)
    
# getting started with graph! 
    fig = go.Figure()
    
    for i, lim in enumerate(limits): # i for index of quartile; lim for bounds of quartile 
        # filtering data for current quartiles for the selected emissions --> calling it data_bub 
        data_bub = data_filtered[(data_filtered[selected_emissions] >= lim[0]) & (data_filtered[selected_emissions] <= lim[1])]  # more filtering...based on quartile 
        color_index = np.digitize(data_bub[selected_emissions], bin_edges) - 1  # assigning each emission value to bin  
        data_bub['color'] = colors[i]  # assigning color to each emission based on quartile index (i) 
        
        fig.add_trace(go.Scattergeo(  # making a bubble map 
            locationmode = 'USA-states', # so dash knows that the longs & lats are in the US 
            lon = data_bub['Longitude'],
            lat = data_bub['Latitude'],
            text = data_bub['Facility Name'] + '<br>' + selected_emissions + ': ' + (data_bub[selected_emissions] / 1000).astype(str) + ' thousand',  # for further descrip when user hovers
            marker = dict(
                size = data_bub[selected_emissions] / scale, # size based on emission amount 
                color = data_bub['color'],
                line_color = 'rgb(40,40,40)',
                line_width = 0.5,
                sizemode = 'area'
            ),
            name = '{0} - {1}'.format(lim[0], lim[1]), # gives the exact high & low limits for each of the categories in the legend 
            showlegend = True
        ))
        
    tickvals = [(max(bin_edges) - min(bin_edges)) / num_categories * i + min(bin_edges) for i in    # defining values for each color in legend 
                range(num_categories + 1)]
    ticktext = [f'{tickvals[i]:.2f} - {tickvals[i + 1]:.2f}' for i in range(num_categories)]  # defining labels for each color in legend 

    fig.update_layout(
        title_text = 'Emissions of each facility in the USA map<br>(Click legend to toggle traces)',
        showlegend = True,
        geo = dict(
            scope = 'usa', # to get USA on map 
            landcolor = 'rgb(217, 217, 217)',
        ),
        coloraxis_colorbar = dict(  # specifying color bar to help with graph 
            tickvals = tickvals,
            ticktext = ticktext
        )
    )

    return fig

# running app! 
if __name__ == '__main__':
    app.run_server(debug=True)
