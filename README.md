# Mesa Virtual RPG - Sistema de Mesa Virtual para RPG Online

Sistema completo de mesa virtual para jogos de RPG com foco em 3D&T (Defensores de Tóquio 3ª Edição), com suporte futuro para Tormenta 20 e D&D 5.5E.

## 🎲 Funcionalidades Implementadas

### ✅ Autenticação e Gerenciamento de Usuários
- Sistema de registro e login com JWT
- Proteção de rotas e controle de acesso
- Múltiplos usuários simultâneos

### ✅ Gerenciamento de Mesas
- Criar múltiplas mesas de RPG
- Cada mesa com ID único e configurações próprias
- Controle de permissões (Mestre/Jogador)
- Persistência de estado em MongoDB

### ✅ Mapa Interativo com Canvas
- Canvas HTML5 com grid quadrado configurável
- Grid configurável em metros por célula (padrão: 1.5m)
- Opção de mostrar/ocultar grid
- Sistema de coordenadas para posicionamento preciso
- Foco no mapa (ocupa ~70% da tela)

### ✅ Sistema de Tokens
- Criar tokens personalizados
- Cores customizáveis (6 presets)
- Tamanho configurável (1-5 células)
- Arrastar e soltar com snap-to-grid
- Visibilidade por papel (todos/somente mestre)
- Sincronização em tempo real via WebSocket
- Gerenciamento de biblioteca de tokens

### ✅ Fichas de Personagem 3D&T
- Template completo para 3D&T:
  - Atributos: Força (F), Habilidade (H), Resistência (R)
  - Atributos secundários: Armadura (A), Poder de Fogo (PdF)
  - Pontos de Vida (PV) e Pontos de Magia (PM)
  - Botões +/- para ajustar PV e PM rapidamente
  - Cálculo automático de PV/PM baseado em Resistência
- Sistema de vantagens/desvantagens (estrutura pronta)
- Perícias e equipamentos (estrutura pronta)
- Notas do personagem

### ✅ Sistema de Rolagem de Dados
- Parser robusto suportando:
  - Notação padrão: `2d6+3`, `1d20`, `3d8-2`
  - D&D Advantage: `d20adv` (rola 2d20, pega o maior)
  - D&D Disadvantage: `d20dis` (rola 2d20, pega o menor)
- Rolagens públicas e privadas
- Histórico completo no chat
- Breakdown detalhado dos resultados

### ✅ Chat em Tempo Real
- Mensagens de texto sincronizadas
- Comando `/roll` integrado (ex: `/roll 2d6+3`)
- Histórico de mensagens e rolagens
- Sincronização via WebSocket
- Interface responsiva com scroll automático

### ✅ Player de Música Ambiente
- Adicionar músicas via link (MP3/OGG/YouTube)
- Player integrado com controles
- Ajuste de volume individual
- Loop automático
- Playlist por mesa

### ✅ Design e UX
- **Tema "Obsidian & Parchment"**: Pergaminho escuro com detalhes dourados
- Paleta medieval minimalista:
  - Background: `#0f0e0d` (Espresso profundo)
  - Foreground: `#e3d5c5` (Off-white pergaminho)
  - Primary: `#c5a059` (Ouro)
  - Accent: `#8a2c2c` (Vermelho medieval)
- Tipografia:
  - Títulos: **Cinzel** (serifada medieval)
  - Corpo: **Lato** (sans-serif legível)
  - Código: **Fira Code** (monospace)
- Interface responsiva (desktop e tablet)
- Componentes com glassmorphism e sombras profundas
- Ícones via Lucide React

## 🏗️ Arquitetura Técnica

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB com Motor (async)
- **Real-time**: Socket.IO para sincronização
- **Auth**: JWT com bcrypt para senhas
- **API**: REST + WebSocket

### Frontend
- **Framework**: React 19
- **Routing**: React Router v7
- **Styling**: Tailwind CSS + Shadcn/UI
- **State Management**: Context API
- **Real-time**: Socket.IO Client
- **UI Components**: Radix UI primitives

### Estrutura do Projeto

```
/app
├── backend/
│   ├── server.py          # FastAPI app principal
│   ├── .env               # Variáveis de ambiente
│   └── requirements.txt   # Dependências Python
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.js          # Autenticação
│   │   │   ├── Dashboard.js      # Lista de mesas
│   │   │   └── TableView.js      # Mesa principal
│   │   ├── components/
│   │   │   ├── MapCanvas.js      # Canvas do mapa
│   │   │   ├── ChatPanel.js      # Chat e dados
│   │   │   ├── TokenPanel.js     # Gerenciar tokens
│   │   │   ├── CharacterPanel.js # Fichas 3D&T
│   │   │   ├── MusicPanel.js     # Player de música
│   │   │   └── ui/               # Shadcn components
│   │   ├── context/
│   │   │   ├── AuthContext.js    # Autenticação
│   │   │   └── WebSocketContext.js # WebSocket
│   │   ├── App.js
│   │   └── index.css
│   ├── package.json
│   └── tailwind.config.js
└── design_guidelines.json  # Design system
```

