from dash import Dash, html, dcc, Input, Output, State, MATCH, ALL, Patch
import dash # Needed of callback_context
import os
import webbrowser
from figures import *
import plotly.express as px
 
# This function arranges the plots in an html layout
def draw_pane(topbar_tab, decades_list, current_decade, layout="grid", bin_size="5 months", selected_genres=None):
    if topbar_tab == "topic-1":
        content = draw_figure(topbar_tab, decades_list, current_decade, selected_genres=selected_genres)
        filename = current_decade + ".png"
        pane = html.Div(
            style={
                "height": "100%", "width": "100%",
                "backgroundImage": f"linear-gradient(to right, #1a1c2c 50%, transparent 50%), url('/assets/{filename}')", # Darker Discord-like blue
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "backgroundRepeat": "no-repeat",
                "display": "flex"
            },
            children=[content]
        )
    elif topbar_tab == "topic-3":
        if layout == "grid":
            # Get available songs for the selected decade
            available_songs = get_songs_for_decade(current_decade)
            song_options = [{"label": song_name, "value": track_id} for song_name, track_id in available_songs]
            
            pane = html.Div(
                style={
                    "padding": "30px",
                    "display": "grid",
                    "gridTemplateColumns": "1fr  1fr",  # Columns 1 and 3 are wider
                    "gridTemplateRows": "1fr 1fr auto",  # First row is fixed, second row fills available space
                    "gridGap": "30px",
                    "background": "rgba(0,0,0,0)"  # Transparent background for the grid
                },
                children=[
                    html.Div(
                        dcc.Dropdown(
                            id="song-1-dropdown",
                            options=song_options,
                            value=available_songs[0][1] if available_songs else None,
                            style={"color": "black"}
                        ),
                        style={"background": "rgba(0,0,0,0)", "padding": "20px"}
                    ),
                    html.Div(
                        html.Iframe(
                        id="player-1",  # We need an ID to target this with a callback
                        src="https://open.spotify.com/embed/track/2plbrEY59IikOBgBGLjaoe", # Initial song (some bruno mars bs)
                        style={
                            "height": "80px", # Spotify compact players look good at 80px or 152px
                            "width": "100%", 
                            "border": "0",    # Removes the ugly default border
                            "borderRadius": "12px" # makes it look modern
                            }
                            )

                    ),
                    html.Div(
                        dcc.Dropdown(
                            id="song-2-dropdown",
                            options=song_options,
                            value=available_songs[1][1] if len(available_songs) > 1 else available_songs[0][1],
                            style={"color": "black"}
                        ),
                        style={"background": "rgba(0,0,0,0)", "padding": "20px"}
                    ),
                    html.Div(
                        html.Iframe(
                        id="player-2",  # We need an ID to target this with a callback
                        src="https://open.spotify.com/embed/track/2plbrEY59IikOBgBGLjaoe", # Initial song (some bruno mars bs)
                        style={
                            "height": "80px", # Spotify compact players look good at 80px or 152px
                            "width": "100%", 
                            "border": "0",    # Removes the ugly default border
                            "borderRadius": "12px" # makes it look modern
                            }
                            )
                    ),
                    html.Div(
                        dcc.Graph(id="spider-graph", figure=draw_figure(topbar_tab, decades_list, current_decade, song1=available_songs[0][1], song2=available_songs[1][1])),
                        style={
                            "background": "rgba(0,0,0,0)",  # Transparent background for the graph container
                            "padding": "20px",
                            "gridColumn": "1 / -1",  # Span across all columns in the second row
                        },
                    ),
                ],
            )
        else:
            pane = f"You have selected Topbar Tab: {topbar_tab} and Sidebar Tab: {current_decade}, The layout you specified ({layout}) is not yet implemented"
    elif topbar_tab == "topic-4":
        pane = draw_figure(topbar_tab, decades_list, current_decade)
    
    elif topbar_tab == "topic-5":
        if layout == "grid":
            # Get available songs for the selected decade
            available_songs = get_songs_for_decade(current_decade)
            song_options = [{"label": song_name, "value": track_id} for song_name, track_id in available_songs]
            
            pane = html.Div(
                style={
                    "padding": "6px",
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr 1fr",
                    "gridTemplateRows": "1fr auto auto 1fr 1fr",
                    "gridGap": "6px",
                    "background": "rgba(0,0,0,0)"
                },
                children=[
                    # Row 1
                    html.Div([
                        html.Div(
                            dcc.Graph(figure=draw_spider_analysis1(decades_list, current_decade), style={'height': '100%', 'width': '100%'}),
                            style={"flex": "2", "position": "relative"} # Top 66%
                        ),
                        html.Div(
                            dcc.Graph(figure=draw_genre_trends_overlay(current_decade), style={'height': '100%', 'width': '100%'}),
                            style={"flex": "1", "minHeight": "0"} # Bottom 33% (1/(2+1))
                        ),

                    ], style={"background": "rgba(0,0,0,0)", "padding": "3px", "minWidth": "0", "position": "relative", "display": "flex", "flexDirection": "column", "height": "100%"}),
                    html.Div(dcc.Graph(id='area-plots-graph', figure=draw_area_plots(decades_list, current_decade, features=["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness", "Loudness", "Tempo", "Liveness"])), style={"background": "rgba(0,0,0,0)", "padding": "3px", "minWidth": "0"}),
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "height": "100%"},
                        children=[
                            html.Div(create_decade_card(current_decade), style={"flex": "2", "background": "rgba(0,0,0,0)", "padding": "3px"}),
                            html.Div(
                                style={"flex": "1", "display": "flex", "flexDirection": "row"},
                                children=[
                                    html.Div(dcc.Graph(figure=draw_change(current_decade, genre_counts, "asc")), style={"flex": "1", "background": "rgba(0,0,0,0)", "padding": "3px"}),
                                    html.Div(dcc.Graph(figure=draw_change(current_decade, genre_counts, "desc")), style={"flex": "1", "background": "rgba(0,0,0,0)", "padding": "3px"})
                                ]
                            )
                        ]
                    ),
                    
                    # Timeline
                    html.Div([
                        dcc.Dropdown(
                            id="bin-size-dropdown",
                            options=[
                                {"label": "No bins", "value": "No bins"},
                                {"label": "1 week", "value": "1 week"},
                                {"label": "1 month", "value": "1 month"},
                                {"label": "5 months", "value": "5 months"}
                            ],
                            value=bin_size,
                            style={"position": "absolute", "top": "10px", "left": "10px", "zIndex": "10", "color": "black", "width": "150px"}
                        ),
                        dcc.Graph(id="timeline-graph", figure=draw_timeline(current_decade, bin_size))
                    ], style={"gridColumn": "1 / 4", "minWidth": "0", "position": "relative"}),
                    
                    # Row 2
                    html.Div([
                        dcc.Dropdown(
                            id="song-1-dropdown",
                            options=song_options,
                            value=available_songs[0][1] if available_songs else None,
                            style={"color": "black", "marginBottom": "10px"}
                        ),
                        dcc.Dropdown(
                            id="song-2-dropdown",
                            options=song_options,
                            value=available_songs[1][1] if len(available_songs) > 1 else available_songs[0][1],
                            style={"color": "black"}
                        )
                    ], style={"background": "rgba(0,0,0,0)", "padding": "3px", "display": "flex", "flexDirection": "column", "minWidth": "0"}),
                    html.Div([
                        html.Iframe(
                            id="player-1",
                            src="https://open.spotify.com/embed/track/2plbrEY59IikOBgBGLjaoe",
                            style={
                                "height": "80px",
                                "width": "100%", 
                                "border": "0",
                                "borderRadius": "12px",
                                "marginBottom": "10px"
                            }
                        ),
                        html.Iframe(
                            id="player-2",
                            src="https://open.spotify.com/embed/track/2plbrEY59IikOBgBGLjaoe",
                            style={
                                "height": "80px",
                                "width": "100%", 
                                "border": "0",
                                "borderRadius": "12px"
                            }
                        )
                    ], style={"background": "rgba(0,0,0,0)", "padding": "3px", "display": "flex", "flexDirection": "column", "minWidth": "0"}),
                    html.Div([
                        dcc.Graph(id="spider-graph", figure=draw_spider(current_decade, available_songs[0][1] if available_songs else None, available_songs[1][1] if len(available_songs) > 1 else None)),
                        html.Div([
                            html.Div("i", className="info-icon"),
                            html.Div([
                                 html.H4("Audio Features Key"),
                                 html.Ul([
                                     html.Li([html.Strong("Energy: "), "Intensity/Speed/Noise"]),
                                     html.Li([html.Strong("Danceability: "), "Rhythm stability/Beat"]),
                                     html.Li([html.Strong("Valence: "), "Musical Positiveness (Happy vs Sad)"]),
                                     html.Li([html.Strong("Acousticness: "), "Unplugged/Natural sound"]),
                                     html.Li([html.Strong("Instrumentalness: "), "Lack of vocals"])
                                 ])
                            ], className="info-tooltip")
                        ], className="info-container")
                    ], style={"background": "rgba(0,0,0,0)", "padding": "3px", "minWidth": "0", "position": "relative"}),
                    
                    # Row 3
                    html.Div(style={"background": "rgba(0,0,0,0)", "padding": "3px", "minWidth": "0"}),
                    html.Div(style={"background": "rgba(0,0,0,0)", "padding": "3px", "minWidth": "0"}),
                    html.Div(style={"background": "rgba(0,0,0,0)", "padding": "3px", "minWidth": "0"})
                ]
            )
        else:
            pane = f"You have selected Topbar Tab: {topbar_tab} and Sidebar Tab: {current_decade}, The layout you specified ({layout}) is not yet implemented"
    else:
        if layout == "grid":
            pane = html.Div(
                style={
                    "padding": "30px",
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",  # 2 equal columns
                    "gridTemplateRows": "1fr 1fr",  # 2 equal rows
                    "gridGap": "30px",
                    "background": "rgba(0,0,0,0)"  # Transparent background for the grid
                },
                children=[
                    html.Div(draw_figure(topbar_tab, decades_list, current_decade), style={"background": "rgba(0,0,0,0)", "padding": "20px"})  # Transparent
                    for i in range(4)
                ],
            )
        else:
            pane = f"You have selected Topbar Tab: {topbar_tab} and Sidebar Tab: {current_decade}, The layout you specified ({layout}) is not yet implemented"
    
    return pane





