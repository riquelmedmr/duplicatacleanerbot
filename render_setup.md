# 🚀 Configuração no Render - Passo a Passo

## ⚠️ Importante: Versão do Python

O bot **precisa** de Python 3.11 (não funciona com 3.13 devido a incompatibilidade da biblioteca).

---

## 📋 Configuração Correta

### No Dashboard do Render:

1. **Vá em Settings → Environment**

2. **Adicione ou edite a variável:**
   ```
   Key: PYTHON_VERSION
   Value: 3.11.0
   ```

3. **Salve as mudanças**

4. **Faça Manual Deploy:**
   - Settings → Build & Deploy
   - Clear build cache (opcional mas recomendado)
   - Manual Deploy → Deploy latest commit

---

## 📁 Arquivos Necessários no Repositório

Certifique-se de ter estes arquivos:

### 1. `.python-version`
```
3.11.0
```

### 2. `requirements.txt`
```
python-telegram-bot==21.9
Flask==3.0.0
```

### 3. `bot.py`
(Código completo do bot)

### 4. `render.yaml` (opcional)
```yaml
services:
  - type: web
    name: telegram-dedup-bot
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python bot.py
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
    autoDeploy: true
    healthCheckPath: /
    numInstances: 1
```

---

## 🔧 Configuração Manual (se não usar render.yaml)

### Build Settings:
```
Build Command: pip install -r requirements.txt
Start Command: python bot.py
```

### Environment Variables:
```
TELEGRAM_BOT_TOKEN = seu_token_aqui
PYTHON_VERSION = 3.11.0
```

### Advanced:
```
Auto-Deploy: Yes
Branch: main
```

---

## ✅ Verificar se Está Funcionando

### 1. Logs devem mostrar:
```
🌐 Iniciando servidor web...
✅ Bot iniciado com sucesso!
🎯 Aguardando mensagens...
```

### 2. URL deve abrir:
```
https://seu-app.onrender.com
```
E mostrar: "✅ Online e Funcionando!"

### 3. Bot responde no Telegram:
```
/start → Recebe boas-vindas
```

---

## 🐛 Se Der Erro

### Erro: "AttributeError: 'Updater' object..."

**Causa:** Python 3.13 sendo usado

**Solução:**
1. Adicione arquivo `.python-version` com `3.11.0`
2. Adicione variável `PYTHON_VERSION=3.11.0`
3. Limpe cache: Settings → Clear build cache
4. Redeploy

### Erro: "Module not found"

**Causa:** Dependências não instaladas

**Solução:**
1. Verifique `requirements.txt`
2. Build Command deve ser: `pip install -r requirements.txt`
3. Redeploy

### Erro: "Application exited early"

**Causa:** Bot não mantém servidor HTTP ativo

**Solução:**
- Código já inclui servidor Flask
- Certifique-se de usar o `bot.py` atualizado

---

## 📊 Monitoramento

### Verificar Saúde do Bot:
```
https://seu-app.onrender.com/health
```

Deve retornar:
```json
{
  "status": "ok",
  "bot": "running"
}
```

### Manter Bot Acordado (Plano Free):

Use [UptimeRobot](https://uptimerobot.com):
- Monitor Type: HTTP(s)
- URL: `https://seu-app.onrender.com/health`
- Interval: 5 minutes

---

## 🔄 Atualizar o Bot

### Método 1: Auto-Deploy (Recomendado)
1. Faça push no GitHub
2. Render detecta e faz deploy automático

### Método 2: Manual
1. Dashboard → Manual Deploy
2. Deploy latest commit

---

## 💾 Backup de Configuração

Salve estas informações:

```
✅ Bot Token: [guarde em local seguro]
✅ Render Service URL: https://seu-app.onrender.com
✅ Python Version: 3.11.0
✅ Build Command: pip install -r requirements.txt
✅ Start Command: python bot.py
```

---

## 🎯 Checklist Final

Antes de considerar pronto:

- [ ] Python 3.11.0 configurado
- [ ] `.python-version` no repositório
- [ ] `requirements.txt` atualizado (v21.9)
- [ ] `TELEGRAM_BOT_TOKEN` configurado
- [ ] Build concluído com sucesso
- [ ] Status = "Live"
- [ ] URL abre página de status
- [ ] `/health` retorna OK
- [ ] Bot responde no Telegram
- [ ] Teste de duplicata funciona

---

## 📞 Suporte

Se nada funcionar:

1. **Logs do Render**
   - Dashboard → Logs
   - Procure por erros em vermelho

2. **GitHub Issues**
   - Reporte o problema com logs

3. **Render Community**
   - [community.render.com](https://community.render.com)

---

**✨ Com a configuração correta, o bot vai funcionar perfeitamente!**
