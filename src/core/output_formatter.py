"""
Output Formatter
===============

Formats translation results into Ren'Py translate block format.
"""

import logging
from typing import List, Dict, Set, TYPE_CHECKING
from pathlib import Path
import re

if TYPE_CHECKING:
    from src.core.translator import TranslationResult

# Date translations for various languages (weekdays, months)
DATE_TRANSLATIONS = {
    "italian": {
        "weekdays": ["Lunedi", "Martedi", "Mercoledi", "Giovedi", "Venerdi", "Sabato", "Domenica"],
        "weekdays_short": ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"],
        "months": ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                   "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
        "months_short": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
        "empty_slot": "slot vuoto",
        "page": "Pagina {}",
        "auto_saves": "Salvataggi automatici",
        "quick_saves": "Salvataggi rapidi",
    },
    "turkish": {
        "weekdays": ["Pazartesi", "Sali", "Carsamba", "Persembe", "Cuma", "Cumartesi", "Pazar"],
        "weekdays_short": ["Pzt", "Sal", "Car", "Per", "Cum", "Cmt", "Paz"],
        "months": ["Ocak", "Subat", "Mart", "Nisan", "Mayis", "Haziran",
                   "Temmuz", "Agustos", "Eylul", "Ekim", "Kasim", "Aralik"],
        "months_short": ["Oca", "Sub", "Mar", "Nis", "May", "Haz", "Tem", "Agu", "Eyl", "Eki", "Kas", "Ara"],
        "empty_slot": "bos yuva",
        "page": "Sayfa {}",
        "auto_saves": "Otomatik kayitlar",
        "quick_saves": "Hizli kayitlar",
    },
    "chinese_s": {
        "weekdays": ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"],
        "weekdays_short": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "months": ["一月", "二月", "三月", "四月", "五月", "六月",
                   "七月", "八月", "九月", "十月", "十一月", "十二月"],
        "months_short": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
        "empty_slot": "空存档位",
        "page": "第 {} 页",
        "auto_saves": "自动存档",
        "quick_saves": "快速存档",
    },
    "chinese_t": {
        "weekdays": ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"],
        "weekdays_short": ["週一", "週二", "週三", "週四", "週五", "週六", "週日"],
        "months": ["一月", "二月", "三月", "四月", "五月", "六月",
                   "七月", "八月", "九月", "十月", "十一月", "十二月"],
        "months_short": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
        "empty_slot": "空存檔位",
        "page": "第 {} 頁",
        "auto_saves": "自動存檔",
        "quick_saves": "快速存檔",
    },
    "japanese": {
        "weekdays": ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"],
        "weekdays_short": ["月", "火", "水", "木", "金", "土", "日"],
        "months": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
        "months_short": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
        "empty_slot": "空きスロット",
        "page": "ページ {}",
        "auto_saves": "オートセーブ",
        "quick_saves": "クイックセーブ",
    },
    "korean": {
        "weekdays": ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"],
        "weekdays_short": ["월", "화", "수", "목", "금", "토", "일"],
        "months": ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"],
        "months_short": ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"],
        "empty_slot": "빈 슬롯",
        "page": "페이지 {}",
        "auto_saves": "자동 저장",
        "quick_saves": "빠른 저장",
    },
    "german": {
        "weekdays": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
        "weekdays_short": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
        "months": ["Januar", "Februar", "Marz", "April", "Mai", "Juni",
                   "Juli", "August", "September", "Oktober", "November", "Dezember"],
        "months_short": ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
        "empty_slot": "leerer Slot",
        "page": "Seite {}",
        "auto_saves": "Automatische Speicherstande",
        "quick_saves": "Schnellspeicher",
    },
    "french": {
        "weekdays": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
        "weekdays_short": ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
        "months": ["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin",
                   "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre"],
        "months_short": ["Jan", "Fev", "Mar", "Avr", "Mai", "Jui", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"],
        "empty_slot": "emplacement vide",
        "page": "Page {}",
        "auto_saves": "Sauvegardes automatiques",
        "quick_saves": "Sauvegardes rapides",
    },
    "spanish": {
        "weekdays": ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"],
        "weekdays_short": ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"],
        "months": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
        "months_short": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
        "empty_slot": "ranura vacia",
        "page": "Pagina {}",
        "auto_saves": "Guardados automaticos",
        "quick_saves": "Guardados rapidos",
    },
    "portuguese": {
        "weekdays": ["Segunda-feira", "Terca-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sabado", "Domingo"],
        "weekdays_short": ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"],
        "months": ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
        "months_short": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
        "empty_slot": "slot vazio",
        "page": "Pagina {}",
        "auto_saves": "Salvamentos automaticos",
        "quick_saves": "Salvamentos rapidos",
    },
    "russian": {
        "weekdays": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"],
        "weekdays_short": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "months": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
        "months_short": ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
        "empty_slot": "пустой слот",
        "page": "Страница {}",
        "auto_saves": "Автосохранения",
        "quick_saves": "Быстрые сохранения",
    },
    "polish": {
        "weekdays": ["Poniedzialek", "Wtorek", "Sroda", "Czwartek", "Piatek", "Sobota", "Niedziela"],
        "weekdays_short": ["Pon", "Wt", "Sr", "Czw", "Pt", "Sob", "Nd"],
        "months": ["Styczen", "Luty", "Marzec", "Kwiecien", "Maj", "Czerwiec",
                   "Lipiec", "Sierpien", "Wrzesien", "Pazdziernik", "Listopad", "Grudzien"],
        "months_short": ["Sty", "Lut", "Mar", "Kwi", "Maj", "Cze", "Lip", "Sie", "Wrz", "Paz", "Lis", "Gru"],
        "empty_slot": "pusty slot",
        "page": "Strona {}",
        "auto_saves": "Autozapisy",
        "quick_saves": "Szybkie zapisy",
    },
    "indonesian": {
        "weekdays": ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
        "weekdays_short": ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"],
        "months": ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                   "Juli", "Agustus", "September", "Oktober", "November", "Desember"],
        "months_short": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"],
        "empty_slot": "slot kosong",
        "page": "Halaman {}",
        "auto_saves": "Simpan otomatis",
        "quick_saves": "Simpan cepat",
    },
    "vietnamese": {
        "weekdays": ["Thu Hai", "Thu Ba", "Thu Tu", "Thu Nam", "Thu Sau", "Thu Bay", "Chu Nhat"],
        "weekdays_short": ["T2", "T3", "T4", "T5", "T6", "T7", "CN"],
        "months": ["Thang 1", "Thang 2", "Thang 3", "Thang 4", "Thang 5", "Thang 6",
                   "Thang 7", "Thang 8", "Thang 9", "Thang 10", "Thang 11", "Thang 12"],
        "months_short": ["Th1", "Th2", "Th3", "Th4", "Th5", "Th6", "Th7", "Th8", "Th9", "Th10", "Th11", "Th12"],
        "empty_slot": "o trong",
        "page": "Trang {}",
        "auto_saves": "Luu tu dong",
        "quick_saves": "Luu nhanh",
    },
    "thai": {
        "weekdays": ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"],
        "weekdays_short": ["จ", "อ", "พ", "พฤ", "ศ", "ส", "อา"],
        "months": ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                   "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"],
        "months_short": ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."],
        "empty_slot": "ช่องว่าง",
        "page": "หน้า {}",
        "auto_saves": "บันทึกอัตโนมัติ",
        "quick_saves": "บันทึกด่วน",
    },
}

