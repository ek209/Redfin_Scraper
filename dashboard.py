from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
from database import * 
import sqlite3
import datetime

app = Dash(__name__, suppress_callback_exceptions=True)
GRAPHS = 12
CITY_GRAPHS = [f"city-graph-{num}" for num in range(0,GRAPHS)]
STATE_GRAPHS = [f"state-graph-{num}" for num in range(0,GRAPHS)]
ZIP_GRAPHS = [f"zip-graph-{num}" for num in range(0,GRAPHS)]
LOCATION_GRAPHS = [f"location-graph-{num}" for num in range(0, GRAPHS)]

app.layout = html.Div([
    (html.H1(f'Data from: {datetime.date.today()}')),
    dcc.Tabs(id='tabs-example-1', value='tab-3', children=[
        dcc.Tab(label='City', value='tab-1'),
        dcc.Tab(label='State', value='tab-2'),
        dcc.Tab(label='Postal code', value='tab-3'),
        dcc.Tab(label='Market', value='tab-4')
    ]),
    html.Div(id='tabs-example-content-1')
])



'''dcc.Dropdown(id='zip-month', 
                        options=[
       {'label': 'January', 'value': '1'},
       {'label': 'February', 'value': '2'},
       {'label': 'March', 'value': '3'},
       {'label': 'April', 'value': '4'},
       {'label': 'May', 'value': '5'},
       {'label': 'June', 'value': '6'},
       {'label': 'July', 'value': '7'},
       {'label': 'August', 'value': '8'},
       {'label': 'September', 'value': '9'},
       {'label': 'October', 'value': '10'},
       {'label': 'November', 'value': '11'},
       {'label': 'December', 'value': '12'}
   ],
   value='1'
)'''

@callback(
    Output('tabs-example-content-1', 'children'),
    Input('tabs-example-1', 'value')
)
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H2('City Data'),
            dcc.Input(id="city-name", type='text', placeholder="City Name", value="Glassell Park", debounce=True),
            dcc.Input(id="state-abbreviation-city", type='text', placeholder="State Abbreviation", value="CA", debounce=True),
            html.Div([dcc.Graph(id) for id in CITY_GRAPHS]),
            ])
    
    elif tab == 'tab-2':
        return html.Div([
            html.H2('State Data'),
            dcc.Input(id="state-name", type='text', placeholder="State Abbreviation", value="WA", debounce=True),
            html.Div([dcc.Graph(id) for id in STATE_GRAPHS]),
            ])
    
    elif tab == 'tab-3':
        return html.Div(
        [html.H2('Postal Code Data'),
        dcc.Input(id="postal-code", type='number', placeholder="Postal code", value=2128, debounce=True),
        html.Div([dcc.Graph(id) for id in ZIP_GRAPHS]),
        dcc.Dropdown(id='prop-year',
                     options=[2023, 2022, 2021, 2020, 2019, 2018],
                     value=2023),
        dcc.Graph(id='zip-sales-by-year'),
        dcc.Graph(id='zip-prop-type-sold-per-year'),
        dcc.Graph(id='zip-prop-price-by-year')        
        ])
    elif tab == "tab-4":
        return html.Div([
        html.H2('Location-Data'),
        dcc.Input(id="location-name", type='text', placeholder="Market", value="North Tacoma", debounce=True),
        html.Div([dcc.Graph(id) for id in LOCATION_GRAPHS]),
        ])


@callback([Output(id, 'figure') for id in ZIP_GRAPHS],
    Output('zip-sales-by-year', 'figure'),
    Output('zip-prop-type-sold-per-year', 'figure'),
    Output('zip-prop-price-by-year', 'figure'),
    Input('postal-code', 'value'),
    Input('prop-year', 'value')
)
def zip_div(postal_code, prop_year):
    con = sqlite3.connect('rf_data.db')
    zip_df = pd.read_sql(('SELECT *  FROM sold_properties WHERE postal_code LIKE (?)'), con, params=(postal_code,))
    con.close()
    graphs = compile_graphs(zip_df, postal_code)

    data_by_year = zip_df.query('sold_year == @prop_year')
    prop_price_by_year = data_by_year[['property_type', 'price']].groupby('property_type', as_index=False).mean(True)
    zip_prop_price_by_year_bar = px.bar(prop_price_by_year, x=prop_price_by_year.get('property_type'), y=prop_price_by_year.get('price'))
    prop_to_year = data_by_year['property_type'].value_counts()
    zip_prop_type_sold_by_year = px.bar(prop_to_year, x=prop_to_year.get('property_type'), y=prop_to_year.get('count'))
    zip_count_by_year = zip_df['sold_year'].value_counts()
    zip_sales_by_year = px.bar(zip_count_by_year, x=zip_count_by_year.get('year'), y=zip_count_by_year.get('count'))
    graphs = graphs + [zip_sales_by_year, zip_prop_type_sold_by_year, zip_prop_price_by_year_bar]
    return tuple(graphs)

@callback(
    [Output(id, 'figure') for id in STATE_GRAPHS],
    Input('state-name', 'value')
)
def state_div(state_name):
    con = sqlite3.connect('rf_data.db')
    state_df = pd.read_sql(('SELECT *  FROM sold_properties WHERE state_prov = (?)'), con, params=(state_name,))
    con.close()
    graphs = compile_graphs(state_df, state_name)
    return tuple(graphs)

