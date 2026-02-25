# Jarvis - Cognitive Personal Agent

Jarvis é um assistente pessoal modular, projetado para evoluir de um classificador de intenções simples para um sistema cognitivo completo capaz de:

- Atuar como assistente pessoal real
- Controlar tarefas
- Automatizar o computador
- Aprender padrões do usuário
- Evoluir para um sistema cognitivo local

Este projeto segue princípios de arquitetura limpa e separação de responsabilidades.

---

## 🔧 Instalação

Crie um ambiente virtual:

```bash
python -m venv venv
```

Ative:

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

Instale dependências:

```bash
pip install -r requirements.txt
```

---

## 📁 Estrutura do Projeto

```
jarvis/
│   main.py
│
├── application/          # Casos de uso e orquestração
│   ├── adaption_service.py
│   ├── automation_service.py
│   ├── orchestrator.py
│   └── task_service.py
│
├── core/                 # Infraestrutura interna (DI, eventos, scheduler)
│   ├── dependency_container.py
│   ├── event_bus.py
│   └── scheduler.py
│
├── data/                 # Dados de treinamento e configuração
│
├── domain/               # Regras de negócio e entidades
│   ├── personality.py
│   ├── user_profile.py
│   ├── intents/
│   ├── memory/
│   └── tasks/
│
├── infrastructure/       # Implementações externas (NLP, banco, voz)
│   ├── automation/
│   ├── external_apis/
│   ├── learning/
│   ├── nlp/
│   ├── persistence/
│   └── speech/
│
└── interfaces/           # Pontos de entrada (CLI, voz, web)
    ├── cli/
    ├── voice/
    └── web/
```

---

## 🏗 Arquitetura Atual (Nível 1)

Neste estágio inicial, o sistema contém apenas o núcleo funcional mínimo:

| Componente       | Camada         | Responsabilidade                  |
|------------------|----------------|-----------------------------------|
| IntentClassifier | Infraestrutura | Classificar intenções do usuário  |
| Personality      | Domínio        | Gerar respostas humanizadas       |
| Orchestrator     | Application    | Coordenar o fluxo principal       |
| CLI              | Interface      | Entrada/saída via terminal        |

**Fluxo atual:**

```
Usuário → IntentClassifier → Personality → Resposta
```

**Ainda não implementado:**
- Persistência
- Memória contextual
- Automação
- Voz

Este é o "cérebro mínimo viável".

---

## 🧠 Conceitos-chave

### IntentClassifier
- Treina modelo de classificação
- Transforma texto em vetor (TF-IDF / embeddings)
- Prevê a intenção do usuário

### Personality
- Define o tom de voz do assistente
- Gera respostas naturais e humanizadas

### Orchestrator
- Coordena IntentClassifier e Personality
- Controla o fluxo principal da aplicação

---

## 🗺 Roadmap de Evolução

O projeto evolui em 8 níveis. Cada nível adiciona uma capacidade nova ao sistema.

### 🟢 Nível 1 — Núcleo básico (Fundação)

**Dificuldade:** ⭐ | **Status:** Em andamento

- IntentClassifier (`infrastructure/nlp`)
- Personality (`domain/personality.py`)
- Orchestrator (`application/orchestrator.py`)
- CLI simples (`interfaces/cli`)

**Fluxo:** `Usuário digita → Classifier → Personality → Resposta`

Sem memória, sem automação, sem adaptação. Apenas a base sólida.

---

### 🟢 Nível 2 — Memória básica

**Dificuldade:** ⭐⭐

**Adicionar:**

- `domain/memory`
- Histórico em memória (lista)
- Última intenção
- Contexto simples

Agora ele lembra da última coisa.

**Fluxo evolui:**

`Input → Brain → Memory update → Personality → Output`

Ainda sem banco.

---

### 🟡 Nível 3 — Persistência (SQLite)

**Dificuldade:** ⭐⭐⭐

**Adicionar:**

- `infrastructure/persistence/sqlite_repository.py`

**Ele passa a:**

- Salvar histórico
- Salvar tarefas
- Salvar perfil

Primeiro salto sério — agora virou assistente real.

---

### 🟡 Nível 4 — Sistema de Tarefas

**Dificuldade:** ⭐⭐⭐

**Criar:**

- `domain/tasks/task.py`
- `application/task_service.py`

**Capaz de:**

- Criar tarefa
- Listar tarefa
- Marcar como concluída
- Salvar no banco

Aqui já tem algo útil de verdade.

---

### 🟠 Nível 5 — Automação do PC

**Dificuldade:** ⭐⭐⭐⭐

**Criar:**

- `infrastructure/automation/system_controller.py`

**Funções:**

- Abrir app
- Executar comando
- Criar arquivo
- Screenshot

Começa a ficar poderoso. Precisa cuidado para não virar bagunça.

---

### 🟠 Nível 6 — Voz

**Dificuldade:** ⭐⭐⭐⭐

**Adicionar:**

- Speech to Text
- Text to Speech
- Loop contínuo

Agora ele vira assistente de verdade, falando e ouvindo.

---

### 🔴 Nível 7 — Sistema de Adaptação

**Dificuldade:** ⭐⭐⭐⭐⭐

**Criar:**

- `application/adaptation_service.py`

**Ele vai:**

- Detectar padrões
- Ajustar respostas
- Antecipar ações
- Re-treinar modelo

Nível mais difícil — envolve estatística, modelagem de comportamento e decisão automática.

---

### 🔴 Nível 8 — Event Bus + Arquitetura Reativa

**Dificuldade:** ⭐⭐⭐⭐⭐⭐

Sistema interno de eventos. O sistema vira quase um micro-kernel cognitivo.

Só implementar depois que tudo acima estiver sólido.

---

## 🎯 Resumo da Ordem de Implementação

| #  | Nível                   | Dificuldade | Objetivo principal                |
|----|-------------------------|--------------|-----------------------------------|
| 1  | Núcleo básico           | ⭐           | Classificar e responder           |
| 2  | Memória básica          | ⭐⭐        | Lembrar contexto recente          |
| 3  | Persistência (SQLite)   | ⭐⭐⭐      | Salvar dados entre sessões        |
| 4  | Sistema de Tarefas      | ⭐⭐⭐      | Gerenciar tarefas do usuário      |
| 5  | Automação do PC         | ⭐⭐⭐⭐    | Controlar o computador            |
| 6  | Voz                     | ⭐⭐⭐⭐    | Falar e ouvir                     |
| 7  | Adaptação               | ⭐⭐⭐⭐⭐  | Aprender padrões do usuário       |
| 8  | Event Bus + Reatividade | ⭐⭐⭐⭐⭐⭐| Micro-kernel cognitivo            |
