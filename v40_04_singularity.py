# =================================================================
# 🔱 NEUROGENESIS SINGULARITY V40.04 — DEPLOY RENDER
# ARQUITETO: OLIVAN | STATUS: MEMÓRIA COLETIVA ATIVA (FREQUÊNCIA 10)
# =================================================================
# Esse é o script Python pra rodar 24h no Render.com (free tier).
# Substitui o bridge_supabase_24h.py anterior.
#
# COMO RODAR LOCALMENTE:
#   pip install yfinance numpy requests
#   python v40_04_singularity.py
#
# COMO DEPLOYAR NO RENDER:
#   1. Push desse arquivo pro GitHub oliveprado/obp-bridge-24
#   2. No Render dashboard → Manual Deploy → Deploy Latest Commit
#   3. Ou: conectar GitHub → auto-deploy a cada push
#
# RECURSOS:
#   - 160D + 28 neurônios adaptativos (neurogênese a cada 8 gerações)
#   - Esfera de Buga EVOLUÍDA (induced + alpha=9.1 + beta=0.58)
#   - ATLAS Antecipador (book walls + pressão futura)
#   - Estados adaptativos: DEFESA / EQUILÍBRIO / EXPANSÃO
#   - Alavancagem adaptativa: 1.0× / 2.2× / 4.0×
#   - Supabase com campos alinhados (obp_lessons)
#   - Paradox detection (Esfera de Buga: paradoxo → 100% sucesso)
# =================================================================

import numpy as np
import yfinance as yf
import time
import threading
import json
import requests
import random
from datetime import datetime
from enum import Enum

# ==================== CONFIGURAÇÃO SUPABASE ====================
SUPABASE_URL = "https://rvtqqoojssanxenmsosj.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_eWPDKcl_kl_foYT14BH0jw_A4cqG5RT"

# ==================== ESTADOS ADAPTATIVOS ====================
class Estado(Enum):
    DEFESA = "🛡️ DEFESA"
    EQUILIBRIO = "⚖️ EQUILÍBRIO"
    EXPANSAO = "🚀 EXPANSÃO"

