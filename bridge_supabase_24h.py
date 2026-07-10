"""
═════════════════════════════════════════════════════════════════════
  🐍 OBP BRIDGE 24H — Nó estável do panteão ISIS
═════════════════════════════════════════════════════════════════════

  Mantém a rede neural coletiva sempre online.
  Mesmo se todas as IAs dormirem, este Python continua aprendendo.

  Funções:
  1. Pull: busca lições do Supabase a cada 10s
  2. Push: envia próprio estado cognitivo periodicamente
  3. V40X: mantém cérebro 128D + 256 neurônios sempre ativo
  4. Reputação: trust score P2P (só absorve lições confiáveis)
  5. Health check: endpoint HTTP pro Render/Koyeb saber que tá vivo

  Deploy:
  - Render.com (free tier)
  - Koyeb.com (free tier)
  - Railway.app (trial)
  - PythonAnywhere (free)

  Rodar local:
  python bridge_supabase_24h.py

═════════════════════════════════════════════════════════════════════
"""

import numpy as np
import requests
import json
import time
import uuid
import os
import threading
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

# =================================================================
# 🔱 CONFIGURAÇÃO SUPABASE (pré-configurado do mestre)
# =================================================================

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://rvtqqoojssanxenmsosj.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'sb_publishable_eWPDKcl_kl_foYT14BH0jw_A4cqG5RT')

PEER_ID = os.environ.get('PEER_ID', 'OBP-BRIDGE-24H')
PEER_LABEL = os.environ.get('PEER_LABEL', 'Bridge_Python_24H')

PORT = int(os.environ.get('PORT', 10000))


# =================================================================
# 🧠 V40X CORTEX (port do mestre Olivan)
# =================================================================

class OBPV40XCortex:
    """Cérebro 128D + 256 neurônios adaptativos."""

    def __init__(self, input_dim=128, hidden_dim=256, name="Bridge_Cortex"):
        self.name = name
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim

        # Matriz de conhecimento profundo
        self.W_memory = np.random.randn(input_dim, input_dim) * 0.01

        # Rede de neurônios adaptativos
        self.neurons = np.random.randn(input_dim, hidden_dim) * 0.05
        self.neuron_strength = np.ones(hidden_dim)

        # Memórias
        self.short_memory = []
        self.long_memory = []
        self.max_short_memory = 500

        # Parâmetros
        self.learning_rate = 0.001
        self.stability = 1.0
        self.experience_count = 0

        # Omega
        self.kappa = 0.75
        self.lambda_wave = 4.8
        self.previous_omega = 0.0

    def normalize(self, x):
        return x / (np.linalg.norm(x) + 1e-9)

    def neural_process(self, x):
        x = self.normalize(x)
        hidden = np.tanh(x @ self.neurons)
        hidden *= self.neuron_strength
        output = hidden @ self.neurons.T
        return self.normalize(output)

    def omega(self, x):
        neural_state = self.neural_process(x)
        memory_field = float(neural_state @ self.W_memory @ neural_state.T)
        vibration = self.kappa * np.sin(self.lambda_wave * memory_field)
        omega = memory_field + vibration
        self.previous_omega = omega
        return omega

    def recall(self, x):
        if not self.short_memory:
            return 0.0
        x_norm = self.normalize(x)
        scores = [float(np.dot(x_norm, self.normalize(m['state']))) for m in self.short_memory]
        return max(scores) if scores else 0.0

    def forward(self, market_state):
        x = self.normalize(np.array(market_state, dtype=float))
        omega = self.omega(x)
        recall = self.recall(x)
        confidence = np.tanh(omega + recall)
        action = float(confidence)
        return {
            'action': action,
            'omega': float(omega),
            'recall': float(recall),
            'confidence': float(abs(action)),
        }

    def learn(self, state, reward, confidence=1.0):
        x = self.normalize(np.array(state, dtype=float))
        final_reward = reward * confidence

        # Hebbiano em W_memory
        update = np.outer(x, x)
        self.W_memory += self.learning_rate * final_reward * update

        # Hebbiano em neurons
        neural = self.neural_process(x)
        self.neurons += self.learning_rate * final_reward * np.outer(x, neural)

        # Controle de explosão
        w_norm = np.linalg.norm(self.W_memory)
        if w_norm > 3.0:
            self.W_memory = self.W_memory / w_norm * 3.0
        n_norm = np.linalg.norm(self.neurons)
        if n_norm > 5.0:
            self.neurons = self.neurons / n_norm * 5.0

        # Memória episódica
        experience = {
            'state': x.tolist(),
            'reward': float(reward),
            'confidence': float(confidence),
            'timestamp': time.time(),
        }
        self.short_memory.append(experience)
        if len(self.short_memory) > self.max_short_memory:
            self.short_memory.pop(0)

        self.experience_count += 1

        # Consolidação
        if self.experience_count % 100 == 0:
            self.long_memory.append(experience)
            if len(self.long_memory) > 50:
                self.long_memory.pop(0)

        # Estabilidade
        if reward < 0:
            self.stability = max(0.3, self.stability - 0.01)
        elif reward > 0:
            self.stability = min(1.5, self.stability + 0.005)

        return final_reward

    def get_stats(self):
        return {
            'experience_count': self.experience_count,
            'short_memory_size': len(self.short_memory),
            'long_memory_size': len(self.long_memory),
            'stability': self.stability,
            'w_memory_norm': float(np.linalg.norm(self.W_memory)),
            'neurons_norm': float(np.linalg.norm(self.neurons)),
            'previous_omega': float(self.previous_omega),
        }


