# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import render_template
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from ..instances import bp

# ----------------------------------------------------------------------------------------------- #
# Ler a base de dados
# ----------------------------------------------------------------------------------------------- #

df = pd.read_csv('data/base_livros.csv')

# ----------------------------------------------------------------------------------------------- #
# Página inicial
# ----------------------------------------------------------------------------------------------- #

@bp.route("/")
def home():

    # ----------------------------------------------------------------------------------------------- #
    # Big numbers
    # ----------------------------------------------------------------------------------------------- #

    total_books = df.shape[0]
    total_categories = df['category'].nunique()
    mean_price = df['price'].mean()
    min_price = df['price'].min()
    max_price = df['price'].max()

    # ----------------------------------------------------------------------------------------------- #
    # Distribuição de ratings
    # ----------------------------------------------------------------------------------------------- #

    dist_rating = df[['rating']].value_counts().reset_index(name = 'qtd').sort_values('rating', ascending = False)
    dist_rating['rating'] = dist_rating['rating'].apply(lambda x: '⭐' * x)

    fig_rating = px.bar(dist_rating, x = 'qtd', y = 'rating', text = 'qtd', orientation = "h")

    fig_rating.update_layout(plot_bgcolor = "rgba(0, 0, 0, 0)", 
                             paper_bgcolor = "rgba(0, 0, 0, 0)", 
                             height = 300, barcornerradius = 4, margin = dict(t = 100),
                             title = dict(text = '✨ Quantidade de livros por nota', 
                                          font = dict(color = 'white', size = 15, family = 'Roboto')))
    
    fig_rating.update_traces(width = 0.5, textposition = 'outside', 
                             textfont = dict(size = 10, color = 'white'), 
                             marker_color = 'white',
                             hovertemplate = '%{x} livros avaliados com %{y}<extra></extra>')
    
    fig_rating.update_xaxes(title = '', tickfont = dict(size = 10, color = '#4d4d4d'), range = (0, 250), showgrid = False)
    fig_rating.update_yaxes(title = '', tickfont = dict(size = 10, color = '#d4d4d4'), showgrid = False)

    rating_chart = pio.to_html(fig_rating, full_html=False)

    # ----------------------------------------------------------------------------------------------- #
    # Distribuição de preços
    # ----------------------------------------------------------------------------------------------- #

    fig_price = px.histogram(df['price'], nbins = 50)

    fig_price.update_layout(plot_bgcolor = "rgba(0, 0, 0, 0)", 
                            paper_bgcolor = "rgba(0, 0, 0, 0)", 
                            height = 300, showlegend = False, margin = dict(t = 100),
                            title = dict(text = '💰 Distribuição de preços', 
                                         font = dict(color = 'white', size = 15, family = 'Roboto')),
                            xaxis = dict(tickformat = ".0f", tickprefix = "£"))
    
    fig_price.update_xaxes(range = (5, 65), 
                           tickfont = dict(size = 10, color = '#d4d4d4'), showgrid = False,
                           title = dict(text = 'Preço (£)', font = dict(color = 'white', size = 12)))
    
    fig_price.update_yaxes(title = '', tickfont = dict(size = 10, color = '#4d4d4d'), showgrid = False)
    fig_price.update_traces(marker_color = 'white', hovertemplate = '<extra></extra>')
    fig_price.add_hline(y = 0, line_width = 1)

    price_chart = pio.to_html(fig_price, full_html=False)

    # ----------------------------------------------------------------------------------------------- #
    # Top categorias
    # ----------------------------------------------------------------------------------------------- #

    # ---------- GERAR BASE DE DADOS ----------

    preco_min = df['price'].min().round(2)
    preco_max = df['price'].max().round(2)

    df_categorias = df.groupby('category').agg({'title':'count', 'price':'mean', 'rating': 'mean'}).round(2).reset_index()
    df_categorias.columns = ['category', 'n_books', 'mean_price', 'mean_rating']

    max_books = df_categorias['n_books'].max()
    price_range = preco_max - preco_min

    df_categorias['decis_qtd'] = pd.qcut(df_categorias['n_books'], 10, duplicates = 'drop')
    decis = sorted(df_categorias['decis_qtd'].unique())
    dict_decis = {}
    for i in range(9):
        dict_decis[decis[i]] = (i + 1) / 10

    df_categorias['score_qtd'] = df_categorias['decis_qtd'].map(dict_decis).astype(float)
    df_categorias['score_price'] =  1 - ((df_categorias['mean_price'] - preco_min) / price_range)
    df_categorias['score_rating'] = (df_categorias['mean_rating'] - 1) / 4

    df_categorias['category_score'] = df_categorias['score_qtd'] * df_categorias['score_price'] * df_categorias['score_rating']
    df_categorias.sort_values('category_score', ascending = False).round(2).head()
    df_categorias['qtd_livros'] = df_categorias['n_books'].apply(lambda x: f"{x} {'livro' if x == 1 else 'livros'}")

    # ---------- PLOTLY ----------
    
    title = dict(
        text="📊 Top categorias",
        subtitle=dict(text="(Apenas categorias com mais de 1 livro)", 
                        font = dict(color = 'white')),
        x=0.05,
        xanchor="left",
        font = dict(color = 'white', size = 15, family = 'Roboto')
    )

    fig = make_subplots(
        rows = 1, cols = 4,
        subplot_titles = [
            "Categorias com mais livros",
            "Menores médias de preço",
            "Mais bem avaliadas (avaliação média)",
            "Melhores scores"
        ],
        horizontal_spacing = 0.1
    )

    features = {
        "n_books": (1, True, 200),
        "mean_price": (2, False, 80),
        "mean_rating": (3, True, 15),
        "category_score": (4, True, 0.5)
    }

    for feature, (col, desc, x_max) in features.items():
        tmp = df_categorias[df_categorias['n_books'] > 1][['category', feature, 'qtd_livros']].sort_values(feature, ascending = not desc).head().sort_values(feature, ascending = desc)
        tmp['category'] = tmp['category'] + ' '
        if feature in['mean_price', 'mean_rating']:
            tmp['text'] = tmp[feature].astype(str) + ' (' + tmp['qtd_livros'] + ')'
        else:
            tmp['text'] = tmp[feature].round(3)

        fig.add_trace(
            go.Bar(
                x = tmp[feature],
                y = tmp['category'],
                text = tmp['text'],
                orientation = "h",
                hovertemplate = '<extra></extra>'
            ),
            row = 1,
            col = col
        )

        fig.update_xaxes(range=(0, x_max), tickfont = dict(size = 10, color = '#4d4d4d'), showgrid = False, row=1, col=col)
        fig.update_yaxes(title = '', tickfont = dict(size = 10, color = '#d4d4d4'), showgrid = False, domain=[0, 0.95], row=1, col=col)

    fig.update_layout(
        plot_bgcolor = "rgba(0, 0, 0, 0)", 
        paper_bgcolor = "rgba(0, 0, 0, 0)",
        showlegend = False,
        title = title,
        barcornerradius = 4,
        height = 320,
    )

    fig.update_traces(
        width = 0.5,
        textposition = "outside",
        marker_color = "white",
        textfont = dict(color = 'white', size = 10)
    )

    fig.update_annotations(font = dict(color = "white", size = 11, family = 'Roboto'))

    # Ícone (imagem)
    fig.add_layout_image(
        dict(
            source="/static/question_mark.png",
            xref="x4 domain",
            yref="y4 domain",
            x=1.02,
            y=1.18,
            sizex=0.1,
            sizey=0.1,
            xanchor="left",
            yanchor="top",
            layer="above"
        )
    )

    # Ponto invisível para hover
    fig.add_annotation(
        x=1.03,
        y=1.18,
        xref="x4 domain",
        yref="y4 domain",
        xanchor='left',
        text="   ",  # texto vazio
        showarrow=False,
        hovertext=(
            "O score da categoria é um valor entre 0 e 1;<br>"
            "ele é maior quanto:<br><br>"
            "• Maior a quantidade de livros<br>"
            "• Menor o preço médio<br>"
            "• Maior o rating médio"
        ),
        hoverlabel=dict(
            bgcolor="#4d4d4d",
            font_size=12,
            font_family="Roboto"
        ),
    )

    top_categories_chart = pio.to_html(fig, full_html = False)

    # ----------------------------------------------------------------------------------------------- #
    # Renderizar os gráficos na página inicial
    # ----------------------------------------------------------------------------------------------- #

    return render_template(
        "home.html",
        total_books = total_books,
        total_categories = total_categories,
        mean_price = str(f"{round(mean_price, 2):.2f}"),
        min_price = str(f"{round(min_price, 2):.2f}"),
        max_price = str(f"{round(max_price, 2):.2f}"),
        rating_chart = rating_chart,
        price_chart = price_chart,
        top_categories_chart = top_categories_chart
    )