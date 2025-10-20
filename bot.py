"""
Bot Telegram SIMPLIFICADO - Remoção de Duplicatas
Usa apenas file_unique_id - sem downloads!
"""

import os
import threading
import logging
from typing import Dict, Set
from collections import defaultdict

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

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== TRADUÇÕES ====================
TRANSLATIONS = {
    'pt': {
        'welcome': '👋 Olá! Eu sou o *Duplicate Cleaner Bot*\n\nAdicione-me a um grupo e eu vou detectar e remover fotos/vídeos duplicados automaticamente!\n\n🔹 Comandos:\n/start - Iniciar\n/lang - Mudar idioma\n/stats - Ver estatísticas\n/clear - Limpar histórico\n/help - Ajuda',
        'lang_select': '🌐 Selecione seu idioma:',
        'lang_changed': '✅ Idioma alterado!',
        'duplicate_found': '🔴 Duplicata detectada e removida!',
        'new_media': '✅ Mídia única salva',
        'stats': '📊 *Estatísticas deste chat*\n\n🖼 Fotos únicas: {photos}\n🎥 Vídeos únicos: {videos}\n📄 Documentos únicos: {documents}\n🗑 Duplicatas removidas: {duplicates}\n💾 Total: {total}',
        'cleared': '🗑 Histórico limpo!',
        'help': '❓ *Como funciona*\n\nAdicione o bot a um grupo e dê permissões de administrador.\n\nO bot detecta duplicatas usando o ID único do Telegram (file_unique_id).\nNão precisa baixar nada! É instantâneo e funciona com arquivos de qualquer tamanho.\n\n*Detecta:*\n• Fotos duplicadas\n• Vídeos duplicados\n• GIFs duplicados\n• Documentos duplicados\n• Áudios duplicados\n• Stickers duplicados\n\nFunciona mesmo com encaminhamentos!',
        'error': '❌ Erro ao processar',
        'need_admin': '⚠️ Preciso ser administrador para deletar mensagens!',
        'group_only': 'ℹ️ Este comando funciona apenas em grupos',
    },
    'en': {
        'welcome': '👋 Hello! I am *Duplicate Cleaner Bot*\n\nAdd me to a group and I will detect and remove duplicate photos/videos automatically!\n\n🔹 Commands:\n/start - Start\n/lang - Change language\n/stats - View statistics\n/clear - Clear history\n/help - Help',
        'lang_select': '🌐 Select your language:',
        'lang_changed': '✅ Language changed!',
        'duplicate_found': '🔴 Duplicate detected and removed!',
        'new_media': '✅ Unique media saved',
        'stats': '📊 *Chat Statistics*\n\n🖼 Unique photos: {photos}\n🎥 Unique videos: {videos}\n📄 Unique documents: {documents}\n🗑 Duplicates removed: {duplicates}\n💾 Total: {total}',
        'cleared': '🗑 History cleared!',
        'help': '❓ *How it works*\n\nAdd the bot to a group and give admin permissions.\n\nBot detects duplicates using Telegram unique ID (file_unique_id).\nNo downloads needed! Instant and works with any file size.\n\n*Detects:*\n• Duplicate photos\n• Duplicate videos\n• Duplicate GIFs\n• Duplicate documents\n• Duplicate audios\n• Duplicate stickers\n\nWorks even with forwards!',
        'error': '❌ Processing error',
        'need_admin': '⚠️ I need admin permissions to delete messages!',
        'group_only': 'ℹ️ This command only works in groups',
    },
    'es': {
        'welcome': '👋 ¡Hola! Soy *Duplicate Cleaner Bot*\n\n¡Agrégame a un grupo y detectaré y eliminaré fotos/videos duplicados automáticamente!\n\n🔹 Comandos:\n/start - Iniciar\n/lang - Cambiar idioma\n/stats - Ver estadísticas\n/clear - Limpiar historial\n/help - Ayuda',
        'lang_select': '🌐 Selecciona tu idioma:',
        'lang_changed': '✅ ¡Idioma cambiado!',
        'duplicate_found': '🔴 ¡Duplicado detectado y eliminado!',
        'new_media': '✅ Medio único guardado',
        'stats': '📊 *Estadísticas del chat*\n\n🖼 Fotos únicas: {photos}\n🎥 Videos únicos: {videos}\n📄 Documentos únicos: {documents}\n🗑 Duplicados eliminados: {duplicates}\n💾 Total: {total}',
        'cleared': '🗑 ¡Historial limpiado!',
        'help': '❓ *Cómo funciona*\n\nAgrega el bot a un grupo y dale permisos de administrador.\n\nEl bot detecta duplicados usando el ID único de Telegram (file_unique_id).\n¡No necesita descargas! Instantáneo y funciona con cualquier tamaño.\n\n*Detecta:*\n• Fotos duplicadas\n• Videos duplicados\n• GIFs duplicados\n• Documentos duplicados\n• Audios duplicados\n• Stickers duplicados\n\n¡Funciona incluso con reenvíos!',
        'error': '❌ Error al procesar',
        'need_admin': '⚠️ ¡Necesito permisos de administrador para eliminar mensajes!',
        'group_only': 'ℹ️ Este comando solo funciona en grupos',
    }
}

