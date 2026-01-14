# Comparação: Mesa Virtual RPG vs Principais VTTs do Mercado

## 🎯 Principais Concorrentes Analisados
- **Roll20** - Líder de mercado, focado em acessibilidade
- **Foundry VTT** - Mais customizável, comunidade de módulos
- **Fantasy Grounds** - Automação profunda, suporte oficial

---

## ✅ Funcionalidades JÁ IMPLEMENTADAS (Paridade Básica)

| Funcionalidade | Nossa Implementação | Roll20 | Foundry | Fantasy Grounds |
|----------------|---------------------|--------|---------|-----------------|
| Autenticação | ✅ JWT | ✅ | ✅ | ✅ |
| Mesas Múltiplas | ✅ | ✅ | ✅ | ✅ |
| Mapa Canvas Grid | ✅ Quadrado | ✅ Quad/Hex | ✅ Quad/Hex | ✅ Quad/Hex |
| Tokens Básicos | ✅ | ✅ | ✅ | ✅ |
| Chat Tempo Real | ✅ WebSocket | ✅ | ✅ | ✅ |
| Rolagem de Dados | ✅ Parser robusto | ✅ | ✅ | ✅ |
| Fichas 3D&T | ✅ Completas | ❌ | ⚠️ Via módulo | ❌ |
| Música Ambiente | ✅ | ✅ | ✅ | ✅ |
| Dark Theme | ✅ Medieval | ⚠️ Limitado | ✅ | ⚠️ |

---

## 🚀 FUNCIONALIDADES A IMPLEMENTAR (Prioridade ALTA)

### 1. ✅ Drag-and-Drop Visual de Tokens
**Status**: Vamos implementar AGORA  
**Importância**: CRÍTICA - UX básica esperada  
**Roll20**: ✅ | **Foundry**: ✅ | **Fantasy Grounds**: ✅

### 2. ✅ Upload de Imagens (Tokens/Mapas)
**Status**: Vamos implementar AGORA  
**Importância**: CRÍTICA - Personalização essencial  
**Roll20**: ✅ (limitado grátis) | **Foundry**: ✅ | **Fantasy Grounds**: ✅

### 3. ✅ Sistema de Iniciativa de Combate
**Status**: Vamos implementar AGORA  
**Importância**: ALTA - Organização de combate  
**Roll20**: ✅ Auto | **Foundry**: ✅ + módulos | **Fantasy Grounds**: ✅ Automação profunda

### 4. ✅ Biblioteca de Livros com Índice Clicável
**Status**: Vamos implementar AGORA  
**Importância**: ALTA - Essencial para 3D&T/Tormenta  
**Roll20**: ⚠️ Handouts básicos | **Foundry**: ✅ Journal | **Fantasy Grounds**: ✅ Integrado

### 5. ✅ Névoa de Guerra (Fog of War)
**Status**: Vamos implementar AGORA  
**Importância**: ALTA - Exploração e mistério  
**Roll20**: ✅ (Pro) | **Foundry**: ✅ | **Fantasy Grounds**: ✅

### 6. ✅ Templates Tormenta 20 e D&D 5.5E
**Status**: Vamos implementar AGORA  
**Importância**: ALTA - Diversidade de sistemas  
**Roll20**: ✅ | **Foundry**: ✅ | **Fantasy Grounds**: ✅

### 7. ✅ Exportação/Importação de Mesas (JSON)
**Status**: Vamos implementar AGORA  
**Importância**: MÉDIA - Backup e portabilidade  
**Roll20**: ⚠️ Limitado | **Foundry**: ✅ | **Fantasy Grounds**: ✅

---

## 📊 FUNCIONALIDADES AVANÇADAS (Para Futuro)

### Visão e Iluminação
| Funcionalidade | Roll20 | Foundry | Fantasy Grounds | Nossa Prioridade |
|----------------|--------|---------|-----------------|------------------|
| Line of Sight (LOS) | ✅ Pro | ✅ | ✅ | 🔶 MÉDIA |
| Iluminação Dinâmica | ✅ Pro | ✅ | ✅ | 🔶 MÉDIA |
| Visão por Token | ✅ Pro | ✅ | ✅ | 🔶 MÉDIA |
| Walls/Obstáculos | ✅ Pro | ✅ | ✅ | 🔶 MÉDIA |

**Análise**: Estas funcionalidades são poderosas mas complexas. Foundry se destaca aqui. Podemos implementar versão básica de LOS e iluminação futuramente.

### Medição e Templates
| Funcionalidade | Roll20 | Foundry | Fantasy Grounds | Nossa Prioridade |
|----------------|--------|---------|-----------------|------------------|
| Medição de Distância | ✅ | ✅ Avançado | ✅ | 🟢 ALTA |
| Templates de Área (AoE) | ✅ | ✅ | ✅ | 🟢 ALTA |
| Pathfinding | ❌ | ⚠️ Módulos | ✅ | 🔴 BAIXA |
| Elevação/Altura | ⚠️ | ✅ | ✅ | 🔴 BAIXA |

**Análise**: Medição de distância e templates AoE são essenciais para combate tático. Vamos implementar junto com iniciativa.