# English weekday/month names for translation mapping
ENGLISH_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ENGLISH_WEEKDAYS_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ENGLISH_MONTHS = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
ENGLISH_MONTHS_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class RenPyOutputFormatter:
    """Formats translations into Ren'Py translate block format."""
    
    # File extensions that should never be translated
    SKIP_FILE_EXTENSIONS = (
        '.otf', '.ttf', '.woff', '.woff2',  # Fonts
        '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.ico',  # Images
        '.mp3', '.ogg', '.wav', '.flac', '.aac', '.m4a',  # Audio
        '.mp4', '.webm', '.avi', '.mkv', '.mov',  # Video
        '.rpy', '.rpyc', '.rpa',  # Ren'Py files
        '.py',  # Only Python source should be skipped
    )
    
    # Ren'Py technical terms that should never be translated
    # NOTE: Only lowercase terms here - Title Case like "History" are valid UI labels
    RENPY_TECHNICAL_TERMS = {
        # Screen elements & style identifiers (always lowercase in code)
        'say', 'window', 'namebox', 'choice', 'quick', 'navigation',
        'return_button', 'page_label', 'page_label_text', 'slot',
        'slot_time_text', 'slot_name_text', 'save_delete', 'pref',
        'radio', 'check', 'slider', 'tooltip_icon', 'tooltip_frame',
        'dismiss', 'history_name', 'color',  # Note: removed 'history', 'help' - valid UI labels
        'confirm_prompt', 'notify',
        'nvl_window', 'nvl_button', 'medium', 'touch', 'small',
        'replay_locked',
        # Style & layout properties
        'show', 'hide', 'unicode', 'left', 'right', 'center',
        'top', 'bottom', 'true', 'false', 'none', 'null', 'auto',
        # Common screen/action identifiers
        'add_post', 'card', 'money_get', 'money_pay', 'mp',
        'pass_time', 'rel_down', 'rel_up',
        # Input/output
        'input', 'output', 'default', 'value',
        # Common config/variable names
        'id', 'name', 'type', 'style', 'action', 'hovered', 'unhovered',
        'selected', 'insensitive', 'activate', 'alternate',
        # Common technical single words
        'idle', 'hover', 'focus', 'insensitive', 'selected_idle',
        'selected_hover', 'selected_focus', 'selected_insensitive',
    }
    
    # Pre-compiled regex patterns for performance (class-level caching)
    _FORMAT_PLACEHOLDER_RE = re.compile(r'\{[^}]*\}')
    _VARIABLE_RE = re.compile(r'\[[^\[\]]+\]')
    _DISAMBIGUATION_RE = re.compile(r'\{#[^}]+\}')
    _TAG_RE = re.compile(r'\{[^{}]*\}')
    _URL_RE = re.compile(r'^(https?://|ftp://|mailto:|www\.)')
    _HEX_COLOR_RE = re.compile(r'^#[0-9a-fA-F]{3,8}$')
    _NUMBER_RE = re.compile(r'^-?\d+\.?\d*$')
    _SNAKE_CASE_RE = re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)+$')
    _SCREAMING_SNAKE_RE = re.compile(r'^[A-Z][A-Z0-9]*(_[A-Z0-9]+)+$')
    _GAME_SAVE_ID_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*-\d+$')
    _VERSION_RE = re.compile(r'^v?\d+\.\d+(\.\d+)?([a-z])?$')
    _FILE_PATH_SLASH_RE = re.compile(r'^[a-zA-Z0-9_/.\-]+$')
    _FILE_PATH_BACKSLASH_RE = re.compile(r'^[a-zA-Z0-9_\\\.\-]+$')
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def _should_skip_translation(self, text: str) -> bool:
        """
        Check if a text should be skipped from translation output.
        Returns True if the text is a technical term, file path, or identifier.
        This is a SAFETY NET - parser should have already filtered most of these.
        Uses pre-compiled regex patterns for performance.
        """
        text_strip = text.strip()
        text_lower = text_strip.lower()
        
        # Skip empty text
        if not text_strip:
            return True
        
        # Skip Python format strings like {:,}, {:3d}, {}, {}Attitude:{} {}
        # These are used for number/string formatting and should not be translated
        if '{' in text_strip:
            # Count format placeholders using cached regex
            format_count = len(self._FORMAT_PLACEHOLDER_RE.findall(text_strip))
            if format_count >= 1:
                # Remove format placeholders and check remaining content
                remaining = self._FORMAT_PLACEHOLDER_RE.sub('', text_strip).strip()
                # If remaining has no meaningful letters, skip
                if not re.search(r'[a-zA-ZçğıöşüÇĞIİÖŞÜа-яА-Яа-яА-Я]{3,}', remaining):
                    return True
                # If format placeholders dominate the string, skip
                if format_count >= 2 and len(remaining) < 10:
                    return True
        
        # Skip file names/paths (fonts, images, audio, etc.)
        if any(text_lower.endswith(ext) for ext in self.SKIP_FILE_EXTENSIONS):
            return True
        
        # Skip paths starting with common folder names
        if text_strip.startswith(('fonts/', 'images/', 'audio/', 'music/', 'sounds/', 
                                   'gui/', 'screens/', 'script/', 'game/', 'tl/')):
            return True
        
        # Skip paths with slashes (file paths like "fonts/something.otf")
        if '/' in text_strip and ' ' not in text_strip:
            if self._FILE_PATH_SLASH_RE.match(text_strip):
                return True
        
        # Skip backslash paths (Windows style)
        if '\\' in text_strip and ' ' not in text_strip:
            if self._FILE_PATH_BACKSLASH_RE.match(text_strip):
                return True
        
        # Skip URLs (using cached pattern)
        if self._URL_RE.match(text_lower):
            return True
        
        # Skip hex color codes (using cached pattern)
        if self._HEX_COLOR_RE.match(text_strip):
            return True
        
        # Skip pure numbers (using cached pattern)
        if self._NUMBER_RE.match(text_strip):
            return True
        
        # Skip Ren'Py technical terms - ONLY exact lowercase match
        # "history" -> skip, "History" -> translate (UI label)
        if text_strip in self.RENPY_TECHNICAL_TERMS:
            return True
        
        # Skip snake_case identifiers (using cached pattern)
        if self._SNAKE_CASE_RE.match(text_strip):
            return True
        
        # Skip SCREAMING_SNAKE_CASE constants (using cached pattern)
        if self._SCREAMING_SNAKE_RE.match(text_strip):
            return True
        
        # Skip save identifiers like "GameName-1234567890" (using cached pattern)
        if self._GAME_SAVE_ID_RE.match(text_strip):
            return True
        
        # Skip version strings (using cached pattern)
        if self._VERSION_RE.match(text_lower):
            return True
        
        # Skip if it's just Ren'Py tags/variables with no actual text
        stripped_of_tags = self._TAG_RE.sub('', text_strip)
        stripped_of_vars = self._VARIABLE_RE.sub('', stripped_of_tags)
        if not stripped_of_vars.strip():
            return True
        
        return False
    
    def sanitize_translation_id(self, text: str) -> str:
        """Create a valid Ren'Py translation ID from text."""
        # Remove special characters and replace with underscores
        text = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        
        # Remove multiple underscores
        text = re.sub(r'_+', '_', text)
        
        # Remove leading/trailing underscores
        text = text.strip('_')
        
        # Ensure it starts with a letter or underscore
        if text and text[0].isdigit():
            text = '_' + text
        
        # Limit length
        if len(text) > 50:
            text = text[:50]
        
        # Ensure it's not empty
        if not text:
            text = 'translated_text'
        
        return text
    
    def escape_renpy_string(self, text: str) -> str:
        """Escape special characters for Ren'Py strings.
        
        Handles:
        - Backslashes, quotes, newlines, tabs, carriage returns
        - Protects Ren'Py variables [var], [var!t] and tags {tag}
        - Protects disambiguation tags {#identifier}
        - Handles double brackets [[ and {{
        """
        if not text:
            return text
            
        import re
        
        # Find all Ren'Py variables [variable] and expressions (including !t flag)
        variable_pattern = re.compile(r'\[[^\[\]]+\]')
        variables = variable_pattern.findall(text)
        
        # CRITICAL: Find disambiguation tags {#...} FIRST - these must be preserved exactly
        disambiguation_pattern = re.compile(r'\{#[^}]+\}')
        disambiguation_tags = disambiguation_pattern.findall(text)
        
        # Find all Ren'Py tags like {i}, {b}, {color=#ff0000}, {/i}, etc.
        tag_pattern = re.compile(r'\{[^{}]*\}')
        tags = tag_pattern.findall(text)
        
        # Replace variables and tags with placeholders temporarily
        temp_text = text
        protection_map = {}
        counter = 0
        
        # Protect disambiguation tags FIRST (highest priority)
        for dtag in disambiguation_tags:
            placeholder = f"⟦DIS{counter:03d}⟧"
            protection_map[placeholder] = dtag
            temp_text = temp_text.replace(dtag, placeholder, 1)
            counter += 1
        
        # Protect variables
        for var in variables:
            placeholder = f"⟦VAR{counter:03d}⟧"
            protection_map[placeholder] = var
            temp_text = temp_text.replace(var, placeholder, 1)
            counter += 1
        
        # Protect tags (excluding disambiguation which are already protected)
        for tag in tags:
            if tag.startswith('{#'):  # Skip disambiguation tags
                continue
            placeholder = f"⟦TAG{counter:03d}⟧"
            protection_map[placeholder] = tag
            temp_text = temp_text.replace(tag, placeholder, 1)
            counter += 1
        
        # Handle literal double brackets BEFORE escaping
        # [[ should become \[\[ in Ren'Py to show literal [
        temp_text = temp_text.replace('[[', '\\[\\[')
        temp_text = temp_text.replace('{{', '\\{\\{')
        
        # Now escape the rest
        temp_text = temp_text.replace('\\', '\\\\')  # Escape backslashes first
        temp_text = temp_text.replace('"', '\\"')     # Escape double quotes
        temp_text = temp_text.replace('\r', '')       # Remove carriage returns
        temp_text = temp_text.replace('\n', '\\n')    # Escape newlines
        temp_text = temp_text.replace('\t', '\\t')    # Escape tabs
        
        # Restore variables and tags
        for placeholder, original_content in protection_map.items():
            temp_text = temp_text.replace(placeholder, original_content)
        
        return temp_text
    
    def generate_translation_block(self, 
                                 original_text: str, 
                                 translated_text: str, 
                                 language_code: str,
                                 translation_id: str = None,
                                 context: str = None,
                                 mode: str = "simple") -> str:
        """Generate a single translation block."""
        
        if not translation_id:
            # Create string-based translation that matches any label
            # This is more compatible with existing Ren'Py games
            import hashlib
            text_hash = hashlib.md5(original_text.encode('utf-8')).hexdigest()[:8]
            translation_id = f"strings_{text_hash}"
        
        escaped_original = self.escape_renpy_string(original_text)
        escaped_translated = self.escape_renpy_string(translated_text)
        
        if mode == "old_new":
            # Old/new format - INDIVIDUAL ENTRY (for building larger block)
            block = (
                f"    old \"{escaped_original}\"\n"
                f"    new \"{escaped_translated}\"\n\n"
            )
        else:
            # Simple format - original text in comment, direct translation line
            comment_original = escaped_original.replace('\n', '\\n')
            block = (
                f"    # \"{comment_original}\"\n"
                f"    \"{escaped_translated}\"\n\n"
            )
        
        return block
    
    def generate_character_translation(self,
                                     character_name: str,
                                     original_text: str,
                                     translated_text: str,
                                     language_code: str,
                                     translation_id: str = None,
                                     mode: str = "simple") -> str:
        """Generate a character dialogue translation block."""
        
        escaped_original = self.escape_renpy_string(original_text)
        escaped_translated = self.escape_renpy_string(translated_text)
        
        if mode == "old_new":
            # String-based format - INDIVIDUAL ENTRY (for building larger block)
            block = (
                f"    old {character_name} \"{escaped_original}\"\n"
                f"    new {character_name} \"{escaped_translated}\"\n\n"
            )
        else:
            # Simple format - original text in comment, direct translation line
            comment_original = escaped_original.replace('\n', '\\n')
            block = (
                f"    # {character_name} \"{comment_original}\"\n"
                f"    {character_name} \"{escaped_translated}\"\n\n"
            )
        
        return block
    
    def generate_menu_translation(self,
                                menu_options: List[Dict],
                                language_code: str,
                                menu_id: str = None) -> str:
        """Generate menu translation block - DEPRECATED. 
        
        Menu translations should use translate strings format instead.
        This method is kept for compatibility but menu items should be 
        included in the main strings block.
        """
        
        # Menu choices should be in translate strings block, not separate menu blocks
        # According to RenPy documentation: menu choices use "translate strings" format
        
        block = f"# NOTE: Menu choices should be in 'translate {language_code} strings:' block\n"
        block += f"# This is the old format and may not work properly in RenPy\n\n"
        
        if not menu_id:
            menu_id = f"menu_{self.sanitize_translation_id('_'.join([opt['original'] for opt in menu_options[:3]]))}"
        
        block += f"translate {language_code} {menu_id}:\n\n"
        
        for i, option in enumerate(menu_options):
            original = self.escape_renpy_string(option['original'])
            translated = self.escape_renpy_string(option['translated'])
            # Add each choice with real newlines
            block += f'    # "{original}"\n'
            block += f'    "{translated}"\n'
        
        block += "\n"
        return block
    
    def format_translation_file(self,
                              translation_results: List,
                              language_code: str,
                              source_file: Path = None,
                              include_header: bool = True,
                              output_format: str = "old_new") -> str:
        """Format complete translation file with SEPARATE blocks for each translation."""
        
        output_lines = []
        
        if include_header:
            header = self.generate_file_header(language_code, source_file)
            output_lines.append(header)
        
        # CRITICAL FIX: Create ONE translate strings block for ALL translations
        # This is the CORRECT Ren'Py format
        
        seen_translations = set()
        string_translations = []
        
        # Add the opening translate strings block
        string_translations.append(f"translate {language_code} strings:")
        string_translations.append("")
        
        for result in translation_results:
            if not result.success or not result.translated_text:
                continue
            
            original_text = result.original_text
            translated_text = result.translated_text
            
            # CRITICAL: Skip technical content that should not be translated
            if self._should_skip_translation(original_text):
                self.logger.debug(f"Skipping technical content: {original_text[:50]}...")
                continue
            
            # Avoid duplicates - use original text including disambiguation tags
            # "New" and "New{#project}" are DIFFERENT strings
            key = f"{original_text}_{translated_text}"
            if key in seen_translations:
                continue
            seen_translations.add(key)
            
            text_type = getattr(result, 'text_type', None)
            
            # Add source file/line comment for translator reference (if available)
            source_info = ""
            if hasattr(result, 'metadata') and result.metadata:
                file_path = result.metadata.get('file_path', '')
                line_number = result.metadata.get('line_number', '')
                if file_path and line_number:
                    # Extract just filename for cleaner output
                    import os
                    filename = os.path.basename(file_path)
                    source_info = f"    # {filename}:{line_number}\n"
            
            # Check if this is a paragraph text (_p() function)
            is_paragraph = (
                text_type == 'paragraph' or 
                '\n\n' in original_text or  # Contains paragraph breaks
                len(original_text) > 200  # Long text likely from _p()
            )
            
            if is_paragraph:
                # Use _p() format for paragraph text
                escaped_original = self._escape_for_old_string(original_text)
                formatted_translated = self._format_p_function_output(translated_text)
                
                if output_format == "old_new":
                    if source_info:
                        string_translations.append(source_info.rstrip())
                    string_translations.append(f'    old "{escaped_original}"')
                    string_translations.append(f'    new {formatted_translated}')
                    string_translations.append("")
                else:
                    if source_info:
                        string_translations.append(source_info.rstrip())
                    comment_original = escaped_original.replace('\n', '\\n')
                    string_translations.append(f'    # "{comment_original}"')
                    string_translations.append(f'    {formatted_translated}')
                    string_translations.append("")
            else:
                # Standard string format
                escaped_original = self.escape_renpy_string(original_text)
                escaped_translated = self.escape_renpy_string(translated_text)
                
                if output_format == "old_new":
                    if source_info:
                        string_translations.append(source_info.rstrip())
                    string_translations.append(f'    old "{escaped_original}"')
                    string_translations.append(f'    new "{escaped_translated}"')
                    string_translations.append("")
                else:
                    if source_info:
                        string_translations.append(source_info.rstrip())
                    comment_original = escaped_original.replace('\n', '\\n')
                    string_translations.append(f'    # "{comment_original}"')
                    string_translations.append(f'    "{escaped_translated}"')
                    string_translations.append("")
        
        # Combine header and strings
        output_lines.extend(string_translations)
        
        # Join sections with real newlines
        return "\n".join(output_lines)
    
    def _escape_for_old_string(self, text: str) -> str:
        """
        Escape text for use in 'old' string.
        Ren'Py expects paragraph breaks as literal \\n\\n in old strings.
        """
        # Protect Ren'Py variables and tags first
        variable_pattern = re.compile(r'\[[^\[\]]+\]')
        tag_pattern = re.compile(r'\{[^{}]*\}')
        
        variables = variable_pattern.findall(text)
        tags = tag_pattern.findall(text)
        
        temp_text = text
        protection_map = {}
        
        for i, var in enumerate(variables):
            placeholder = f"__VAR_{i}__"
            protection_map[placeholder] = var
            temp_text = temp_text.replace(var, placeholder, 1)
        
        for i, tag in enumerate(tags):
            placeholder = f"__TAG_{i}__"
            protection_map[placeholder] = tag
            temp_text = temp_text.replace(tag, placeholder, 1)
        
        # Escape quotes and backslashes
        temp_text = temp_text.replace('\\', '\\\\')
        temp_text = temp_text.replace('"', '\\"')
        
        # Convert newlines to escaped form for old string
        temp_text = temp_text.replace('\n', '\\n')
        
        # Restore protected content
        for placeholder, original_content in protection_map.items():
            temp_text = temp_text.replace(placeholder, original_content)
        
        return temp_text
    
    def _format_p_function_output(self, text: str) -> str:
        """
        Format translated text as _p() function for Ren'Py.
        Example output:
        _p(\"\"\"
            First paragraph line one
            first paragraph line two.

            Second paragraph.
            \"\"\")
        """
        # Split by paragraph breaks
        paragraphs = text.split('\n\n')
        
        # Format with proper indentation for _p() 
        lines = ['_p("""']
        
        for i, para in enumerate(paragraphs):
            # Each paragraph on its own line with indentation
            para_lines = para.split('\n')
            for line in para_lines:
                lines.append(f"    {line.strip()}")
            
            # Add blank line between paragraphs (except after last)
            if i < len(paragraphs) - 1:
                lines.append("")
        
        lines.append('    """)')
        
        return '\n'.join(lines)
    
    def generate_file_header(self, language_code: str, source_file: Path = None) -> str:
        """Generate file header with metadata."""
        from datetime import datetime
        from src.version import VERSION
        
        header = f"""# Ren'Py Translation File
# Language: {language_code}
# Generated by: RenLocalizer v{VERSION}
# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if source_file:
            header += f"# Source file: {source_file}\\n"
        
        header += """
