"""
Bot Telegram - Remoção de Duplicatas Inteligente
Verifica histórico REAL do grupo ao invés de salvar em memória!
Se você apagou, pode enviar de novo sem problemas.
"""

import os
import threading
import logging
from typing import Dict, Set, Optional
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

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== TRADUÇÕES ====================
TRANSLATIONS = {
    'pt': {
        'welcome': '👋 Olá! Eu sou o *Duplicate Cleaner Bot Inteligente*\n\nAdicione-me a um grupo como ADMINISTRADOR e eu vou:\n✅ Detectar duplicatas verificando o histórico real\n✅ Permitir reenvio de mídias que você apagou\n✅ Remover apenas duplicatas que existem no grupo\n\n🔹 Comandos:\n/start - Iniciar\n/lang - Mudar idioma\n/stats - Ver estatísticas\n/config - Configurações\n/help - Ajuda\n\n⚠️ *Importante:* Preciso ser ADMIN com permissão de:\n• Ler mensagens\n• Deletar mensagens',
        'lang_select': '🌐 Selecione seu idioma:',
        'lang_changed': '✅ Idioma alterado!',
        'duplicate_found': '🔴 Duplicata encontrada no histórico e removida!\n📍 Mensagem original em: {date}',
        'new_media': '✅ Mídia única salva no grupo',
        'stats': '📊 *Estatísticas deste chat*\n\n🗑 Duplicatas removidas: {duplicates}\n⏱ Verificações realizadas: {checks}\n🕐 Última verificação: {last_check}\n\n💡 *Como funciona:*\nVerifico as últimas {scan_limit} mensagens do histórico real do grupo.',
        'config': '⚙️ *Configurações*\n\n📊 Verificar últimas: {scan_limit} mensagens\n⏱ Tempo máximo: {max_days} dias\n\n💡 Use /config_limit <número> para alterar\nExemplo: /config_limit 500',
        'config_updated': '✅ Configuração atualizada!\nAgora verifico as últimas {scan_limit} mensagens.',
        'help': '❓ *Como funciona*\n\n*Método Inteligente:*\nQuando alguém envia uma mídia:\n1️⃣ Busco no histórico real do grupo\n2️⃣ Procuro pela mesma mídia (file_unique_id)\n3️⃣ Se encontrar = DUPLICATA → Deleto\n4️⃣ Se não encontrar = NOVA → Deixo no grupo\n\n*Vantagens:*\n✅ Se você apagou, pode enviar de novo\n✅ Verifica apenas o que está no grupo\n✅ Não salva nada em memória/banco\n✅ Funciona com histórico real\n\n*Detecta:*\n• Fotos • Vídeos • GIFs\n• Documentos • Áudios • Stickers\n\n*Configurável:*\nUse /config_limit <número> para definir quantas mensagens verificar.\nPadrão: 1000 mensagens ou 30 dias',
        'error': '❌ Erro ao processar',
        'need_admin': '⚠️ Preciso ser administrador com permissão de LER e DELETAR mensagens!\n\n📋 Configure:\n1. Grupo → Configurações\n2. Administradores → Adicione o bot\n3. Marque: ✅ Deletar mensagens ✅ Ler histórico',
        'group_only': 'ℹ️ Este comando funciona apenas em grupos',
        'checking': '🔍 Verificando histórico...',
        'no_permission': '⚠️ Não tenho permissão para ler o histórico!\nPromova-me para administrador.',
    },
    'en': {
        'welcome': '👋 Hello! I am *Smart Duplicate Cleaner Bot*\n\nAdd me to a group as ADMIN and I will:\n✅ Detect duplicates by checking real history\n✅ Allow resending media you deleted\n✅ Remove only duplicates that exist in group\n\n🔹 Commands:\n/start - Start\n/lang - Change language\n/stats - View statistics\n/config - Settings\n/help - Help\n\n⚠️ *Important:* I need ADMIN with:\n• Read messages\n• Delete messages',
        'lang_select': '🌐 Select your language:',
        'lang_changed': '✅ Language changed!',
        'duplicate_found': '🔴 Duplicate found in history and removed!\n📍 Original message at: {date}',
        'new_media': '✅ Unique media saved in group',
        'stats': '📊 *Chat Statistics*\n\n🗑 Duplicates removed: {duplicates}\n⏱ Checks performed: {checks}\n🕐 Last check: {last_check}\n\n💡 *How it works:*\nI check the last {scan_limit} messages from real group history.',
        'config': '⚙️ *Settings*\n\n📊 Check last: {scan_limit} messages\n⏱ Max time: {max_days} days\n\n💡 Use /config_limit <number> to change\nExample: /config_limit 500',
        'config_updated': '✅ Settings updated!\nNow checking last {scan_limit} messages.',
        'help': '❓ *How it works*\n\n*Smart Method:*\nWhen someone sends media:\n1️⃣ Search in real group history\n2️⃣ Look for same media (file_unique_id)\n3️⃣ If found = DUPLICATE → Delete\n4️⃣ If not found = NEW → Keep in group\n\n*Advantages:*\n✅ If you deleted, can send again\n✅ Checks only what is in group\n✅ Saves nothing in memory/database\n✅ Works with real history\n\n*Detects:*\n• Photos • Videos • GIFs\n• Documents • Audios • Stickers\n\n*Configurable:*\nUse /config_limit <number> to define messages to check.\nDefault: 1000 messages or 30 days',
        'error': '❌ Processing error',
        'need_admin': '⚠️ I need admin permissions to READ and DELETE messages!\n\n📋 Setup:\n1. Group → Settings\n2. Administrators → Add bot\n3. Check: ✅ Delete messages ✅ Read history',
        'group_only': 'ℹ️ This command only works in groups',
        'checking': '🔍 Checking history...',
        'no_permission': '⚠️ I dont have permission to read history!\nPromote me to administrator.',
    },
    'es': {
        'welcome': '👋 ¡Hola! Soy *Duplicate Cleaner Bot Inteligente*\n\nAgrégame a un grupo como ADMIN y:\n✅ Detectaré duplicados verificando el historial real\n✅ Permitiré reenviar medios que eliminaste\n✅ Eliminaré solo duplicados que existen en el grupo\n\n🔹 Comandos:\n/start - Iniciar\n/lang - Cambiar idioma\n/stats - Ver estadísticas\n/config - Configuración\n/help - Ayuda\n\n⚠️ *Importante:* Necesito ser ADMIN con:\n• Leer mensajes\n• Eliminar mensajes',
        'lang_select': '🌐 Selecciona tu idioma:',
        'lang_changed': '✅ ¡Idioma cambiado!',
        'duplicate_found': '🔴 ¡Duplicado encontrado en el historial y eliminado!\n📍 Mensaje original en: {date}',
        'new_media': '✅ Medio único guardado en grupo',
        'stats': '📊 *Estadísticas del chat*\n\n🗑 Duplicados eliminados: {duplicates}\n⏱ Verificaciones realizadas: {checks}\n🕐 Última verificación: {last_check}\n\n💡 *Cómo funciona:*\nVerifico los últimos {scan_limit} mensajes del historial real del grupo.',
        'config': '⚙️ *Configuración*\n\n📊 Verificar últimos: {scan_limit} mensajes\n⏱ Tiempo máximo: {max_days} días\n\n💡 Usa /config_limit <número> para cambiar\nEjemplo: /config_limit 500',
        'config_updated': '✅ ¡Configuración actualizada!\nAhora verifico los últimos {scan_limit} mensajes.',
        'help': '❓ *Cómo funciona*\n\n*Método Inteligente:*\nCuando alguien envía un medio:\n1️⃣ Busco en el historial real del grupo\n2️⃣ Busco el mismo medio (file_unique_id)\n3️⃣ Si encuentro = DUPLICADO → Elimino\n4️⃣ Si no encuentro = NUEVO → Lo dejo\n\n*Ventajas:*\n✅ Si eliminaste, puedes enviar de nuevo\n✅ Verifica solo lo que está en el grupo\n✅ No guarda nada en memoria/base de datos\n✅ Funciona con historial real\n\n*Detecta:*\n• Fotos • Videos • GIFs\n• Documentos • Audios • Stickers\n\n*Configurable:*\nUsa /config_limit <número> para definir mensajes a verificar.\nPredeterminado: 1000 mensajes o 30 días',
        'error': '❌ Error al procesar',
        'need_admin': '⚠️ ¡Necesito permisos de administrador para LEER y ELIMINAR mensajes!\n\n📋 Configurar:\n1. Grupo → Configuración\n2. Administradores → Agregar bot\n3. Marcar: ✅ Eliminar mensajes ✅ Leer historial',
        'group_only': 'ℹ️ Este comando solo funciona en grupos',
        'checking': '🔍 Verificando historial...',
        'no_permission': '⚠️ ¡No tengo permiso para leer el historial!\nPromuéveme a administrador.',
    }
}