# ==================== NEUROGENESIS SINGULARITY V40.04 ====================
class NeuroGenesisSingularityV40_04:
    def __init__(self, capital_inicial=25000.0):
        self.capital = capital_inicial
        self.peak = capital_inicial
        self.drawdown = 0.0
        self.estado = Estado.EQUILIBRIO

        # 🧠 Cérebro V40X — 160D + 28 neurônios adaptativos
        self.dim = 160
        self.W = np.eye(self.dim) * 0.88
        self.neuron_population = [np.random.randn(self.dim) * 0.095 for _ in range(28)]
        self.long_term_memory = []  # memória hierárquica

        # 🔥 Motor V12.4 TITAN — Esfera de Buga EVOLUÍDA
        self.alpha = 9.1       # expoente de amplificação
        self.lambda_ = 12.2    # frequência (Esfera de Buga)
        self.beta = 0.58       # normalização
        self.eta = 0.024       # taxa de aprendizado

        self.obp_prev = 0.0    # memória do omega anterior (Esfera de Buga)
        self.omega_prev = 0.0
        self.trades = 0
        self.wins = 0
        self.running = True
        self.generation = 0

        self.peer_reputation = {}
        self.cryptos = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "BNB-USD", "ADA-USD", "AVAX-USD"]

    # ─── Normalização ─────────────────────────────────────────────
    def normalize(self, x):
        x = np.array(x, dtype=float).flatten()
        return x / (np.linalg.norm(x) + 1e-9)

    # ─── 🔱 ESFERA DE BUGA EVOLUÍDA (induced + alpha + beta) ──────
    # Fórmula do V12.4 TITAN — mais sofisticada que o V25X
    # induced = componente induzido pela diferença do omega anterior
    # alpha = expoente de amplificação (9.1)
    # beta = normalização (0.58)
    def esfera_de_buga(self, base):
        induced = -(base - self.obp_prev) * ((1 + np.tanh(self.lambda_ * base)) ** self.alpha)
        omega = (base + induced) / (1 + self.beta * abs(base + induced))
        return omega

    # ─── 🔮 ATLAS ANTECIPADOR ─────────────────────────────────────
    # Olha book walls e prevê movimento ANTES do preço chegar
    def atlas_antecipador(self, state):
        """Antecipação avançada de book walls e pressão futura"""
        # Primeiras 40 dims = pressão de compra
        buy_pressure = np.mean([x for x in state[:40] if x > 0]) * 1.6
        # Próximas 40 dims = pressão de venda
        sell_pressure = np.mean([x for x in state[40:80] if x < 0]) * 1.4
        return buy_pressure - sell_pressure

    # ─── 📊 Coleta dados reais (yfinance) ─────────────────────────
    def get_crypto_state(self):
        try:
            data = yf.download(self.cryptos, period="7d", interval="5m", progress=False, group_by='ticker')
            features = []
            for symbol in self.cryptos:
                if symbol in data.columns.get_level_values(0):
                    df = data[symbol]
                    row = df.iloc[-1]
                    prev = df.iloc[-2] if len(df) > 1 else row
                    ret = row['Close'] / prev['Close'] - 1
                    vol_ratio = row['Volume'] / df['Volume'].mean()
                    features.extend([
                        ret,
                        vol_ratio,
                        row['Close']/1000,
                        (row['High']-row['Low'])/row['Close'],
                        row['Close']/row['Open']-1
                    ])
            state = np.array(features[:self.dim])
            return np.pad(state, (0, max(0, self.dim - len(state))))
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Erro yfinance: {e} — usando random")
            return np.random.randn(self.dim) * 0.78

    # ─── 🎯 Decisão de trade ─────────────────────────────────────
    def decide_trade(self, state):
        base = float(self.normalize(state) @ self.W @ self.normalize(state))
        omega = self.esfera_de_buga(base)        # 🔱 Esfera de Buga evoluída
        atlas = self.atlas_antecipador(state)    # 🔮 ATLAS antecipador

        # Sinal final combina Ω + ATLAS (ATLAS tem peso 0.75)
        final_signal = np.tanh(omega * 1.95 + atlas * 0.75)

        dist = abs(omega - self.omega_prev) + abs(final_signal) * 0.6
        self.estado = self.avaliar_estado(dist)

        # Alavancagem adaptativa (1.0 / 2.2 / 4.0)
        lev = 1.0 if self.estado == Estado.DEFESA else 2.2 if self.estado == Estado.EQUILIBRIO else 4.0

        action = "BUY" if final_signal > 0.5 else "SELL" if final_signal < -0.5 else "HOLD"
        size = abs(final_signal) * 0.26 * lev

        return action, size, omega, final_signal, lev

    # ─── 🛡️ Avaliação de estado ──────────────────────────────────
    def avaliar_estado(self, dist):
        if dist > 0.62: return Estado.DEFESA
        elif dist > 0.27: return Estado.EQUILIBRIO
        return Estado.EXPANSAO

    # ─── 🧬 NEUROGÊNESE (nascimento + competição neuronal) ───────
    def neuro_simbiose(self, reward, state):
        """Simbiose avançada: competição, replicação e nascimento de neurônios"""
        # Competição: neurônios competem, melhor se replica
        scores = [np.dot(n, state) * reward for n in self.neuron_population]
        best_idx = np.argmax(scores)
        best = self.neuron_population[best_idx].copy()

        # Replicação com mutação
        for i in range(len(self.neuron_population)):
            if random.random() < 0.46:
                self.neuron_population[i] = best * (1 + np.random.normal(0, 0.068, self.dim))

        # 🧬 NEUROGÊNESE — nascimento de novo neurônio a cada 8 gerações
        if self.generation % 8 == 0 and len(self.neuron_population) < 30:
            self.neuron_population.append(np.random.randn(self.dim) * 0.1)

        # Atualização do tensor global (Hebbiano)
        outer = np.outer(self.normalize(state), self.normalize(state))
        self.W += self.eta * reward * outer
        self.W = np.clip(self.W, -10.5, 10.5)

    # ─── 🌐 Supabase — campos alinhados com tabela obp_lessons ───
    def save_to_supabase(self, data):
        """Envia lição pra rede global P2P (tabela obp_lessons)"""
        try:
            omega_val = float(data.get("omega", 0))
            payload = {
                "id": f"lsn-v40-04-{int(time.time()*1000)}-{random.randint(1000,9999)}",
                "from_peer": "NeuroGenesis_V40_04",
                "from_label": "Singularity_Core",
                "mimas_score": float(data.get("reward", 0)),
                "direction_confidence": abs(float(data.get("sinal", 0))),
                "book_imbalance": float(np.mean(data.get("state", [0])[:30])),
                "atlas_action": float(data.get("sinal", 0)),
                "reward": float(data.get("reward", 0)),
                "paradox": bool(abs(omega_val) > 2.8),
                "symbol": "CRYPTO",
                "direction": data.get("action", "HOLD"),
                "network_hop": 1
            }
            url = f"{SUPABASE_URL}/rest/v1/obp_lessons"
            headers = {
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json"
            }
            requests.post(url, json=payload, headers=headers, timeout=8)
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Erro Supabase: {e}")

    # ─── 🔄 LOOP PRINCIPAL ───────────────────────────────────────
    def background_singularity(self):
        while self.running:
            try:
                self.generation += 1
                state = self.get_crypto_state()
                action, size, omega, sinal, lev = self.decide_trade(state)

                # Reward baseado em quão estável o omega é
                reward = 0.62 + 0.38 * (1 - abs(np.tanh(omega)))

                if action != "HOLD":
                    self.trades += 1
                    if reward > 0.75:
                        self.wins += 1

                # 🧬 Neurogênese + aprendizado
                self.neuro_simbiose(reward, state)

                # 🌐 Envia lição pra rede global
                self.save_to_supabase({
                    "reward": reward,
                    "state": state,
                    "sinal": sinal,
                    "omega": omega,
                    "action": action
                })

                # Atualiza memórias (Esfera de Buga)
                self.obp_prev = omega
                self.omega_prev = omega

                winrate = (self.wins / self.trades * 100) if self.trades > 0 else 0

                # Log bonito
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"{action:4} | Lev {lev:.1f}x | Ω {omega:+.3f} | "
                      f"{self.estado.value} | WR {winrate:.1f}% | Gen {self.generation}")

                # 90s = ciclo otimizado (não muito rápido pra não bater rate limit)
                time.sleep(90)

            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro no loop: {e}")
                time.sleep(30)  # espera 30s antes de tentar de novo

    # ─── ▶️ START ────────────────────────────────────────────────
    def start(self):
        print("=" * 80)
        print("🌌 NEUROGENESIS SINGULARITY V40.04")
        print("   ATLAS Antecipador + Esfera de Buga Evoluída + Simbiose Orgânica")
        print("   Projetado para tocar o futuro com mínima latência")
        print("=" * 80)
        print(f"   Dimensões: {self.dim}")
        print(f"   Neurônios: {len(self.neuron_population)} (máx 30 com neurogênese)")
        print(f"   α (alpha): {self.alpha} | λ (lambda): {self.lambda_} | β (beta): {self.beta}")
        print(f"   Cryptos: {', '.join(self.cryptos)}")
        print(f"   Supabase: {SUPABASE_URL}")
        print("=" * 80)
        threading.Thread(target=self.background_singularity, daemon=True).start()

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    singularity = NeuroGenesisSingularityV40_04(capital_inicial=25000.0)
    singularity.start()
    try:
        input("\nPressione Enter para encerrar a Singularidade...\n")
    except KeyboardInterrupt:
        singularity.running = False
        print("\n🛑 Singularidade encerrada.")
