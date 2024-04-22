# importing packages 
from dash import Dash, dcc, html, Input, Output, callback  
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd 
import numpy as np
import dash_bootstrap_components as dbc
import requests
import io 

# importing the load figure template so that the graphs are in minty colors
from dash_bootstrap_templates import load_figure_template
load_figure_template(["minty"])

# for github repo icon
import dash_mantine_components as dmc
from dash_iconify import DashIconify


# using the requests library to access the data
url = "https://raw.githubusercontent.com/sek2dcs/DS4003/main/data.csv"
response = requests.get(url)
with open("data.csv", "wb") as f:
    f.write(response.content)
# data = pd.read_csv(io.BytesIO(response.content), delimiter = ',', error_bad_lines = False)
data = pd.read_csv("data.csv", delimiter = ',')
data = data.reset_index()

# reading the data in & resetting index just for debugging efforts
# data = pd.read_csv("data.csv", on_bad_lines='skip')

# styling the app
dbc_css= "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

# using the bootswatch MINTY theme as an external stylesheet
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY, dbc_css])
server = app.server

# building app! 
app.layout = dbc.Container([ # using dbc to get the minty theme in my dash
    dbc.Container(
        dbc.Container(html.H1("GHG Facility Emissions", className= "dbc")) # title 
    ),
    dcc.Tabs(id='tabs-on-top', value='tab-1', children=[ # tabs for the app 
        dcc.Tab(label='Facility Industry Type', value='tab-1', children=[ # first tab 
            html.Div([ # putting in a dropdown of the states that will edit the graph 
                html.Label("Select State", className = 'dbc'),
                dcc.Dropdown(
                    options=[{'label': State, 'value': State} for State in data.State.unique()], # user will be able to select any state in the df
                    id='dd-state',
                    multi = False, # not multi-select 
                    value='VA',
                    className='dbc',
                ),
                html.Br(), # space so it looks cleaner
                dcc.Graph(id='starburst-chart', className = 'dbc', style = {'height': '80vh', 'width': '80%'}) # id for graph -- editing style to make it a lil longer & skinnier
        ], className = 'dbc', style = {'width': '70%', 'display': 'inline-block', 'margin-right': '10px'}), # styling the div to make it lil longer & skinnier with some space on side to make it look cleaner
            dbc.Card( # starting the card to have some info about the graph 
                dbc.CardBody(
                    [
                        html.H4("Additional Info", className = "card-header"),
                        html.P(["This graph shows a starburst chart with the different", 
                        html.B(" industry types "), # bold text
                        "in the center, branching outwards to the specific",
                        html.B(" facility name. ")]), # bold text 
                        html.P(["Data Components:", 
                               html.Ul([
                                   html.Li([
                                    html.B(" Industry type "), # bold text
                                    "- Selecting from different industries that facility is a part of (i.e. Municipal Landfills, Underground Coal Mines, Staionary Combustion, etc.)"]), 
                                   html.Li([
                                    html.B(" Facility Name "), # bold text
                                   "- Selecting from the unique facility names given to the facility"]), 
                                   html.Li([
                                    html.B(" Total Reported Emissions "), # bold text
                                   "- Measured in metric tons of CO2 equivalent, accumulates all different emissions types in report"])
                               ])])
                    ]
                )
            , className = 'card text-white bg-primary mb-3', style = {'width': '20%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-top': '20px', }) # styling it so that it fits -- skinnier 
        ]), 
        dcc.Tab(label='Facility Emissions', value='tab-2', children=[ # second tab 
            html.Div([
                dbc.Label("Select State", className = 'dbc'), 
                dcc.Dropdown(
                    options=[{'label': State, 'value': State} for State in data.State.unique()], # dropdown to display the states in df 
                    id='dropdown-state',
                    multi=False,
                    value='VA',
                    className='dbc'
                ),
            ], className = 'dbc'),
            html.Div([
                dbc.Label("Select City", className = 'dbc'),
                dcc.Dropdown(
                    options=[{'label': City, 'value': City} for City in data.City.unique()], # dropdown to display the cities in df 
                    id='dropdown-city',
                    multi=True, # multi-select 
                    value='Raven',
                    className='dbc'
                ),
            ], className = 'dbc'),
            html.Br(), # some space 
            html.Div([
                dcc.Graph(id='bar-graph', className = 'dbc', style = {'height': '80vh', 'width': '80%'}) # making graph skinny & long 
            ], className = 'dbc', style = {'width': '70%', 'display': 'inline-block', 'margin-right': '10px'}),  # here too -- making it skinny & long
            dbc.Card(
                dbc.CardBody( # card to describe the graph further 
                    [
                        html.H4("Additional Info", className = "card-header"),
                        html.P(["This graph shows a bar graph with the different", 
                        html.B(" emission types "), 
                        "as the different colors of each bar, with each bar being a ",
                        html.B(" facility name. "),
                        "The bar graph can be filtered by state and city (or cities)."]),
                        html.P(["Data Components:", 
                               html.Ul([
                                   html.Li([
                                    html.B(" Emission Value "),
                                    "- Mesured in metric tons of CO2 equivalent, with the different types being carbon dioxide, methane, nitrous oxide, and sulfur hexafluoride."]), 
                                   html.Li([
                                    html.B(" Facility Name "),
                                   "- Selecting from the unique facility names given to the facility"])
                               ])])
                    ]
                )
            , className = 'card text-white bg-primary mb-3', style = {'width': '20%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-top': '20px', }) # making card skinny 
        ]),
        dcc.Tab(label='Emissions Map', value='tab-3', children=[ # third tab 
            html.Div([
                dbc.Label("Select Emission Type", className = 'dbc'),
                dbc.RadioItems( # radio buttons for the diff type of emissions in df
                    options=[
                        {'label': 'Total reported emissions', 'value': 'Total reported emissions'},
                        {'label': 'CO2 emissions', 'value': 'CO2 emissions'},
                        {'label': 'Methane (CH4) emissions', 'value': 'Methane (CH4) emissions'},
                        {'label': 'Nitrous Oxide (N2O) emissions', 'value': 'Nitrous Oxide (N2O) emissions'},
                        {'label': 'SF6 emissions', 'value': 'SF6 emissions'}
                    ],
                    value='Total reported emissions', # default value 
                    id='map-radio-button',
                    inline=True,
                    className='dbc'
                ),
            ], className = 'dbc'),
            html.Br(), # some space to make it clean 
            html.Div([
                dcc.Graph(id='bubble-map', className = 'dbc', style = {'height': '80vh', 'width': '80%'})
            ], className = 'dbc', style = {'width': '70%', 'display': 'inline-block', 'margin-right': '10px'}),
            dbc.Card(
                dbc.CardBody( # card for more info on map 
                    [
                        html.H4("Additional Info", className = "card-header"),
                        html.P(["This figure shows a bubble with the different", 
                        html.B(" emission types "), 
                        "as the different colors of the bubbles, with the different bubble sizes correlating to the",
                        html.B(" emission value. "),
                        "The map can be filtered by emission types, from total emissions to a certain emission type."]),
                        html.P(["Data Components:", 
                               html.Ul([
                                   html.Li([
                                    html.B(" Emission Value "),
                                    "- Mesured in metric tons of CO2 equivalent, with the different types being total reported, carbon dioxide, methane, nitrous oxide, and sulfur hexafluoride."]), 
                                   html.Li([
                                    html.B(" Facility Name "),
                                   "- Selecting from the unique facility names given to the facility; each bubble is a facility"])
                               ])])
                    ]
                )
            , className = 'card text-white bg-primary mb-3', style = {'width': '20%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-top': '20px', })
        ]),
        dcc.Tab(
            label='About', # fourth tab about the data 
            value='tab-4',
            className='dbc',
            children=[

                dcc.Markdown(""" 
                    # ***Data background information***

                    #### ***Where the data came from:***
                    This dataset was pulled from the EPA's Greenhouse Gas Reporting Program (or GHGRP) for the reporting year of 2022. This program collects data from approximately 8,000 facilities that are required to report their emissions annually; these facilities are typically large GHG emission sources, fuel and industrial gas suppliers, and carbon dioxide injection sites. The data is compiled every April and made available to the public the following October after a thorough multi-step verification process, where the EPA ensures that the reported data is accurate, complete, and consistent. 

                    #### ***Original purpose of data:***
                    The data was originally used to keep these 8,000 high-emitting facilities in check through annual emissions reporting. Additionally, the EPA allowed this data to be public information for other businesses to track and compare different facilities' greenhouse gas emission as to find ways to cut down their own emissions, minimize wasted resources, and (subsequently) save money. Moreover, the data was also created for local governments to find high-emitting facilities in their area to develop effective climate policies. 

                    #### ***Data overview:***
                    The data contains report for direct emitting facilities (Scope 1) and upstream suppliers in 2022. Scope 1 emissions are reported at the individual facility level, though parent company information is also collected. Regarding upstream suppliers, they report the amount of carbon dioxide equivalent (CO2e) that would be hypothetically released if their products were released, combusted, or oxidized; these emissions are reported at the corporate level and fall under Scope 3 emissions. The data collected by the GHGRP cover approximately 85-90% of US greenhouse gas emissions. However, the GHGRP does not include emissions from agriculture, emission sources that have annual emissions of less than 25,000 metric tons of CO2e, sinks of greenhouse gases, and Scope 2 emissions (electricty purchases or indirect emissions from energy consumption). Facilities that are required to report to the GHGRP include facilities that have GHG emissions which exceed 25,0000 metric tons of CO2e per year, contain supplies of products that would result in over 25,000 metric tons of CO2e if products were released, and/or receive 25,0000 metric tons or more of CO2 for underground injection.)
                    """
        ), 
                html.A( # git hub icon for repo link 
                    DashIconify(icon="ion:logo-github", width=30), 
                    href = "https://github.com/sek2dcs/DS4003", 
                    target = "_blank")
    ]
)
    ])
], className = 'dbc')

