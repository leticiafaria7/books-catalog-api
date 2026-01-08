# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import render_template
from sqlalchemy import func
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from ..instances import db, bp, Book

# ----------------------------------------------------------------------------------------------- #
# Página inicial
# ----------------------------------------------------------------------------------------------- #

@bp.route("/")
def home():

    # ----------------------------------------------------------------------------------------------- #
    # Big numbers
    # ----------------------------------------------------------------------------------------------- #

    total_books = db.session.query(func.count(Book.id)).scalar()
    total_categories = db.session.query(func.count(func.distinct(Book.category))).scalar()
    mean_price = round(db.session.query(func.avg(Book.price)).scalar(), 2)
    min_price, max_price = db.session.query(
        func.min(Book.price), func.max(Book.price)
    ).first()

    # ----------------------------------------------------------------------------------------------- #
    # Distribuição de ratings
    # ----------------------------------------------------------------------------------------------- #

    ratings = (
        db.session.query(Book.rating, func.count(Book.id).label("qtd"))
        .group_by(Book.rating)
        .order_by(Book.rating.desc())
        .all()
    )

    fig_rating = px.bar(
        x=[r.qtd for r in ratings],
        # y=[f"{str(r.rating)} {'star ' if r.rating == 1 else 'stars '}" for r in ratings],
        y = ['⭐' * r.rating for r in ratings],
        text=[r.qtd for r in ratings],
        orientation="h"
    )

    fig_rating.update_layout(plot_bgcolor = "rgba(0, 0, 0, 0)", paper_bgcolor = "rgba(0, 0, 0, 0)", height = 300, barcornerradius = 4, margin = dict(t = 100),
                             title = dict(text = '✨ Quantidade de livros por nota', font = dict(color = 'white', size = 15, family = 'Roboto')))
    fig_rating.update_traces(width = 0.5, textposition = 'outside', textfont = dict(size = 10, color = 'white'), marker_color = 'white',
                             hovertemplate = '%{x} livros avaliados com %{y}<extra></extra>')
    fig_rating.update_xaxes(title = '', tickfont = dict(size = 10, color = '#4d4d4d'), range = (0, 250), showgrid = False)
    fig_rating.update_yaxes(title = '', tickfont = dict(size = 10, color = '#d4d4d4'), showgrid = False)
    rating_chart = pio.to_html(fig_rating, full_html=False)

    # ----------------------------------------------------------------------------------------------- #
    # Distribuição de preços
    # ----------------------------------------------------------------------------------------------- #

    prices = [p[0] for p in db.session.query(Book.price).all()]
    fig_price = px.histogram(prices, nbins = 50)

    fig_price.update_layout(plot_bgcolor = "rgba(0, 0, 0, 0)", paper_bgcolor = "rgba(0, 0, 0, 0)", height = 300, showlegend = False, margin = dict(t = 100),
                            title = dict(text = '💰 Distribuição de preços', font = dict(color = 'white', size = 15, family = 'Roboto')),
                            xaxis = dict(tickformat = ".0f", tickprefix = "£"))
    fig_price.update_xaxes(range = (5, 65), tickfont = dict(size = 10, color = '#d4d4d4'), showgrid = False,
                           title = dict(text = 'Preço (£)', font = dict(color = 'white', size = 12)))
    fig_price.update_yaxes(title = '', tickfont = dict(size = 10, color = '#4d4d4d'), showgrid = False)
    fig_price.update_traces(marker_color = 'white', hovertemplate = '<extra></extra>')
    fig_price.add_hline(y = 0, line_width = 1)
    price_chart = pio.to_html(fig_price, full_html=False)

    # ----------------------------------------------------------------------------------------------- #
    # Top categorias
    # ----------------------------------------------------------------------------------------------- #
    rows = (
        db.session.query(
            Book.category.label("category"),
            func.count(Book.id).label("n_books"),
            func.avg(Book.price).label("mean_price"),
            func.avg(Book.rating).label("mean_rating")
        )
        .group_by(Book.category)
        .all()
    )

    data = []
    for r in rows:
        data.append({
            "category": r.category,
            "n_books": r.n_books,
            "mean_price": float(r.mean_price),
            "mean_rating": float(r.mean_rating)
        })

    # ---------- MÉTRICAS GLOBAIS ----------
    prices = [d["mean_price"] for d in data]
    preco_min = min(prices)
    preco_max = max(prices)
    price_range = preco_max - preco_min

    # ---------- SCORE (replicando o pandas) ----------
    data_sorted = sorted(data, key=lambda x: x["n_books"])
    n = len(data_sorted)

    for i, d in enumerate(data_sorted):
        d["score_qtd"] = (i + 1) / n
        d["score_price"] = 1 - ((d["mean_price"] - preco_min) / price_range)
        d["score_rating"] = (d["mean_rating"] - 1) / 4
        d["category_score"] = (
            d["score_qtd"] * d["score_price"] * d["score_rating"]
        )
        d["qtd_livros"] = f"{d['n_books']} livro" if d["n_books"] == 1 else f"{d['n_books']} livros"

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
        rows=1,
        cols=4,
        subplot_titles=[
            "Categorias com mais livros",
            "Menores médias de preço",
            "Mais bem avaliadas (avaliação média)",
            "Melhores scores"
        ],
        horizontal_spacing=0.1
    )

    features = {
        "n_books": (1, True, 200),
        "mean_price": (2, False, 80),
        "mean_rating": (3, True, 15),
        "category_score": (4, True, 0.5)
    }

    for feature, (col, desc, x_max) in features.items():
        tmp = sorted(sorted(
            [d for d in data if d["n_books"] > 1],
            key=lambda x: x[feature],
            reverse = desc
        )[:5],
        key=lambda x: x[feature],
        reverse = not desc)

        fig.add_trace(
            go.Bar(
                x=[d[feature] for d in tmp],
                y=[d["category"] for d in tmp],
                text=[
                    f"{round(d[feature], 2)} ({d['qtd_livros']})"
                    if feature in ["mean_price", "mean_rating"]
                    else round(d[feature], 2)
                    for d in tmp
                ],
                orientation="h",
                hovertemplate = '<extra></extra>'
            ),
            row=1,
            col=col
        )

        fig.update_xaxes(range=(0, x_max), tickfont = dict(size = 10, color = '#4d4d4d'), showgrid = False, row=1, col=col)
        fig.update_yaxes(title = '', tickfont = dict(size = 10, color = '#d4d4d4'), showgrid = False, domain=[0, 0.95], row=1, col=col)

    fig.update_layout(
        plot_bgcolor = "rgba(0, 0, 0, 0)", 
        paper_bgcolor = "rgba(0, 0, 0, 0)",
        showlegend=False,
        title = title,
        barcornerradius=4,
        height=320,
        # margin = dict(t = 150)
    )

    fig.update_traces(
        width=0.5,
        textposition="outside",
        marker_color="white",
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
            "ele é maior quanto:<br>"
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

    top_categories_chart = pio.to_html(fig, full_html=False)

    # ----------------------------------------------------------------------------------------------- #
    # Renderizar
    # ----------------------------------------------------------------------------------------------- #

    return render_template(
        "home.html",
        total_books=total_books,
        total_categories=total_categories,
        mean_price=str(f"{round(mean_price, 2):.2f}"),
        min_price=str(f"{round(min_price, 2):.2f}"),
        max_price=str(f"{round(max_price, 2):.2f}"),
        rating_chart=rating_chart,
        price_chart=price_chart,
        top_categories_chart=top_categories_chart
    )