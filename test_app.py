import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.Button('Button 1', id={'btn-id': '1', 'type': 'button'}),
    html.Button('Button 2', id={'btn-id': '2', 'type': 'button'}),
    html.P(id={'id': 'p', 'type': 'button'})
])

@app.callback(
    Output({'id': 'p', 'type': MATCH}, 'children'),
    [Input({'btn-id': ALL, 'type': MATCH}, 'n_clicks')]
)
def callback(button_clicks):
    print(button_clicks)
    return 'hello world'

if __name__ == '__main__':
    app.run_server(debug=True)