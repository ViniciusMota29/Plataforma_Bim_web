# Plataforma Web de Gestão de Ativos BIM/IFC

Plataforma web completa para gestão de ativos usando BIM e IFC, baseada no artigo "BIM-FM Integration through openBIM: Solutions for Interoperability towards Efficient Operations" (Otranto et al., 2025).

## 📋 Estrutura do Projeto

```
Plataforma Web/
├── backend/          # API FastAPI com IfcOpenShell
├── frontend/         # Aplicação React com IFC.js
├── database/         # Scripts SQL e migrações
├── docs/            # Documentação e guias
└── blender-addon/   # Add-on Blender para sincronização
```

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+ com PostGIS
- Blender 3.0+ (para add-on)

### Instalação

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend

```bash
cd frontend
npm install
```

#### Banco de Dados

```bash
# Criar banco de dados
createdb bim_fm_platform
psql -d bim_fm_platform -f database/schema.sql
```

### Execução

#### Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm start
```

## 📚 Documentação

Consulte a pasta `docs/` para:
- Guia de implementação completo
- Arquitetura do sistema
- API Reference
- Guia do add-on Blender

## 🔧 Funcionalidades

- ✅ Upload e processamento de arquivos IFC
- ✅ Visualizador 3D interativo (IFC.js)
- ✅ Gestão de inspeções
- ✅ Análise de imagens com IA (SwinDeepLab)
- ✅ Edição de propriedades BIM
- ✅ Sincronização bidirecional com Blender
- ✅ Exportação de IFC atualizado
- ✅ Dashboard com estatísticas

## 📖 Referências

- Artigo: "BIM-FM Integration through openBIM: Solutions for Interoperability towards Efficient Operations"
- DOI: 10.36680/j.itcon.2025.012
- Disponível em: https://www.itcon.org/papers/2025_12-ITcon-Otranto.pdf

