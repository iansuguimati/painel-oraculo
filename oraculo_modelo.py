#!/usr/bin/env python3
"""ORACULO - Modelo de gols ATAQUE/DEFESA (Maher / Poisson regularizado + recencia).
Ajusta ataque e defesa por selecao dos jogos internacionais reais (2024+, API ESPN),
com correcao de adversario automatica, regularizacao L2 (Newton, numpy puro) e
PESO POR RECENCIA (jogo recente pesa mais; meia-vida ~300 dias, validado).
Uso: python3 oraculo_modelo.py [--cache]  -> grava ratings_ad.json
lambda_casa = exp(b0 + atk[casa] + dfn[fora] + home se anfitriao senao 0)"""
import numpy as np, json, urllib.request, time, sys, os
from math import exp
from datetime import date

ANFITRIOES = {"USA", "MEX", "CAN"}

# Craques GRITANTES de verdade: top-punhado do mundo E em forma em 2026 (curado 22/06).
# Tirei Cristiano (41a, fora do top) e De Bruyne (em queda); adicionei Yamal (Espanha) e
# Dembele (atual Bola de Ouro 2025). Messi e Salah ficam como lendas ainda decisivas.
# Boost regularizado +8% na lambda de ATAQUE do time (validado 10 jogos OOS, 99% bootstrap).
ESTRELAS = {"FRA": "Mbappe / Dembele", "ESP": "Lamine Yamal", "ENG": "Harry Kane",
            "NOR": "Haaland", "BRA": "Vinicius Jr", "ARG": "Messi", "EGY": "Salah"}
BOOST_ESTRELA = 0.08

# Fator de TORNEIO (abertura): esta Copa esta MUITO aberta - 3.05 gols/jogo REAL vs ~2.47
# que o modelo (calibrado em amistosos/eliminatorias) esperava. Escala a lambda p/ casar a
# media observada. Validado OUT-OF-SAMPLE (treino 22 jogos / teste 22): RPS 0.1676->0.156,
# Over2.5 42%->56% (real 59%), bolao +14 pts. Regularizado em 1.18 (abaixo do cru 1.235).
# A tarefa diaria RECALIBRA por media movel (sobe se seguir aberto, cai no mata-mata).
G_TORNEIO = 1.073  # mata-mata (fases avancadas ficaram mais abertas, 2.82 gols)

def fator_torneio(media_real, media_modelo, peso=0.8, cap=1.30, piso=1.0):
    """Escala de abertura do torneio: razao (gols reais / gols esperados), regularizada.
    peso<1 encolhe rumo a 1 (anti-overfit); cap evita explosao em amostra pequena."""
    if not media_modelo or media_modelo <= 0:
        return 1.0
    g = 1.0 + peso * (media_real / media_modelo - 1.0)
    return max(piso, min(cap, g))

# Craques com risco de lesao/poupanca: so aplicar o boost se CONFIRMADO no XI titular.
# A tarefa diaria checa a escalacao (WebSearch) antes de cada jogo desses times.
CRAQUE_CHECAR_ESCALACAO = {"ESP": "Lamine Yamal (voltou de lesao de coxa em abr/26; apto, mas confirmar no XI)"}

def _get(url, timeout=20):
    return json.load(urllib.request.urlopen(url, timeout=timeout))

def pull_matches():
    ids = {}
    base = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates="
    for D in ["20260611","20260612","20260613","20260614","20260615","20260616",
              "20260617","20260618","20260619","20260620","20260621","20260622",
              "20260623","20260624","20260625","20260626","20260627"]:
        try:
            d = _get(base + D)
        except Exception:
            continue
        for e in d.get("events", []):
            for c in e["competitions"][0]["competitors"]:
                ids[c["team"]["abbreviation"]] = c["team"]["id"]
    matches, seen = [], set()
    for ab, tid in ids.items():
        try:
            d = _get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/teams/{tid}/schedule")
        except Exception:
            continue
        for ev in d.get("events", []):
            comp = ev.get("competitions", [{}])[0]
            if comp.get("status", {}).get("type", {}).get("state") != "post":
                continue
            dt = ev.get("date", "")[:10]
            if dt < "2024-01-01":
                continue
            cs = comp.get("competitors", [])
            if len(cs) != 2:
                continue
            try:
                h = [x for x in cs if x.get("homeAway") == "home"][0]
                a = [x for x in cs if x.get("homeAway") == "away"][0]
                ha, aa = h["team"]["abbreviation"], a["team"]["abbreviation"]
                hs = int(h.get("score", {}).get("value"))
                as_ = int(a.get("score", {}).get("value"))
            except Exception:
                continue
            key = tuple(sorted([ha, aa])) + (dt, hs + as_)
            if key in seen:
                continue
            seen.add(key)
            matches.append({"d": dt, "h": ha, "hs": hs, "a": aa, "as": as_})
        time.sleep(0.04)
    return matches

