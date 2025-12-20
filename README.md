# API para consulta de livros
*Tech Challenge da Fase 1 do curso de [pós-graduação em Engenharia de Machine Learning FIAP](https://postech.fiap.com.br/curso/machine-learning-engineering/)*

## Descrição do projeto
*[descrição e contexto]*

Informações disponíveis dos livros:
- Título
- Preço
- Rating
- Disponibilidade
- Categoria
- Imagem

## Arquitetura
*[colocar o desenho da arquitetura]*
- Pipeline desde ingestão -> processamento -> API -> consumo
- Arquitetura pensada para escalabilidade futura
- Cenário de uso para cientistas de dados/ML
- Plano de integração como modelos de ML

## Instalação e configuração

## Rotas da API (Endpoints)
**Obrigatórios:**
1. `GET /api/v1/books` | listar todos os livros disponíveis na base de dados)
2. `GET /api/v1/books/{id}` | retorna detalhes completos de um livro específico pelo ID
3. `GET /api/v1/books/search?title={title}&category={category}` | busca livros por título e/ou categoria)
4. `GET /api/v1/categories` | lista todas as categorias de livros disponíveis
5. `GET /api/v1/health` | verifica status da API e conectividade com os dados
6. `swagger` | documentação

**Opcionais:**
1. `GET /api/v1/stats/overview` | estatísticas gerais da coleção (total de livros, preço médio, distribuição de ratings)
2. `GET /api/v1/stats/categories` | estatísticas detalhadas por categoria (quantidade de livros, preços por categoria)
3. `GET /api/v1/books/top-rated` | lista os livros com melhor avaliação (rating mais alto)
4. `GET /api/v1/books/price-range?min={min}&max={max}` | filtra livros dentro de uma faixa de preço específica

**[Opcional] Sistema de autenticação**
1. `POST /api/v1/auth/login` | obter token
2. `POST /api/v1/auth/refresh` | renovar token
3. `/api/v1/scraping/trigger` | proteger endpoints de admin

**[Opcional] Pipeline ML-ready (endpoints para consumo de modelos ML)**
1. `GET /api/v1/ml/features` | dados formatados para features
2. `GET /api/v1/ml/training-data` | dataset para treinamento
3. `POST /api/v1/ml/predictions` | endpoint para receber predições

**[Opcional] Monitoramento e analytics**
1. Logs estruturados de todas as chamadas
2. Métricas de performance da API
3. Dashboard simples de uso (streamlit)

## Exemplos de chamadas com requests/responses

## Instruções para execução

## Referências
[Books to scrape](https://books.toscrape.com/)
