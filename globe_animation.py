import plotly.graph_objects as go
import numpy as np
from dash import Dash, dcc, html, Input, Output, clientside_callback
import geopandas as gpd
import json

# Constants
GLOBE_HEIGHT = 600
GLOBE_WIDTH = 600
BACKGROUND_COLOR = "aliceblue"

# Load country polygons
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Generate sample poverty data for each country
world['poverty_level'] = np.random.uniform(0, 100, len(world))

def create_globe():
    """
    Create a 3D globe visualization with poverty data.
    
    Returns:
        plotly.graph_objects.Figure: The globe figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Choropleth(
        locations=world['iso_a3'],
        z=world['poverty_level'],
        text=world['name'],
        colorscale='Viridis',
        autocolorscale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        showscale=False, # This hides the colorbar
        #colorbar_title='Poverty Level'
    ))
    
    fig.update_geos(
        projection_type="orthographic",
        showcoastlines=True, coastlinecolor="Black",
        showland=True, landcolor="White",
        showocean=True, oceancolor="LightBlue",
        showframe=False,
        lataxis_range=[-90,90],
        lonaxis_range=[-180,180],
        center=dict(lon=20, lat=0)  # Add this line to shift the center
    )
    
    fig.update_layout(
        title_text='Global Poverty Levels',
        height=GLOBE_HEIGHT,
        width=GLOBE_WIDTH,
        margin={"r":50,"t":0,"l":50,"b":0},
        paper_bgcolor=BACKGROUND_COLOR,
        autosize=True, 
    )
    
    return fig

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(
        id='globe-visualization',
        figure=create_globe(),
        config={
            'scrollZoom': False,
            'displayModeBar': False,
        }
    ),
    dcc.Store(id='view-state', data=json.dumps({'rotation': {'lon': 0, 'lat': 0}, 'velocity': {'lon': 0, 'lat': 0}})),
], style={'backgroundColor': BACKGROUND_COLOR, 'padding': '0px'})

clientside_callback(
    """
    function(n_intervals, stored_state) {
        const state = JSON.parse(stored_state);
        const friction = 1.5;  // Adjust this value to change how quickly the globe slows down
        
        // Apply inertia
        state.rotation.lon += state.velocity.lon;
        state.rotation.lat += state.velocity.lat;
        
        // Apply friction
        state.velocity.lon *= friction;
        state.velocity.lat *= friction;
        
        // Normalize rotations
        state.rotation.lon = (state.rotation.lon + 180) % 360 - 180;
        state.rotation.lat = Math.max(-90, Math.min(90, state.rotation.lat));
        
        // Update the globe
        Plotly.relayout('globe-visualization', {
            'geo.projection.rotation': state.rotation
        });
        
        return JSON.stringify(state);
    }
    """,
    Output('view-state', 'data'),
    Input('globe-visualization', 'n_intervals'),
    Input('view-state', 'data'),
)

app.clientside_callback(
    """
    function(relayoutData, clickData, stored_state) {
        const state = JSON.parse(stored_state);
        let isDragging = false;
        let lastX, lastY;

        const globe = document.getElementById('globe-visualization');

        function handleMouseDown(e) {
            isDragging = true;
            lastX = e.clientX;
            lastY = e.clientY;
        }

        function handleMouseMove(e) {
            if (!isDragging) return;
            
            const deltaX = e.clientX - lastX;
            const deltaY = e.clientY - lastY;
            
            state.rotation.lon -= deltaX * 0.2;
            state.rotation.lat += deltaY * 0.2;
            
            state.velocity.lon = -deltaX * 0.2;
            state.velocity.lat = deltaY * 0.2;
            
            lastX = e.clientX;
            lastY = e.clientY;
            
            Plotly.relayout('globe-visualization', {
                'geo.projection.rotation': state.rotation
            });
        }

        function handleMouseUp() {
            isDragging = false;
        }

        globe.removeEventListener('mousedown', handleMouseDown);
        globe.removeEventListener('mousemove', handleMouseMove);
        globe.removeEventListener('mouseup', handleMouseUp);
        globe.removeEventListener('mouseleave', handleMouseUp);

        globe.addEventListener('mousedown', handleMouseDown);
        globe.addEventListener('mousemove', handleMouseMove);
        globe.addEventListener('mouseup', handleMouseUp);
        globe.addEventListener('mouseleave', handleMouseUp);

        // Start the animation loop
        if (!globe.animating) {
            globe.animating = true;
            function animate() {
                globe.dispatchEvent(new CustomEvent('interval'));
                requestAnimationFrame(animate);
            }
            requestAnimationFrame(animate);
        }

        return JSON.stringify(state);
    }
    """,
    Output('view-state', 'data'),
    Input('globe-visualization', 'relayoutData'),
    Input('globe-visualization', 'clickData'),
    Input('view-state', 'data'),
)

if __name__ == '__main__':
    app.run_server(debug=True)