## 📡 API Endpoints

### Autenticação
- `POST /api/auth/register` - Criar conta
- `POST /api/auth/login` - Login

### Mesas
- `POST /api/tables` - Criar mesa
- `GET /api/tables` - Listar minhas mesas
- `GET /api/tables/{id}` - Detalhes da mesa

### Personagens
- `POST /api/characters` - Criar personagem 3D&T
- `GET /api/characters/table/{table_id}` - Listar personagens da mesa
- `PUT /api/characters/{id}` - Atualizar personagem

### Tokens
- `POST /api/tokens` - Criar token
- `GET /api/tokens/table/{table_id}` - Listar tokens da mesa
- `DELETE /api/tokens/{id}` - Remover token

### Chat
- `POST /api/messages` - Enviar mensagem
- `GET /api/messages/table/{table_id}` - Histórico de chat

### Dados
- `POST /api/dice/roll` - Rolar dados
  ```json
  {
    "expression": "2d6+3",
    "table_id": "uuid",
    "is_private": false
  }
  ```

### Livros
- `POST /api/books` - Adicionar livro
- `GET /api/books/table/{table_id}` - Listar livros da mesa

### Música
- `POST /api/music` - Adicionar música
- `GET /api/music/table/{table_id}` - Listar músicas da mesa

## 🔌 WebSocket Events

### Cliente → Servidor
- `join_table` - Entrar em uma mesa
- `leave_table` - Sair de uma mesa
- `token_moved` - Mover token no mapa
- `chat_message` - Enviar mensagem
- `dice_rolled` - Rolar dados

### Servidor → Cliente
- `user_joined` - Usuário entrou
- `user_left` - Usuário saiu
- `token_updated` - Token movido
- `new_message` - Nova mensagem
- `dice_result` - Resultado de dados

## 🚀 Como Rodar

### Backend
```bash
cd /app/backend
pip install -r requirements.txt
uvicorn server:socket_app --host 0.0.0.0 --port 8001
```

### Frontend
```bash
cd /app/frontend
yarn install
yarn start
```

Acesse: `http://localhost:3000`

## 📊 Modelos de Dados

### User
```json
{
  "id": "uuid",
  "email": "usuario@email.com",
  "username": "MestreRPG",
  "password_hash": "bcrypt_hash",
  "created_at": "ISO8601"
}
```

### Table
```json
{
  "id": "uuid",
  "name": "A Taverna do Dragão",
  "description": "Campanha de fantasia medieval",
  "master_id": "user_uuid",
  "players": ["user_uuid"],
  "grid_size": 30,
  "grid_scale": 1.5,
  "show_grid": true,
  "created_at": "ISO8601"
}
```

### Character3DT
```json
{
  "id": "uuid",
  "table_id": "table_uuid",
  "user_id": "user_uuid",
  "name": "Aragorn",
  "forca": 3,
  "habilidade": 4,
  "resistencia": 3,
  "armadura": 0,
  "poder_de_fogo": 0,
  "pv_max": 7,
  "pv_current": 7,
  "pm_max": 7,
  "pm_current": 7,
  "vantagens": [],
  "desvantagens": [],
  "pericias": [],
  "equipamentos": [],
  "notas": "",
  "avatar_url": null,
  "created_at": "ISO8601"
}
```

### Token
```json
{
  "id": "uuid",
  "table_id": "table_uuid",
  "name": "Goblin",
  "color": "#8a2c2c",
  "size": 1,
  "image_url": null,
  "visible_to_all": true,
  "x": 5,
  "y": 10,
  "created_at": "ISO8601"
}
```

## 🎯 Próximos Passos (Roadmap)

### Curto Prazo
- [ ] Upload de imagens para tokens e mapas
- [ ] Arrastar tokens no canvas (funcionalidade básica já existe)
- [ ] Sistema de camadas no mapa (fundo, tokens, névoa)
- [ ] Biblioteca de livros com índice de habilidades clicável
- [ ] Editor completo de fichas (vantagens, desvantagens, perícias)

### Médio Prazo
- [ ] Templates para Tormenta 20 e D&D 5.5E
- [ ] Sistema de névoa de guerra (fog of war)
- [ ] Medição de distância no mapa
- [ ] Grid hexagonal (além do quadrado)
- [ ] Sistema de iniciativa/combate
- [ ] Anotações no mapa (marcadores, áreas)

### Longo Prazo
- [ ] Upload de músicas (além de links)
- [ ] Sistema de permissões avançado
- [ ] Exportação/importação de mesas (JSON)
- [ ] Snapshots automáticos do estado
- [ ] Modo offline com sincronização
- [ ] Integração com PDFs de livros

## 🐛 Problemas Conhecidos

- SocketIO precisa de configuração de CORS em produção
- Canvas de tokens precisa melhorar renderização de imagens
- Chat pode precisar paginação para muitas mensagens

## 📝 Licença

Projeto desenvolvido como sistema de mesa virtual para RPG.

## 🤝 Contribuindo

Este é um projeto em desenvolvimento ativo. Sugestões e melhorias são bem-vindas!