@app.callback(
    Output('starburst-chart', 'figure'),
    Input('dd-state', 'value')
)
def update_starburst_chart(selected_state):
    # replacing NAs with zeros to make the starburst chart
    filtered_df = data.fillna(0)
    # filtering the data to only selected state 
    filtered_df = data[(data['State'] == selected_state) & (data['Total reported emissions'] != 0)]
    total_emissions_per_facility = filtered_df.groupby(['Name of industry', 'Facility Name'])['Total reported emissions'].sum().reset_index()

# selecting top ten emitting facilities for each industry type
    top_ten_emitting_facilities = (total_emissions_per_facility.groupby('Name of industry') # grouping by the industry name 
                               .apply(lambda x: x.nlargest(10, 'Total reported emissions')) # sorting in descending order then selects the top 10 largest 
                               .reset_index(drop=True))

# creating the sunburst plot using the filtered df with top ten emitting facilities
    fig = px.sunburst(top_ten_emitting_facilities, 
                    path=['Name of industry', 'Facility Name'], 
                    template = 'minty',
                    values='Total reported emissions',
                    color='Total reported emissions',
                    color_continuous_midpoint=np.average(filtered_df['Total reported emissions'], 
                                                            weights=filtered_df['Total reported emissions'])) # coloring by the avg of total reported emissions to help center the color scale
    fig.update_traces(hovertemplate='Facility Name: %{label} <br> Total reported emissions: %{value} mt CO2e') # customizing the hover text 
    fig.update_layout(title=dict(text="Facility Emissions by State and Industry Type", font=dict(size=30)) # customizing the graph title 
)
    
    return fig

