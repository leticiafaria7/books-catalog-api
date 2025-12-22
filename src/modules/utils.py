
def sep_milhar(num, casas_decimais = 0):
    return f"{num:,.{casas_decimais}f}".replace(",", ".")