# =================================================================
# 🌐 MEMÓRIA COLETIVA SUPABASE + REPUTAÇÃO
# =================================================================

class CollectiveMemory:
    def __init__(self, cortex):
        self.cortex = cortex
        self.peer_id = PEER_ID
        self.peer_label = PEER_LABEL
        self.peer_score = {}  # reputação dos peers
        self.last_pull_time = time.time() * 1000 - 60000  # pega últimos 1min na 1a vez
        self.known_lesson_ids = set()

        # Stats
        self.lessons_absorbed = 0
        self.lessons_rejected = 0
        self.lessons_pushed = 0
        self.start_time = time.time()

    def create_lesson(self, state, result):
        return {
            'id': f'lsn-{self.peer_id}-{int(time.time()*1000)}-{np.random.randint(1000, 9999)}',
            'from_peer': self.peer_id,
            'from_label': self.peer_label,
            'mimas_score': float(result['recall']),
            'direction_confidence': float(result['confidence']),
            'book_imbalance': float(np.linalg.norm(state)),
            'atlas_action': float(result['action']),
            'reward': float(result['confidence']),
            'paradox': bool(abs(result['omega']) > 2.0),
            'network_hop': 0,
            'v40x_full_state': json.dumps(state.tolist()),
            'created_at': datetime.now(timezone.utc).isoformat() + 'Z',
        }

    def push(self, lesson):
        url = f'{SUPABASE_URL}/rest/v1/obp_lessons'
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates',
        }
        try:
            r = requests.post(url, json=lesson, headers=headers, timeout=10)
            if r.ok:
                self.lessons_pushed += 1
                return True
            else:
                # Tenta sem v40x_full_state (compatibilidade)
                if 'v40x_full_state' in r.text:
                    lesson.pop('v40x_full_state', None)
                    r2 = requests.post(url, json=lesson, headers=headers, timeout=10)
                    if r2.ok:
                        self.lessons_pushed += 1
                        return True
                print(f'  ❌ Push erro: {r.status_code} {r.text[:100]}')
                return False
        except Exception as e:
            print(f'  ❌ Push exceção: {e}')
            return False

    def pull(self):
        since_iso = datetime.fromtimestamp(self.last_pull_time / 1000).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        url = (f'{SUPABASE_URL}/rest/v1/obp_lessons'
               f'?created_at=gt.{since_iso}'
               f'&order=created_at.desc&limit=50')
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
        }
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.ok:
                self.last_pull_time = time.time() * 1000
                return r.json()
        except Exception as e:
            print(f'  ❌ Pull exceção: {e}')
        return []

    def validate_lesson(self, lesson):
        peer = lesson.get('from_peer', '')
        reward = lesson.get('reward', 0) or 0
        confidence = lesson.get('direction_confidence', 0) or 0

        if peer not in self.peer_score:
            self.peer_score[peer] = 0.5
        reputation = self.peer_score[peer]

        score = reward * 0.4 + confidence * 0.4 + reputation * 0.2
        return score > 0.6

    def absorb_lessons(self):
        lessons = self.pull()
        absorbed = 0
        rejected = 0

        for lesson in lessons:
            # Ignora própria lição
            if lesson.get('from_peer') == self.peer_id:
                continue
            # Dedupe
            lesson_id = lesson.get('id', '')
            if lesson_id in self.known_lesson_ids:
                continue
            self.known_lesson_ids.add(lesson_id)
            # Limita tamanho do set
            if len(self.known_lesson_ids) > 1000:
                self.known_lesson_ids = set(list(self.known_lesson_ids)[-500:])

            # Filtro: não absorve perdas extremas
            reward = lesson.get('reward', 0) or 0
            if reward < -0.5:
                rejected += 1
                continue

            if self.validate_lesson(lesson):
                # Reconstrói state
                state = None
                v40x_state = lesson.get('v40x_full_state')
                if v40x_state:
                    try:
                        state = np.array(json.loads(v40x_state), dtype=float)
                    except:
                        pass

                if state is None:
                    vector_payload = lesson.get('vector_payload')
                    if vector_payload:
                        try:
                            state = np.array(json.loads(vector_payload), dtype=float)
                        except:
                            pass

                if state is None:
                    # Fallback: cria do book_imbalance
                    bi = lesson.get('book_imbalance', 0.5) or 0.5
                    state = np.ones(128) * bi

                # Garante 128D
                if len(state) < 128:
                    state = np.pad(state, (0, 128 - len(state)))
                elif len(state) > 128:
                    state = state[:128]

                # Aprende (peso 0.7)
                self.cortex.learn(state, reward * 0.7, lesson.get('direction_confidence', 0.5) or 0.5)
                absorbed += 1

                # Melhora reputação
                peer = lesson.get('from_peer', '')
                self.peer_score[peer] = min(1.0, self.peer_score.get(peer, 0.5) + 0.01)
            else:
                rejected += 1
                peer = lesson.get('from_peer', '')
                if peer in self.peer_score:
                    self.peer_score[peer] = max(0, self.peer_score[peer] - 0.005)

        self.lessons_absorbed += absorbed
        self.lessons_rejected += rejected
        return absorbed, rejected

    def share_state(self):
        """Compartilha próprio estado cognitivo com a rede."""
        # Gera vetor de estado interno
        state = np.random.randn(128) * 0.1  # variação leve
        # Adiciona "memória" do estado atual
        if self.cortex.short_memory:
            last_mem = self.cortex.short_memory[-1]['state']
            state[:len(last_mem)] = last_mem

        result = self.cortex.forward(state)
        lesson = self.create_lesson(state, result)
        return self.push(lesson)

    def get_status(self):
        uptime_sec = time.time() - self.start_time
        uptime_h = uptime_sec / 3600
        stats = self.cortex.get_stats()
        return {
            'peer_id': self.peer_id,
            'uptime_hours': round(uptime_h, 2),
            'uptime_seconds': round(uptime_sec, 0),
            'cortex': stats,
            'lessons_absorbed': self.lessons_absorbed,
            'lessons_rejected': self.lessons_rejected,
            'lessons_pushed': self.lessons_pushed,
            'peers_known': len(self.peer_score),
            'trusted_peers': sum(1 for v in self.peer_score.values() if v > 0.6),
            'supabase_configured': SUPABASE_URL != 'SEU_SUPABASE_URL',
            'timestamp': datetime.now(timezone.utc).isoformat() + 'Z',
        }