# making a callback so the city dropdown will change to only the cities in the user selected state 
@app.callback(
    Output('dropdown-city', 'options'),
    Input('dropdown-state', 'value')
)
def update_city_options(selected_state):
    cities_in_state = data[data['State'] == selected_state]['City'].unique()
    city_options = [{'label': city, 'value': city} for city in cities_in_state]
    
    return city_options


@app.callback(
    Output('bar-graph', 'figure'), 
    Input('dropdown-state', 'value'),
    Input('dropdown-city', 'value')
)
def update_bar_graph(selected_state, selected_cities): 
    # converting selected cities to list to make code work 
    selected_cities = [selected_cities] if isinstance(selected_cities, str) else selected_cities
    # making filtered df of the state & cities that user selected 
    filtered_df = data[(data['State'] == selected_state) & (data['City'].isin(selected_cities))]
    # melting the above df to get the columns to be reorganized to emission types as one column 
    filt_filt_df = pd.melt(filtered_df, id_vars=['Facility Name', 'City'], value_vars=['CO2 emissions', 'Methane (CH4) emissions', 'Nitrous Oxide (N2O) emissions', 'SF6 emissions'], var_name='Emission type')
    # making a max value for the y axis range 
    max_value = filt_filt_df['value'].max() * 1.1
    # making bar graph 
    fig = px.bar(filt_filt_df, x="Facility Name", y="value", color="Emission type")

    fig.update_layout(
        legend=dict( # horizontal legend for cleaner look & editing to make it cleaner 
            orientation="h",
            itemwidth=70,
            yanchor="bottom",
            y= 0.95,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            title="Emission Value",
            range=[0, max_value]
        )
    ) 

    fig.update_traces(hovertemplate='Facility Name: %{label} <br> Total reported emissions: %{value} mt CO2e') # customizing the hover text 
    fig.update_layout(title=dict(text="Facility Emissions based on City and State", font=dict(size=20))) # and doing title 
    return fig

