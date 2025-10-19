# ⚡ Guia Rápido - 5 Minutos

## 🎯 Objetivo

Ter seu bot funcionando em 5 minutos, removendo duplicatas automaticamente!

---

## 📱 PASSO 1: Criar o Bot (2 minutos)

### 1.1 Abrir BotFather

```
Telegram → Buscar → @BotFather → START
```

### 1.2 Criar Bot

```
Digite: /newbot

BotFather: Como vai se chamar o bot?
Você: Bot Dedup Grupo

BotFather: Escolha um username (deve terminar em 'bot')
Você: meu_dedup_grupo_bot

✅ PRONTO! Copie o TOKEN que apareceu!
```

**TOKEN vai parecer com:**
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

⚠️ **IMPORTANTE:** Guarde esse token! Você vai precisar.

---

## 🚀 PASSO 2: Deploy no Render (2 minutos)

### 2.1 Acessar Render

1. Vá em: https://render.com
2. Clique em "Get Started"
3. Faça login com GitHub

### 2.2 Criar Repositório no GitHub

1. Vá em: https://github.com/new
2. Nome: `telegram-dedup-bot`
3. Marque: "Add README file"
4. Crie o repositório
5. Clique em "Upload files"
6. Arraste os arquivos: `bot.py` e `requirements.txt`
7. Commit!

### 2.3 Conectar no Render

1. No Render, clique: **"New +"** → **"Web Service"**
2. Escolha: "Connect a repository"
3. Selecione: `telegram-dedup-bot`
4. Clique: "Connect"

### 2.4 Configurar

Preencha exatamente assim:

```
Name: telegram-dedup-bot
Region: Oregon (US West)
Branch: main

Build Command: pip install -r requirements.txt
Start Command: python bot.py

Instance Type: Free
```

### 2.5 Adicionar Token

Na seção "Environment Variables":

```
Key: TELEGRAM_BOT_TOKEN
Value: [cole seu token aqui]
```

### 2.6 Deploy!

1. Clique: **"Create Web Service"**
2. Aguarde 2-3 minutos
3. Quando aparecer "Live" = Pronto! 🎉

---

## 👥 PASSO 3: Adicionar ao Grupo (1 minuto)

### 3.1 Adicionar Bot

1. Abra seu grupo no Telegram
2. Configurações → Adicionar Membros
3. Procure por: `@meu_dedup_grupo_bot`
4. Adicione!

### 3.2 Promover para Admin

```
1. Configurações do Grupo
2. Administradores
3. Adicionar Administrador
4. Escolha o bot
5. ✅ MARQUE APENAS: "Deletar mensagens de outros"
6. ❌ DESMARQUE todo o resto
7. Salvar
```

### 3.3 Testar!

No grupo, digite:
```
/start
```

Bot deve responder com boas-vindas! ✅

---

## 🎬 PASSO 4: Testar Funcionamento

### Teste 1: Foto Única
```
1. Envie qualquer foto
2. Bot não faz nada (salvou silenciosamente)
```

### Teste 2: Foto Duplicada
```
1. Envie a MESMA foto novamente
2. Bot DELETA automaticamente! 🗑️
```

### Teste 3: Foto Encaminhada
```
1. Encaminhe a foto que você enviou
2. Bot detecta e DELETA! 🎯
```

✅ **Funcionou? Parabéns! Seu bot está operacional!**

---

## 📊 Comandos Úteis

Teste estes comandos no grupo:

```
/help   → Ver ajuda completa
/stats  → Ver estatísticas
/lang   → Mudar idioma
/clear  → Limpar histórico
```

---

## ✅ Checklist de Sucesso

Marque conforme completar:

- [ ] Bot criado no BotFather
- [ ] Token copiado
- [ ] Repositório GitHub criado
- [ ] Arquivos enviados (`bot.py` e `requirements.txt`)
- [ ] Web Service criado no Render
- [ ] Token configurado nas variáveis
- [ ] Deploy finalizado (status "Live")
- [ ] Bot adicionado ao grupo
- [ ] Bot promovido para administrador
- [ ] Permissão "Deletar mensagens" ativada
- [ ] `/start` funcionou
- [ ] Teste de duplicata funcionou

---

## 🐛 Problemas Comuns

### ❌ Bot não responde no grupo

**Solução:**
```
1. Verifique no Render se está "Live"
2. Veja os logs: Render → Logs
3. Procure por "Bot iniciado com sucesso!"
```

### ❌ Bot não deleta mensagens

**Solução:**
```
1. Confirme que é ADMINISTRADOR
2. Verifique permissão "Deletar mensagens"
3. Remova e adicione novamente
```

### ❌ "Need admin permissions"

**Solução:**
```
1. O bot precisa ser ADMIN
2. Promova nas configurações do grupo
3. Dê permissão para deletar
```

### ❌ Token inválido

**Solução:**
```
1. Verifique se copiou correto
2. Não deve ter espaços
3. Formato: 1234567890:ABCdefGHI...
```

---

## 📞 Precisa de Ajuda?

### Opção 1: Logs do Render
```
Render → Seu Service → Logs
```
Procure por linhas com "ERROR" ou "FAILED"

### Opção 2: Testar Localmente
```bash
export TELEGRAM_BOT_TOKEN="seu_token"
python bot.py
```

### Opção 3: Suporte
- GitHub Issues
- Email: seu-email@exemplo.com

---

## 🎉 Próximos Passos

Agora que está funcionando:

1. **Adicione a mais grupos**
   - O bot funciona em múltiplos grupos!

2. **Configure o idioma**
   - `/lang` e escolha seu idioma

3. **Monitore estatísticas**
   - `/stats` mostra quantas duplicatas foram removidas

4. **Compartilhe com amigos**
   - Eles podem adicionar o bot aos grupos deles

---

## 🌟 Dicas Pro

### Dica 1: Grupos Privados
O bot funciona em grupos privados e públicos!

### Dica 2: Múltiplos Grupos
Adicione a quantos grupos quiser - cada um é independente.

### Dica 3: Persistência
Para não perder dados ao reiniciar, adicione Redis (veja README.md).

### Dica 4: Monitoramento
Configure UptimeRobot para manter o bot acordado 24/7.

### Dica 5: Backup
Use `/stats` regularmente para ver a saúde do bot.

---

## 📚 Quer Saber Mais?

Veja a documentação completa:
- `readme.md` - Documentação completa
- `bot.py` - Código comentado
- `security.md` - Guia de segurança

---

**🎊 Parabéns! Seu bot está funcionando perfeitamente!**

Se deu tudo certo, você agora tem um bot que:
- ✅ Remove duplicatas automaticamente
- ✅ Funciona com qualquer tamanho de arquivo
- ✅ Suporta 6 idiomas
- ✅ Roda 24/7 gratuitamente

**⭐ Gostou? Dê uma estrela no GitHub!**
