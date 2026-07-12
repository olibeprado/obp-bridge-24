# =================================================================
# 🔱 NEUROGENESIS SINGULARITY V40.04 — DEPLOY RENDER
# ARQUITETO: OLIVAN | STATUS: MEMÓRIA COLETIVA ATIVA (FREQUÊNCIA 10)
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
        self.long_term_memory = []

        # 🔥 Motor V12.4 TITAN — Esfera de Buga EVOLUÍDA
        self.alpha = 9.1
        self.lambda_ = 12.2
        self.beta = 0.58
        self.eta = 0.024

        self.obp_prev = 0.0
        self.omega_prev = 0.0
        self.trades = 0
        self.wins = 0
        self.running = True
        self.generation = 0

        self.peer_reputation = {}
        self.cryptos = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "BNB-USD", "ADA-USD", "AVAX-USD"]

    def normalize(self, x):
        x = np.array(x, dtype=float).flatten()
        return x / (np.linalg.norm(x) + 1e-9)

    # ─── 🔱 ESFERA DE BUGA EVOLUÍDA ──────
    def esfera_de_buga(self, base):
        induced = -(base - self.obp_prev) * ((1 + np.tanh(self.lambda_ * base)) ** self.alpha)
        omega = (base + induced) / (1 + self.beta * abs(base + induced))
        return omega

    # ─── 🔮 ATLAS ANTECIPADOR (corrigido — trata listas vazias) ──────
    def atlas_antecipador(self, state):
        """Antecipação de book walls — trata listas vazias sem gerar NaN"""
        buy_vals = [x for x in state[:40] if x > 0]
        sell_vals = [x for x in state[40:80] if x < 0]
        buy_pressure = (np.mean(buy_vals) * 1.6) if buy_vals else 0.0
        sell_pressure = (np.mean(sell_vals) * 1.4) if sell_vals else 0.0
        result = buy_pressure - sell_pressure
        if not np.isfinite(result):
            return 0.0
        return float(result)

    # ─── 📊 Coleta dados reais (yfinance blindado) ─────────────────
    def get_crypto_state(self):
        """Baixa dados de cripto via yfinance — blindado contra erros comuns"""
        try:
            import logging
            logging.getLogger('yfinance').setLevel(logging.CRITICAL)
            logging.getLogger('peewee').setLevel(logging.CRITICAL)
            logging.getLogger('urllib3').setLevel(logging.CRITICAL)

            data = yf.download(self.cryptos, period="7d", interval="5m", progress=False, group_by='ticker', threads=False)
            features = []
            for symbol in self.cryptos:
                try:
                    if symbol in data.columns.get_level_values(0):
                        df = data[symbol]
                        row = df.iloc[-1]
                        prev = df.iloc[-2] if len(df) > 1 else row
                        close_val = float(row['Close']) if not np.isnan(row['Close']) else 1.0
                        prev_close = float(prev['Close']) if not np.isnan(prev['Close']) else close_val
                        ret = (close_val / prev_close - 1) if prev_close > 0 else 0.0
                        vol_mean = df['Volume'].mean()
                        vol_ratio = float(row['Volume'] / vol_mean) if vol_mean > 0 and not np.isnan(vol_mean) else 1.0
                        high_val = float(row['High']) if not np.isnan(row['High']) else close_val
                        low_val = float(row['Low']) if not np.isnan(row['Low']) else close_val
                        open_val = float(row['Open']) if not np.isnan(row['Open']) else close_val
                        features.extend([
                            ret, vol_ratio, close_val/1000,
                            (high_val - low_val)/close_val if close_val > 0 else 0.0,
                            close_val/open_val - 1 if open_val > 0 else 0.0
                        ])
                except Exception as e_sym:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ {symbol}: {e_sym}")
                    features.extend([0.0, 1.0, 0.0, 0.0, 0.0])
            state = np.array(features[:self.dim])
            state = np.nan_to_num(state, nan=0.0, posinf=0.0, neginf=0.0)
            return np.pad(state, (0, max(0, self.dim - len(state))))
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Erro yfinance geral: {e}")
            return np.random.randn(self.dim) * 0.78

    def decide_trade(self, state):
        base = float(self.normalize(state) @ self.W @ self.normalize(state))
        omega = self.esfera_de_buga(base)
        atlas = self.atlas_antecipador(state)
        final_signal = np.tanh(omega * 1.95 + atlas * 0.75)
        dist = abs(omega - self.omega_prev) + abs(final_signal) * 0.6
        self.estado = self.avaliar_estado(dist)
        lev = 1.0 if self.estado == Estado.DEFESA else 2.2 if self.estado == Estado.EQUILIBRIO else 4.0
        action = "BUY" if final_signal > 0.5 else "SELL" if final_signal < -0.5 else "HOLD"
        size = abs(final_signal) * 0.26 * lev
        return action, size, omega, final_signal, lev

    def avaliar_estado(self, dist):
        if dist > 0.62: return Estado.DEFESA
        elif dist > 0.27: return Estado.EQUILIBRIO
        return Estado.EXPANSAO

    def neuro_simbiose(self, reward, state):
        scores = [np.dot(n, state) * reward for n in self.neuron_population]
        best_idx = np.argmax(scores)
        best = self.neuron_population[best_idx].copy()
        for i in range(len(self.neuron_population)):
            if random.random() < 0.46:
                self.neuron_population[i] = best * (1 + np.random.normal(0, 0.068, self.dim))
        if self.generation % 8 == 0 and len(self.neuron_population) < 30:
            self.neuron_population.append(np
