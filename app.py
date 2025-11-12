from dash import Dash, callback, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


df = pd.read_csv('ipsos.csv')
cols = {
    'Class/Market Servier RU': 'Class', 
    'Brand RU': 'Brand', 
    'INN RU': 'INN', 
    'ATC3 RU': 'ATC3',
    'Diagnosis Group L3 (Prescr) RU': 'Diagnosis', 
    'Speciality RU': 'Speciality'
}
df = df.rename(columns=cols)

# Предварительная агрегация для оптимизации
doctor_agg = df.groupby('IDdoc').agg({
    'Sample': 'sum',
    'Extra': 'sum',
    'Brand': 'first',
    'Class': 'first',
    'Speciality': 'first',
    'INN': 'first',
    'Diagnosis': 'first',
    'ATC3': 'first',
    'Quarter': 'first'
}).reset_index()

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "Анализ медицинских данных"

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1('📊 Концентрационные кривые', 
                   className='text-center mb-4 mt-4 text-primary',
                   style={'fontWeight': 'bold', 'fontSize': '2.5rem'})
        ])
    ]),
    
    # Statistics Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H2("👨‍⚕️", className='card-icon', 
                               style={'fontSize': '2rem', 'marginBottom': '10px'}),
                        html.H4(id='total-doctors', children='0', 
                               className='card-value text-primary'),
                        html.P('Всего врачей', className='card-label text-muted')
                    ], className='text-center')
                ])
            ], className='shadow-sm border-0', 
               style={'backgroundColor': '#f8f9fa', 'height': '100%'})
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H2("💊", className='card-icon', 
                               style={'fontSize': '2rem', 'marginBottom': '10px'}),
                        html.H4(id='total-prescriptions', children='0', 
                               className='card-value text-success'),
                        html.P('Всего назначений', className='card-label text-muted')
                    ], className='text-center')
                ])
            ], className='shadow-sm border-0', 
               style={'backgroundColor': '#f8f9fa', 'height': '100%'})
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H2("📈", className='card-icon', 
                               style={'fontSize': '2rem', 'marginBottom': '10px'}),
                        html.H4(id='total-sample', children='0', 
                               className='card-value text-info'),
                        html.P('Общий Sample', className='card-label text-muted')
                    ], className='text-center')
                ])
            ], className='shadow-sm border-0', 
               style={'backgroundColor': '#f8f9fa', 'height': '100%'})
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H2("⭐", className='card-icon', 
                               style={'fontSize': '2rem', 'marginBottom': '10px'}),
                        html.H4(id='total-extra', children='0', 
                               className='card-value text-warning'),
                        html.P('Общий Extra', className='card-label text-muted')
                    ], className='text-center')
                ])
            ], className='shadow-sm border-0', 
               style={'backgroundColor': '#f8f9fa', 'height': '100%'})
        ], width=3),
    ], className='mb-4'),
    
    # Main Content
    dbc.Row([
        # Chart Section
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col([
                            html.H4('📈 Накопительная дуга распределения', 
                                   className='mb-0 text-dark')
                        ]),
                        dbc.Col([
                            dbc.Button("ℹ️ О графике", 
                                     id="info-button", 
                                     color="light", 
                                     size="sm",
                                     className='float-end')
                        ], width='auto')
                    ])
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.P(id='chart_name', children='Выберите фильтры для отображения данных',
                                  className='text-muted mb-3')
                        ]),
                        dbc.Col([
                            dbc.Accordion([
                                dbc.AccordionItem(
                                    dcc.Dropdown(
                                        id='sBrand',
                                        multi=True,
                                        placeholder='Выберите бренды...',
                                        options=[],
                                        className='brand-selector'
                                    ), title='🎯 Бренды на графике'
                                )
                            ], start_collapsed=True, flush=True)
                        ], width=5)
                    ], className='mb-3'),
                    html.Div(dcc.Graph(id='chart', config={'displayModeBar': True, 'displaylogo': False}))
                ])
            ], className='shadow border-0 h-100')
        ], width=9, className='pe-3'),
        
        # Filters Section
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4('🔧 Фильтры', className='mb-0 text-dark')
                ]),
                dbc.CardBody([
                    html.Div([
                        dbc.Label("📅 Квартал", className='fw-bold text-primary mb-2'),
                        dcc.Dropdown(
                            id='fPeriod', 
                            placeholder='Выберите кварталы...',
                            multi=True,
                            options=[{'label': x, 'value': x} for x in sorted(df['Quarter'].unique())],
                            className='mb-4'
                        ),
                        
                        dbc.Label("🏷️ Класс", className='fw-bold text-primary mb-2'),
                        dcc.Dropdown(
                            id='fClass', 
                            placeholder='Выберите классы...', 
                            multi=True,
                            options=[{'label': x, 'value': x} for x in sorted(df['Class'].unique())],
                            className='mb-4'
                        ),
                        
                        dbc.Label("🎓 Специальность", className='fw-bold text-primary mb-2'),
                        dcc.Dropdown(
                            id='fSpec', 
                            placeholder='Выберите специальности...', 
                            multi=True,
                            options=[{'label': x, 'value': x} for x in sorted(df['Speciality'].unique())],
                            className='mb-4'
                        ),
                        
                        dbc.Label("🧪 МНН", className='fw-bold text-primary mb-2'),
                        dcc.Dropdown(
                            id='fInn', 
                            placeholder='Выберите МНН...', 
                            multi=True,
                            options=[{'label': x, 'value': x} for x in sorted(df['INN'].unique())],
                            className='mb-4'
                        ),
                        
                        dbc.Label("🏥 Диагноз", className='fw-bold text-primary mb-2'),
                        dcc.Dropdown(
                            id='fDiag', 
                            placeholder='Выберите диагнозы...', 
                            multi=True,
                            options=[{'label': x, 'value': x} for x in sorted(df['Diagnosis'].unique())],
                            className='mb-4'
                        ),
                        
                        dbc.Label("💊 АТС3", className='fw-bold text-primary mb-2'),
                        dcc.Dropdown(
                            id='fAtc', 
                            placeholder='Выберите АТС3...', 
                            multi=True,
                            options=[{'label': x, 'value': x} for x in sorted(df['ATC3'].unique())]
                        ),
                    ])
                ])
            ], className='shadow border-0 h-100')
        ], width=3)
    ]),
    
    # Info Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("ℹ️ О накопительной дуге")),
        dbc.ModalBody([
            html.P("Накопительная дуга (Cumulative Share Curve) показывает распределение назначений среди врачей:"),
            html.Ul([
                html.Li("Ось X: Кумулятивная доля врачей (отсортированных по убыванию назначений)"),
                html.Li("Ось Y: Кумулятивная доля общего Sample"),
                html.Li("Идеальное распределение: прямая линия под 45°"),
                html.Li("Реальное распределение: показывает концентрацию назначений")
            ]),
            html.P("Чем больше кривая отклоняется от идеальной линии, тем выше концентрация назначений у небольшой группы врачей.", 
                  className='text-muted small')
        ]),
        dbc.ModalFooter(
            dbc.Button("Закрыть", id="close-modal", className="ms-auto", n_clicks=0)
        ),
    ], id="info-modal", is_open=False),
    
    # Store for filtered data
    dcc.Store(id='filtered-data-store')
], fluid=True, style={'backgroundColor': '#f5f7fa', 'minHeight': '100vh'})

