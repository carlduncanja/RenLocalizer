# Release Notes

## Version 2.0.1 - RenPy Integration Update (2025-09-11)

### 🎯 New Features
- **RenPy-specific parsing**: Correctly handles conditional menu choices (`"choice" if condition:`)
- **Technical string filtering**: Automatically excludes color codes, font files, and performance metrics
- **Improved output format**: Each translation in separate `translate strings` blocks (RenPy standard)
- **Better language initialization**: Modern, compatible language setup for RenPy games
- **Enhanced encoding support**: Proper UTF-8 handling for international characters

### 🔧 Improvements
- **Parser accuracy**: More precise extraction of translatable content
- **Menu support**: Full support for RenPy menu choices and UI elements
- **Error handling**: Better error messages and recovery mechanisms
- **Performance**: Optimized translation processing and memory usage
- **Code quality**: Refactored core components for better maintainability

### 🐛 Bug Fixes
- Fixed multi-line string parsing issues
- Resolved character encoding problems
- Corrected RenPy cache handling
- Fixed conditional menu choice extraction
- Improved placeholder preservation in translations

### 📦 Dependencies
- Updated to support Python 3.8+
- Improved compatibility with modern PyQt6/PySide6
- Better proxy handling with aiohttp

### 🚀 Technical Changes
- Rewritten parser engine for better accuracy
- Improved output formatter with RenPy compliance
- Enhanced error logging and debugging capabilities
- Better separation of concerns in codebase architecture

### 📋 Known Issues
- DeepL API integration needs testing with various key types
- Some very long texts might need chunking for certain engines
- Proxy rotation could be more sophisticated

### 🔄 Migration Notes
- Config format is backward compatible
- Old translation files can be migrated using built-in tools
- No breaking changes for existing workflows

---

### 📊 Statistics
- **Lines of code**: ~3000+ (core functionality)
- **Supported formats**: .rpy files (RenPy visual novels)
- **Supported engines**: Google Translate, DeepL API
- **UI languages**: English, Turkish
- **Themes**: 4 professional themes available
- **Version**: 2.0.1

## Version 2.0.5 - 2025-09-15

### 🧹 Removal
- **Deep-Translator removed:** The experimental `Deep-Translator` multi-engine wrapper and its UI entry were removed for stability and maintainability. Please use supported engines (Google, DeepL, Yandex, LibreTranslator).

### 🧹 Removal: OPUS-MT (Argos Translate)
- **Removed OPUS-MT (Argos Translate):** All OPUS-MT / Argos Translate integration, model download UI, and related code paths have been removed due to instability and crashes observed in production. Offline model download/dialog features related to OPUS-MT were deleted, and references in UI/locales/docs were cleaned up.