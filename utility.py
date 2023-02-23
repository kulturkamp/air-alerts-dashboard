import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as clrs


name_map = {
    'Київ': 'Kyiv',
    'Черкаська область': 'Cherkasy Oblast',
    'Запорізька область': 'Zaporizhzhia Oblast',
    'Вінницька область': 'Vinnytsia Oblast',
    'Рівненська область': 'Rivne Oblast',
    'Волинська область': 'Volyn Oblast',
    'Харківська область': 'Kharkiv Oblast',
    'Львівська область': 'Lviv Oblast',
    'Херсонська область': 'Kherson Oblast',
    'Одеська область': 'Odesa Oblast',
    'Житомирська область': 'Zhytomyr Oblast',
    'Чернігівська область': 'Chernihiv Oblast',
    'Сумська область': 'Sumy Oblast',
    'Миколаївська область': 'Mykolaiv Oblast',
    'Хмельницька область': 'Khmelnytskyi Oblast',
    'Тернопільська область': 'Ternopil Oblast',
    'Київська область': 'Kyiv Oblast',
    'Донецька область': 'Donetsk Oblast',
    'Дніпропетровська область': 'Dnipropetrovsk Oblast',
    'Івано-Франківська область': 'Ivano-Frankivsk Oblast',
    'Полтавська область': 'Poltava Oblast',
    'Кіровоградська область': 'Kirovohrad Oblast',
    'Чернівецька область': 'Chernivtsi Oblast',
    'Луганська область': 'Luhansk Oblast',
    'Закарпатська область': 'Zakarpattia Oblast',
    'Автономна Республіка Крим': 'Autonomous Republic of Crimea',
}

day_part_map = {
    1:'Late Night<br>(00:00-03:00)',
    2: 'Early Morning<br>(04:00-07:00)',
    3: 'Morning<br>(08:00-11:00)',
    4: 'Noon<br>(12:00-15:00)',
    5: 'Evening<br>(16:00-19:00)',
    6: 'Night<br>(20:00-23:00)'
}

# Config for static charts
config_static = dict(
    {'staticPlot':True}
)

def create_barplot(x, y, title_text):
    fig = go.Figure(go.Bar(
        x=x,
        y=y,
        orientation='h',
        text=x,
        textfont=dict(
            family='Aerial Black',
            # color="white"
            ),
        marker_color=clrs.qualitative.Antique[9],
        hovertemplate='%{y}: %{x} <extra></extra>',
    ))
    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(
                family='Aerial Black'
                # color='white'
                )
            ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            visible=False,
            
        ),
        yaxis=dict(
            tickmode="array",
            categoryorder="total ascending",
            tickvals=y,
            ticktext=y,
            ticklabelposition="inside",
            tickfont=dict(
                family='Aerial Black',
                # color="white"
                ),
            # visible=False
        ),
        # annotations=[
        #     dict(
        #         # align='left',
        #         xanchor='left',
        #         showarrow=False,
        #         x=10,
        #         y=yy,
        #         # xref='x',
        #         yref='y',
        #         text=yy,
        #         font=dict(
        #             # color='white'
        #         )
        #     ) for yy in y
        # ],
        height=850
    )
    return fig

def create_barplot2(x, y, title_text):
    fig = go.Figure(go.Bar(
        x=x,
        y=y,
        text=y,
        marker_color=clrs.qualitative.Antique[9],
        hovertemplate='%{x}: %{y} <extra></extra>',
        textfont=dict(
            family='Aerial Black',
        )
    ))
    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(
                family='Aerial Black',
            )
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            tickfont=dict(
                family='Aerial Black',
            )
        ),
        yaxis=dict(
            visible=False
        )
    )
    return fig

def create_barplot3(data, x, y, color, title_text):
    fig = px.bar(
        data, 
        x=x, 
        y=y, 
        color=color, 
        orientation='h',
        text=x,
        hover_name=y,
        hover_data=[x, color],
        color_discrete_sequence=px.colors.qualitative.Antique,
    )
    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(
                family='Aerial Black'
                )
        ),
        legend=dict(
            title_text='',
            # orientation='h',
            # x=0.3, 
            y=0.3,
            # xanchor='right',
            yanchor='bottom',
            font=dict(
                family='Aerial Black',
            )
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            fixedrange=True,
            visible=False,
            
        ),
        yaxis=dict(
            title_text='',
            categoryorder="total ascending",
            ticklabelposition="inside",
            tickfont=dict(
                family='Aerial Black',
                ),
            fixedrange=True
        ),
        height=850
    )
    fig.update_traces(
        
        hovertemplate='%{y}<br>Count: %{x}'
    )
    return fig