### Automação e Combate
| Funcionalidade | Roll20 | Foundry | Fantasy Grounds | Nossa Prioridade |
|----------------|--------|---------|-----------------|------------------|
| Macros | ✅ | ✅ JS | ✅ Lua | 🟡 MÉDIA |
| Condições/Status | ⚠️ | ✅ | ✅ Auto | 🟡 MÉDIA |
| Automação de Dano/AC | ❌ Grátis | ⚠️ Módulos | ✅ Nativa | 🔴 BAIXA |
| Effects Engine | ❌ | ✅ | ✅ | 🔴 BAIXA |

**Análise**: Fantasy Grounds lidera em automação. Para 3D&T (sistema mais simples), não precisamos de automação tão profunda inicialmente.

### Conteúdo e Assets
| Funcionalidade | Roll20 | Foundry | Fantasy Grounds | Nossa Prioridade |
|----------------|--------|---------|-----------------|------------------|
| Marketplace | ✅ | ✅ | ✅ | 🔴 BAIXA |
| Compêndio Monstros | ✅ | ✅ | ✅ | 🟡 MÉDIA |
| Handouts/Documentos | ✅ | ✅ | ✅ | 🟡 MÉDIA |
| Journal do Mestre | ✅ | ✅ | ✅ | 🟡 MÉDIA |

**Análise**: Útil mas não crítico para MVP. Podemos adicionar seção de "Compêndio" e "Journal" depois.

### Multimídia
| Funcionalidade | Roll20 | Foundry | Fantasy Grounds | Nossa Prioridade |
|----------------|--------|---------|-----------------|------------------|
| Vídeo Chat Integrado | ✅ | ⚠️ Módulos | ❌ | 🔴 BAIXA |
| Dados 3D Animados | ⚠️ | ✅ Módulos | ⚠️ | 🔴 BAIXA |
| Efeitos Visuais | ⚠️ | ✅ | ⚠️ | 🔴 BAIXA |
| Música por Proximidade | ❌ | ✅ | ✅ | 🔴 BAIXA |

**Análise**: Legal mas não essencial. Usuários podem usar Discord/Zoom para vídeo. Efeitos visuais são "nice to have".

---

## 🎖️ NOSSAS VANTAGENS ÚNICAS

### 1. ✨ Foco em RPGs Brasileiros
- **3D&T nativo** (nenhum VTT tem suporte dedicado)
- **Tormenta 20** (pouco suporte nos VTTs principais)
- Interface em **português completo**
- Templates específicos para sistemas nacionais

### 2. 🎨 Design Medieval Minimalista
- Tema "Obsidian & Parchment" único
- Interface limpa focada no mapa (70% da tela)
- Sem poluição visual dos concorrentes
- Tipografia Cinzel medieval premium

### 3. 💰 Modelo de Preço Simples
- **Roll20**: Grátis limitado, Pro = $10/mês
- **Foundry**: $50 uma vez + hospedagem
- **Fantasy Grounds**: $40-150 uma vez
- **Nós**: A definir (mas com vantagem de simplicidade)

### 4. 🚀 Stack Moderna
- React 19 + FastAPI (mais rápido que Roll20 legado)
- WebSocket nativo (não depende de plugins)
- MongoDB flexível (melhor que SQL para RPG)

---

## 📋 PLANO DE IMPLEMENTAÇÃO (Próximas Etapas)

### Fase 1: HOJE - Funcionalidades Críticas ⚡
1. ✅ Drag-and-drop visual de tokens no canvas
2. ✅ Upload de imagens (tokens e mapas de fundo)
3. ✅ Sistema de iniciativa de combate
4. ✅ Biblioteca de livros com índice clicável
5. ✅ Névoa de guerra básica
6. ✅ Templates Tormenta 20 e D&D 5.5E
7. ✅ Exportação/importação de mesas

### Fase 2: Semana Seguinte - Combate Tático 🎲
8. Medição de distância (régua no mapa)
9. Templates de área (cone, círculo, linha)
10. Marcadores de condições (envenenado, atordoado, etc)
11. Layers de mapa (background, objetos, tokens, fog)
12. Melhorar drag-and-drop com preview

### Fase 3: Mês Seguinte - Qualidade de Vida ⭐
13. Macros básicos para rolagens rápidas
14. Line of Sight básico
15. Iluminação simples (fontes de luz)
16. Journal do Mestre
17. Compêndio de criaturas
18. Handouts para jogadores

### Fase 4: Futuro - Diferenciação 🌟
19. Sistema de crafting (Tormenta)
20. Cálculo automático de custos de magia (3D&T)
21. Integração com fichas do GDrive
22. Modo offline com sync
23. App mobile (visualização)

---

## 🎯 CONCLUSÃO

**Nosso sistema está em paridade BÁSICA com Roll20 gratuito**, mas ainda falta:
- ✅ **CRÍTICO**: Drag-and-drop, upload de imagens, iniciativa → Implementar HOJE
- 🟢 **IMPORTANTE**: Névoa de guerra, biblioteca de livros, medição → Implementar HOJE
- 🟡 **DESEJÁVEL**: Macros, condições, LOS → Próxima iteração
- 🔴 **OPCIONAL**: Efeitos visuais, vídeo chat, marketplace → Muito depois

**Nossa diferenciação está no foco em RPGs brasileiros (3D&T/Tormenta) e design superior.**
Roll20 e Foundry são generalistas. Fantasy Grounds é muito caro e complexo.
Podemos ser a **melhor opção para mestres brasileiros** com as implementações de hoje.

Vamos começar! 🚀
