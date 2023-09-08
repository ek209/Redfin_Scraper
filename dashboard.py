from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
from database import * 
import sqlite3
import datetime

app = Dash(__name__, suppress_callback_exceptions=True)

con = sqlite3.connect('rf_data.db')
data = pd.read_sql(('SELECT *  FROM sold_properties'), con)
data['sold_date'] = pd.to_datetime(data['sold_date'], format="%B-%d-%Y")
data['year'] = data['sold_date'].dt.year
data['day'] = data['sold_date'].dt.day
data['month'] = data['sold_date'].dt.month
con.close()

app.layout = html.Div([
    (html.H1(f'Data from: {datetime.date.today()}')),
    dcc.Tabs(id='tabs-example-1', value='tab-1', children=[
        dcc.Tab(label='Overall', value='tab-1'),
        dcc.Tab(label='State', value='tab-2'),
        dcc.Tab(label='Postal code', value='tab-3'),
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
            html.H2('Overall Data')
            ]
        ) 
    
    elif tab == 'tab-2':
        return html.Div([
            html.H2('State Data'),
            dcc.Input(id="state-name", type='text', placeholder="State Abbreviation", value="WA", debounce=True),
            dcc.Graph(id="state-house-breakdown"),
        ])
    elif tab == 'tab-3':
        return html.Div(
        [html.H2('Postal Code Data'),
        dcc.Input(id="postal-code", type='number', placeholder="Postal code", value=2128, debounce=True),
        
        dcc.Graph(id="zip-house-breakdown"),
        dcc.Graph(id='zip-proptype-price-average'),
        dcc.Graph(id='zip-proptype-beds-average'),
        dcc.Graph(id='zip-proptype-baths-average'),
        dcc.Graph(id='zip-sales-by-year'),
        dcc.Dropdown(id='prop-year',
                     options=[2023, 2022, 2021, 2020, 2019, 2018],
                     value=2023),
        dcc.Graph(id='zip-prop-type-sold-per-year'),
        dcc.Graph(id='zip-prop-price-by-year')
        
        ])

@callback(
    Output('zip-house-breakdown', 'figure'),
    Output('zip-proptype-price-average', 'figure'),
    Output('zip-proptype-beds-average', 'figure'),
    Output('zip-proptype-baths-average', 'figure'),
    Output('zip-sales-by-year', 'figure'),
    Output('zip-prop-type-sold-per-year', 'figure'),
    Output('zip-prop-price-by-year', 'figure'),
    Input('postal-code', 'value'),
    Input('prop-year', 'value')
)
def zip_div(postal_code, prop_year):
    zip_df = data.query('postal_code == @postal_code')
    prop_type_fig = px.pie(zip_df, names=zip_df['property_type'])

    zip_avg = zip_df[['property_type', 'price', 'beds', 'baths']].groupby('property_type', as_index=False).mean(True)
    prop_price_avg_fig = px.bar(zip_avg,x=zip_avg.get('property_type'),y=zip_avg.get('price'))
    zip_avg = zip_df[['property_type', 'beds']].groupby('property_type', as_index=False).mean(True).dropna()
    prop_bed_avg_fig = px.bar(zip_avg,x=zip_avg.get('property_type'),y=zip_avg.get('beds'))
    zip_avg = zip_df[['property_type', 'baths']].groupby('property_type', as_index=False).mean(True).dropna()
    prop_bath_avg_fig = px.bar(zip_avg,x=zip_avg.get('property_type'),y=zip_avg.get('baths'))
    data_by_year = zip_df.query('year == @prop_year')
    prop_price_by_year = data_by_year[['property_type', 'price']].groupby('property_type', as_index=False).mean(True)
    zip_prop_price_by_year_bar = px.bar(prop_price_by_year, x=prop_price_by_year.get('property_type'), y=prop_price_by_year.get('price'))
    prop_to_year = data_by_year['property_type'].value_counts()
    zip_prop_type_sold_by_year = px.bar(prop_to_year, x=prop_to_year.get('property_type'), y=prop_to_year.get('count'))
    zip_count_by_year = zip_df['year'].value_counts()
    zip_sales_by_year = px.bar(zip_count_by_year, x=zip_count_by_year.get('year'), y=zip_count_by_year.get('count'))
    return prop_type_fig, prop_price_avg_fig, prop_bed_avg_fig, prop_bath_avg_fig, zip_sales_by_year, zip_prop_type_sold_by_year, zip_prop_price_by_year_bar

@callback(
    Output('state-house-breakdown', 'figure'),
    Input('state-name', 'value')
)
def state_div(state_name):
    con = sqlite3.connect('rf_data.db')
    state_data = pd.query('state_prov == @state_name')
    state_prop_type_fig = px.pie(state_data, names=state_data['property_type'])
    con.close()
    return state_prop_type_fig



if __name__ == '__main__':
    app.run(debug=True)