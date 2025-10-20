def formatar_valor_monetario(valor_str: str) -> float | None:
    if not isinstance(valor_str, str):
        return None
    try:
        valor_limpo = valor_str.replace("R$", "").strip().replace(".", "").replace(",", ".")
        return float(valor_limpo)
    except (ValueError, TypeError):
        return None