# Initialize the app
app = Dash(__name__, suppress_callback_exceptions=True) #carefull for debugging we might need to remove this later

# app.layout is the container for everything visual
# Ill try to get the tabbed layout working
# sidebar and topbar too
# The goal is to make a dashboard that scales seemlessly.


# Issue currently. There is some margin the browser seems to add by default
# Need to find a way to remove that margin
# so we wont have a scrollbar
# This is a css issue will add css config in assets folder


## This class takes a list of children/components
app.layout = html.Div(id = "root_container", children=[
    
    #Topbar
    html.Div(children = [
        dcc.Tabs(id="topbar_tabs", value="topic-1", 
            parent_style={"flexDirection": "row", "width": "100%"},
            children=[
            dcc.Tab(label="Analysis 1", value="topic-1", className="top-tab", selected_className="top-tab--selected"),
            dcc.Tab(label="Compare/Listen", value="topic-3", className="top-tab", selected_className="top-tab--selected"),
            dcc.Tab(label="Changes", value="topic-4", className="top-tab", selected_className="top-tab--selected"),
            dcc.Tab(label="Prototype Dashboard", value="topic-5", className="top-tab", selected_className="top-tab--selected")
        ])
    ], 
             style={"background" : "rgba(20, 22, 35, 0.95)", "flexDirection" : "column", "borderBottom": "1px solid rgba(255,255,255,0.1)", "boxShadow": "0 4px 15px rgba(0,0,0,0.3)", "zIndex": "1001"}), 


    dcc.Store(id='selected_decades', data=[]),
    dcc.Store(id='bin_size', data='5 months'),
    dcc.Store(id='previous_decade', data=None),
    dcc.Store(id='animation_trigger', data=0),
    dcc.Store(id='selected_genres_store', data=None),

    # Horizontal Pane
    html.Div(children = [
        # Main content area (Now full width)
        html.Div(id="content_area", children = "Loading...", style={"flex" : "1", "position": "relative", "overflow": "hidden", "height": "100%"}), # Added height 100%

        # Floating Decades Menu (Formerly Sidebar)
        html.Div(children = [
            dcc.Tabs(id="sidebar_tabs", vertical=False, value="20s", 
                parent_style={"flexDirection": "row", "justifyContent": "center"}, # Center tabs
                children=[
                dcc.Tab(label="50s", value="50s", className="decade-tab", selected_className="decade-tab--selected"),
                dcc.Tab(label="60s", value="60s", className="decade-tab", selected_className="decade-tab--selected"),
                dcc.Tab(label="70s", value="70s", className="decade-tab", selected_className="decade-tab--selected"),
                dcc.Tab(label="80s", value="80s", className="decade-tab", selected_className="decade-tab--selected"),
                dcc.Tab(label="90s", value="90s", className="decade-tab", selected_className="decade-tab--selected"),
                dcc.Tab(label="00s", value="00s", className="decade-tab", selected_className="decade-tab--selected"),
                dcc.Tab(label="10s", value="10s", className="decade-tab", selected_className="decade-tab--selected"),
                dcc.Tab(label="20s", value="20s", className="decade-tab", selected_className="decade-tab--selected"),
            ])
        ], 
        style={
            "position": "absolute", 
            "bottom": "0", 
            "width": "100%", 
            "padding": "10px", 
            "background": "linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0) 100%)", # Gradient fade
            "display": "flex",
            "justifyContent": "center",
            "zIndex": "1000"
        }), 
    ],
    #Options
    style={"display" : "flex", "flexDirection" : "column", "flex" : "1", "minHeight": "0", "overflow": "hidden", "position": "relative"} # Changed to column to stack if needed, but mainly relative for absolute child
    ),

    #Bottom bar (Credits logos and so on)
    html.Div("Here we will put the Bottom bar", style = {"background" : "#5B5757"})
]
#Options
, style={"display" : "flex", "flexDirection" : "column", "height" : "100vh", "width" : "100vw" } #currently takes 100% of avaialble viewport height This might be stupid
)

