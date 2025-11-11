# 🚀 Quick Start - Plataforma BIM-FM

Guia rápido para começar a usar a plataforma.

## ⚡ Início Rápido (5 minutos)

### 1. Backend

```bash
cd "Plataforma Web/backend"
python -m venv venv
venv\Scripts\activate  # Windows
# ou: source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Criar arquivo .env
echo DATABASE_URL=postgresql://user:password@localhost:5432/bim_fm_platform > .env
echo SECRET_KEY=your-secret-key >> .env

# Iniciar servidor
uvicorn main:app --reload
```

### 2. Banco de Dados

```bash
# Criar banco
createdb bim_fm_platform

# Executar schema
psql -d bim_fm_platform -f database/schema.sql
```

### 3. Frontend

```bash
cd "Plataforma Web/frontend"
npm install

# Criar arquivo .env
echo VITE_API_URL=http://localhost:8000 > .env

# Iniciar
npm run dev
```

### 4. Acessar

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 📋 Checklist de Configuração

- [ ] PostgreSQL instalado e rodando
- [ ] Banco de dados criado
- [ ] Schema SQL executado
- [ ] Backend rodando (porta 8000)
- [ ] Frontend rodando (porta 3000)
- [ ] Modelo de IA acessível (opcional)
- [ ] Arquivo .env configurado

## 🎯 Primeiros Passos

1. **Upload IFC**: Vá em "Visualizador 3D" e faça upload de um arquivo IFC
2. **Criar Inspeção**: Vá em "Inspeções" > "Nova Inspeção"
3. **Ver Dashboard**: Acesse a página inicial para ver estatísticas

## ❓ Problemas Comuns

**Erro de conexão com banco?**
- Verifique se PostgreSQL está rodando
- Confirme DATABASE_URL no .env

**CORS error?**
- Adicione URL do frontend em CORS_ORIGINS no backend .env

**Modelo de IA não encontrado?**
- Verifique AI_MODEL_PATH no .env
- Modelo deve estar em: `../PonteInspecao.lib/best_deeplab_lr0.0001_bs4_fold2.pth`

## 📚 Documentação Completa

Consulte `docs/GUIA_IMPLEMENTACAO.md` para instruções detalhadas.

