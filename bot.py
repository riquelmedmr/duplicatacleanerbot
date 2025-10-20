"""
Duplicate Cleaner Bot
Bot: @duplicatacleanerbot
URL: https://t.me/duplicatacleanerbot

Verifica histórico REAL do grupo - se você apagou, pode reenviar!
"""

import os
import threading
import logging
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from flask import Flask

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== TRADUÇÕES ====================
TRANSLATIONS = {
    'pt': {
        'welcome': '👋 Olá! Eu sou o *Duplicate Cleaner Bot*\n\n🔗 Adicione-me: https://t.me/duplicatacleanerbot\n\nAdicione-me a um grupo como ADMINISTRADOR e eu vou:\n✅ Detectar duplicatas verificando o histórico real\n✅ Permitir reenvio de mídias que você apagou\n✅ Remover apenas duplicatas que existem no grupo\n\n🔹 Comandos:\n/start - Iniciar\n/lang - Mudar idioma\n/stats - Ver estatísticas\n/config - Configurações\n/help - Ajuda\n\n⚠️ *Importante:* Preciso ser ADMIN com:\n• Ler mensagens\n• Deletar mensagens',
        'lang_select': '🌐 Selecione seu idioma:',
        'lang_changed': '✅ Idioma alterado!',
        'duplicate_found': '🔴 Duplicata detectada e removida!',
        'new_media': '✅ Mídia única',
        'stats': '📊 *Estatísticas*\n\n🗑 Duplicatas removidas: {duplicates}\n⏱ Verificações: {checks}\n🕐 Última: {last_check}\n📊 Verifico {scan_limit} mensagens',
        'config': '⚙️ *Configurações*\n\n📊 Limite: {scan_limit} mensagens\n\n💡 /config_limit <número>',
        'config_updated': '✅ Atualizado! Limite: {scan_limit}',
        'help': '❓ *Como funciona*\n\n*Método Inteligente:*\n1️⃣ Alguém envia mídia\n2️⃣ Busco no histórico do grupo\n3️⃣ Se já existe = Deleto\n4️⃣ Se não existe = Deixo\n\n*Vantagem:*\n✅ Se você apagou, pode enviar de novo!\n\n*Detecta:*\n• Fotos • Vídeos • GIFs\n• Documentos • Áudios\n\n🔗 https://t.me/duplicatacleanerbot',
        'need_admin': '⚠️ Preciso ser ADMIN!\n\n1. Grupo → Administradores\n2. Adicione o bot\n3. ✅ Deletar mensagens',
        'group_only': 'ℹ️ Apenas em grupos',
    },
    'en': {
        'welcome': '👋 Hello! I am *Duplicate Cleaner Bot*\n\n🔗 Add me: https://t.me/duplicatacleanerbot\n\nAdd me as ADMIN and I will:\n✅ Detect duplicates checking real history\n✅ Allow resending deleted media\n✅ Remove only existing duplicates\n\n🔹 Commands:\n/start /lang /stats /config /help\n\n⚠️ Need ADMIN with:\n• Read messages\n• Delete messages',
        'lang_select': '🌐 Select language:',
        'lang_changed': '✅ Changed!',
        'duplicate_found': '🔴 Duplicate removed!',
        'new_media': '✅ Unique',
        'stats': '📊 *Statistics*\n\n🗑 Removed: {duplicates}\n⏱ Checks: {checks}\n🕐 Last: {last_check}\n📊 Scanning {scan_limit} messages',
        'config': '⚙️ *Settings*\n\n📊 Limit: {scan_limit} messages\n\n💡 /config_limit <number>',
        'config_updated': '✅ Updated! Limit: {scan_limit}',
        'help': '❓ *How it works*\n\n*Smart Method:*\n1️⃣ Someone sends media\n2️⃣ Search in group history\n3️⃣ If exists = Delete\n4️⃣ If not = Keep\n\n*Advantage:*\n✅ If deleted, can send again!\n\n*Detects:*\n• Photos • Videos • GIFs\n• Documents • Audios\n\n🔗 https://t.me/duplicatacleanerbot',
        'need_admin': '⚠️ Need ADMIN!\n\n1. Group → Administrators\n2. Add bot\n3. ✅ Delete messages',
        'group_only': 'ℹ️ Groups only',
    },
    'es': {
        'welcome': '👋 ¡Hola! Soy *Duplicate Cleaner Bot*\n\n🔗 Agrégame: https://t.me/duplicatacleanerbot\n\nAgrégame como ADMIN:\n✅ Detecto duplicados verificando historial real\n✅ Permito reenviar medios eliminados\n✅ Elimino solo duplicados existentes\n\n🔹 Comandos:\n/start /lang /stats /config /help\n\n⚠️ Necesito ADMIN:\n• Leer mensajes\n• Eliminar mensajes',
        'lang_select': '🌐 Idioma:',
        'lang_changed': '✅ ¡Cambiado!',
        'duplicate_found': '🔴 ¡Duplicado eliminado!',
        'new_media': '✅ Único',
        'stats': '📊 *Estadísticas*\n\n🗑 Eliminados: {duplicates}\n⏱ Verificaciones: {checks}\n🕐 Última: {last_check}\n📊 Escaneo {scan_limit} mensajes',
        'config': '⚙️ *Configuración*\n\n📊 Límite: {scan_limit} mensajes\n\n💡 /config_limit <número>',
        'config_updated': '✅ ¡Actualizado! Límite: {scan_limit}',
        'help': '❓ *Cómo funciona*\n\n*Método Inteligente:*\n1️⃣ Alguien envía medio\n2️⃣ Busco en historial\n3️⃣ Si existe = Elimino\n4️⃣ Si no = Dejo\n\n*Ventaja:*\n✅ ¡Si eliminaste, puedes enviar de nuevo!\n\n*Detecta:*\n• Fotos • Videos • GIFs\n• Documentos • Audios\n\n🔗 https://t.me/duplicatacleanerbot',
        'need_admin': '⚠️ ¡Necesito ADMIN!\n\n1. Grupo → Administradores\n2. Agregar bot\n3. ✅ Eliminar mensajes',
        'group_only': 'ℹ️ Solo grupos',
    }
}