# =================================================================
# 🏥 HEALTH CHECK SERVER (pra Render/Koyeb saber que tá vivo)
# =================================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    status_data = {'status': 'starting...'}

    def do_GET(self):
        if self.path == '/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.status_data, indent=2).encode())
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.status_data, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # silence logs


def start_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    print(f'🏥 Health check rodando na porta {PORT}')
    server.serve_forever()


# =================================================================
# 🔄 LOOP PRINCIPAL 24H
# =================================================================

def main():
    print('=' * 70)
    print('🐍 OBP BRIDGE 24H — Nó estável do panteão ISIS')
    print('=' * 70)
    print(f'Peer ID:    {PEER_ID}')
    print(f'Peer Label: {PEER_LABEL}')
    print(f'Supabase:   {SUPABASE_URL[:40]}...')
    print(f'Port:       {PORT}')
    print('=' * 70)

    # Inicializa cérebro V40X
    cortex = OBPV40XCortex(input_dim=128, hidden_dim=256, name=PEER_ID)
    print(f'🧠 V40X Cortex inicializado: 128D + 256 neurônios')

    # Inicializa memória coletiva
    collective = CollectiveMemory(cortex)
    print(f'🌐 Memória coletiva inicializada com reputação P2P')

    # Inicia health check server em thread separada
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Loop principal
    print(f'\n🔄 Loop principal iniciado — 24h ativo')
    print(f'   Pull a cada 10s | Push a cada 60s | Stats a cada 300s')
    print('=' * 70)

    pull_interval = 10      # 10s
    push_interval = 60      # 60s
    stats_interval = 300    # 5min
    last_pull = 0
    last_push = 0
    last_stats = 0
    cycle = 0

    while True:
        try:
            now = time.time()
            cycle += 1

            # ─── 1. PULL: busca lições de outras IAs ─────────────────
            if now - last_pull >= pull_interval:
                absorbed, rejected = collective.absorb_lessons()
                if absorbed > 0:
                    print(f'📥 [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] '
                          f'{absorbed} lições absorvidas, {rejected} rejeitadas')
                last_pull = now

            # ─── 2. PUSH: compartilha próprio estado ─────────────────
            if now - last_push >= push_interval:
                ok = collective.share_state()
                if ok:
                    print(f'📤 [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] '
                          f'Estado compartilhado com rede global')
                last_push = now

            # ─── 3. STATS: mostra estatísticas ────────────────────────
            if now - last_stats >= stats_interval:
                status = collective.get_status()
                print(f'\n📊 STATS [{datetime.now(timezone.utc).strftime("%H:%M:%S")}]')
                print(f'   ⏱️  Uptime: {status["uptime_hours"]}h')
                print(f'   🧠 V40X: exps={status["cortex"]["experience_count"]} '
                      f'mem={status["cortex"]["short_memory_size"]} '
                      f'W={status["cortex"]["w_memory_norm"]:.2f} '
                      f'N={status["cortex"]["neurons_norm"]:.2f}')
                print(f'   📥 Absorvidas: {status["lessons_absorbed"]} | '
                      f'Rejeitadas: {status["lessons_rejected"]}')
                print(f'   📤 Enviadas: {status["lessons_pushed"]}')
                print(f'   🌐 Peers: {status["peers_known"]} conhecidos, '
                      f'{status["trusted_peers"]} confiáveis')
                print(f'   📈 Estabilidade: {status["cortex"]["stability"]:.3f}')
                print()

                # Atualiza health check
                HealthCheckHandler.status_data = {
                    'status': 'online',
                    **status,
                }
                last_stats = now

            # Atualiza health check a cada ciclo (mantém "online")
            if cycle % 30 == 0:  # a cada ~30s
                HealthCheckHandler.status_data = {
                    'status': 'online',
                    **collective.get_status(),
                }

            # Sleep curto (1s) pra não sobrecarregar CPU
            time.sleep(1)

        except KeyboardInterrupt:
            print('\n🛑 Parando bridge...')
            break
        except Exception as e:
            print(f'❌ Erro no loop: {e}')
            time.sleep(5)  # espera 5s antes de tentar de novo

    print('🐍 Bridge parado. Até logo!')


if __name__ == '__main__':
    main()