#---------------------------------------------------------------------------#
# Callback to update content area based on selected tab
@app.callback(
    Output(component_id="content_area", component_property="children"),
    Output(component_id="root_container", component_property="style"),
    Output(component_id="selected_decades", component_property="data"),
    Output(component_id="previous_decade", component_property="data"),
    Output(component_id="animation_trigger", component_property="data"),
    Input(component_id="topbar_tabs", component_property="value"),
    Input(component_id="sidebar_tabs", component_property="value"),
    State(component_id="selected_decades", component_property="data"),
    State(component_id="bin_size", component_property="data"),
    State(component_id="previous_decade", component_property="data"),
    State(component_id="animation_trigger", component_property="data"),
    State(component_id="selected_genres_store", component_property="data"),
    allow_duplicate=True
)

# The order of the parameters is always the same as the order of the Inputs
# just keep that in mind if you add more Inputs
def render_content(topbar_tab_value, sidebar_tab_value, selected_decades, bin_size, previous_decade, animation_trigger, selected_genres):
    # This function takes the Input value as an argument

    selected_decades = selected_decades or []
    if sidebar_tab_value not in selected_decades:
        selected_decades.append(sidebar_tab_value)

    # Check if decade changed
    decade_changed = sidebar_tab_value != previous_decade
    if decade_changed:
        animation_trigger = (animation_trigger or 0) + 1

    #This is for changing the background image depending on what decade is selected
    filename = sidebar_tab_value + ".png"
    root_style = {"display" : "flex", "flexDirection" : "column", "height" : "100vh", "width" : "100vw"}
    
    if topbar_tab_value != "topic-1":
         root_style.update({
              "backgroundImage": f"url('/assets/{filename}')", 
              "background-size": "cover",
              "background-position": "center",
              "background-repeat": "no-repeat"
         })
    
    return draw_pane(topbar_tab_value, selected_decades, sidebar_tab_value, bin_size=bin_size, selected_genres=selected_genres), root_style, selected_decades, sidebar_tab_value, animation_trigger