# ==================== CLASSE BOT ====================
class SimpleDedupBot:
    def __init__(self):
        self.photo_ids = defaultdict(set)
        self.video_ids = defaultdict(set)
        self.document_ids = defaultdict(set)
        self.audio_ids = defaultdict(set)
        self.sticker_ids = defaultdict(set)
        self.animation_ids = defaultdict(set)
        self.chat_languages = defaultdict(lambda: 'pt')
        self.stats = defaultdict(lambda: {'photos': 0, 'videos': 0, 'documents': 0, 'duplicates': 0})
    
    def get_text(self, chat_id, key, **kwargs):
        lang = self.chat_languages[chat_id]
        text = TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, '')
        return text.format(**kwargs) if kwargs else text
    
    def is_duplicate(self, chat_id, file_unique_id, media_type):
        storage = {
            'photo': self.photo_ids,
            'video': self.video_ids,
            'document': self.document_ids,
            'audio': self.audio_ids,
            'sticker': self.sticker_ids,
            'animation': self.animation_ids
        }.get(media_type)
        
        if not storage:
            return False
        
        return file_unique_id in storage[chat_id]
    
    def add_media(self, chat_id, file_unique_id, media_type):
        storage = {
            'photo': self.photo_ids,
            'video': self.video_ids,
            'document': self.document_ids,
            'audio': self.audio_ids,
            'sticker': self.sticker_ids,
            'animation': self.animation_ids
        }.get(media_type)
        
        if storage:
            storage[chat_id].add(file_unique_id)
            
            if media_type == 'photo':
                self.stats[chat_id]['photos'] += 1
            elif media_type == 'video':
                self.stats[chat_id]['videos'] += 1
            elif media_type == 'document':
                self.stats[chat_id]['documents'] += 1

bot_instance = SimpleDedupBot()

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
    
    await query.edit_message_text(
        bot_instance.get_text(chat_id, 'lang_changed')
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if update.effective_chat.type == 'private':
        await update.message.reply_text(
            bot_instance.get_text(chat_id, 'group_only')
        )
        return
    
    stats = bot_instance.stats[chat_id]
    total = stats['photos'] + stats['videos'] + stats['documents']
    
    await update.message.reply_text(
        bot_instance.get_text(
            chat_id,
            'stats',
            photos=stats['photos'],
            videos=stats['videos'],
            documents=stats['documents'],
            duplicates=stats['duplicates'],
            total=total
        ),
        parse_mode='Markdown'
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if update.effective_chat.type == 'private':
        await update.message.reply_text(
            bot_instance.get_text(chat_id, 'group_only')
        )
        return
    
    bot_instance.photo_ids[chat_id].clear()
    bot_instance.video_ids[chat_id].clear()
    bot_instance.document_ids[chat_id].clear()
    bot_instance.audio_ids[chat_id].clear()
    bot_instance.sticker_ids[chat_id].clear()
    bot_instance.animation_ids[chat_id].clear()
    bot_instance.stats[chat_id] = {'photos': 0, 'videos': 0, 'documents': 0, 'duplicates': 0}
    
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'cleared')
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
    
    media_info = None
    
    if message.photo:
        photo = message.photo[-1]
        media_info = ('photo', photo.file_unique_id)
    elif message.video:
        media_info = ('video', message.video.file_unique_id)
    elif message.animation:
        media_info = ('animation', message.animation.file_unique_id)
    elif message.document:
        media_info = ('document', message.document.file_unique_id)
    elif message.audio:
        media_info = ('audio', message.audio.file_unique_id)
    elif message.sticker:
        media_info = ('sticker', message.sticker.file_unique_id)
    
    if not media_info:
        return
    
    media_type, file_unique_id = media_info
    
    if bot_instance.is_duplicate(chat_id, file_unique_id, media_type):
        try:
            await message.delete()
            bot_instance.stats[chat_id]['duplicates'] += 1
            logger.info(f"Duplicata removida no chat {chat_id}: {media_type}")
        except Exception as e:
            logger.error(f"Erro ao deletar: {e}")
            if "not enough rights" in str(e).lower():
                await message.reply_text(
                    bot_instance.get_text(chat_id, 'need_admin')
                )
    else:
        bot_instance.add_media(chat_id, file_unique_id, media_type)
        logger.info(f"Nova mídia salva no chat {chat_id}: {media_type}")

# ==================== SERVIDOR WEB ====================
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Duplicate Cleaner Bot - Online</title>
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
            .info { font-size: 1.1em; opacity: 0.9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Duplicate Cleaner Bot</h1>
            <div class="status">✅ Online e Funcionando!</div>
            <div class="info">
                Bot Telegram para remoção de duplicatas<br>
                Adicione-me ao seu grupo!
                https://t.me/duplicatacleanerbot
            </div>
        </div>
    </body>
    </html>
    '''

@web_app.route('/health')
def health():
    return {"status": "ok", "bot": "running"}

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
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(lang_callback, pattern='^lang_'))
    
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.ANIMATION | 
        filters.Document.ALL | filters.AUDIO | filters.Sticker.ALL,
        handle_media
    ))
    
    logger.info("✅ Bot iniciado com sucesso!")
    logger.info("🎯 Aguardando mensagens...")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
