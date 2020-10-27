# -*- coding: utf-8 -*-
import dash
import dash_cytoscape as cyto
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_table
import numpy as np
import pandas as pd
import json
import base64
from collections import OrderedDict


# Reading JSON Files
with open('solutionColor.json', 'r') as myfile:
    sCdata=myfile.read()
sixStepsColors = json.loads(sCdata)

with open('concepts.json', 'r') as myfile:
    conceptData=myfile.read()
concepts = json.loads(conceptData)


# Creating Mindmap Structure
nodes = [
    {
        'data': {'id': short, 'label': label, 'status': status}
    }
    for short, label, status in (
        ('0', 'GPT', 1),
        ('1', 'Variablen', 1),
        ('11', 'String', 1),
        ('12', 'Integer', 1),
        ('13', 'Boolean', 1),
        ('2', 'Kontrollstrukturen', 3),
        ('21', 'If-Else', 3),
        ('22', 'For-Schleife', 2),
        ('23', 'While-Schleife', 2)
    )
]
edges = [
    {'data': {'source': source, 'target': target}}
    for source, target in (
        ('0', '1'),
        ('0', '2'),
        ('1', '11'),
        ('1', '12'),
        ('1', '13'),
        ('2', '21'),
        ('2', '22'),
        ('2', '23')
    )
]
elements = nodes + edges



# Reading csv files (old)
df_concepts =   pd.read_csv('concepts.csv')
df_tasks =      pd.read_csv('tasks.csv')
df_solutions =  pd.read_csv('solutions.csv')

# Function that returns the number of solved Tasks in a concept when status is 3
def solvedTasks(concepts):
    count = 0
    for i in range(len(concepts)):
        if(len(concepts[i]['solutions']) == 0):
            return 0
        else:
            for s in range(len(concepts[i]['solutions'])):
                if(concepts[i]['solutions'][s]['status'] == 3):
                    count += 1
    return count


# Fetch all the concepts for the concepts table
my_concepts = []
for i in range(0, len(concepts)):
    my_concepts += [{
                    "Main Concept": concepts[i].get('value'),
                    "Tasks Solved": solvedTasks(concepts[i].get('tasks')),
                    "Level of Understanding": concepts[i].get('understanding'),
                    "Status": concepts[i].get('status'),
                    "Priority": concepts[i].get('priority') 
                    }]
    


emptyTaskRow =      {'Task Name': '','Main Concept': '','Solutions': 0,'Duration': 0, 'Difficulty': 1,'Priority': 1}

# Fetch all the tasks for the tasks table
my_tasks = []
for i in range(0, len(concepts)):
    #if(len(concepts[i]['solutions']) > 0):
        my_tasks += [{
                        "Task Name": concepts[i].get('value'),
                        "Tasks Solved": solvedTasks(concepts[i].get('tasks')),
                        "Level of Understanding": concepts[i].get('understanding'),
                        "Status": concepts[i].get('status'),
                        "Priority": concepts[i].get('priority') 
                        }]

print(concepts[0]['tasks'])

emptySolutionRow =  {'Task Name': '','Status': 1,'Concepts Used': '','Reinterpret': 0, 'Analogous': 0,'Search': 0, 'Evaluate':0,'Implement':0, 'Document':0}


# Fetch all the Solutions for the solution table





# Styles
buttonStyle =   {'padding':'15px 32px','text-align': 'center'}
greenNode =     {'background-color': '#16C60C','shape': 'circle','label': 'data(label)' }
greyNode =      {'background-color': '#A1A1A1','shape': 'circle','label': 'data(label)' }
yellowNode =    {'background-color': '#EDD500','shape': 'circle','label': 'data(label)' }
redNode =       {'background-color': '#EC4D4D','shape': 'circle','label': 'data(label)' }