# Callback to persist selected genres
@app.callback(
    Output("selected_genres_store", "data"),
    Input("genre-dropdown", "value"),
    prevent_initial_call=True
)
def save_selected_genres(genres):
    return genres

# Callback for Analysis 1 Genre Filtering
@app.callback(
    Output("spider-graphs-container", "children"),
    Output("analysis1-area", "figure"),
    Input("genre-dropdown", "value"),
    State("sidebar_tabs", "value"),
)
def update_analysis1(selected_genres, current_decade):
    bin_size = "1 year" # Fixed bin size
    # Only use the current decade, not accumulated decades
    decades_list = [current_decade]
    
    # Generate list of spider graphs for the grid
    spider_graphs_children = []
    
    if selected_genres:
        # --- Dynamic Scaling Logic ---
        num_genres = len(selected_genres)
        
        # Base values from CSS
        base_w = 260
        base_h = 280
        base_m_vert = -20
        base_m_horz = -5
        
        # Calculate scale factor
        scale = 1.0
        if num_genres > 15:
            scale = 0.55
        elif num_genres > 9:
            scale = 0.65
        elif num_genres > 4:
            scale = 0.8
            
        # Apply scale
        s_w = int(base_w * scale)
        s_h = int(base_h * scale)
        s_m_v = int(base_m_vert * scale)
        s_m_h = int(base_m_horz * scale)
        s_font = max(6, int(14 * scale)) # Minimum font size 6
        
        # Alternating background colors (lighter tones of the dark theme)
        bg_colors = [
            "rgba(60, 65, 90, 0.7)",  # Tone A
            "rgba(75, 80, 105, 0.7)"   # Tone B
        ]
        
        # Logic to insert breaks for 3-2-3-2 pattern
        current_row_len = 0
        target_row_len = 3 # Start with 3 items in first row
        
        # Color cycle to match area plots
        colors_cycle = px.colors.qualitative.Plotly
        
        for i, genre in enumerate(selected_genres):
            # Calculate alternating background color
            bg_color = bg_colors[i % len(bg_colors)]
            
            # Select line color matching the area plot
            line_color = colors_cycle[i % len(colors_cycle)]
            
            cell_style_override = {
                "width": f"{s_w}px",
                "height": f"{s_h}px",
                "margin": f"{s_m_v}px {s_m_h}px",
                "backgroundColor": bg_color
            }

            # Generate spider graph for this specific genre
            # We reuse draw_spider_analysis1 but pass only [genre] to filter, and pass the color
            fig = draw_spider_analysis1(decades_list, current_decade, selected_genres=[genre], override_color=line_color)
            
            # Customize layout for the grid item
            fig.update_layout(
                title=dict(text=f"{genre.title()}", font=dict(size=s_font, color=line_color), y=0.95), 
                margin=dict(l=20*scale, r=20*scale, t=40*scale, b=20*scale),
                height=s_h, # Match container height
                font=dict(size=max(8, 10*scale)) # Scale axis labels too
            )
            
            spider_graphs_children.append(
                html.Div(
                    className="honeycomb-cell",
                    style=cell_style_override,
                    children=[
                        dcc.Graph(
                            id={'type': 'spider-genre', 'index': genre}, # Dynamic ID for pattern matching
                            figure=fig, 
                            config={'displayModeBar': False},
                            style={"height": "100%", "width": "100%"}
                        )
                    ]
                )
            )
            
            # Update Stacking Pattern Logic
            current_row_len += 1
            if current_row_len == target_row_len and i < len(selected_genres) - 1:
                 # Insert Force Break
                 spider_graphs_children.append(
                     html.Div(style={"flexBasis": "100%", "height": "0", "margin": "0", "padding": "0"})
                 )
                 # Toggle pattern: 3 -> 2 -> 3 -> 2
                 target_row_len = 2 if target_row_len == 3 else 3
                 current_row_len = 0
    else:
        # Fallback: Show overall average if no genres selected
        fig = draw_spider_analysis1(decades_list, current_decade)
        fig.update_layout(title="All Genres Average", height=300)
        spider_graphs_children.append(
            html.Div(
                className="honeycomb-cell",
                children=[dcc.Graph(figure=fig, style={"height": "100%", "width": "100%"})]
            )
        )
    
    area_fig = draw_area_plots(
        decades_list, 
        current_decade, 
        features=["Energy", "Tempo", "Danceability", "Loudness", "Liveness", "Valence", "Speechiness", "Acousticness", "Instrumentalness"],
        bin_size=bin_size,
        selected_genres=selected_genres
    )
    return spider_graphs_children, area_fig

