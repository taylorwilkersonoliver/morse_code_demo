import dash
from dash.dependencies import Input, Output
import dash.html as html
import dash.dcc as dcc

import config
from mc_main import MorseMain

mm = MorseMain()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(children=[
        html.H1('Does not handle \\n intentionally.'),
        dcc.Textarea(
            id=config.ascii_to_morse_text_area_id,
            value='Enter ASCII text here',
            style={'width': '100%', 'height': 100},
        ),
        html.Div(id=config.ascii_to_morse_text_area_id_output, style={'width': '80%',  'overflow-wrap': 'break-word'}),
        dcc.Textarea(
            id=config.morse_to_ascii_text_area_id,
            value=mm.get_morse('Enter ASCII text here'),
            style={'width': '100%', 'height': 100},
        ),
        html.Div(id=config.morse_to_ascii_text_area_id_output, style={'width': '80%', 'overflow-wrap': 'break-word'}),
    ])
])




@app.callback(
    Output(config.ascii_to_morse_text_area_id_output, 'children'),
    Input(config.ascii_to_morse_text_area_id, 'value')
)
def ascii_to_morse(value):
    return mm.api_output_morse(value)


@app.callback(
    Output(config.morse_to_ascii_text_area_id_output, 'children'),
    Input(config.morse_to_ascii_text_area_id, 'value')
)
def morse_to_ascii(value):
    return mm.api_output_ascii(value)


if __name__ == '__main__':
    app.run_server(
        host=config.host,
        port=config.port,
        proxy=config.proxy,
        debug=config.debug,
        dev_tools_ui=config.dev_tools_ui,
        dev_tools_props_check=config.dev_tools_props_check,
        dev_tools_serve_dev_bundles=config.dev_tools_serve_dev_bundles,
        dev_tools_hot_reload=config.dev_tools_hot_reload,
        dev_tools_hot_reload_interval=config.dev_tools_hot_reload_interval,
        dev_tools_hot_reload_watch_interval=config.dev_tools_hot_reload_watch_interval,
        dev_tools_hot_reload_max_retry=config.dev_tools_hot_reload_max_retry,
        dev_tools_silence_routes_logging=config.dev_tools_silence_routes_logging,
        dev_tools_prune_errors=config.dev_tools_prune_errors,
    )
