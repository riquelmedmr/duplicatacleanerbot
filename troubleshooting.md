# 🔧 Solução de Problemas

## ❌ Erro: "Application exited early"

### Causa
O Render detecta que o aplicativo encerrou antes de responder às requisições HTTP.

### ✅ Solução (JÁ IMPLEMENTADA)
O código agora inclui um servidor Flask que mantém o serviço ativo:

```python
# Servidor web roda em paralelo ao bot
web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()

# Bot continua rodando normalmente
application.run_polling()
```

### Verificar se está funcionando:
1. Acesse: `https://seu-app.onrender.com`
2. Deve aparecer: "✅ Online e Funcionando!"

---

## ❌ Erro: "TELEGRAM_BOT_TOKEN não configurado"

### Causa
A variável de ambiente não foi configurada no Render.

### ✅ Solução

1. No Render, vá em: **Environment**
2. Clique em: **Add Environment Variable**
3. Adicione:
   ```
   Key: TELEGRAM_BOT_TOKEN
   Value: seu_token_do_botfather
   ```
4. Clique em: **Save Changes**
5. Aguarde o redeploy automático

---

## ❌ Erro: "Failed to build"

### Causa
Erro ao instalar dependências do Python.

### ✅ Solução

**Verifique o `requirements.txt`:**
```
python-telegram-bot==20.7
Flask==3.0.0
```

**Verifique a versão do Python:**
- No Render, em **Settings** → **Environment**
- Python Version: 3.11 (recomendado)

**Limpe o cache:**
1. No Render: **Settings** → **Build & Deploy**
2. Clique em: **Clear build cache**
3. Faça: **Manual Deploy** → **Deploy latest commit**

---

## ❌ Erro: "Connection timed out"

### Causa
O bot não consegue conectar à API do Telegram.

### ✅ Solução

1. **Verifique o token:**
   - Deve ter formato: `1234567890:ABCdef...`
   - Sem espaços extras
   - Sem aspas

2. **Teste o token:**
   ```bash
   curl https://api.telegram.org/bot<SEU_TOKEN>/getMe
   ```
   Deve retornar dados do bot

3. **Verifique firewall:**
   - Render permite conexões externas por padrão
   - Se bloqueado, entre em contato com suporte

---

## ❌ Erro: "Bot não responde no Telegram"

### Causa
Bot está online mas não processa mensagens.

### ✅ Solução

**1. Verifique se está rodando:**
```
Render → Logs → procure por "✅ Bot iniciado com sucesso!"
```

**2. Teste com o BotFather:**
- Abra @BotFather
- Envie: `/mybots`
- Selecione seu bot
- Verifique se está ativo

**3. Verifique permissões:**
- Bot precisa ver mensagens no grupo
- Settings → Privacy Mode deve estar OFF

**4. Teste em privado primeiro:**
- Abra conversa privada com o bot
- Envie: `/start`
- Deve responder

---

## ❌ Erro: "Bot não deleta mensagens"

### Causa
Bot não tem permissões de administrador.

### ✅ Solução

**No grupo:**
1. Configurações → Administradores
2. Adicionar Administrador → Escolha o bot
3. **Marque APENAS:**
   - ✅ Deletar mensagens de outros
4. **Desmarque todo o resto**
5. Salve

**Teste:**
```
1. Envie uma foto
2. Envie a mesma foto novamente
3. Bot deve deletar a segunda
```

**Se ainda não funcionar:**
- Remova o bot do grupo
- Adicione novamente
- Promova para admin
- Teste novamente

---

## ❌ Erro: "Service is sleeping"

### Causa
Plano grátis do Render dorme após 15min de inatividade.

### ✅ Solução 1: Ping Automático (Grátis)