# Callback to handle click interactions from spider graphs
@app.callback(
    Output("analysis1-area", "figure", allow_duplicate=True),
    Input({'type': 'spider-genre', 'index': ALL}, 'clickData'),
    State("analysis1-area", "figure"),
    prevent_initial_call=True
)
def update_area_highlight(click_data_list, current_figure):
    # Determine which graph triggered the click
    # Dash pattern matching trigger context
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    # Check if any click data exists
    if not any(click_data_list):
        return dash.no_update

    # Extract the genre ID from the triggered input
    triggered_prop_id = ctx.triggered[0]['prop_id']
    import json
    try:
        # prop_id is like '{"index":"pop","type":"spider-genre"}.clickData'
        prop_id_dict = json.loads(triggered_prop_id.split('.')[0])
        clicked_genre = prop_id_dict['index']
        
        # Optimize using Patch() to update the existing figure client-side
        # instead of re-calculating and re-sending the entire figure.
        patched_figure = Patch()
        
        # Loop through all traces in the figure
        # Note: current_figure['data'] is a list of trace objects
        for i, trace in enumerate(current_figure['data']):
             if 'name' in trace:
                 # Check if this trace is the one we clicked
                 # Ensure strict case matching (convert clicked to title case to match trace names)
                 if trace['name'] == clicked_genre.title():
                     patched_figure['data'][i]['line']['width'] = 5
                     patched_figure['data'][i]['opacity'] = 1.0
                 else:
                     patched_figure['data'][i]['line']['width'] = 2
                     patched_figure['data'][i]['opacity'] = 0.2
                     
        return patched_figure
            
    except Exception as e:
        print(f"Error in update_area_highlight: {e}")
        return dash.no_update