# This file contains automatic translations.
# Please review and edit as needed.

"""
        return header
    
    def save_translation_file(self,
                            translation_results: List,
                            output_path: Path,
                            language_code: str,
                            source_file: Path = None,
                            output_format: str = "simple") -> bool:
        """Save translations to file."""
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate content
            content = self.format_translation_file(
                translation_results,
                language_code,
                source_file,
                output_format=output_format
            )
            
            # Write file with UTF-8 encoding (with BOM for Windows compatibility)
            # Using utf-8-sig ensures Ren'Py correctly reads the file on all systems
            with open(output_path, 'w', encoding='utf-8-sig', newline='\n') as f:
                f.write(content)
            
            self.logger.info(f"Saved translation file: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving translation file {output_path}: {e}")
            return False
    
    def organize_output_files(self,
                            translation_results: List,
                            output_base_dir: Path,
                            language_code: str,
                            source_files: List[Path] = None,
                            output_format: str = "old_new",
                            create_renpy_structure: bool = True) -> List[Path]:
        """Organize translations into language-specific directories."""
        
        output_files = []
        
        # Determine if this is a Ren'Py project and create proper structure
        if create_renpy_structure:
            # Check if we're in a Ren'Py project (has game folder)
            game_dir = self._find_game_directory(output_base_dir)
            if game_dir:
                # Create Ren'Py translation structure: game/tl/[language]/
                lang_dir = game_dir / "tl" / language_code
                self.logger.info(f"Creating Ren'Py translation structure: {lang_dir}")
                
                # Create language initialization file for Ren'Py - do it immediately
                self._create_language_init_file(game_dir, language_code)
            else:
                # Not a Ren'Py project, create standard structure
                lang_dir = output_base_dir / language_code
                self.logger.info(f"Creating standard translation structure: {lang_dir}")
        else:
            # Create language directory
            lang_dir = output_base_dir / language_code
        
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        # CRITICAL FIX: Create ONE translation file for all strings
        # This prevents duplicate string errors in Ren'Py
        
        # Global deduplication - remove EXACT duplicates only
        # NOTE: Case-sensitive! "Cafeteria" and "cafeteria" are DIFFERENT strings in Ren'Py
        seen_strings = set()
        unique_results = []
        
        for result in translation_results:
            # Case-sensitive key - Ren'Py treats "Cafeteria" and "cafeteria" as different strings
            string_key = result.original_text.strip()
            if string_key not in seen_strings:
                seen_strings.add(string_key)
                unique_results.append(result)
            else:
                self.logger.debug(f"Skipping duplicate string: {result.original_text[:50]}...")
        
        # Create single master translation file
        # Use 'strings.rpy' for Ren'Py compatibility (same as _run_translate_command)
        output_filename = f"strings.rpy"
        output_path = lang_dir / output_filename
        
        if self.save_translation_file(
            unique_results, 
            output_path, 
            language_code, 
            None,  # No specific source file
            output_format=output_format
        ):
            output_files.append(output_path)
            self.logger.info(f"Created master translation file: {output_path} with {len(unique_results)} unique strings")
        
        return output_files
    
    def _find_game_directory(self, base_path: Path) -> Path:
        """Find the game directory in a Ren'Py project."""
        # Check current directory and parent directories for 'game' folder
        current = Path(base_path).resolve()
        
        # Check if current path contains 'game' folder
        if (current / "game").exists() and (current / "game").is_dir():
            return current / "game"
        
        # Check parent directories
        for parent in current.parents:
            game_dir = parent / "game"
            if game_dir.exists() and game_dir.is_dir():
                # Verify it's a Ren'Py game directory by checking for common files
                if any((game_dir / file).exists() for file in ["options.rpy", "script.rpy", "gui.rpy"]):
                    return game_dir
        
        # Check if current directory itself is the game directory
        if any((current / file).exists() for file in ["options.rpy", "script.rpy", "gui.rpy"]):
            return current
        
        return None
    
    def _create_language_init_file(self, game_dir: Path, language_code: str):
        """RenPy dökümantasyonuna tam uyumlu, sade başlatıcı dosya üretimi."""
        try:
            init_file_path = game_dir / f"a0_{language_code}_language.rpy"
            init_content = f'define config.language = "{language_code}"\n'
            with open(init_file_path, 'w', encoding='utf-8-sig', newline='\n') as f:
                f.write(init_content)
            self.logger.info(f"Created minimal language file: {init_file_path}")
            
            # Also create date translations file
            self._create_date_translations_file(game_dir, language_code)
        except Exception as e:
            self.logger.error(f"Error creating language init file: {e}")
    
    def _create_date_translations_file(self, game_dir: Path, language_code: str):
        """Create common.rpy with date/time translations for the target language."""
        try:
            # Check if we have translations for this language
            if language_code not in DATE_TRANSLATIONS:
                self.logger.info(f"No date translations available for {language_code}, skipping")
                return
            
            tl_dir = game_dir / "tl" / language_code
            tl_dir.mkdir(parents=True, exist_ok=True)
            
            common_file = tl_dir / "common.rpy"
            
            # Don't overwrite if file already exists
            if common_file.exists():
                self.logger.info(f"Date translations file already exists: {common_file}")
                return
            
            trans = DATE_TRANSLATIONS[language_code]
            
            lines = [
                f"# {language_code.title()} translations for Ren'Py common strings",
                "# Auto-generated by RenLocalizer - Date and time formatting",
                "",
                f"translate {language_code} strings:",
                "",
                "    # Weekday names (full)",
            ]
            
            # Weekdays
            for i, (eng, loc) in enumerate(zip(ENGLISH_WEEKDAYS, trans["weekdays"])):
                lines.append(f'    old "{{#weekday}}{eng}"')
                lines.append(f'    new "{{#weekday}}{loc}"')
                lines.append("")
            
            lines.append("    # Weekday names (short)")
            for eng, loc in zip(ENGLISH_WEEKDAYS_SHORT, trans["weekdays_short"]):
                lines.append(f'    old "{{#weekday_short}}{eng}"')
                lines.append(f'    new "{{#weekday_short}}{loc}"')
                lines.append("")
            
            lines.append("    # Month names (full)")
            for eng, loc in zip(ENGLISH_MONTHS, trans["months"]):
                lines.append(f'    old "{{#month}}{eng}"')
                lines.append(f'    new "{{#month}}{loc}"')
                lines.append("")
            
            lines.append("    # Month names (short)")
            for eng, loc in zip(ENGLISH_MONTHS_SHORT, trans["months_short"]):
                lines.append(f'    old "{{#month_short}}{eng}"')
                lines.append(f'    new "{{#month_short}}{loc}"')
                lines.append("")
            
            # Only date-specific translations with special tags are included
            # Other strings like file_time may already exist in strings.rpy
            
            content = "\n".join(lines)
            
            with open(common_file, 'w', encoding='utf-8-sig', newline='\n') as f:
                f.write(content)
            
            self.logger.info(f"Created date translations file: {common_file}")
            
        except Exception as e:
            self.logger.error(f"Error creating date translations file: {e}")