Use [UptimeRobot](https://uptimerobot.com):

1. Crie conta gratuita
2. Add New Monitor:
   ```
   Monitor Type: HTTP(s)
   URL: https://seu-app.onrender.com
   Monitoring Interval: 5 minutes
   ```
3. Salve!

Agora o bot ficará sempre acordado! 🎉

### ✅ Solução 2: Upgrade (Pago)

Render Starter Plan ($7/mês):
- Sem dormência
- Mais RAM e CPU
- Deploy mais rápido

---

## ❌ Erro: "Out of memory"

### Causa
Bot usando muita memória (raro na versão simplificada).

### ✅ Solução

**1. Limpe dados periodicamente:**
```python
# Adicione limpeza automática
from datetime import datetime, timedelta

# No bot.py, adicione:
def cleanup_old_data():
    # Remove dados de mais de 30 dias
    for chat_id in list(bot_instance.photo_ids.keys()):
        # Limpa se grupo inativo
        pass
```

**2. Use Redis (recomendado para produção):**
```bash
# No Render, adicione:
New + → Redis (Free tier)

# Conecte ao bot
```

**3. Upgrade do plano:**
- Free: 512MB RAM
- Starter: 1GB RAM
- Standard: 2GB+ RAM

---

## ❌ Erro: "Rate limit exceeded"

### Causa
Muitas requisições para a API do Telegram.

### ✅ Solução

**Já implementado no código:**
- Limites da API do Telegram são respeitados
- python-telegram-bot gerencia automaticamente

**Se ainda ocorrer:**
1. Reduza frequência de mensagens
2. Aguarde alguns minutos
3. API do Telegram libera automaticamente

---

## ❌ Erro: "Import error"

### Causa
Biblioteca não instalada.

### ✅ Solução

**Verifique imports no `bot.py`:**
```python
# Todos estes devem estar no requirements.txt
from telegram import ...  # python-telegram-bot
from flask import ...     # Flask
```

**Adicione ao `requirements.txt` se faltar:**
```
python-telegram-bot==20.7
Flask==3.0.0
```

**Redeploy:**
```
Render → Manual Deploy → Deploy latest commit
```

---

## 🔍 Como Ler os Logs

### Acessar logs:
```
Render → Seu Service → Logs
```

### Logs importantes:

**✅ Sucesso:**
```
🌐 Iniciando servidor web...
✅ Bot iniciado com sucesso!
🎯 Aguardando mensagens...
📡 Servidor web rodando na porta 10000
```

**❌ Erro de Token:**
```
❌ TELEGRAM_BOT_TOKEN não configurado!
Configure a variável de ambiente TELEGRAM_BOT_TOKEN
```

**❌ Erro de Permissão:**
```
ERROR - Erro ao deletar: not enough rights
```
**Solução:** Promova bot para admin

**❌ Erro de Conexão:**
```
ERROR - Connection timed out
```
**Solução:** Verifique token e internet

---

## 📊 Verificar Status do Bot

### Método 1: Via Web
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

### Método 2: Via Telegram
```
/start → Bot deve responder
/help → Bot deve mostrar ajuda
```

### Método 3: Via Render Dashboard
```
Render → Seu Service → Status
```
Deve mostrar: 🟢 **Live**

---

## 🆘 Última Opção: Reset Completo

Se nada funcionar:

### 1. Delete o Service
```
Render → Seu Service → Settings → Delete Service
```

### 2. Recrie do Zero
```
Siga o QUICK_START.md novamente
```

### 3. Verifique Lista:
- [ ] Token correto
- [ ] requirements.txt com Flask
- [ ] bot.py com servidor web
- [ ] Variável TELEGRAM_BOT_TOKEN configurada
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python bot.py`

---

## 💬 Precisa de Mais Ajuda?

### Opção 1: GitHub Issues
[Abra um issue](seu-repo/issues) com:
- Logs do Render (últimas 50 linhas)
- Descrição do problema
- O que já tentou

### Opção 2: Render Support
- [Render Community](https://community.render.com)
- [Render Docs](https://render.com/docs)

### Opção 3: Telegram
- Entre em grupos de desenvolvimento de bots
- Pergunte na comunidade

---

## ✅ Checklist de Diagnóstico

Marque cada item:

### Configuração Básica
- [ ] Token está correto (formato: 1234567890:ABC...)
- [ ] Token está nas variáveis de ambiente
- [ ] requirements.txt tem Flask
- [ ] bot.py tem servidor web

### Deploy
- [ ] Build concluído com sucesso
- [ ] Status mostra "Live"
- [ ] Logs mostram "Bot iniciado"
- [ ] URL abre página "Online e Funcionando"

### Telegram
- [ ] Bot responde em privado (/start)
- [ ] Bot adicionado ao grupo
- [ ] Bot é administrador
- [ ] Bot tem permissão "Deletar mensagens"
- [ ] Privacy mode está OFF

### Funcionalidade
- [ ] Envia foto → bot silencioso (OK)
- [ ] Envia mesma foto → bot deleta
- [ ] /stats mostra contadores
- [ ] /lang muda idioma

Se todos marcados e ainda não funciona → Delete e recrie!

---

**💪 Não desista! 99% dos problemas são token incorreto ou falta de permissões de admin.**
