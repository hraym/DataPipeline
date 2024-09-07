import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import re

styles = {
    'body': {
        'fontFamily': "'Roboto', 'Helvetica Neue', Arial, sans-serif",
        'backgroundColor': '#f5f7fa',
        'color': '#2c3e50',
        'lineHeight': '1.6'
    },
    'container': {
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': '10px'
    },
    'h1': {
        'fontSize': '32px',
        'fontWeight': '300',
        'color': '#34495e',
        'marginBottom': '10px',
        'textAlign': 'center'
    },
    'dropdown_container': {
        'backgroundColor': '#ffffff',
        'borderRadius': '8px',
        'boxShadow': '0 2px 10px rgba(0, 0, 0, 0.1)',
        'padding': '10px',
        'marginBottom': '10px'
    },
    'dropdown': {
        'borderColor': '#bdc3c7',
        'borderRadius': '4px'
    },
    'graph_container': {
        'backgroundColor': '#ffffff',
        'borderRadius': '8px',
        'boxShadow': '0 2px 10px rgba(0, 0, 0, 0.1)',
        'padding': '10px',
        'marginBottom': '10px'
    }
}

def truncate_indicator_name(name):
    return name.split(' (')[0]

def extract_axis_title(indicator_name):
    match = re.search(r'\(((?:[^()]*|\([^()]*\))*)\)$', indicator_name)
    if match:
        return match.group(1)
    else:
        return indicator_name

def create_color_map(countries):
    color_scale = px.colors.qualitative.Plotly
    return {country: color_scale[i % len(color_scale)] for i, country in enumerate(countries)}