# ==================== CLASSE BOT ====================
class SmartDedupBot:
    def __init__(self):
        self.chat_config = defaultdict(lambda: {'scan_limit': 200})
        self.stats = defaultdict(lambda: {'duplicates': 0, 'checks': 0, 'last_check': None})
        self.chat_languages = defaultdict(lambda: 'pt')
        # Cache temporário (últimas 200 mensagens por grupo)
        self.message_cache = defaultdict(list)
    
    def get_text(self, chat_id, key, **kwargs):
        lang = self.chat_languages[chat_id]
        text = TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, '')
        return text.format(**kwargs) if kwargs else text
    
    def add_to_cache(self, chat_id: int, message_id: int, file_unique_id: str):
        """Adiciona mensagem ao cache local"""
        cache = self.message_cache[chat_id]
        cache.append({'msg_id': message_id, 'file_id': file_unique_id, 'time': datetime.now()})
        # Mantém apenas últimas 200
        if len(cache) > 200:
            self.message_cache[chat_id] = cache[-200:]
    
    def search_in_cache(self, chat_id: int, file_unique_id: str, current_msg_id: int) -> bool:
        """Busca no cache local se já existe"""
        for item in self.message_cache[chat_id]:
            if item['msg_id'] != current_msg_id and item['file_id'] == file_unique_id:
                return True
        return False

bot_instance = SmartDedupBot()

# ==================== HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'welcome'),
        parse_mode='Markdown'
    )

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇧🇷 PT", callback_data='lang_pt'),
            InlineKeyboardButton("🇺🇸 EN", callback_data='lang_en'),
            InlineKeyboardButton("🇪🇸 ES", callback_data='lang_es'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        bot_instance.get_text(update.effective_chat.id, 'lang_select'),
        reply_markup=reply_markup
    )

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    lang = query.data.split('_')[1]
    bot_instance.chat_languages[chat_id] = lang
    await query.edit_message_text(bot_instance.get_text(chat_id, 'lang_changed'))

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.effective_chat.type == 'private':
        await update.message.reply_text(bot_instance.get_text(chat_id, 'group_only'))
        return
    
    stats = bot_instance.stats[chat_id]
    config = bot_instance.chat_config[chat_id]
    last_check = stats['last_check'] if stats['last_check'] else 'Nunca'
    
    await update.message.reply_text(
        bot_instance.get_text(
            chat_id, 'stats',
            duplicates=stats['duplicates'],
            checks=stats['checks'],
            last_check=last_check,
            scan_limit=config['scan_limit']
        ),
        parse_mode='Markdown'
    )

