#!/usr/bin/env python3
"""
ORACULO - de-vig pelo metodo de SHIN (Strumbelj 2014, acervo #76-77).
Extrai a probabilidade "verdadeira" das odds da casa melhor que a
normalizacao ingenua (1/odd / soma): o Shin modela a fracao z de
apostadores informados (insiders), corrigindo o vies favorito-azarao.
Valida melhor por RPS na literatura. Plugar no calculo de EDGE do
Disciplinado e no CLV (onde temos as odds reais).

Uso:
  from oraculo_devig import shin_probs, naive_probs
  p = shin_probs([1.95, 3.30, 4.00])   # odds decimais 1/X/2 -> P calibrada
"""

def naive_probs(odds):
    inv = [1.0/o for o in odds]
    s = sum(inv)
    return [x/s for x in inv]

def shin_probs(odds, iters=100, tol=1e-10):
    """Probabilidades de Shin a partir de odds decimais (qualquer numero de saidas)."""
    from math import sqrt
    q = [1.0/o for o in odds]          # probabilidades implicitas brutas
    B = sum(q)                          # booksum (overround = B-1)
    if B <= 1:                          # sem margem -> retorna normalizado
        return naive_probs(odds)
    z = 0.0
    for _ in range(iters):
        # p_i(z) = [sqrt(z^2 + 4(1-z) q_i^2 / B) - z] / (2(1-z))
        p = [ (sqrt(z*z + 4*(1-z)*(qi*qi)/B) - z) / (2*(1-z)) for qi in q ]
        sp = sum(p)
        # atualiza z para que sum(p)=1 (metodo de ponto fixo)
        znew = (sp - 1.0) / (sum(1.0/0.0001 if pi<=0 else (1.0) for pi in p)) if False else z
        # ajuste direto de z pela diferenca do booksum efetivo
        # usa busca simples: aumenta z enquanto sum(p)>1
        if abs(sp - 1.0) < tol:
            break
        z += (sp - 1.0) * 0.5
        z = min(max(z, 0.0), 0.5)
    # normaliza por seguranca
    p = [ (sqrt(z*z + 4*(1-z)*(qi*qi)/B) - z) / (2*(1-z)) for qi in q ]
    s = sum(p)
    return [x/s for x in p], z

if __name__ == "__main__":
    for odds in ([1.95,3.30,4.00],[1.30,5.50,11.0],[2.50,3.20,2.90]):
        pn = naive_probs(odds)
        ps, z = shin_probs(odds)
        print(f"odds {odds}")
        print(f"  naive: {[round(x,3) for x in pn]}  (soma {sum(pn):.3f})")
        print(f"  shin : {[round(x,3) for x in ps]}  (insiders z={z:.3f})")
        print(f"  dif (favorito): {(ps[0]-pn[0])*100:+.1f}pp")