app = dash.Dash()
app.layout = html.Div([
    html.Div([
        cyto.Cytoscape(
            id='cytoscape-two-nodes',
            layout={
                'name': 'cose'
            },
            style={'width': '100%', 'height': '400px'},
            elements=elements,
            userZoomingEnabled=False,
            userPanningEnabled=False,
            autoungrabify=True,
            stylesheet=[
                { 'selector': '[status = 3]','style': greenNode },
                { 'selector': '[status = 2]','style': yellowNode },
                { 'selector': '[status = 1]','style': greyNode },
            ]   
        ),
        html.H2('Concepts'),
        dash_table.DataTable(
            id='table-concepts',
            columns = [
                {"name": "Main Concept", "id": "Main Concept", "presentation": "dropdown"},
                {"name": "Tasks Solved", "id": "Tasks Solved"},
                {"name": "Level of Understanding", "id": "Level of Understanding", "presentation": "dropdown"},
                {"name": "Status", "id": "Status", "presentation": "dropdown"},
                {"name": "Priority", "id": "Priority", "presentation": "dropdown"}
            ],
            data= my_concepts,
            editable=True,
            sort_action="native",
            row_deletable=True,
            style_as_list_view=True,
            style_cell={'padding': '5px'},
            style_header={
                'backgroundColor': 'C4C4C4',
                'fontWeight': 'bold'},
            style_cell_conditional=[{
                'if': {'column_id': ['Status','Main Concept','Level of Understanding', 'Tasks Solved']},
                'textAlign': 'left'
            }],
            dropdown={
                'Level of Understanding': {
                    'options': [{'label': "⭐" * i, 'value': i} for i in range(1,6,1)]
                },
                'Priority': {
                    'options': [{'label': '1', 'value': 1},
                                {'label': '2', 'value': 2},
                                {'label': '3', 'value': 3},
                                {'label': '4', 'value': 4},
                                {'label': '5', 'value': 5}]
                },
                'Status': {
                    'options': [{'label': '⚪ Open', 'value': 1},
                                {'label': '🟡 In Progress', 'value': 2},
                                {'label': '🟢 Studied', 'value': 3}]
                },
                'Main Concept': {
                    'options': concepts
                }
            }
        ),
        html.H2('Tasks'),
        dash_table.DataTable(
            id='table-tasks',
            columns = [
                {"name": "Task Name", "id": "Task Name"},
                {"name": "Main Concept", "id": "Main Concept", "presentation": "dropdown"},
                {"name": "Solutions", "id": "Solutions"},
                {"name": "Duration", "id": "Duration"},
                {"name": "Difficulty", "id": "Difficulty", "presentation": "dropdown"},
                {"name": "Priority", "id": "Priority", "presentation": "dropdown"}
            ],
            data = df_tasks.to_dict('records'),
            sort_action="native",
            row_deletable=True,
            style_as_list_view=True,
            style_cell={'padding': '5px'},
            style_header={
                'backgroundColor': 'C4C4C4',
                'fontWeight': 'bold'},
            style_cell_conditional=[{
                'if': {'column_id': ['Task Name','Main Concept', 'Difficulty']},
                'textAlign': 'left'
            }],
            editable=True,
            dropdown={
                'Difficulty': {
                    'options': [{'label': "🔥" * i, 'value': i} for i in range(1,6,1)]
                },
                'Priority': {
                    'options': [{'label': '1', 'value': 1},
                                {'label': '2', 'value': 2},
                                {'label': '3', 'value': 3},
                                {'label': '4', 'value': 4},
                                {'label': '5', 'value': 5}]
                },
                'Main Concept': {
                    'options': concepts
                }
            }
        ),
        html.Button('Add Task', id='editing-taskrows-button', n_clicks=0, style={'margin-bottom': '50px', 'margin-top': '16px'}),
        html.H2('Solutions'),
        html.H5(['3: Green = Well performed, 2: Yellow = Partly performed, 1: Red = Not performed, 0: Grey = Not started'], style={'float':'right'}),
        dash_table.DataTable(
            id='table-solutions',
            columns = [
                {"name": "Task Name", "id": "Task Name"},
                {"name": "Status", "id": "Status", "presentation": "dropdown"},
                {"name": "Concepts Used", "id": "Concepts Used", "presentation": "dropdown"},
                {"name": "Reinterpret", "id": "Reinterpret"},
                {"name": "Analogous", "id": "Analogous"},
                {"name": "Search", "id": "Search"},
                {"name": "Evaluate", "id": "Evaluate"},
                {"name": "Implement", "id": "Implement"},
                {"name": "Document", "id": "Document"}
            ],
            data= df_solutions.to_dict('records'),
            editable=True,
            sort_action="native",
            row_deletable=True,
            style_as_list_view=True,
            style_cell={'padding': '5px'},
            style_header={
                'backgroundColor': 'C4C4C4',
                'fontWeight': 'bold'},
            style_cell_conditional=[{
                'if': {'column_id': ['Task Name','Status', 'Concepts Used']},
                'textAlign': 'left'
            }],
            style_data_conditional=sixStepsColors,
            tooltip_data = [{
                'Reinterpret':'Step 1: Reinterpret the problem prompt (Understand, interpret, clarify)',
                'Analogous':'Step 2: Search for analogous problems (Reuse knowledge from past)',
                'Search':'Step 3: Search for Solutions (seek, adapt, find)',
                'Evaluate':'Step 4: Evaluate a potential solution (sketching, simulation)',
                'Implement':'Step 5: Implement a solution (translate solution into code)',
                'Document':'Step 6: Evaluate implemented solution (testing, debugging)'
            }],
            tooltip_duration = None,
            dropdown={
                'Status': {
                    'options': [{'label': '⚪ Open', 'value': 1},
                                {'label': '🟡 In Progress', 'value': 2},
                                {'label': '🟢 Done', 'value': 3}]
                },
                'Concepts Used': {
                    'options':concepts
                },
            }
        ),
        html.Button('Add Solution', id='editing-solutionrows-button', n_clicks=0, style={'margin-bottom': '50px', 'margin-top': '16px'}),
    ],style={'margin-left':'10%', 'margin-right':'10%'})
])


@app.callback(
    Output('table-tasks', 'data'),
    [Input('editing-taskrows-button', 'n_clicks')],
    [State('table-tasks', 'data'),
     State('table-tasks', 'columns')])
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append(emptyTaskRow)
    return rows

@app.callback(
    Output('table-solutions', 'data'),
    [Input('editing-solutionrows-button', 'n_clicks')],
    [State('table-solutions', 'data'),
     State('table-solutions', 'columns')])
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append(emptySolutionRow)
    return rows



# Callback for updating the Mindmap


# Callback for updating the concepts barchart


if __name__ == '__main__': app.run_server()