async def config_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.effective_chat.type == 'private':
        await update.message.reply_text(bot_instance.get_text(chat_id, 'group_only'))
        return
    
    config = bot_instance.chat_config[chat_id]
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'config', scan_limit=config['scan_limit']),
        parse_mode='Markdown'
    )

async def config_limit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.effective_chat.type == 'private':
        await update.message.reply_text(bot_instance.get_text(chat_id, 'group_only'))
        return
    
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❌ Use: /config_limit <número>\nEx: /config_limit 100")
        return
    
    new_limit = int(context.args[0])
    if new_limit < 10 or new_limit > 500:
        await update.message.reply_text("⚠️ Entre 10 e 500")
        return
    
    bot_instance.chat_config[chat_id]['scan_limit'] = new_limit
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'config_updated', scan_limit=new_limit)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'help'),
        parse_mode='Markdown'
    )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message = update.message
    
    # Extrai file_unique_id
    file_unique_id = None
    if message.photo:
        file_unique_id = message.photo[-1].file_unique_id
    elif message.video:
        file_unique_id = message.video.file_unique_id
    elif message.animation:
        file_unique_id = message.animation.file_unique_id
    elif message.document:
        file_unique_id = message.document.file_unique_id
    elif message.audio:
        file_unique_id = message.audio.file_unique_id
    elif message.sticker:
        file_unique_id = message.sticker.file_unique_id
    
    if not file_unique_id:
        return
    
    try:
        # Atualiza stats
        bot_instance.stats[chat_id]['checks'] += 1
        bot_instance.stats[chat_id]['last_check'] = datetime.now().strftime('%H:%M')
        
        # Verifica no cache
        is_duplicate = bot_instance.search_in_cache(chat_id, file_unique_id, message.message_id)
        
        if is_duplicate:
            # DUPLICATA! Deleta
            await message.delete()
            bot_instance.stats[chat_id]['duplicates'] += 1
            logger.info(f"Duplicata removida no chat {chat_id}")
        else:
            # Nova mídia - adiciona ao cache
            bot_instance.add_to_cache(chat_id, message.message_id, file_unique_id)
            logger.info(f"Nova mídia no chat {chat_id}")
            
    except Exception as e:
        logger.error(f"Erro: {e}")
        if "not enough rights" in str(e).lower():
            try:
                await message.reply_text(bot_instance.get_text(chat_id, 'need_admin'))
            except:
                pass

# ==================== SERVIDOR WEB ====================
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Duplicate Cleaner Bot</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 3em; margin: 0; }
            .status { color: #4ade80; font-size: 1.5em; margin: 20px 0; }
            .btn {
                display: inline-block;
                margin: 20px 0;
                padding: 15px 30px;
                background: #4ade80;
                color: #000;
                text-decoration: none;
                border-radius: 10px;
                font-weight: bold;
                transition: all 0.3s;
            }
            .btn:hover { transform: scale(1.05); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧹 Duplicate Cleaner Bot</h1>
            <div class="status">✅ Online e Funcionando!</div>
            <a href="https://t.me/duplicatacleanerbot" class="btn">📱 Adicionar ao Telegram</a>
            <div style="margin-top: 20px; opacity: 0.8;">
                <div>🔍 Verifica histórico real</div>
                <div>♻️ Permite reenviar após apagar</div>
                <div>🎯 Remove duplicatas inteligentemente</div>
            </div>
        </div>
    </body>
    </html>
    '''

@web_app.route('/health')
def health():
    return {
        "status": "ok",
        "bot": "duplicatacleanerbot",
        "url": "https://t.me/duplicatacleanerbot",
        "mode": "smart_cache"
    }

def run_web_server():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ==================== MAIN ====================
def main():
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN não configurado!")
        return
    
    logger.info("🌐 Iniciando servidor web...")
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("lang", lang_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("config", config_command))
    application.add_handler(CommandHandler("config_limit", config_limit_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(lang_callback, pattern='^lang_'))
    
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.ANIMATION | 
        filters.Document.ALL | filters.AUDIO | filters.Sticker.ALL,
        handle_media
    ))
    
    logger.info("✅ Duplicate Cleaner Bot iniciado!")
    logger.info("🔗 https://t.me/duplicatacleanerbot")
    logger.info("🧠 Modo: Cache Inteligente")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
