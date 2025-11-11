# Guia de Implementação - Plataforma BIM-FM

Este guia fornece instruções passo a passo para implementar e configurar a plataforma web de gestão de ativos BIM/IFC.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação do Backend](#instalação-do-backend)
3. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
4. [Instalação do Frontend](#instalação-do-frontend)
5. [Configuração do Modelo de IA](#configuração-do-modelo-de-ia)
6. [Instalação do Add-on Blender](#instalação-do-add-on-blender)
7. [Executando a Plataforma](#executando-a-plataforma)
8. [Troubleshooting](#troubleshooting)

## Pré-requisitos

### Software Necessário

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 14+** com PostGIS - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/)

### Dependências do Sistema

- **CUDA** (opcional, para aceleração GPU do modelo de IA)
- **Blender 3.0+** (para add-on)

## Instalação do Backend

### 1. Criar Ambiente Virtual

```bash
cd "Plataforma Web/backend"
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na pasta `backend/`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/bim_fm_platform
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
AI_MODEL_PATH=../PonteInspecao.lib/best_deeplab_lr0.0001_bs4_fold2.pth
```

## Configuração do Banco de Dados

### 1. Criar Banco de Dados

```bash
# Conectar ao PostgreSQL
psql -U postgres

# Criar banco de dados
CREATE DATABASE bim_fm_platform;

# Criar usuário (opcional)
CREATE USER bimfm_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bim_fm_platform TO bimfm_user;
```

### 2. Executar Schema SQL

```bash
psql -U postgres -d bim_fm_platform -f "Plataforma Web/database/schema.sql"
```

### 3. Inicializar MIR Requirements

```bash
psql -U postgres -d bim_fm_platform -f "Plataforma Web/database/init_mir_requirements.sql"
```

## Instalação do Frontend

### 1. Instalar Dependências

```bash
cd "Plataforma Web/frontend"
npm install
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na pasta `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

## Configuração do Modelo de IA

### 1. Verificar Caminho do Modelo

O modelo de IA (SwinDeepLab) deve estar localizado em:
```
../PonteInspecao.lib/best_deeplab_lr0.0001_bs4_fold2.pth
```

### 2. Verificar Arquivo swin_model.py

O arquivo `swin_model.py` deve estar acessível. O serviço de IA tentará importá-lo de:
```
../PonteInspecao.lib/swin_model.py
```

### 3. Testar Modelo

```bash
cd backend
python -c "from app.services.ai_service import load_model; load_model('path/to/model.pth', 'cpu')"
```

## Instalação do Add-on Blender

### 1. Localizar Pasta de Add-ons do Blender

- **Windows**: `%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons\`
- **Linux**: `~/.config/blender/<version>/scripts/addons/`
- **Mac**: `~/Library/Application Support/Blender/<version>/scripts/addons/`

### 2. Copiar Add-on

```bash
# Copiar pasta do add-on
cp -r "Plataforma Web/blender-addon" "<blender_addons_path>/bimfm_platform"
```

### 3. Ativar Add-on no Blender

1. Abrir Blender
2. Ir em `Edit > Preferences > Add-ons`
3. Buscar "BIM-FM Platform Sync"
4. Ativar o add-on
5. Configurar URL da API e IFC File ID no painel lateral (N)

## Executando a Plataforma

### 1. Iniciar Banco de Dados

```bash
# Windows (se instalado como serviço, já está rodando)
# Linux/Mac
sudo systemctl start postgresql
```

### 2. Iniciar Backend

```bash
cd "Plataforma Web/backend"
source venv/bin/activate  # ou venv\Scripts\activate no Windows
uvicorn main:app --reload --port 8000
```

O backend estará disponível em: `http://localhost:8000`
Documentação da API: `http://localhost:8000/docs`

### 3. Iniciar Frontend

```bash
cd "Plataforma Web/frontend"
npm run dev
```

O frontend estará disponível em: `http://localhost:3000`

## Uso da Plataforma

### 1. Upload de Arquivo IFC

1. Acesse o frontend
2. Vá para "Visualizador 3D"
3. Faça upload de um arquivo IFC
4. Aguarde o processamento (pode levar alguns minutos)

### 2. Criar Inspeção

1. Vá para "Inspeções"
2. Clique em "Nova Inspeção"
3. Preencha os dados:
   - Código único
   - Selecione o ativo
   - Data da inspeção
   - Local
   - Se há patologia e severidade
4. Adicione fotos (opcional)
5. Salve

### 3. Análise com IA

Ao criar uma inspeção com fotos, a análise de IA será executada automaticamente:
- Detecta armadura exposta
- Gera máscaras de detecção
- Cria heatmaps de probabilidade
- Calcula confiança da detecção

### 4. Sincronização com Blender

1. Abra Blender
2. Abra o painel "BIM-FM" (tecla N)
3. Configure URL da API e IFC File ID
4. Clique em "Carregar da Plataforma" para importar dados
5. Clique em "Enviar para Plataforma" para exportar modificações

## Troubleshooting

### Erro: "Model not found"

**Solução**: Verifique se o caminho do modelo está correto no arquivo `.env`:
```env
AI_MODEL_PATH=../PonteInspecao.lib/best_deeplab_lr0.0001_bs4_fold2.pth
```

### Erro: "Database connection failed"

**Solução**: 
1. Verifique se PostgreSQL está rodando
2. Confirme as credenciais no `.env`
3. Teste conexão: `psql -U user -d bim_fm_platform`

### Erro: "CORS error" no frontend

**Solução**: Adicione a URL do frontend em `CORS_ORIGINS` no backend `.env`:
```env
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Erro: "IFC file processing failed"

**Solução**:
1. Verifique se o arquivo IFC é válido
2. Confirme se IfcOpenShell está instalado: `pip install ifcopenshell`
3. Verifique logs do backend para mais detalhes

### Add-on Blender não aparece

**Solução**:
1. Verifique se copiou para a pasta correta
2. Reinicie Blender
3. Verifique console do Blender para erros (Window > Toggle System Console)

## Próximos Passos

1. **Configurar autenticação**: Implementar sistema de login/usuários
2. **Otimizar processamento IFC**: Usar cache e processamento assíncrono
3. **Melhorar visualizador 3D**: Implementar navegação completa com IFC.js
4. **Exportar IFC atualizado**: Implementar exportação com modificações
5. **Dashboard avançado**: Adicionar gráficos e relatórios

## Suporte

Para questões e problemas:
1. Consulte a documentação da API em `/docs`
2. Verifique logs do backend e frontend
3. Consulte o artigo de referência para arquitetura

