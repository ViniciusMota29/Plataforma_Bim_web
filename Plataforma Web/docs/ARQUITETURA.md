# Arquitetura da Plataforma BIM-FM

Este documento descreve a arquitetura da plataforma baseada no artigo "BIM-FM Integration through openBIM: Solutions for Interoperability towards Efficient Operations" (Otranto et al., 2025).

## Visão Geral

A plataforma segue uma arquitetura de três camadas:

```
┌─────────────────────────────────────────┐
│         Frontend (React + IFC.js)        │
│     Interface Web + Visualizador 3D      │
└─────────────────────────────────────────┘
                    ↕ HTTP/REST
┌─────────────────────────────────────────┐
│      Backend (FastAPI + IfcOpenShell)   │
│    API REST + Processamento IFC + IA   │
└─────────────────────────────────────────┘
                    ↕ SQL
┌─────────────────────────────────────────┐
│    Database (PostgreSQL + PostGIS)      │
│     Dados BIM + Inspeções + MIR        │
└─────────────────────────────────────────┘
```

## Componentes Principais

### 1. Frontend (React + TypeScript)

**Tecnologias:**
- React 18
- TypeScript
- React Router
- React Query
- IFC.js / Three.js
- Vite

**Estrutura:**
```
frontend/
├── src/
│   ├── pages/          # Páginas principais
│   ├── components/     # Componentes reutilizáveis
│   ├── api/           # Cliente API
│   └── App.tsx        # Roteamento
```

**Funcionalidades:**
- Upload e visualização de arquivos IFC
- Gestão de inspeções
- Gestão de ativos
- Dashboard com estatísticas
- Análise de imagens com IA

### 2. Backend (FastAPI + Python)

**Tecnologias:**
- FastAPI
- SQLAlchemy (ORM)
- IfcOpenShell (processamento IFC)
- PyTorch (modelo de IA)
- Pydantic (validação)

**Estrutura:**
```
backend/
├── app/
│   ├── routers/       # Endpoints da API
│   ├── models/        # Modelos SQLAlchemy
│   ├── schemas/       # Schemas Pydantic
│   ├── services/      # Lógica de negócio
│   └── database.py    # Configuração DB
└── main.py            # Aplicação FastAPI
```

**Endpoints Principais:**

- `/api/ifc/` - Upload e processamento de IFC
- `/api/assets/` - Gestão de ativos
- `/api/inspections/` - Gestão de inspeções
- `/api/ai/analyze` - Análise de imagens
- `/api/blender/sync` - Sincronização Blender

### 3. Banco de Dados (PostgreSQL + PostGIS)

**Schema Principal:**

- `ifc_files` - Arquivos IFC carregados
- `ifc_elements` - Elementos IFC brutos
- `assets` - Ativos com dados MIR
- `inspections` - Registros de inspeção
- `inspection_photos` - Fotos das inspeções
- `mir_requirements` - Requisitos MIR (45)

**MIR (Minimum Information Requirements):**

45 requisitos organizados em categorias:
- Design (1-5)
- Manufacturer (6-10)
- Location (11-15)
- Warranty (16-20)
- Life Cycle (21-25)
- Spare Parts (26-30)
- Documentation (31-35)
- Maintenance (36-40)
- Inspection (41-45)

## Fluxo de Dados

### 1. Upload e Processamento de IFC

```
1. Usuário faz upload de arquivo IFC
   ↓
2. Backend salva arquivo
   ↓
3. Processamento assíncrono com IfcOpenShell
   ↓
4. Extração de elementos e propriedades
   ↓
5. Criação de registros Asset no banco
   ↓
6. Status atualizado para "completed"
```

### 2. Criação de Inspeção

```
1. Usuário preenche formulário de inspeção
   ↓
2. Upload de fotos (opcional)
   ↓
3. Backend cria registro Inspection
   ↓
4. Se houver fotos, análise com IA:
   - Carrega modelo SwinDeepLab
   - Processa cada imagem
   - Gera máscaras e heatmaps
   - Salva resultados
   ↓
5. Atualiza condição do Asset
```

### 3. Sincronização Blender

**Para Plataforma (from_blender):**
```
1. Blender add-on coleta dados da cena
   ↓
2. Envia para API /api/blender/sync
   ↓
3. Backend atualiza Assets no banco
```

**Da Plataforma (to_blender):**
```
1. Blender add-on solicita dados
   ↓
2. API retorna Assets e Inspeções
   ↓
3. Add-on atualiza objetos no Blender
   ↓
4. Aplica cores baseadas em condição
```

## Integração com IA

### Modelo SwinDeepLab

**Arquitetura:**
- Backbone: Swin Transformer (Tiny)
- Decoder: DeepLabV3+
- Saída: Máscara binária (armadura exposta)

**Processamento:**
1. Pré-processamento: Redimensiona para 512x512
2. Normalização: Albumentations
3. Inferência: PyTorch
4. Pós-processamento:
   - Threshold (0.30)
   - Máscara binária
   - Heatmap de probabilidade
   - Contornos

**Resultados:**
- Máscara de detecção (PNG)
- Heatmap (PNG)
- Imagem com contornos (JPG)
- Confiança (0-1)

## Segurança

### Implementações Futuras:

1. **Autenticação JWT**
   - Login/registro de usuários
   - Tokens de acesso
   - Refresh tokens

2. **Autorização**
   - Roles (Admin, Inspector, Viewer)
   - Permissões por recurso

3. **Validação**
   - Validação de arquivos IFC
   - Sanitização de inputs
   - Rate limiting

## Escalabilidade

### Otimizações:

1. **Processamento Assíncrono**
   - Background tasks para IFC
   - Queue system (Celery/RQ)

2. **Cache**
   - Cache de elementos IFC processados
   - Redis para sessões

3. **CDN**
   - Servir arquivos estáticos
   - Imagens e resultados de IA

4. **Banco de Dados**
   - Índices otimizados
   - Particionamento de tabelas grandes
   - Read replicas

## Extensibilidade

### Pontos de Extensão:

1. **Novos Modelos de IA**
   - Interface padrão para serviços de IA
   - Plugins para diferentes modelos

2. **Formatos Adicionais**
   - Suporte para outros formatos BIM
   - Conversores customizados

3. **Integrações**
   - APIs externas
   - Sistemas CMMS
   - Plataformas IoT

## Referências

- Otranto, R.B., Miceli Junior, G., & Pellanda, P.C. (2025). "BIM-FM Integration through openBIM: Solutions for Interoperability towards Efficient Operations"
- DOI: 10.36680/j.itcon.2025.012
- Disponível em: https://www.itcon.org/papers/2025_12-ITcon-Otranto.pdf