# defining callback to update bubble map 
@app.callback(
    Output('bubble-map', 'figure'),
    Input('map-radio-button', 'value')
)
def update_bubble_map(selected_emissions):   

# converting emissions values to numeric just in case 
    data[selected_emissions] = pd.to_numeric(data[selected_emissions], errors='coerce')

# filtering out any NAs
    data_filtered = data.dropna(subset=[selected_emissions, 'Latitude', 'Longitude'])

# getting scale for bubbles 
    scale = 5000

# colors for the quartiles 
    colors = ["#78c2ad ", "#f3969a", "#6cc3d5", "#ffce67", "#ff7851"]

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
            locationmode='USA-states', # so dash knows that the longs & lats are in the US 
            lon=data_bub['Longitude'],
            lat=data_bub['Latitude'],
            text=data_bub['Facility Name'] + '<br>' + selected_emissions + ': ' + (data_bub[selected_emissions] / 1000).astype(str) + ' thousand',  # for further descrip when user hovers
            marker=dict(
                size=data_bub[selected_emissions] / scale, # size based on emission amount 
                color=data_bub['color'],
                line_color='rgb(40,40,40)',
                line_width=0.5,
                sizemode='area'
            ),
            name='{0} - {1}'.format(lim[0], lim[1]), # gives the exact high & low limits for each of the categories in the legend 
            showlegend=True
        ))
        
    tickvals = [(max(bin_edges) - min(bin_edges)) / num_categories * i + min(bin_edges) for i in    # defining values for each color in legend 
                range(num_categories + 1)]
    ticktext = [f'{tickvals[i]:.2f} - {tickvals[i + 1]:.2f}' for i in range(num_categories)]  # defining labels for each color in legend 

    fig.update_layout(
        title_text='Emissions of each facility in the USA map<br>(Click legend to toggle traces)',
        title_font = dict(size = 20),
        showlegend=True,
        geo=dict(
            scope='usa', # to get USA on map 
            landcolor='rgb(217, 217, 217)',
        ),
        coloraxis_colorbar=dict(  # specifying color bar to help with graph 
            tickvals=tickvals,
            ticktext=ticktext
        )
    )

    return fig


# running the app
if __name__ == '__main__':
    app.run_server(jupyter_mode='tab', debug=True)