@callback([Output(id, 'figure') for id in CITY_GRAPHS],
    Input('city-name', 'value'),
    Input('state-abbreviation-city', 'value')
)
def city_div(city_name, state_name):
    con = sqlite3.connect('rf_data.db')
    city_df = pd.read_sql(('SELECT *  FROM sold_properties WHERE state_prov = (?) AND city = (?)'), con, params=(state_name, city_name))
    con.close()
    graphs = compile_graphs(city_df, city_name)
    return tuple(graphs)


@callback(
    [Output(id, 'figure') for id in LOCATION_GRAPHS],
    Input('location-name', 'value')
)
def market_div(market_name):
    con = sqlite3.connect('rf_data.db')
    market_df = pd.read_sql(('SELECT *  FROM sold_properties WHERE location = (?)'), con, params=(market_name,))
    con.close()
    graphs = compile_graphs(market_df, market_name)
    return tuple(graphs)

def prop_type_bar_graphs(dataframe, location):
    column_list = ['price', 'beds', 'baths', 'sqft', 'lot_size', 'price_per_sqft']
    bar_figure_list = [bar_property_price_v_avg_var(dataframe, location, column) for column in column_list]
    bar_figure_list.append(bar_average_year_built_by_prop_type(dataframe, location))
    return bar_figure_list

def prop_type_scatter_graphs(dataframe, location):
    column_list = ["sqft", "lot_size"]
    scatter_figure_list = [scatter_price_v_var_by_prop_type(dataframe, location, column) for column in column_list]
    return scatter_figure_list

def prop_type_line_graphs(dataframe, location):
    column_list = ["price", "price_per_sqft"]
    line_figure_list = [line_avg_var_by_prop_type_by_year(dataframe, location, column) for column in column_list]
    return line_figure_list

def compile_graphs(dataframe, location):
    prop_type_pie_list = [pie_property_data(dataframe, location)]
    bar_figure_list = prop_type_bar_graphs(dataframe, location)
    scatter_figure_list = prop_type_scatter_graphs(dataframe, location)
    line_figure_list = prop_type_line_graphs(dataframe, location)
    graphs = prop_type_pie_list + bar_figure_list + scatter_figure_list + line_figure_list
    return graphs

def pie_property_data(dataframe, location):
    """Takes dataframe and creates pie chart based 
    on property_type distribution

    Args:
        dataframe (dataframe): Dataframe with property_type data to chart.

    Returns:
        figure: Plotly express pie chart
    """
    if dataframe.shape[0] == 0:
        return None
    else:
        return px.pie(dataframe.dropna(), 
                    names=dataframe['property_type'], 
                    title=f"Property type breakdown for {location}")


def line_avg_var_by_prop_type_by_year(dataframe, location, secondary_column):
    dataframe = dataframe[~dataframe['property_type'].isin(['Unknown', 'Other', 'Timeshare'])]
    df = dataframe[['property_type', secondary_column, 'sold_year']]
    if df.shape[0] == 0:
        return None
    else: 
        df = df.groupby(['sold_year', 'property_type'], as_index=False).mean(True)  
        return px.line(df,
                    x=df.get('sold_year'),
                    y=df.get(secondary_column),
                    color="property_type",
                    title=f"Average {secondary_column} by property type per year for {location}",
                    labels={secondary_column : f"{secondary_column}",
                            "sold_year" : "Year",
                            "property_type" : "Property Type"})


def scatter_price_v_var_by_prop_type(dataframe, location, secondary_column):
    dataframe = dataframe[~dataframe['property_type'].isin(['Unknown', 'Other', 'Timeshare'])]
    df = dataframe[['property_type', secondary_column, 'price']]
    if df.shape[0] == 0:
        return None
    else:    
        return px.scatter(df,
                    x=df.get(secondary_column),
                    y=df.get('price'),
                    color="property_type",
                    trendline='ols',
                    title=f"Price vs {secondary_column} by property type for {location}",
                    labels={secondary_column : f"{secondary_column}",
                            "Price" : "Price"})

def bar_property_price_v_avg_var(dataframe, location, secondary_column):
    """Takes dataframe and creates bar chart based 
    on property_type distribution and average of var secondary column

    Args:
        dataframe (dataframe): Dataframe with property_type and price data to chart.

    Returns:
        figure: Plotly express bar chart
    """
    dataframe[~dataframe['property_type'].isin(['Unknown', 'Other', 'Timeshare'])]
    avg_price = dataframe[['property_type', secondary_column]]
    if avg_price.shape[0] == 0:
        return None
    else:
        avg_price = avg_price.groupby('property_type', as_index=False).mean(True)
        return px.bar(avg_price,
                      x=avg_price.get('property_type'),
                      y=avg_price.get(secondary_column),
                      color="property_type",
                      title=f"Average {secondary_column} by property type {location}",
                      labels={secondary_column : f"Average {secondary_column}",
                              "property_type" : "Property Type"})

def bar_average_year_built_by_prop_type(dataframe, location):
    seconday_column = 'year_built'
    dataframe[~dataframe['property_type'].isin(['Unknown', 'Other', 'Timeshare'])]

    avg = dataframe[['property_type', seconday_column]].groupby('property_type', as_index=False).mean(True).dropna()
    if avg.shape[0] == 0:
        return None
    else:    
        return px.bar(avg,
                    x=avg.get('property_type'),
                    y=avg.get(seconday_column),
                    color="property_type",
                    title=f"Average year built by property type for {location}",
                    range_y=[1900, datetime.date.today().year],
                    labels={seconday_column : "Average Year Built",
                            "property_type" : "Property Type"})
    
if __name__ == '__main__':
    app.run(debug=True)