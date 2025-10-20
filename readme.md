# 🤖 Bot Telegram - Remoção de Duplicatas SIMPLIFICADO

Bot ultra-leve que remove duplicatas sem baixar nada! Usa apenas o `file_unique_id` do Telegram.

## ✨ Por que é melhor?

### ❌ Versão Antiga (Complexa)
- Baixava cada arquivo (limitado a 20MB)
- Processava imagens com hash perceptual
- Processava vídeos frame por frame
- Gastava muita memória e CPU
- Lento para arquivos grandes

### ✅ Versão Nova (Simples)
- **NÃO baixa nada!** Usa `file_unique_id` do Telegram
- **Sem limite de tamanho!** Funciona com arquivos gigantes
- **Instantâneo!** Verificação imediata
- **Leve!** Apenas 1 dependência
- **100% preciso!** Usa ID único do Telegram

## 🎯 Como Funciona

```python
# O Telegram já dá um ID único para cada arquivo
message.photo[0].file_unique_id  # "AgADAwAD4KcxGw"

# Se esse ID já existir = DUPLICATA!
if file_unique_id in saved_ids:
    delete_message()  # Remove duplicata
else:
    saved_ids.add(file_unique_id)  # Salva novo
```

**Simples assim!** Sem downloads, sem processamento pesado.

## 🚀 Recursos

### Detecta Duplicatas de:
- 🖼 **Fotos** (qualquer tamanho)
- 🎥 **Vídeos** (qualquer tamanho, até 2GB+)
- 🎞 **GIFs/Animações**
- 📄 **Documentos** (PDF, ZIP, etc)
- 🎵 **Áudios**
- 🎭 **Stickers**

### Funciona Com:
- ✅ Arquivos enviados diretamente
- ✅ Arquivos encaminhados
- ✅ Arquivos reenviados
- ✅ Arquivos de qualquer tamanho
- ✅ Múltiplos grupos simultaneamente

### Multilíngue:
- 🇧🇷 Português
- 🇺🇸 English
- 🇪🇸 Español
- 🇫🇷 Français
- 🇩🇪 Deutsch
- 🇮🇹 Italiano

## 📦 Deploy Rápido (3 minutos)

### 1️⃣ Criar Bot

```
1. Abra @BotFather no Telegram
2. Envie: /newbot
3. Escolha nome e username
4. Copie o TOKEN
```

### 2️⃣ Deploy no Render

```
1. Acesse render.com
2. New + → Web Service
3. Conecte este repositório
4. Configure:
   - Build: pip install -r requirements.txt
   - Start: python bot.py
   - Variável: TELEGRAM_BOT_TOKEN = seu_token
5. Deploy!
```

### 3️⃣ Adicionar ao Grupo

```
1. Adicione o bot ao grupo
2. Promova para ADMINISTRADOR
3. Dê permissão para "Deletar mensagens"
4. Pronto! Comece a enviar fotos/vídeos
```

## 📱 Comandos

- `/start` - Mensagem de boas-vindas
- `/help` - Explicação completa
- `/`