def fit(matches, alpha=4.0, iters=25, half=300):
    teams = sorted(set([m["h"] for m in matches] + [m["a"] for m in matches]))
    ti = {t: i for i, t in enumerate(teams)}
    T = len(teams)
    P = 2 * T + 2
    hoje = date.today()
    def peso(d):
        try:
            y_, mo_, dd_ = map(int, d.split("-"))
            return 0.5 ** (max((hoje - date(y_, mo_, dd_)).days, 0) / half)
        except Exception:
            return 1.0
    rows, y, wts = [], [], []
    for m in matches:
        wt = peso(m["d"])
        r = np.zeros(P); r[ti[m["h"]]] = 1; r[T + ti[m["a"]]] = 1; r[2*T] = 1; r[2*T+1] = 1
        rows.append(r); y.append(m["hs"]); wts.append(wt)
        r = np.zeros(P); r[ti[m["a"]]] = 1; r[T + ti[m["h"]]] = 1; r[2*T+1] = 1
        rows.append(r); y.append(m["as"]); wts.append(wt)
    X = np.array(rows); y = np.array(y, float); W = np.array(wts)
    w = np.zeros(P)
    R = np.ones(P); R[2*T+1] = 0.0
    for _ in range(iters):
        mu = np.exp(np.clip(X @ w, -10, 10))
        g = X.T @ (W*(mu - y)) + 2*alpha*R*w
        H = X.T @ (X * (W*mu)[:, None]) + 2*alpha*np.diag(R) + 1e-6*np.eye(P)
        w = w - np.linalg.solve(H, g)
    atk = {t: float(w[ti[t]]) for t in teams}
    dfn = {t: float(w[T + ti[t]]) for t in teams}
    return {"b0": float(w[2*T+1]), "home": float(w[2*T]), "alpha": alpha, "atk": atk, "dfn": dfn, "teams": teams}

def lam(model, home, away, neutral=True):
    hadv = (0.50 if home in ANFITRIOES else 0.0) if neutral else model["home"]  # bonus anfitriao de Copa (validado: hosts venceram 4/5 + literatura)
    lh = exp(model["b0"] + model["atk"].get(home, 0) + model["dfn"].get(away, 0) + hadv)
    la = exp(model["b0"] + model["atk"].get(away, 0) + model["dfn"].get(home, 0))
    if home in ESTRELAS:                  # fator estrela: craque eleva o ataque (validado, declarado)
        lh *= (1 + BOOST_ESTRELA)
    if away in ESTRELAS:
        la *= (1 + BOOST_ESTRELA)
    lh *= G_TORNEIO; la *= G_TORNEIO     # fator de abertura do torneio (Copa correndo aberta)
    return lh, la

def fator_empate(lh, la, k=0.5, base=1.6, piso=1.0):
    """Fator de empate F DEPENDENTE DO CONTEXTO (validado 22/06/2026, 40 jogos OOS).
    Em jogo parelho o favorito tropeca mais (empate comum) -> F alto (=base 1.6).
    Em mismatch o empate e raro -> F cai linearmente com o gap de forca |lh-la|.
    Corrige a humildade-excessiva do modelo em mismatch (Brasil x Haiti, Japao x Suecia).
    Ganho OOS: RPS 0.1758->0.1724, acerto 55->55%, bolao +6pts; melhora 27/40 jogos (91% bootstrap).
    k regularizado em 0.5 (otimo cru 0.7-1.0 nao adotado, anti-overfit)."""
    return max(piso, base - k * abs(lh - la))

def fator_decisao(stakes):
    """Peso de DECISAO/tabela (declarado, hipotese - 24/06/2026). Modula a prob de EMPATE
    pela motivacao REAL que o mercado pode subestimar. O mercado ja precifica must-win, entao
    o fator e PEQUENO e so atua onde a tabela/chaveamento da sinal claro:
      'seeding_forte': os 2 ja classificados mas brigam por 1o lugar com PREMIO grande
                       (adversario mais fraco + descanso + mando no mata-mata) -> os 2 vao
                       pra vitoria -> MENOS empate (x0.82).
      'mustwin_both' : empate elimina os 2 -> os 2 atacam -> MENOS empate (x0.80).
      'biscotto'     : empate CLASSIFICA os 2 (melhor 3o) -> jogo trava -> MAIS empate (x1.12).
      'mata_mata'   : jogo de mata-mata (empate de 90min e RARO ~15% real vs 34% do modelo;\n                       os times decidem no tempo normal) -> MENOS empate (x0.50, validado 13 jogos).\n      'normal'/'dead': neutro (x1.0) - deixa o mercado mandar.
    Retorna multiplicador da prob de empate; aplicar DEPOIS do blend e renormalizar.
    So vale pro PALPITE do bolao (nao mexe em edge/tips)."""
    return {"seeding_forte": 0.82, "mustwin_both": 0.80, "biscotto": 1.12,
            "mata_mata": 0.50, "normal": 1.0, "dead": 1.0}.get(stakes, 1.0)

