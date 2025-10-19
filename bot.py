"""
Bot Telegram SIMPLIFICADO - Remoção de Duplicatas
Não precisa baixar nada! Usa apenas o file_unique_id do Telegram
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
        'welcome': '👋 Olá! Eu sou o *DedupBot*\n\n'
                   'Adicione-me a um grupo e eu vou detectar e remover fotos/vídeos duplicados automaticamente!\n\n'
                   '🔹 Comandos:\n'
                   '/start - Iniciar\n'
                   '/lang - Mudar idioma\n'
                   '/stats - Ver estatísticas\n'
                   '/clear - Limpar histórico\n'
                   '/help - Ajuda',
        'lang_select': '🌐 Selecione seu idioma:',
        'lang_changed': '✅ Idioma alterado!',
        'duplicate_found': '🔴 Duplicata detectada e removida!',
        'new_media': '✅ Mídia única salva',
        'stats': '📊 *Estatísticas deste chat*\n\n'
                 '🖼 Fotos únicas: {photos}\n'
                 '🎥 Vídeos únicos: {videos}\n'
                 '📄 Documentos únicos: {documents}\n'
                 '🗑 Duplicatas removidas: {duplicates}\n'
                 '💾 Total: {total}',
        'cleared': '🗑 Histórico limpo!',
        'help': '❓ *Como funciona*\n\n'
                'Adicione o bot a um grupo e dê permissões de administrador.\n\n'
                'O bot detecta duplicatas usando o ID único do Telegram (file_unique_id).\n'
                'Não precisa baixar nada! É instantâneo e funciona com arquivos de qualquer tamanho.\n\n'
                '*Detecta:*\n'
                '• Fotos duplicadas\n'
                '• Vídeos duplicados\n'
                '• GIFs duplicados\n'
                '• Documentos duplicados\n'
                '• Áudios duplicados\n'
                '• Stickers duplicados\n\n'
                'Funciona mesmo com encaminhamentos!',
        'error': '❌ Erro ao processar',
        'need_admin': '⚠️ Preciso ser administrador para deletar mensagens!',
        'group_only': 'ℹ️ Este comando funciona apenas em grupos',
    },
    'en': {
        'welcome': '👋 Hello! I am *DedupBot*\n\n'
                   'Add me to a group and I will detect and remove duplicate photos/videos automatically!\n\n'
                   '🔹 Commands:\n'
                   '/start - Start\n'
                   '/lang - Change language\n'
                   '/stats - View statistics\n'
                   '/clear - Clear history\n'
                   '/help - Help',
        'lang_select': '🌐 Select your language:',
        'lang_changed': '✅ Language changed!',
        'duplicate_found': '🔴 Duplicate detected and removed!',
        'new_media': '✅ Unique media saved',
        'stats': '📊 *Chat Statistics*\n\n'
                 '🖼 Unique photos: {photos}\n'
                 '🎥 Unique videos: {videos}\n'
                 '📄 Unique documents: {documents}\n'
                 '🗑 Duplicates removed: {duplicates}\n'
                 '💾 Total: {total}',
        'cleared': '🗑 History cleared!',
        'help': '❓ *How it works*\n\n'
                'Add the bot to a group and give admin permissions.\n\n'
                'Bot detects duplicates using Telegram\'s unique ID (file_unique_id).\n'
                'No downloads needed! Instant and works with any file size.\n\n'
                '*Detects:*\n'
                '• Duplicate photos\n'
                '• Duplicate videos\n'
                '• Duplicate GIFs\n'
                '• Duplicate documents\n'
                '• Duplicate audios\n'
                '• Duplicate stickers\n\n'
                'Works even with forwards!',
        'error': '❌ Processing error',
        'need_admin': '⚠️ I need admin permissions to delete messages!',
        'group_only': 'ℹ️ This command only works in groups',
    },
    'es': {
        'welcome': '👋 ¡Hola! Soy *DedupBot*\n\n'
                   '¡Agrégame a un grupo y detectaré y eliminaré fotos/videos duplicados automáticamente!\n\n'
                   '🔹 Comandos:\n'
                   '/start - Iniciar\n'
                   '/lang - Cambiar idioma\n'
                   '/stats - Ver estadísticas\n'
                   '/clear - Limpiar historial\n'
                   '/help - Ayuda',
        'lang_select': '🌐 Selecciona tu idioma:',
        'lang_changed': '✅ ¡Idioma cambiado!',
        'duplicate_found': '🔴 ¡Duplicado detectado y eliminado!',
        'new_media': '✅ Medio único guardado',
        'stats': '📊 *Estadísticas del chat*\n\n'
                 '🖼 Fotos únicas: {photos}\n'
                 '🎥 Videos únicos: {videos}\n'
                 '📄 Documentos únicos: {documents}\n'
                 '🗑 Duplicados eliminados: {duplicates}\n'
                 '💾 Total: {total}',
        'cleared': '🗑 ¡Historial limpiado!',
        'help': '❓ *Cómo funciona*\n\n'
                'Agrega el bot a un grupo y dale permisos de administrador.\n\n'
                'El bot detecta duplicados usando el ID único de Telegram (file_unique_id).\n'
                '¡No necesita descargas! Instantáneo y funciona con cualquier tamaño.\n\n'
                '*Detecta:*\n'
                '• Fotos duplicadas\n'
                '• Videos duplicados\n'
                '• GIFs duplicados\n'
                '• Documentos duplicados\n'
                '• Audios duplicados\n'
                '• Stickers duplicados\n\n'
                '¡Funciona incluso con reenvíos!',
        'error': '❌ Error al procesar',
        'need_admin': '⚠️ ¡Necesito permisos de administrador para eliminar mensajes!',
        'group_only': 'ℹ️ Este comando solo funciona en grupos',
    },
    'fr': {
        'welcome': '👋 Bonjour! Je suis *DedupBot*\n\n'
                   'Ajoutez-moi à un groupe et je détecterai et supprimerai automatiquement les photos/vidéos en double!\n\n'
                   '🔹 Commandes:\n'
                   '/start - Démarrer\n'
                   '/lang - Changer de langue\n'
                   '/stats - Voir les statistiques\n'
                   '/clear - Effacer l\'historique\n'
                   '/help - Aide',
        'lang_select': '🌐 Sélectionnez votre langue:',
        'lang_changed': '✅ Langue changée!',
        'duplicate_found': '🔴 Doublon détecté et supprimé!',
        'new_media': '✅ Média unique enregistré',
        'stats': '📊 *Statistiques du chat*\n\n'
                 '🖼 Photos uniques: {photos}\n'
                 '🎥 Vidéos uniques: {videos}\n'
                 '📄 Documents uniques: {documents}\n'
                 '🗑 Doublons supprimés: {duplicates}\n'
                 '💾 Total: {total}',
        'cleared': '🗑 Historique effacé!',
        'help': '❓ *Comment ça marche*\n\n'
                'Ajoutez le bot à un groupe et donnez les permissions admin.\n\n'
                'Le bot détecte les doublons en utilisant l\'ID unique de Telegram (file_unique_id).\n'
                'Pas de téléchargements! Instantané et fonctionne avec toutes les tailles.\n\n'
                '*Détecte:*\n'
                '• Photos en double\n'
                '• Vidéos en double\n'
                '• GIFs en double\n'
                '• Documents en double\n'
                '• Audios en double\n'
                '• Stickers en double\n\n'
                'Fonctionne même avec les transferts!',
        'error': '❌ Erreur de traitement',
        'need_admin': '⚠️ J\'ai besoin des permissions admin pour supprimer les messages!',
        'group_only': 'ℹ️ Cette commande ne fonctionne que dans les groupes',
    },
    'de': {
        'welcome': '👋 Hallo! Ich bin *DedupBot*\n\n'
                   'Füge mich zu einer Gruppe hinzu und ich erkenne und entferne automatisch doppelte Fotos/Videos!\n\n'
                   '🔹 Befehle:\n'
                   '/start - Starten\n'
                   '/lang - Sprache ändern\n'
                   '/stats - Statistiken anzeigen\n'
                   '/clear - Verlauf löschen\n'
                   '/help - Hilfe',
        'lang_select': '🌐 Wählen Sie Ihre Sprache:',
        'lang_changed': '✅ Sprache geändert!',
        'duplicate_found': '🔴 Duplikat erkannt und entfernt!',
        'new_media': '✅ Eindeutiges Medium gespeichert',
        'stats': '📊 *Chat-Statistiken*\n\n'
                 '🖼 Eindeutige Fotos: {photos}\n'
                 '🎥 Eindeutige Videos: {videos}\n'
                 '📄 Eindeutige Dokumente: {documents}\n'
                 '🗑 Entfernte Duplikate: {duplicates}\n'
                 '💾 Gesamt: {total}',
        'cleared': '🗑 Verlauf gelöscht!',
        'help': '❓ *Wie es funktioniert*\n\n'
                'Füge den Bot zu einer Gruppe hinzu und gib Admin-Berechtigungen.\n\n'
                'Bot erkennt Duplikate mit Telegrams eindeutiger ID (file_unique_id).\n'
                'Keine Downloads! Sofort und funktioniert mit jeder Dateigröße.\n\n'
                '*Erkennt:*\n'
                '• Doppelte Fotos\n'
                '• Doppelte Videos\n'
                '• Doppelte GIFs\n'
                '• Doppelte Dokumente\n'
                '• Doppelte Audios\n'
                '• Doppelte Sticker\n\n'
                'Funktioniert auch mit Weiterleitungen!',
        'error': '❌ Verarbeitungsfehler',
        'need_admin': '⚠️ Ich brauche Admin-Rechte zum Löschen von Nachrichten!',
        'group_only': 'ℹ️ Dieser Befehl funktioniert nur in Gruppen',
    },
    'it': {
        'welcome': '👋 Ciao! Sono *DedupBot*\n\n'
                   'Aggiungimi a un gruppo e rileverò e rimuoverò automaticamente foto/video duplicati!\n\n'
                   '🔹 Comandi:\n'
                   '/start - Avvia\n'
                   '/lang - Cambia lingua\n'
                   '/stats - Visualizza statistiche\n'
                   '/clear - Cancella cronologia\n'
                   '/help - Aiuto',
        'lang_select': '🌐 Seleziona la tua lingua:',
        'lang_changed': '✅ Lingua cambiata!',
        'duplicate_found': '🔴 Duplicato rilevato e rimosso!',
        'new_media': '✅ Media unico salvato',
        'stats': '📊 *Statistiche chat*\n\n'
                 '🖼 Foto uniche: {photos}\n'
                 '🎥 Video unici: {videos}\n'
                 '📄 Documenti unici: {documents}\n'
                 '🗑 Duplicati rimossi: {duplicates}\n'
                 '💾 Totale: {total}',
        'cleared': '🗑 Cronologia cancellata!',
        'help': '❓ *Come funziona*\n\n'
                'Aggiungi il bot a un gruppo e dai i permessi di amministratore.\n\n'
                'Il bot rileva i duplicati usando l\'ID unico di Telegram (file_unique_id).\n'
                'Nessun download necessario! Istantaneo e funziona con qualsiasi dimensione.\n\n'
                '*Rileva:*\n'
                '• Foto duplicate\n'
                '• Video duplicati\n'
                '• GIF duplicate\n'
                '• Documenti duplicati\n'
                '• Audio duplicati\n'
                '• Sticker duplicati\n\n'
                'Funziona anche con gli inoltri!',
        'error': '❌ Errore di elaborazione',
        'need_admin': '⚠️ Ho bisogno dei permessi di amministratore per eliminare i messaggi!',
        'group_only': 'ℹ️ Questo comando funziona solo nei gruppi',
    }
}

# ==================== CLASSE PRINCIPAL ====================
class SimpleDedupBot:
    def __init__(self):
        # Armazena apenas file_unique_id por chat
        self.photo_ids: Dict[int, Set[str]] = defaultdict(set)
        self.video_ids: Dict[int, Set[str]] = defaultdict(set)
        self.document_ids: Dict[int, Set[str]] = defaultdict(set)
        self.audio_ids: Dict[int, Set[str]] = defaultdict(set)
        self.sticker_ids: Dict[int, Set[str]] = defaultdict(set)
        self.animation_ids: Dict[int, Set[str]] = defaultdict(set)
        
        # Idioma por chat
        self.chat_languages: Dict[int, str] = defaultdict(lambda: 'pt')
        
        # Estatísticas por chat
        self.stats: Dict[int, Dict] = defaultdict(lambda: {
            'photos': 0,
            'videos': 0,
            'documents': 0,
            'duplicates': 0
        })
    
    def get_text(self, chat_id: int, key: str, **kwargs) -> str:
        """Retorna texto traduzido"""
        lang = self.chat_languages[chat_id]
        text = TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, '')
        return text.format(**kwargs) if kwargs else text
    
    def is_duplicate(self, chat_id: int, file_unique_id: str, media_type: str) -> bool:
        """Verifica se é duplicata usando file_unique_id do Telegram"""
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
    
    def add_media(self, chat_id: int, file_unique_id: str, media_type: str):
        """Adiciona mídia ao registro"""
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
            
            # Atualiza estatísticas
            if media_type == 'photo':
                self.stats[chat_id]['photos'] += 1
            elif media_type == 'video':
                self.stats[chat_id]['videos'] += 1
            elif media_type == 'document':
                self.stats[chat_id]['documents'] += 1

# Instância global
bot_instance = SimpleDedupBot()

# ==================== HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'welcome'),
        parse_mode='Markdown'
    )

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /lang"""
    keyboard = [
        [
            InlineKeyboardButton("🇧🇷 PT", callback_data='lang_pt'),
            InlineKeyboardButton("🇺🇸 EN", callback_data='lang_en'),
            InlineKeyboardButton("🇪🇸 ES", callback_data='lang_es'),
        ],
        [
            InlineKeyboardButton("🇫🇷 FR", callback_data='lang_fr'),
            InlineKeyboardButton("🇩🇪 DE", callback_data='lang_de'),
            InlineKeyboardButton("🇮🇹 IT", callback_data='lang_it'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        bot_instance.get_text(update.effective_chat.id, 'lang_select'),
        reply_markup=reply_markup
    )

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para mudança de idioma"""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    lang = query.data.split('_')[1]
    bot_instance.chat_languages[chat_id] = lang
    
    await query.edit_message_text(
        bot_instance.get_text(chat_id, 'lang_changed')
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats"""
    chat_id = update.effective_chat.id
    
    # Só funciona em grupos
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
    """Comando /clear"""
    chat_id = update.effective_chat.id
    
    # Só funciona em grupos
    if update.effective_chat.type == 'private':
        await update.message.reply_text(
            bot_instance.get_text(chat_id, 'group_only')
        )
        return
    
    # Limpa tudo deste chat
    bot_instance.photo_ids[chat_id].clear()
    bot_instance.video_ids[chat_id].clear()
    bot_instance.document_ids[chat_id].clear()
    bot_instance.audio_ids[chat_id].clear()
    bot_instance.sticker_ids[chat_id].clear()
    bot_instance.animation_ids[chat_id].clear()
    bot_instance.stats[chat_id] = {
        'photos': 0,
        'videos': 0,
        'documents': 0,
        'duplicates': 0
    }
    
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'cleared')
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'help'),
        parse_mode='Markdown'
    )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler universal para todas as mídias"""
    chat_id = update.effective_chat.id
    message = update.message
    
    # Detecta tipo de mídia e pega file_unique_id
    media_info = None
    
    if message.photo:
        # Pega a maior resolução
        photo = message.photo[-1]
        media_info = ('photo', photo.file_unique_id)
    
    elif message.video:
        media_info = ('video', message.video.file_unique_id)
    
    elif message.animation:  # GIF
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
    
    # Verifica se é duplicata
    if bot_instance.is_duplicate(chat_id, file_unique_id, media_type):
        try:
            # Deleta mensagem duplicada
            await message.delete()
            bot_instance.stats[chat_id]['duplicates'] += 1
            
            logger.info(f"Duplicata removida no chat {chat_id}: {media_type}")
        except Exception as e:
            logger.error(f"Erro ao deletar: {e}")
            # Avisa se não tem permissão
            if "not enough rights" in str(e).lower():
                await message.reply_text(
                    bot_instance.get_text(chat_id, 'need_admin')
                )
    else:
        # Nova mídia - adiciona ao registro
        bot_instance.add_media(chat_id, file_unique_id, media_type)
        logger.info(f"Nova mídia salva no chat {chat_id}: {media_type}")

# ==================== SERVIDOR WEB (para Render) ====================
from flask import Flask
import threading

# Cria servidor Flask simples
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DedupBot - Online</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                             '/lang - Mudar idioma\n'
                   '/stats - Ver estatísticas\n'
                   '/clear - Limpar histórico\n'
                   '/help - Ajuda',
        'lang_select': '🌐 Selecione seu idioma:',
        'lang_changed': '✅ Idioma alterado!',
        'duplicate_found': '🔴 Duplicata detectada e removida!',
        'new_media': '✅ Mídia única salva',
        'stats': '📊 *Estatísticas deste chat*\n\n'
                 '🖼 Fotos únicas: {photos}\n'
                 '🎥 Vídeos únicos: {videos}\n'
                 '📄 Documentos únicos: {documents}\n'
                 '🗑 Duplicatas removidas: {duplicates}\n'
                 '💾 Total: {total}',
        'cleared': '🗑 Histórico limpo!',
        'help': '❓ *Como funciona*\n\n'
                'Adicione o bot a um grupo e dê permissões de administrador.\n\n'
                'O bot detecta duplicatas usando o ID único do Telegram (file_unique_id).\n'
                'Não precisa baixar nada! É instantâneo e funciona com arquivos de qualquer tamanho.\n\n'
                '*Detecta:*\n'
                '• Fotos duplicadas\n'
                '• Vídeos duplicados\n'
                '• GIFs duplicados\n'
                '• Documentos duplicados\n'
                '• Áudios duplicados\n'
                '• Stickers duplicados\n\n'
                'Funciona mesmo com encaminhamentos!',
        'error': '❌ Erro ao processar',
        'need_admin': '⚠️ Preciso ser administrador para deletar mensagens!',
        'group_only': 'ℹ️ Este comando funciona apenas em grupos',
    },
    'en': {
        'welcome': '👋 Hello! I am *Duplicate Cleaner Bot*\n\n'
                   'Add me to a group and I will detect and remove duplicate photos/videos automatically!\n\n'
                   '🔹 Commands:\n'
                   '/start - Start\n'
                   '/lang - Change language\n'
                   '/stats - View statistics\n'
                   '/clear - Clear history\n'
                   '/help - Help',
        'lang_select': '🌐 Select your language:',
        'lang_changed': '✅ Language changed!',
        'duplicate_found': '🔴 Duplicate detected and removed!',
        'new_media': '✅ Unique media saved',
        'stats': '📊 *Chat Statistics*\n\n'
                 '🖼 Unique photos: {photos}\n'
                 '🎥 Unique videos: {videos}\n'
                 '📄 Unique documents: {documents}\n'
                 '🗑 Duplicates removed: {duplicates}\n'
                 '💾 Total: {total}',
        'cleared': '🗑 History cleared!',
        'help': '❓ *How it works*\n\n'
                'Add the bot to a group and give admin permissions.\n\n'
                'Bot detects duplicates using Telegram\'s unique ID (file_unique_id).\n'
                'No downloads needed! Instant and works with any file size.\n\n'
                '*Detects:*\n'
                '• Duplicate photos\n'
                '• Duplicate videos\n'
                '• Duplicate GIFs\n'
                '• Duplicate documents\n'
                '• Duplicate audios\n'
                '• Duplicate stickers\n\n'
                'Works even with forwards!',
        'error': '❌ Processing error',
        'need_admin': '⚠️ I need admin permissions to delete messages!',
        'group_only': 'ℹ️ This command only works in groups',
    },
    'es': {
        'welcome': '👋 ¡Hola! Soy *Duplicate Cleaner Bot*\n\n'
                   '¡Agrégame a un grupo y detectaré y eliminaré fotos/videos duplicados automáticamente!\n\n'
                   '🔹 Comandos:\n'
                   '/start - Iniciar\n'
                   '/lang - Cambiar idioma\n'
                   '/stats - Ver estadísticas\n'
                   '/clear - Limpiar historial\n'
                   '/help - Ayuda',
        'lang_select': '🌐 Selecciona tu idioma:',
        'lang_changed': '✅ ¡Idioma cambiado!',
        'duplicate_found': '🔴 ¡Duplicado detectado y eliminado!',
        'new_media': '✅ Medio único guardado',
        'stats': '📊 *Estadísticas del chat*\n\n'
                 '🖼 Fotos únicas: {photos}\n'
                 '🎥 Videos únicos: {videos}\n'
                 '📄 Documentos únicos: {documents}\n'
                 '🗑 Duplicados eliminados: {duplicates}\n'
                 '💾 Total: {total}',
        'cleared': '🗑 ¡Historial limpiado!',
        'help': '❓ *Cómo funciona*\n\n'
                'Agrega el bot a un grupo y dale permisos de administrador.\n\n'
                'El bot detecta duplicados usando el ID único de Telegram (file_unique_id).\n'
                '¡No necesita descargas! Instantáneo y funciona con cualquier tamaño.\n\n'
                '*Detecta:*\n'
                '• Fotos duplicadas\n'
                '• Videos duplicados\n'
                '• GIFs duplicados\n'
                '• Documentos duplicados\n'
                '• Audios duplicados\n'
                '• Stickers duplicados\n\n'
                '¡Funciona incluso con reenvíos!',
        'error': '❌ Error al procesar',
        'need_admin': '⚠️ ¡Necesito permisos de administrador para eliminar mensajes!',
        'group_only': 'ℹ️ Este comando solo funciona en grupos',
    },
    'fr': {
        'welcome': '👋 Bonjour! Je suis *Duplicate Cleaner Bot*\n\n'
                   'Ajoutez-moi à un groupe et je détecterai et supprimerai automatiquement les photos/vidéos en double!\n\n'
                   '🔹 Commandes:\n'
                   '/start - Démarrer\n'
                   '/lang - Changer de langue\n'
                   '/stats - Voir les statistiques\n'
                   '/clear - Effacer l\'historique\n'
                   '/help - Aide',
        'lang_select': '🌐 Sélectionnez votre langue:',
        'lang_changed': '✅ Langue changée!',
        'duplicate_found': '🔴 Doublon détecté et supprimé!',
        'new_media': '✅ Média unique enregistré',
        'stats': '📊 *Statistiques du chat*\n\n'
                 '🖼 Photos uniques: {photos}\n'
                 '🎥 Vidéos uniques: {videos}\n'
                 '📄 Documents uniques: {documents}\n'
                 '🗑 Doublons supprimés: {duplicates}\n'
                 '💾 Total: {total}',
        'cleared': '🗑 Historique effacé!',
        'help': '❓ *Comment ça marche*\n\n'
                'Ajoutez le bot à un groupe et donnez les permissions admin.\n\n'
                'Le bot détecte les doublons en utilisant l\'ID unique de Telegram (file_unique_id).\n'
                'Pas de téléchargements! Instantané et fonctionne avec toutes les tailles.\n\n'
                '*Détecte:*\n'
                '• Photos en double\n'
                '• Vidéos en double\n'
                '• GIFs en double\n'
                '• Documents en double\n'
                '• Audios en double\n'
                '• Stickers en double\n\n'
                'Fonctionne même avec les transferts!',
        'error': '❌ Erreur de traitement',
        'need_admin': '⚠️ J\'ai besoin des permissions admin pour supprimer les messages!',
        'group_only': 'ℹ️ Cette commande ne fonctionne que dans les groupes',
    },
    'de': {
        'welcome': '👋 Hallo! Ich bin *Duplicate Cleaner Bot*\n\n'
                   'Füge mich zu einer Gruppe hinzu und ich erkenne und entferne automatisch doppelte Fotos/Videos!\n\n'
                   '🔹 Befehle:\n'
                   '/start - Starten\n'
                   '/lang - Sprache ändern\n'
                   '/stats - Statistiken anzeigen\n'
                   '/clear - Verlauf löschen\n'
                   '/help - Hilfe',
        'lang_select': '🌐 Wählen Sie Ihre Sprache:',
        'lang_changed': '✅ Sprache geändert!',
        'duplicate_found': '🔴 Duplikat erkannt und entfernt!',
        'new_media': '✅ Eindeutiges Medium gespeichert',
        'stats': '📊 *Chat-Statistiken*\n\n'
                 '🖼 Eindeutige Fotos: {photos}\n'
                 '🎥 Eindeutige Videos: {videos}\n'
                 '📄 Eindeutige Dokumente: {documents}\n'
                 '🗑 Entfernte Duplikate: {duplicates}\n'
                 '💾 Gesamt: {total}',
        'cleared': '🗑 Verlauf gelöscht!',
        'help': '❓ *Wie es funktioniert*\n\n'
                'Füge den Bot zu einer Gruppe hinzu und gib Admin-Berechtigungen.\n\n'
                'Bot erkennt Duplikate mit Telegrams eindeutiger ID (file_unique_id).\n'
                'Keine Downloads! Sofort und funktioniert mit jeder Dateigröße.\n\n'
                '*Erkennt:*\n'
                '• Doppelte Fotos\n'
                '• Doppelte Videos\n'
                '• Doppelte GIFs\n'
                '• Doppelte Dokumente\n'
                '• Doppelte Audios\n'
                '• Doppelte Sticker\n\n'
                'Funktioniert auch mit Weiterleitungen!',
        'error': '❌ Verarbeitungsfehler',
        'need_admin': '⚠️ Ich brauche Admin-Rechte zum Löschen von Nachrichten!',
        'group_only': 'ℹ️ Dieser Befehl funktioniert nur in Gruppen',
    },
    'it': {
        'welcome': '👋 Ciao! Sono *Duplicate Cleaner Bot*\n\n'
                   'Aggiungimi a un gruppo e rileverò e rimuoverò automaticamente foto/video duplicati!\n\n'
                   '🔹 Comandi:\n'
                   '/start - Avvia\n'
                   '/lang - Cambia lingua\n'
                   '/stats - Visualizza statistiche\n'
                   '/clear - Cancella cronologia\n'
                   '/help - Aiuto',
        'lang_select': '🌐 Seleziona la tua lingua:',
        'lang_changed': '✅ Lingua cambiata!',
        'duplicate_found': '🔴 Duplicato rilevato e rimosso!',
        'new_media': '✅ Media unico salvato',
        'stats': '📊 *Statistiche chat*\n\n'
                 '🖼 Foto uniche: {photos}\n'
                 '🎥 Video unici: {videos}\n'
                 '📄 Documenti unici: {documents}\n'
                 '🗑 Duplicati rimossi: {duplicates}\n'
                 '💾 Totale: {total}',
        'cleared': '🗑 Cronologia cancellata!',
        'help': '❓ *Come funziona*\n\n'
                'Aggiungi il bot a un gruppo e dai i permessi di amministratore.\n\n'
                'Il bot rileva i duplicati usando l\'ID unico di Telegram (file_unique_id).\n'
                'Nessun download necessario! Istantaneo e funziona con qualsiasi dimensione.\n\n'
                '*Rileva:*\n'
                '• Foto duplicate\n'
                '• Video duplicati\n'
                '• GIF duplicate\n'
                '• Documenti duplicati\n'
                '• Audio duplicati\n'
                '• Sticker duplicati\n\n'
                'Funziona anche con gli inoltri!',
        'error': '❌ Errore di elaborazione',
        'need_admin': '⚠️ Ho bisogno dei permessi di amministratore per eliminare i messaggi!',
        'group_only': 'ℹ️ Questo comando funziona solo nei gruppi',
    }
}

# ==================== CLASSE PRINCIPAL ====================
class SimpleDuplicate Cleaner Bot:
    def __init__(self):
        # Armazena apenas file_unique_id por chat
        self.photo_ids: Dict[int, Set[str]] = defaultdict(set)
        self.video_ids: Dict[int, Set[str]] = defaultdict(set)
        self.document_ids: Dict[int, Set[str]] = defaultdict(set)
        self.audio_ids: Dict[int, Set[str]] = defaultdict(set)
        self.sticker_ids: Dict[int, Set[str]] = defaultdict(set)
        self.animation_ids: Dict[int, Set[str]] = defaultdict(set)
        
        # Idioma por chat
        self.chat_languages: Dict[int, str] = defaultdict(lambda: 'pt')
        
        # Estatísticas por chat
        self.stats: Dict[int, Dict] = defaultdict(lambda: {
            'photos': 0,
            'videos': 0,
            'documents': 0,
            'duplicates': 0
        })
    
    def get_text(self, chat_id: int, key: str, **kwargs) -> str:
        """Retorna texto traduzido"""
        lang = self.chat_languages[chat_id]
        text = TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, '')
        return text.format(**kwargs) if kwargs else text
    
    def is_duplicate(self, chat_id: int, file_unique_id: str, media_type: str) -> bool:
        """Verifica se é duplicata usando file_unique_id do Telegram"""
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
    
    def add_media(self, chat_id: int, file_unique_id: str, media_type: str):
        """Adiciona mídia ao registro"""
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
            
            # Atualiza estatísticas
            if media_type == 'photo':
                self.stats[chat_id]['photos'] += 1
            elif media_type == 'video':
                self.stats[chat_id]['videos'] += 1
            elif media_type == 'document':
                self.stats[chat_id]['documents'] += 1

# Instância global
bot_instance = SimpleDuplicate Cleaner Bot()

# ==================== HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'welcome'),
        parse_mode='Markdown'
    )

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /lang"""
    keyboard = [
        [
            InlineKeyboardButton("🇧🇷 PT", callback_data='lang_pt'),
            InlineKeyboardButton("🇺🇸 EN", callback_data='lang_en'),
            InlineKeyboardButton("🇪🇸 ES", callback_data='lang_es'),
        ],
        [
            InlineKeyboardButton("🇫🇷 FR", callback_data='lang_fr'),
            InlineKeyboardButton("🇩🇪 DE", callback_data='lang_de'),
            InlineKeyboardButton("🇮🇹 IT", callback_data='lang_it'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        bot_instance.get_text(update.effective_chat.id, 'lang_select'),
        reply_markup=reply_markup
    )

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para mudança de idioma"""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    lang = query.data.split('_')[1]
    bot_instance.chat_languages[chat_id] = lang
    
    await query.edit_message_text(
        bot_instance.get_text(chat_id, 'lang_changed')
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats"""
    chat_id = update.effective_chat.id
    
    # Só funciona em grupos
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
    """Comando /clear"""
    chat_id = update.effective_chat.id
    
    # Só funciona em grupos
    if update.effective_chat.type == 'private':
        await update.message.reply_text(
            bot_instance.get_text(chat_id, 'group_only')
        )
        return
    
    # Limpa tudo deste chat
    bot_instance.photo_ids[chat_id].clear()
    bot_instance.video_ids[chat_id].clear()
    bot_instance.document_ids[chat_id].clear()
    bot_instance.audio_ids[chat_id].clear()
    bot_instance.sticker_ids[chat_id].clear()
    bot_instance.animation_ids[chat_id].clear()
    bot_instance.stats[chat_id] = {
        'photos': 0,
        'videos': 0,
        'documents': 0,
        'duplicates': 0
    }
    
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'cleared')
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'help'),
        parse_mode='Markdown'
    )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler universal para todas as mídias"""
    chat_id = update.effective_chat.id
    message = update.message
    
    # Detecta tipo de mídia e pega file_unique_id
    media_info = None
    
    if message.photo:
        # Pega a maior resolução
        photo = message.photo[-1]
        media_info = ('photo', photo.file_unique_id)
    
    elif message.video:
        media_info = ('video', message.video.file_unique_id)
    
    elif message.animation:  # GIF
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
    
    # Verifica se é duplicata
    if bot_instance.is_duplicate(chat_id, file_unique_id, media_type):
        try:
            # Deleta mensagem duplicada
            await message.delete()
            bot_instance.stats[chat_id]['duplicates'] += 1
            
            logger.info(f"Duplicata removida no chat {chat_id}: {media_type}")
        except Exception as e:
            logger.error(f"Erro ao deletar: {e}")
            # Avisa se não tem permissão
            if "not enough rights" in str(e).lower():
                await message.reply_text(
                    bot_instance.get_text(chat_id, 'need_admin')
                )
    else:
        # Nova mídia - adiciona ao registro
        bot_instance.add_media(chat_id, file_unique_id, media_type)
        logger.info(f"Nova mídia salva no chat {chat_id}: {media_type}")

# ==================== SERVIDOR WEB (para Render) ====================
from flask import Flask
import threading

# Cria servidor Flask simples
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Duplicate Cleaner Bot - Online</title>
        <style>
            body {
             rò automaticamente foto/video duplicati!\n\n'
                   '🔹 Comandi:\n'
                   '/start - Avvia\n'
                   '/lang - Cambia lingua\n'
                   '/stats - Visualizza statistiche\n'
                   '/clear - Cancella cronologia\n'
                   '/help - Aiuto',
        'lang_select': '🌐 Seleziona la tua lingua:',
        'lang_changed': '✅ Lingua cambiata!',
        'duplicate_found': '🔴 Duplicato rilevato e rimosso!',
        'new_media': '✅ Media unico salvato',
        'stats': '📊 *Statistiche chat*\n\n'
                 '🖼 Foto uniche: {photos}\n'
                 '🎥 Video unici: {videos}\n'
                 '📄 Documenti unici: {documents}\n'
                 '🗑 Duplicati rimossi: {duplicates}\n'
                 '💾 Totale: {total}',
        'cleared': '🗑 Cronologia cancellata!',
        'help': '❓ *Come funziona*\n\n'
                'Aggiungi il bot a un gruppo e dai i permessi di amministratore.\n\n'
                'Il bot rileva i duplicati usando l\'ID unico di Telegram (file_unique_id).\n'
                'Nessun download necessario! Istantaneo e funziona con qualsiasi dimensione.\n\n'
                '*Rileva:*\n'
                '• Foto duplicate\n'
                '• Video duplicati\n'
                '• GIF duplicate\n'
                '• Documenti duplicati\n'
                '• Audio duplicati\n'
                '• Sticker duplicati\n\n'
                'Funziona anche con gli inoltri!',
        'error': '❌ Errore di elaborazione',
        'need_admin': '⚠️ Ho bisogno dei permessi di amministratore per eliminare i messaggi!',
        'group_only': 'ℹ️ Questo comando funziona solo nei gruppi',
    }
}

# ==================== CLASSE PRINCIPAL ====================
class SimpleDedupBot:
    def __init__(self):
        # Armazena apenas file_unique_id por chat
        self.photo_ids: Dict[int, Set[str]] = defaultdict(set)
        self.video_ids: Dict[int, Set[str]] = defaultdict(set)
        self.document_ids: Dict[int, Set[str]] = defaultdict(set)
        self.audio_ids: Dict[int, Set[str]] = defaultdict(set)
        self.sticker_ids: Dict[int, Set[str]] = defaultdict(set)
        self.animation_ids: Dict[int, Set[str]] = defaultdict(set)
        
        # Idioma por chat
        self.chat_languages: Dict[int, str] = defaultdict(lambda: 'pt')
        
        # Estatísticas por chat
        self.stats: Dict[int, Dict] = defaultdict(lambda: {
            'photos': 0,
            'videos': 0,
            'documents': 0,
            'duplicates': 0
        })
    
    def get_text(self, chat_id: int, key: str, **kwargs) -> str:
        """Retorna texto traduzido"""
        lang = self.chat_languages[chat_id]
        text = TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, '')
        return text.format(**kwargs) if kwargs else text
    
    def is_duplicate(self, chat_id: int, file_unique_id: str, media_type: str) -> bool:
        """Verifica se é duplicata usando file_unique_id do Telegram"""
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
    
    def add_media(self, chat_id: int, file_unique_id: str, media_type: str):
        """Adiciona mídia ao registro"""
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
            
            # Atualiza estatísticas
            if media_type == 'photo':
                self.stats[chat_id]['photos'] += 1
            elif media_type == 'video':
                self.stats[chat_id]['videos'] += 1
            elif media_type == 'document':
                self.stats[chat_id]['documents'] += 1

# Instância global
bot_instance = SimpleDedupBot()

# ==================== HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'welcome'),
        parse_mode='Markdown'
    )

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /lang"""
    keyboard = [
        [
            InlineKeyboardButton("🇧🇷 PT", callback_data='lang_pt'),
            InlineKeyboardButton("🇺🇸 EN", callback_data='lang_en'),
            InlineKeyboardButton("🇪🇸 ES", callback_data='lang_es'),
        ],
        [
            InlineKeyboardButton("🇫🇷 FR", callback_data='lang_fr'),
            InlineKeyboardButton("🇩🇪 DE", callback_data='lang_de'),
            InlineKeyboardButton("🇮🇹 IT", callback_data='lang_it'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        bot_instance.get_text(update.effective_chat.id, 'lang_select'),
        reply_markup=reply_markup
    )

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para mudança de idioma"""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    lang = query.data.split('_')[1]
    bot_instance.chat_languages[chat_id] = lang
    
    await query.edit_message_text(
        bot_instance.get_text(chat_id, 'lang_changed')
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats"""
    chat_id = update.effective_chat.id
    
    # Só funciona em grupos
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
    """Comando /clear"""
    chat_id = update.effective_chat.id
    
    # Só funciona em grupos
    if update.effective_chat.type == 'private':
        await update.message.reply_text(
            bot_instance.get_text(chat_id, 'group_only')
        )
        return
    
    # Limpa tudo deste chat
    bot_instance.photo_ids[chat_id].clear()
    bot_instance.video_ids[chat_id].clear()
    bot_instance.document_ids[chat_id].clear()
    bot_instance.audio_ids[chat_id].clear()
    bot_instance.sticker_ids[chat_id].clear()
    bot_instance.animation_ids[chat_id].clear()
    bot_instance.stats[chat_id] = {
        'photos': 0,
        'videos': 0,
        'documents': 0,
        'duplicates': 0
    }
    
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'cleared')
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'help'),
        parse_mode='Markdown'
    )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler universal para todas as mídias"""
    chat_id = update.effective_chat.id
    message = update.message
    
    # Detecta tipo de mídia e pega file_unique_id
    media_info = None
    
    if message.photo:
        # Pega a maior resolução
        photo = message.photo[-1]
        media_info = ('photo', photo.file_unique_id)
    
    elif message.video:
        media_info = ('video', message.video.file_unique_id)
    
    elif message.animation:  # GIF
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
    
    # Verifica se é duplicata
    if bot_instance.is_duplicate(chat_id, file_unique_id, media_type):
        try:
            # Deleta mensagem duplicada
            await message.delete()
            bot_instance.stats[chat_id]['duplicates'] += 1
            
            logger.info(f"Duplicata removida no chat {chat_id}: {media_type}")
        except Exception as e:
            logger.error(f"Erro ao deletar: {e}")
            # Avisa se não tem permissão
            if "not enough rights" in str(e).lower():
                await message.reply_text(
                    bot_instance.get_text(chat_id, 'need_admin')
                )
    else:
        # Nova mídia - adiciona ao registro
        bot_instance.add_media(chat_id, file_unique_id, media_type)
        logger.info(f"Nova mídia salva no chat {chat_id}: {media_type}")

# ==================== SERVIDOR WEB (para Render) ====================
from flask import Flask
import threading

# Cria servidor Flask simples
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DedupBot - Online</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
              n'
                   '/start - Avvia\n'
                   '/lang - Cambia lingua\n'
                   '/stats - Visualizza statistiche\n'
                   '/clear - Cancella cronologia\n'
                   '/help - Aiuto',
        'lang_select': '🌐 Seleziona la tua lingua:',
        'lang_changed': '✅ Lingua cambiata!',
        'duplicate_found': '🔴 Duplicato rilevato e rimosso!',
        'new_media': '✅ Media unico salvato',
        'stats': '📊 *Statistiche chat*\n\n'
                 '🖼 Foto uniche: {photos}\n'
                 '🎥 Video unici: {videos}\n'
                 '📄 Documenti unici: {documents}\n'
                 '🗑 Duplicati rimossi: {duplicates}\n'
                 '💾 Totale: {total}',
        'cleared': '🗑 Cronologia cancellata!',
        'help': '❓ *Come funziona*\n\n'
                'Aggiungi il bot a un gruppo e dai i permessi di amministratore.\n\n'
                'Il bot rileva i duplicati usando l\'ID unico di Telegram (file_unique_id).\n'
                'Nessun download necessario! Istantaneo e funziona con qualsiasi dimensione.\n\n'
                '*Rileva:*\n'
                '• Foto duplicate\n'
                '• Video duplicati\n'
                '• GIF duplicate\n'
                '• Documenti duplicati\n'
                '• Audio duplicati\n'
                '• Sticker duplicati\n\n'
                'Funziona anche con gli inoltri!',
        'error': '❌ Errore di elaborazione',
        'need_admin': '⚠️ Ho bisogno dei permessi di amministratore per eliminare i messaggi!',
        'group_only': 'ℹ️ Questo comando funziona solo nei gruppi',
    }
}

# ==================== CLASSE PRINCIPAL ====================
class SimpleDedupBot:
    def __init__(self):
        # Armazena apenas file_unique_id por chat
        self.photo_ids: Dict[int, Set[str]] = defaultdict(set)
        self.video_ids: Dict[int, Set[str]] = defaultdict(set)
        self.document_ids: Dict[int, Set[str]] = defaultdict(set)
        self.audio_ids: Dict[int, Set[str]] = defaultdict(set)
        self.sticker_ids: Dict[int, Set[str]] = defaultdict(set)
        self.animation_ids: Dict[int, Set[str]] = defaultdict(set)
        
        # Idioma por chat
        self.chat_languages: Dict[int, str] = defaultdict(lambda: 'pt')
        
        # Estatísticas por chat
        self.stats: Dict[int, Dict] = defaultdict(lambda: {
            'photos': 0,
            'videos': 0,
            'documents': 0,
            'duplicates': 0
        })
    
    def get_text(self, chat_id: int, key: str, **kwargs) -> str:
        """Retorna texto traduzido"""
        lang = self.chat_languages[chat_id]
        text = TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, '')
        return text.format(**kwargs) if kwargs else text
    
    def is_duplicate(self, chat_id: int, file_unique_id: str, media_type: str) -> bool:
        """Verifica se é duplicata usando file_unique_id do Telegram"""
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
    
    def add_media(self, chat_id: int, file_unique_id: str, media_type: str):
        """Adiciona mídia ao registro"""
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
            
            # Atualiza estatísticas
            if media_type == 'photo':
                self.stats[chat_id]['photos'] += 1
            elif media_type == 'video':
                self.stats[chat_id]['videos'] += 1
            elif media_type == 'document':
                self.stats[chat_id]['documents'] += 1

# Instância global
bot_instance = SimpleDedupBot()

# ==================== HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'welcome'),
        parse_mode='Markdown'
    )

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /lang"""
    keyboard = [
        [
            InlineKeyboardButton("🇧🇷 PT", callback_data='lang_pt'),
            InlineKeyboardButton("🇺🇸 EN", callback_data='lang_en'),
            InlineKeyboardButton("🇪🇸 ES", callback_data='lang_es'),
        ],
        [
            InlineKeyboardButton("🇫🇷 FR", callback_data='lang_fr'),
            InlineKeyboardButton("🇩🇪 DE", callback_data='lang_de'),
            InlineKeyboardButton("🇮🇹 IT", callback_data='lang_it'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        bot_instance.get_text(update.effective_chat.id, 'lang_select'),
        reply_markup=reply_markup
    )

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para mudança de idioma"""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    lang = query.data.split('_')[1]
    bot_instance.chat_languages[chat_id] = lang
    
    await query.edit_message_text(
        bot_instance.get_text(chat_id, 'lang_changed')
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats"""
    chat_id = update.effective_chat.id
    
    # Só funciona em grupos
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
    """Comando /clear"""
    chat_id = update.effective_chat.id
    
    # Só funciona em grupos
    if update.effective_chat.type == 'private':
        await update.message.reply_text(
            bot_instance.get_text(chat_id, 'group_only')
        )
        return
    
    # Limpa tudo deste chat
    bot_instance.photo_ids[chat_id].clear()
    bot_instance.video_ids[chat_id].clear()
    bot_instance.document_ids[chat_id].clear()
    bot_instance.audio_ids[chat_id].clear()
    bot_instance.sticker_ids[chat_id].clear()
    bot_instance.animation_ids[chat_id].clear()
    bot_instance.stats[chat_id] = {
        'photos': 0,
        'videos': 0,
        'documents': 0,
        'duplicates': 0
    }
    
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'cleared')
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        bot_instance.get_text(chat_id, 'help'),
        parse_mode='Markdown'
    )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler universal para todas as mídias"""
    chat_id = update.effective_chat.id
    message = update.message
    
    # Detecta tipo de mídia e pega file_unique_id
    media_info = None
    
    if message.photo:
        # Pega a maior resolução
        photo = message.photo[-1]
        media_info = ('photo', photo.file_unique_id)
    
    elif message.video:
        media_info = ('video', message.video.file_unique_id)
    
    elif message.animation:  # GIF
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
    
    # Verifica se é duplicata
    if bot_instance.is_duplicate(chat_id, file_unique_id, media_type):
        try:
            # Deleta mensagem duplicada
            await message.delete()
            bot_instance.stats[chat_id]['duplicates'] += 1
            
            logger.info(f"Duplicata removida no chat {chat_id}: {media_type}")
        except Exception as e:
            logger.error(f"Erro ao deletar: {e}")
            # Avisa se não tem permissão
            if "not enough rights" in str(e).lower():
                await message.reply_text(
                    bot_instance.get_text(chat_id, 'need_admin')
                )
    else:
        # Nova mídia - adiciona ao registro
        bot_instance.add_media(chat_id, file_unique_id, media_type)
        logger.info(f"Nova mídia salva no chat {chat_id}: {media_type}")

# ==================== MAIN ====================
def main():
    """Função principal"""
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN não configurado!")
        logger.info("Configure a variável de ambiente TELEGRAM_BOT_TOKEN")
        return
    
    # Cria aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add