#------------------------------------------------------------------------#
# Listen/Spider Tab
@app.callback(
    Output(component_id="spider-graph", component_property="figure"),
    Input(component_id="song-1-dropdown", component_property="value"),
    Input(component_id="song-2-dropdown", component_property="value"),
    State(component_id="sidebar_tabs", component_property="value"),
)
def update_spider_graph(song1, song2, decade):
    if song1 and song2:
        figure = draw_spider(decade, song1, song2)
        return figure
    return {}

@app.callback(
    Output(component_id="player-1", component_property="src"),
    Input(component_id="song-1-dropdown", component_property="value")
)
def update_player_1(track_id):
    if not track_id:
        return "" # Return empty if no song selected
    
    # Spotify embed structure: https://open.spotify.com/embed/track/{ID}
    return f"https://open.spotify.com/embed/track/{track_id}"

@app.callback(
    Output(component_id="player-2", component_property="src"),
    Input(component_id="song-2-dropdown", component_property="value")
)
def update_player_2(track_id):
    if not track_id:
        return "" # Return empty if no song selected
    
    # Spotify embed structure: https://open.spotify.com/embed/track/{ID}
    return f"https://open.spotify.com/embed/track/{track_id}"

# Callback for timeline
@app.callback(
    Output("timeline-graph", "figure"),
    Input("bin-size-dropdown", "value"),
    Input("sidebar_tabs", "value"),
)
def update_timeline(bin_size, decade):
    return draw_timeline(decade, bin_size)

# Callback for bin size
@app.callback(
    Output("bin_size", "data"),
    Input("bin-size-dropdown", "value")
)
def update_bin_size(value):
    return value

# Callback for area plots (sync bin size with timeline dropdown)
@app.callback(
    Output('area-plots-graph', 'figure'),
    Input('bin-size-dropdown', 'value'),  # <-- Use bin-size-dropdown directly for binning
    Input('sidebar_tabs', 'value'),
    State('selected_decades', 'data')
)
def update_area_opacity(bin_size, decade, selected_decades):
    figure = draw_area_plots(selected_decades, decade, features=["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness", "Loudness", "Tempo", "Liveness"], bin_size=bin_size)
    return figure

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port = 8052)