# ==================== CLASSE BOT ====================
class SmartDedupBot:
    def __init__(self):
        # Configurações por chat
        self.chat_config = defaultdict(lambda: {
            'scan_limit': 1000,  # Quantas mensagens verificar
            'max_days': 30,      # Máximo de dias no passado
        })
        
        # Estatísticas por chat
        self.stats = defaultdict(lambda: {
            'duplicates': 0,
            'checks': 0,
            'last_check': None
        })
        
        # Idioma por chat
        self.chat_languages = defaultdict(lambda: 'pt')
    
    def get_text(self, chat_id, key, **kwargs):
        lang = self.chat_languages[chat_id]
        text = TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, '')
        return text.format(**kwargs) if kwargs else text
    
    async def search_in_history(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, file_unique_id: str, current_message_id: int):
        """
        Busca no histórico REAL do grupo pela mídia
        Retorna: (is_duplicate, original_message_date)
        """
        config = self.chat_config[chat_id]
        scan_limit = config['scan_limit']
        max_days = config['max_days']
        
        try:
            # Atualiza estatísticas
            self.stats[chat_id]['checks'] += 1
            self.stats[chat_id]['last_check'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            
            # Busca nas mensagens do histórico
            messages_checked = 0
            oldest_date = datetime.now() - timedelta(days=max_days)
            
            # Itera pelas mensagens do histórico (do mais recente para o mais antigo)
            async for message in context.bot.get_chat_history(chat_id, limit=scan_limit):
                # Não verifica a própria mensagem atual
                if message.message_id == current_message_id:
                    continue
                
                # Para se ultrapassar limite de tempo
                if message.date < oldest_date:
                    break
                
                messages_checked += 1
                
                # Verifica cada tipo de mídia
                media_id = None
                if message.photo:
                    media_id = message.photo[-1].file_unique_id
                elif message.video:
                    media_id = message.video.file_unique_id
                elif message.animation:
                    media_id = message.animation.file_unique_id
                elif message.document:
                    media_id = message.document.file_unique_id
                elif message.audio:
                    media_id = message.audio.file_unique_id
                elif message.sticker:
                    media_id = message.sticker.file_unique_id
                
                # Se encontrou a mesma mídia = DUPLICATA!
                if media_id and media_id == file_unique_id:
                    logger.info(f"Duplicata encontrada! Original em {message.date}")
                    return True, message.date
            
            logger.info(f"Nenhuma duplicata encontrada após verificar {messages_checked} mensagens")
            return False, None
            
        except Exception as e:
            logger.error(f"Erro ao buscar histórico: {e}")
            return False, None

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
    config = bot_instance.chat_config[chat_id]
    
    last_check = stats['last_check'] if stats['last_check'] else 'Nunca'
    
    await update.message.reply_text(
        bot_instance.get_text(
            chat_id,
            'stats',
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
        await update.message.reply_text(
            bot_instance.get_text(chat_id, 'group_only')
        )
        return
    
    config = bot_instance.chat_config[chat_id]
    
    await update.message.reply_text(
        bot_instance.get_text(
            chat_id,
            'config',
            scan_limit=config['scan_limit'],
            max_days=config['max_days']
        ),
        parse_mode='Markdown'
    )

async def config_limit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if update.effective_chat.type == 'private':
        await update.message.reply_text(
            bot_instance.get_text(chat_id, 'group_only')
        )
        return
    
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "❌ Use: /config_limit <número>\nExemplo: /config_limit 500"
        )
        return
    
    new_limit = int(context.args[0])
    
    if new_limit < 10 or new_limit > 5000:
        await update.message.reply_text(
            "⚠️ O limite deve estar entre 10 e 5000 mensagens"
        )
        return
    
    bot_instance.chat_config[chat_id]['scan_limit'] = new_limit
    
    await update.message.reply_text(
        bot_instance.get_text(
            chat_id,
            'config_updated',
            scan_limit=new_limit
        )
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
    
    # Extrai informações da mídia
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
    
    try:
        # Busca no histórico do grupo
        is_duplicate, original_date = await bot_instance.search_in_history(
            context,
            chat_id,
            file_unique_id,
            message.message_id
        )
        
        if is_duplicate:
            # DUPLICATA! Deleta a mensagem
            await message.delete()
            bot_instance.stats[chat_id]['duplicates'] += 1
            
            date_str = original_date.strftime('%d/%m/%Y %H:%M') if original_date else 'desconhecida'
            logger.info(f"Duplicata removida no chat {chat_id}. Original: {date_str}")
        else:
            # Mídia única - não faz nada, deixa no grupo
            logger.info(f"Nova mídia no chat {chat_id}: {media_type}")
            
    except Exception as e:
        logger.error(f"Erro ao processar mídia: {e}")
        if "not enough rights" in str(e).lower() or "permission" in str(e).lower():
            await message.reply_text(
                bot_instance.get_text(chat_id, 'need_admin')
            )

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
            .feature { margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 Duplicate Cleaner Bot</h1>
            <div class="status">✅ Online e Funcionando!</div>
            <div class="info">
                <div class="feature">🔍 Verifica histórico real do grupo</div>
                <div class="feature">♻️ Permite reenvio após deletar</div>
                <div class="feature">🎯 Remove apenas duplicatas existentes</div>
                <a href="https://t.me/duplicatacleanerbot">https://t.me/duplicatacleanerbot</a>
            </div>
        </div>
    </body>
    </html>
    '''

@web_app.route('/health')
def health():
    return {"status": "ok", "bot": "running", "mode": "smart_history_check"}

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

    