def aplica_decisao(M, stakes):
    """Reescala a matriz pra refletir o fator de decisao na prob de empate."""
    if stakes in (None, "normal", "dead"):
        return M
    P = prob_1x2(M); fD = fator_decisao(stakes)
    Pn = [P[0], P[1]*fD, P[2]]; sN = sum(Pn); Pn = [x/sN for x in Pn]
    fac = [Pn[k]/P[k] if P[k] > 0 else 0.0 for k in range(3)]
    R, C = len(M), len(M[0]); out = [[0.0]*C for _ in range(R)]
    for i in range(R):
        for j in range(C):
            o = 0 if i > j else (1 if i == j else 2)
            out[i][j] = M[i][j]*fac[o]
    t = sum(sum(r) for r in out)
    return [[v/t for v in r] for r in out]

def pontos_prodefy(i, j, a, b):
    """Pontuacao Prodefy: 6 placar exato, 4 vencedor+1 placar, 3 so vencedor, 1 so 1 placar, 0."""
    if i == a and j == b:
        return 6
    wc = (i > j and a > b) or (i < j and a < b) or (i == j and a == b)
    og = (i == a) or (j == b)
    return 4 if wc and og else 3 if wc else 1 if og else 0

def prob_1x2(M):
    """Probabilidades 1/X/2 (casa/empate/fora) a partir da matriz de placares."""
    R, C = len(M), len(M[0])
    H = sum(M[i][j] for i in range(R) for j in range(C) if i > j)
    D = sum(M[i][i] for i in range(min(R, C)))
    return [H, D, 1.0 - H - D]

def blend_mercado(M, p_mercado, w=0.5):
    """Blinda o palpite do BOLAO com o sinal do MERCADO (grandes favoritos das casas).
    P_blend = w*P_modelo + (1-w)*P_mercado (use shin_probs do oraculo_devig nas odds).
    Reescala a matriz de placares p/ casar P_blend mantendo a FORMA do modelo. SO para o
    PALPITE - NUNCA para edge/tips (esses ficam cegos as odds: anti-circularidade).
    O mercado ja precifica estrelas/must-win/lesoes, entao o blend subsume esses fatores.
    Validado OUT-OF-SAMPLE (treino 22 / teste 22): RPS modelo 0.158 -> blend 0.135."""
    Pm = prob_1x2(M)
    Pb = [w * Pm[k] + (1 - w) * p_mercado[k] for k in range(3)]
    s = sum(Pb); Pb = [x / s for x in Pb]
    fac = [Pb[k] / Pm[k] if Pm[k] > 0 else 0.0 for k in range(3)]
    R, C = len(M), len(M[0]); out = [[0.0] * C for _ in range(R)]
    for i in range(R):
        for j in range(C):
            o = 0 if i > j else (1 if i == j else 2)
            out[i][j] = M[i][j] * fac[o]
    tot = sum(sum(r) for r in out)
    return [[v / tot for v in r] for r in out]

def placar_bolao(M, elastic=True, thr=0.10, N=7):
    """Placar do bolao que MAXIMIZA o EP do Prodefy. Com elastic=True (padrao desde 23/06,
    pedido do usuario): DESEMPATE ELASTICO - entre placares a <=thr de EP do melhor E com o
    MESMO vencedor, escolhe o de MAIS gols (Copa correndo aberta; custo ~0.03 EP/jogo, ganha
    upside de cravar o 6). Placares cheios (Inglaterra 2x1) em vez de 1x0 quando empatam."""
    R, C = len(M), len(M[0])
    def outc(i, j):
        return 0 if i > j else (1 if i == j else 2)
    tab = []
    for i in range(N):
        for j in range(N):
            e = sum(M[a][b] * pontos_prodefy(i, j, a, b) for a in range(R) for b in range(C))
            tab.append((e, i, j))
    tab.sort(reverse=True)
    best = tab[0]
    if not elastic:
        return (best[1], best[2])
    bo = outc(best[1], best[2])
    cand = [(i + j, e, i, j) for e, i, j in tab if e >= best[0] - thr and outc(i, j) == bo]
    cand.sort(reverse=True)
    return (cand[0][2], cand[0][3])

if __name__ == "__main__":
    if "--cache" in sys.argv and os.path.exists("/tmp/intl.json"):
        matches = json.load(open("/tmp/intl.json"))
    else:
        matches = pull_matches()
        json.dump(matches, open("/tmp/intl.json", "w"))
    train = [m for m in matches if m["d"] < "2026-06-11"]
    model = fit(train)
    out = {"_meta": {"modelo": "Maher ataque/defesa Poisson L2 + recencia (half 300d)",
                     "jogos_treino": len(train), "data_fit": time.strftime("%Y-%m-%d"),
                     "alpha": model["alpha"], "home_adv": round(model["home"], 3), "b0": round(model["b0"], 3)},
           "b0": model["b0"], "home": model["home"], "atk": model["atk"], "dfn": model["dfn"]}
    json.dump(out, open("ratings_ad.json", "w"), ensure_ascii=False, indent=2)
    print(f"OK: {len(train)} jogos de treino, {len(model['teams'])} selecoes.")
    for t in ["ESP","GER","IRN","URU","JPN","ARG","ALG"]:
        if t in model["atk"]:
            print(f"  {t}: ataque {exp(model['b0']+model['atk'][t]):.2f} | defesa {exp(model['b0']+model['dfn'][t]):.2f}")