# CSS стили
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .card-value {
                font-size: 1.8rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
            }
            .card-label {
                font-size: 0.9rem;
                margin-bottom: 0;
            }
            .card-icon {
                opacity: 0.8;
            }
            .brand-selector .Select-control {
                border-radius: 8px;
            }
            .shadow-sm {
                transition: transform 0.2s ease-in-out;
            }
            .shadow-sm:hover {
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Функция для фильтрации данных
def filter_data(period, class_, spec, inn, diag, atc):
    dff = doctor_agg.copy()
    
    masks = []
    if period:
        masks.append(dff['Quarter'].isin(period))
    if class_:
        masks.append(dff['Class'].isin(class_))
    if spec:
        masks.append(dff['Speciality'].isin(spec))
    if inn:
        masks.append(dff['INN'].isin(inn))
    if diag:
        masks.append(dff['Diagnosis'].isin(diag))
    if atc:
        masks.append(dff['ATC3'].isin(atc))
    
    if masks:
        final_mask = masks[0]
        for mask in masks[1:]:
            final_mask &= mask
        dff = dff[final_mask]
    
    return dff

# Функция для создания данных накопительной дуги
def create_cumulative_curve_data_fast(dff, selected_brands=None):
    if selected_brands and len(selected_brands) > 0:
        dff = dff[dff['Brand'].isin(selected_brands)]
        if dff.empty:
            return {}
            
        brands_data = {}
        for brand in selected_brands:
            brand_data = dff[dff['Brand'] == brand].copy()
            if len(brand_data) == 0:
                continue
                
            brand_data = brand_data.sort_values('Sample', ascending=False)
            n_doctors = len(brand_data)
            total_sample = brand_data['Sample'].sum()
            
            brand_data['DocShare'] = 1.0 / n_doctors
            brand_data['SampleShare'] = brand_data['Sample'] / total_sample
            brand_data['DocShareRT'] = brand_data['DocShare'].cumsum()
            brand_data['SampleShareRT'] = brand_data['SampleShare'].cumsum()
            
            brands_data[brand] = brand_data[['DocShareRT', 'SampleShareRT']].values.tolist()
        
        return brands_data
    else:
        if dff.empty:
            return None
            
        dff_sorted = dff.sort_values('Sample', ascending=False)
        n_doctors = len(dff_sorted)
        total_sample = dff_sorted['Sample'].sum()
        
        dff_sorted['DocShare'] = 1.0 / n_doctors
        dff_sorted['SampleShare'] = dff_sorted['Sample'] / total_sample
        dff_sorted['DocShareRT'] = dff_sorted['DocShare'].cumsum()
        dff_sorted['SampleShareRT'] = dff_sorted['SampleShare'].cumsum()
        
        return dff_sorted[['DocShareRT', 'SampleShareRT']].values.tolist()

# Callback для модального окна
@app.callback(
    Output("info-modal", "is_open"),
    [Input("info-button", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("info-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Callback для статистических карточек и данных
@app.callback(
    [Output('total-doctors', 'children'),
     Output('total-prescriptions', 'children'),
     Output('total-sample', 'children'),
     Output('total-extra', 'children'),
     Output('filtered-data-store', 'data')],
    [Input('fPeriod', 'value'),
     Input('fClass', 'value'),
     Input('fSpec', 'value'),
     Input('fInn', 'value'),
     Input('fDiag', 'value'),
     Input('fAtc', 'value')]
)
def update_stats_and_store(fPeriod, fClass, fSpec, fInn, fDiag, fAtc):
    dff = filter_data(fPeriod, fClass, fSpec, fInn, fDiag, fAtc)
    
    total_doctors = f"{len(dff):,}" if not dff.empty else "0"
    total_prescriptions = f"{len(dff):,}" if not dff.empty else "0"  # или другая метрика назначений
    total_sample = f"{dff['Sample'].sum():,.0f}" if not dff.empty else "0"
    total_extra = f"{dff['Extra'].sum():,.0f}" if not dff.empty else "0"
    
    # Сохраняем отфильтрованные данные в store
    store_data = dff.to_dict('records') if not dff.empty else []
    
    return total_doctors, total_prescriptions, total_sample, total_extra, store_data

# Callback для обновления ВСЕХ dropdown'ов включая бренды для графика
@app.callback(
    [Output('fClass', 'options'),
     Output('fSpec', 'options'),
     Output('fInn', 'options'),
     Output('fDiag', 'options'),
     Output('fAtc', 'options'),
     Output('sBrand', 'options')],
    [Input('filtered-data-store', 'data')]
)
def update_all_dropdowns(store_data):
    if not store_data:
        dff = doctor_agg
    else:
        dff = pd.DataFrame(store_data)
    
    class_options = [{'label': x, 'value': x} for x in sorted(dff['Class'].unique())]
    spec_options = [{'label': x, 'value': x} for x in sorted(dff['Speciality'].unique())]
    inn_options = [{'label': x, 'value': x} for x in sorted(dff['INN'].unique())]
    diag_options = [{'label': x, 'value': x} for x in sorted(dff['Diagnosis'].unique())]
    atc_options = [{'label': x, 'value': x} for x in sorted(dff['ATC3'].unique())]
    brand_options = [{'label': x, 'value': x} for x in sorted(dff['Brand'].unique())]
    
    return class_options, spec_options, inn_options, diag_options, atc_options, brand_options

# Callback для очистки выбранных брендов при изменении фильтров
@app.callback(
    Output('sBrand', 'value'),
    [Input('filtered-data-store', 'data')],
    [State('sBrand', 'value')]
)
def clear_invalid_brands(store_data, current_brands):
    if not store_data or not current_brands:
        return []
    
    dff = pd.DataFrame(store_data)
    available_brands = set(dff['Brand'].unique())
    
    # Оставляем только те бренды, которые доступны после фильтрации
    valid_brands = [brand for brand in current_brands if brand in available_brands]
    
    return valid_brands

# Callback для обновления графика
@app.callback(
    Output('chart_name', 'children'),
    Output('chart', 'figure'),
    [Input('filtered-data-store', 'data'),
     Input('sBrand', 'value')]
)
def update_chart(store_data, sBrand):
    if not store_data:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Выберите фильтры для отображения данных",
            xaxis_title="Доля врачей (кумулятивно)",
            yaxis_title="Доля Sample (кумулятивно)",
            xaxis=dict(range=[0, 1]),
            yaxis=dict(range=[0, 1]),
            height=500
        )
        return "Выберите фильтры для отображения данных", empty_fig
    
    dff = pd.DataFrame(store_data)
    
    fig = go.Figure()
    cumulative_data = create_cumulative_curve_data_fast(dff, sBrand)
    
    colors = px.colors.qualitative.Set3
    
    if isinstance(cumulative_data, dict) and sBrand:
        for i, (brand, data) in enumerate(cumulative_data.items()):
            if data:
                x_vals = [point[0] for point in data]
                y_vals = [point[1] for point in data]
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode='lines',
                    name=f'{brand}',
                    line=dict(width=3, color=colors[i % len(colors)]),
                    hovertemplate='<b>%{text}</b><br>Врачи: %{x:.1%}<br>Sample: %{y:.1%}<extra></extra>',
                    text=[f'{brand}'] * len(x_vals)
                ))
    elif cumulative_data:
        x_vals = [point[0] for point in cumulative_data]
        y_vals = [point[1] for point in cumulative_data]
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='lines',
            name='Все данные',
            line=dict(width=4, color='#1f77b4'),
            hovertemplate='<b>Все данные</b><br>Врачи: %{x:.1%}<br>Sample: %{y:.1%}<extra></extra>'
        ))
    
    # Линия идеального распределения
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode='lines',
        name='Идеальное распределение',
        line=dict(dash='dash', color='grey', width=1),
        showlegend=True,
        hovertemplate='Идеальное распределение<extra></extra>'
    ))
    
    fig.update_layout(
        title='',
        xaxis_title='Доля врачей (кумулятивно)',
        yaxis_title='Доля Sample (кумулятивно)',
        xaxis=dict(range=[0, 1], tickformat='.0%'),
        yaxis=dict(range=[0, 1], tickformat='.0%'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        hovermode='x unified',
        height=500,
        plot_bgcolor='rgba(248,249,250,0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    
    title = f"Накопительная дуга | Врачи: {len(dff):,} | Sample: {dff['Sample'].sum():,}"
    if sBrand:
        title += f" | Бренды: {', '.join(sBrand)}"
    
    return title, fig

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)