def create_dashboard(data, indicators_standard, indicator_mapping):
    app = dash.Dash(__name__)

    if not data:
        app.layout = html.Div("No data available")
        return app

    first_df = next(iter(data.values()))
    countries = sorted(first_df.index.get_level_values('country_name').unique().tolist())
    color_map = create_color_map(countries)

    # Get the indicator names from the data
    indicator_names = {code: df['indicator_name'].iloc[0] for code, df in data.items()}

    global_available_indicators = {category: [ind for ind in indicators if ind in data]
                                   for category, indicators in indicators_standard.items()}
    available_categories = [k for k, v in global_available_indicators.items() if v]

    app.layout = html.Div([
        html.Div([
            html.H1("Sustainable Development Goals Dashboard", style=styles['h1']),
            
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='category-dropdown',
                        options=[{'label': k, 'value': k} for k in available_categories],
                        value=available_categories[0] if available_categories else None,
                        style=styles['dropdown']
                    )
                ], style={'width': '26%', 'display': 'inline-block', 'marginRight': '1%'}),
                
                html.Div([
                    dcc.Dropdown(
                        id='indicator-dropdown',
                        style=styles['dropdown']
                    )
                ], style={'width': '40%', 'display': 'inline-block', 'marginRight': '1%'}),
                
                html.Div([
                    dcc.Dropdown(
                        id='country-dropdown',
                        options=[{'label': country, 'value': country} for country in countries],
                        value=countries[:5] if len(countries) >= 5 else countries,
                        multi=True,
                        style=styles['dropdown'],
                        className='dropdown'
                    )
                ], style={'width': '32%', 'display': 'inline-block'})
            ], style=styles['dropdown_container']),
            
            html.Div([
                dcc.Graph(id='main-graph')
            ], style=styles['graph_container']),
            
            html.Div([
                html.Div([
                    dcc.Graph(id='bar-chart')
                ], style={'width': '49%', 'display': 'inline-block', 'marginRight': '2%'}),
                
                html.Div([
                    dcc.Graph(id='scatter-plot')
                ], style={'width': '49%', 'display': 'inline-block'})
            ], style=styles['graph_container'])
        ], style=styles['container'])
    ], style=styles['body'])

    @app.callback(
        Output('indicator-dropdown', 'options'),
        Output('indicator-dropdown', 'value'),
        Input('category-dropdown', 'value')
    )
    def update_indicator_dropdown(selected_category):
        if not selected_category:
            return [], None
        options = [{'label': indicator_names.get(indicator, indicator), 
                    'value': indicator} 
                   for indicator in global_available_indicators[selected_category]]
        return options, options[0]['value'] if options else None

    @app.callback(
        Output('main-graph', 'figure'),
        Input('indicator-dropdown', 'value'),
        Input('country-dropdown', 'value')
    )
    def update_main_graph(selected_indicator, selected_countries):
        if not selected_indicator or not selected_countries:
            return {}
        df = data[selected_indicator]
        df_filtered = df.loc[df.index.get_level_values('country_name').isin(selected_countries)]
        df_filtered = df_filtered.reset_index()
        
        # Check for empty DataFrame
        if df_filtered.empty:
            print("Warning: Filtered DataFrame is empty")
            return {}
        
        # Check for required columns
        required_columns = ['year', 'value', 'country_name']
        missing_columns = [col for col in required_columns if col not in df_filtered.columns]
        if missing_columns:
            print(f"Warning: Missing columns: {missing_columns}")
            return {}
        
        try:
            indicator_name = indicator_names.get(selected_indicator, selected_indicator)
            fig = px.line(df_filtered, x='year', y='value', color='country_name',
                          color_discrete_map=color_map,
                          title=f'{indicator_name}')
            fig.update_layout(yaxis_title=indicator_name, xaxis_title="Year", legend_title_text='Country')
            return update_graph_layout(fig)
        except Exception as e:
            print(f"Error creating figure: {str(e)}")
            return {}
    
    @app.callback(
        Output('bar-chart', 'figure'),
        Input('indicator-dropdown', 'value'),
        Input('country-dropdown', 'value')
    )
    def update_bar_chart(selected_indicator, selected_countries):
        if not selected_indicator or not selected_countries:
            return {}
        df = data[selected_indicator]
        df_filtered = df.loc[df.index.get_level_values('country_name').isin(selected_countries)]
        latest_year = df_filtered.index.get_level_values('year').max()
        df_latest = df_filtered.loc[df_filtered.index.get_level_values('year') == latest_year]
        df_latest = df_latest.reset_index()
        indicator_name = indicator_names.get(selected_indicator, selected_indicator)
        fig = px.bar(df_latest, x='country_name', y='value',
                     color='country_name', color_discrete_map=color_map,
                     title=f'{indicator_name} - Latest Year ({latest_year})')
        fig.update_layout(yaxis_title=indicator_name, xaxis_title="Country", showlegend=False)
        return update_graph_layout(fig)
    
    @app.callback(
        Output('scatter-plot', 'figure'),
        Input('category-dropdown', 'value'),
        Input('country-dropdown', 'value')
    )
    def update_scatter_plot(selected_category, selected_countries):
        if not selected_category or not selected_countries:
            return {}
        
        category_indicators = [ind for ind in global_available_indicators[selected_category] if ind in data]
        
        if len(category_indicators) < 2:
            return {}
        
        indicator1, indicator2 = category_indicators[:2]
        df1 = data[indicator1].loc[data[indicator1].index.get_level_values('country_name').isin(selected_countries)]
        df2 = data[indicator2].loc[data[indicator2].index.get_level_values('country_name').isin(selected_countries)]
        
        df_merged = pd.merge(df1.reset_index(), df2.reset_index(), on=['country_name', 'country_code', 'year'])
        
        latest_year = df_merged['year'].max()
        df_latest = df_merged[df_merged['year'] == latest_year]
        
        indicator_name1 = indicator_names.get(indicator1, indicator1)
        indicator_name2 = indicator_names.get(indicator2, indicator2)
        
        fig = px.scatter(df_latest, x='value_x', y='value_y', 
                         color='country_name', color_discrete_map=color_map,
                         hover_name='country_name',
                         labels={'value_x': indicator_name1, 'value_y': indicator_name2},
                         title=f'{indicator_name1} vs {indicator_name2} - {latest_year}')
        
        fig.update_traces(marker=dict(size=12))  # Increase marker size
        fig.update_layout(showlegend=False)  # Remove legend
        
        return update_graph_layout(fig)

    return app

def update_graph_layout(fig):
    fig.update_layout(
        font=dict(family=styles['body']['fontFamily']),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=20, color=styles['h1']['color']),
        legend_title_font=dict(size=14),
        legend_font=dict(size=12),
        xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12))
    )
    return fig

def run_dashboard(data, indicators_standard, indicator_mapping):
    app = create_dashboard(data, indicators_standard, indicator_mapping)
    app.run_server(debug=True)