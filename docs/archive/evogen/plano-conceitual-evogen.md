# EvoGen — Plano Conceitual de Pesquisa

## Motor Leve de Aprendizado Genético, Aprendizado Direto por Resposta e Seleção Natural em C++

**Versão:** 1.0 (rascunho para discussão)  
**Tipo de documento:** Plano conceitual / proposta técnica de projeto de pesquisa  
**Linguagem núcleo:** C++17/20  
**Interface:** Web (visualização e controle experimental)  
**Repositório:** este projeto (`ai-conceitual-teste` → produto **EvoGen**)

> Documento normativo de produto/pesquisa. Planos de implementação por fase (etapas + validações) ficam em `.local/phases/` (gitignored).  
> Glossário e arquitetura em inglês para agentes: [GLOSSARY.md](GLOSSARY.md), [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 1. Objetivo do Projeto

Construir uma prova de conceito (PoC) de um sistema de aprendizado artificial que combine três mecanismos biologicamente inspirados, operando juntos em vez de isolados:

1. **Aprendizado genético (populacional)** — evolução de uma população de agentes através de gerações, via seleção, cruzamento e mutação.
2. **Aprendizado direto por resposta (intra-vida / online)** — cada agente ajusta seus próprios parâmetros internos imediatamente após cada interação/resposta, sem esperar o fim da geração (análogo a plasticidade neural em tempo real, tipo Hebbian ou gradiente local).
3. **Seleção natural (pressão ambiental)** — um ambiente ou função de tarefa que define sucesso/fracasso e determina quem sobrevive e se reproduz.

A meta não é criar um framework genérico de ML, e sim **demonstrar experimentalmente** que a combinação desses três mecanismos produz aprendizado mais rápido ou mais robusto do que qualquer um isoladamente — com um sistema leve o suficiente para rodar em hardware modesto e ser auditável (poucas dependências, código pequeno, fácil de instrumentar).

### Por que isso é uma contribuição de pesquisa válida

- Algoritmos genéticos clássicos otimizam **entre** gerações, mas não **dentro** da vida de um indivíduo.
- Aprendizado por reforço/gradiente clássico otimiza **dentro** da vida, mas não explora população nem seleção estrutural.
- O ponto de investigação é o **efeito Baldwin** (aprendizado individual acelerando/guiando a evolução genética) e se um motor simples consegue exibir esse efeito de forma mensurável e visualizável.

---

## 2. Fundamentação Conceitual

### 2.1 Genoma do agente

Cada agente é definido por um **genoma leve**: um vetor de parâmetros numéricos (pesos de uma rede neural minúscula, ou coeficientes de uma política simples, ou regras condicionais parametrizadas). O genoma é a parte **herdada**.

```
struct Genome {
    std::vector<float> weights;   // parâmetros herdáveis
    float mutation_rate;          // taxa de mutação, ela própria evoluível
    float learning_rate;          // taxa de aprendizado direto, também evoluível
};
```

Evoluir `mutation_rate` e `learning_rate` junto com os pesos é o que permite ao sistema aprender **como aprender** (meta-aprendizado emergente), sem precisar de um mecanismo separado.

### 2.2 Aprendizado direto por resposta (dentro da vida)

Depois de cada resposta/ação do agente diante de um estímulo, um pequeno ajuste local é aplicado aos pesos **antes** de qualquer reprodução — por exemplo, uma regra Hebbiana simples ou um gradiente estocástico de um passo:

```
peso_i += learning_rate * erro * entrada_i
```

Esse ajuste é **não herdado diretamente** (hipótese Darwiniana estrita) — mas pode ser configurado como parcialmente herdado para testar hipóteses tipo-Lamarckiana como variante experimental. Ver [RESEARCH-QUESTIONS.md](RESEARCH-QUESTIONS.md).

### 2.3 Seleção natural

Um ambiente/tarefa (`Environment`) apresenta estímulos aos agentes e calcula um **fitness acumulado** ao longo da "vida" do agente (soma de recompensas, acurácia, sobrevivência etc.). Ao fim de uma geração:

- Os agentes de maior fitness têm maior probabilidade de reprodução (seleção por torneio ou roleta).
- Cruzamento combina genomas de dois pais (crossover uniforme ou de ponto único).
- Mutação gaussiana perturba os pesos herdados.

---

## 3. Arquitetura Geral do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        Interface Web                        │
│   (visualização de gerações, fitness, genomas, replay)      │
└───────────────────────────▲─────────────────────────────────┘
                             │ WebSocket / REST (JSON)
┌───────────────────────────┴─────────────────────────────────┐
│                    Camada de Serviço (C++)                  │
│   API leve (cpp-httplib / Crow) expõe:                       │
│   - iniciar/pausar/configurar experimento                    │
│   - stream de métricas em tempo real                         │
│   - snapshot de população (genomas, fitness, linhagem)       │
└───────────────────────────▲─────────────────────────────────┘
                             │ chamadas diretas (mesmo processo)
┌───────────────────────────┴─────────────────────────────────┐
│                     Núcleo Evolutivo (C++)                   │
│  Population → Genome[]                                       │
│  Environment (tarefa/fitness)                                │
│  Loop: avaliação → aprendizado direto → fitness → seleção    │
│        → reprodução → mutação → próxima geração              │
└─────────────────────────────────────────────────────────────┘
```

**Princípio de leveza:** um único binário C++ contém o motor evolutivo e o servidor web embutido. Sem microsserviços, sem banco de dados externo obrigatório (dados podem ser persistidos em JSON/SQLite opcional).

Detalhe de camadas e limites de arquivo/função: [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 4. Componentes do Núcleo (C++)

| Componente | Responsabilidade | Observações de leveza |
|---|---|---|
| `Genome` | Representação herdável + hiperparâmetros evoluíveis | struct simples |
| `Agent` | Genoma + estado de vida (fitness, histórico curto) | composição, sem herança virtual pesada |
| `Environment` | Estímulo → resposta esperada/recompensa | interface mínima `evaluate()` |
| `Population` | Agentes + operadores genéticos | `std::vector`, paralelizável |
| `SelectionOperator` | Torneio, roleta, elitismo | estratégias plugáveis |
| `MutationOperator` | Mutação gaussiana adaptativa | taxa lida do genoma |
| `DirectLearner` | Ajuste intra-vida | O(n) nos pesos por resposta |
| `Recorder` | Métricas por geração | JSON para a web |
| `WebServer` | API REST/WS | biblioteca leve |

### 4.1 Fluxo do loop principal (pseudocódigo)

```cpp
for (int gen = 0; gen < max_generations; ++gen) {
    for (auto& agent : population.agents) {
        for (auto& stimulus : environment.episode()) {
            auto response = agent.respond(stimulus);
            float reward = environment.evaluate(response, stimulus);
            agent.direct_learn(stimulus, response, reward);
            agent.fitness += reward;
        }
    }
    recorder.log_generation(gen, population);
    auto parents = selection.select(population);
    population = reproduction.crossover_and_mutate(parents);
}
```

---

## 5. Interface Web (Camada de Demonstração)

Ferramenta de **observação científica**, não produto comercial.

Componentes: painel de gerações, painel intra-geração, árvore de linhagem, mapa de diversidade genética, painel de controle, replay de agente.

Stack: backend C++ embutido; frontend HTML/JS leve (Chart.js/D3); JSON via WebSocket. Ver [TECH-STACK.md](TECH-STACK.md) e [API-CONTRACT.md](API-CONTRACT.md).

---

## 6. Design Experimental

Ver documento dedicado: [EXPERIMENTAL-DESIGN.md](EXPERIMENTAL-DESIGN.md).

Resumo das condições:

| ID | Condição |
|----|----------|
| A | Só genético + seleção (sem aprendizado direto) |
| B | Só aprendizado direto (sem evolução entre gerações) |
| C | Sistema completo |

Tarefas de bancada iniciais: aproximação de função, grade 2D, classificador com concept drift.

---

## 7. Estrutura de Pastas Alvo

```
evogen/   (raiz deste repositório)
├── src/
│   ├── core/
│   ├── environments/
│   ├── server/
│   └── main.cpp
├── web/
├── experiments/
├── results/          (gitignored logs por rodada)
├── docs/
│   └── plano-conceitual-evogen.md   (este documento)
└── CMakeLists.txt
```

Implementação faseada: ver `.local/IMPLEMENTATION-PLAN.md` e fases `03+`.

---

## 8. Perguntas de Pesquisa

Ver [RESEARCH-QUESTIONS.md](RESEARCH-QUESTIONS.md).

---

## 9. Roadmap

| Fase | Entregável | Fase local |
|------|------------|------------|
| 1 | Núcleo evolutivo mínimo (CLI) | `.local/phases/03-core-evolutionary-loop/` |
| 2 | DirectLearner + aproximação de função | `.local/phases/04-direct-learner-function-approx/` |
| 3 | Servidor web + streaming de métricas | `.local/phases/05-embedded-web-metrics/` |
| 4 | Dashboard completo | `.local/phases/06-dashboard-full/` |
| 5 | Ambientes grid + concept drift | `.local/phases/07-additional-environments/` |
| 6 | Experimentos A/B/C + resultados | `.local/phases/08-abc-experiments/` |
| 7 | Relatório científico | `.local/phases/09-scientific-report/` |

---

## 10. Engenharia para Leveza

- Sem frameworks de ML pesados (sem PyTorch/TensorFlow).
- `std::vector` pré-alocado; paralelismo simples (`std::thread` / OpenMP).
- JSON header-only (`nlohmann/json`); CMake único; seed de RNG logada.
- Hard caps do harness: ciclomática ≤10 (caps de linhas por arquivo/função **dispensados** neste repositório).

---

## 11. Próximos Passos Imediatos

1. Validar este plano e as hipóteses (seção 8 / RESEARCH-QUESTIONS).
2. Congelar a primeira tarefa: **aproximação de função**.
3. Implementar o núcleo (Fase 1) **antes** de qualquer interface web.
4. Só então acoplar a camada web.

*Documento de plano conceitual. Pode ser refinado para proposta formal (laboratório, pós-graduação, ou repositório aberto de pesquisa em IA evolutiva).*
