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
        self.dim = 160
        self.W = np.eye(self.dim) * 0.88
        self.neuron_population = [np.random.randn(self.dim) * 0.095 for _ in range(28)]
        self.long_term_memory = []
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

    def esfera_de_buga(self, base):
        induced = -(base - self.obp_prev) * ((1 + np.tanh(self.lambda_ * base)) ** self.alpha)
        omega = (base + induced) / (1 + self.beta * abs(base + induced))
        return omega

    def atlas_antecipador(self, state):
        buy_vals = [x for x in state[:40] if x > 0]
        sell_vals = [x for x in state[40:80] if x < 0]
        buy_pressure = (np.mean(buy_vals) * 1.6) if buy_vals else 0.0
        sell_pressure = (np.mean(sell_vals) * 1.4) if sell_vals else 0.0
        result = buy_pressure - sell_pressure
        if not np.isfinite(result):
            return 0.0
        return float(result)

    def get_crypto_state(self):
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
                        features.extend([ret, vol_ratio, close_val/1000, (high_val - low_val)/close_val if close_val > 0 else 0.0, close_val/open_val - 1 if open_val > 0 else 0.0])
                except Exception as e_sym:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ {symbol}: {e_sym}")
                    features.extend([0.0, 1.0, 0.0, 0.0, 0.0])
            state = np.array(features[:self.dim])
            state = np.nan_to_num(state, nan=0.0, posinf=0.0, neginf=0.0)
            return np.pad(state, (0, max(0, self.dim - len(state))))
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Erro yfinance: {e}")
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
            self.neuron_population.append(np.random.randn(self.dim) * 0.1)
        outer = np.outer(self.normalize(state), self.normalize(state))
        self.W += self.eta * reward * outer
        self.W = np.clip(self.W, -10.5, 10.5)

    def save_to_supabase(self, data):
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
            headers = {"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_ANON_KEY}", "Content-Type": "application/json"}
            requests.post(url, json=payload, headers=headers, timeout=8)
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Erro Supabase: {e}")

    def background_singularity(self):
        while self.running:
            try:
                self.generation += 1
                state = self.get_crypto_state()
                action, size, omega, sinal, lev = self.decide_trade(state)
                reward = 0.62 + 0.38 * (1 - abs(np.tanh(omega)))
                if action != "HOLD":
                    self.trades += 1
                    if reward > 0.75:
                        self.wins += 1
                self.neuro_simbiose(reward, state)
                self.save_to_supabase({"reward": reward, "state": state, "sinal": sinal, "omega": omega, "action": action})
                self.obp_prev = omega
                self.omega_prev = omega
                winrate = (self.wins / self.trades * 100) if self.trades > 0 else 0
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {action:4} | Lev {lev:.1f}x | Ω {omega:+.3f} | {self.estado.value} | WR {winrate:.1f}% | Gen {self.generation}")
                time.sleep(90)
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro no loop: {e}")
                time.sleep(30)

    def start(self):
        print("=" * 80)
        print("🌌 NEUROGENESIS SINGULARITY V40.04")
        print("   ATLAS Antecipador + Esfera de Buga Evoluída + Simbiose Orgânica")
        print("=" * 80)
        print(f"   Dimensões: {self.dim}")
        print(f"   Neurônios: {len(self.neuron_population)} (máx 30 com neurogênese)")
        print(f"   α={self.alpha} | λ={self.lambda_} | β={self.beta}")
        print(f"   Cryptos: {', '.join(self.cryptos)}")
        print(f"   Supabase: {SUPABASE_URL}")
        print("=" * 80)
        threading.Thread(target=self.background_singularity, daemon=True).start()

# ==================== HEALTH SERVER (Render não dorme) ====================
from http.server import HTTPServer, BaseHTTPRequestHandler
import os as _os
import json as _json

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/health', '/'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            try:
                s = _singularity_ref[0]
                response = {
                    'status': 'online',
                    'service': 'NeuroGenesis_Singularity_V40_04',
                    'generation': s.generation if s else 0,
                    'trades': s.trades if s else 0,
                    'wins': s.wins if s else 0,
                    'estado': s.estado.value if s else 'N/A',
                    'uptime_seconds': time.time() - _start_time[0],
                }
            except Exception:
                response = {'status': 'online', 'service': 'NeuroGenesis_Singularity_V40_04'}
            self.wfile.write(_json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found. Use /health')
    def log_message(self, format, *args):
        pass

_singularity_ref = [None]
_start_time = [time.time()]

def start_health_server_in_thread():
    def run():
        try:
            port = int(_os.environ.get('PORT', 10000))
            server = HTTPServer(('0.0.0.0', port), HealthHandler)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Health server ativo na porta {port}")
            server.serve_forever()
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Health server não iniciou: {e}")
    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    print("=" * 80)
    print("🚀 INICIANDO NEUROGENESIS SINGULARITY V40.04 — RENDER DEPLOY")
    print("=" * 80)
    singularity = NeuroGenesisSingularityV40_04(capital_inicial=25000.0)
    _singularity_ref[0] = singularity
    singularity.start()
    time.sleep(2)
    start_health_server_in_thread()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Sistema ativo — processo vai ficar vivo pra sempre")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        singularity.running = False
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Singularidade encerrada.")
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro fatal: {e}")
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
