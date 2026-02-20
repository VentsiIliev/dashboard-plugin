# Dashboard Localization Guide

## Overview

The generic dashboard uses **PyQt6's built-in translation system** (`QTranslator`) for internationalization (i18n) and localization (l10n).

**Location**: `src/dashboard/localization/`

## Quick Start

### 1. Basic Usage in Your Application

```python
from PyQt6.QtWidgets import QApplication
from dashboard.localization import TranslationManager, Language

app = QApplication([])

# Initialize translation manager
translation_manager = TranslationManager(app)

# Load German translation
translation_manager.load_language(Language.GERMAN)

# Your dashboard code here...
app.exec()
```

### 2. Using Translations in Widgets

```python
from dashboard.localization import tr

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Use tr() function for translatable strings
        self.start_button = QPushButton(tr("Start"))
        self.stop_button = QPushButton(tr("Stop"))
        self.status_label = QLabel(tr("Ready"))
        
    def changeEvent(self, event):
        """Handle language change events."""
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
    
    def retranslateUi(self):
        """Update UI text when language changes."""
        self.start_button.setText(tr("Start"))
        self.stop_button.setText(tr("Stop"))
        self.status_label.setText(tr("Ready"))
```

## Translation Workflow

### Step 1: Mark Translatable Strings

Use `tr()` function for all user-visible text:

```python
from dashboard.localization import tr

# Simple translation
button.setText(tr("Start"))

# Translation with context
label.setText(tr("Ready", "StatusMessages"))
```

### Step 2: Create Translation Files

Translation files use Qt's `.ts` XML format:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="de">
<context>
    <name>DashboardWidget</name>
    <message>
        <source>Start</source>
        <translation>Starten</translation>
    </message>
    <message>
        <source>Stop</source>
        <translation>Stoppen</translation>
    </message>
</context>
</TS>
```

**File naming convention**: `dashboard_{language_code}.ts`
- `dashboard_de.ts` - German
- `dashboard_fr.ts` - French
- `dashboard_es.ts` - Spanish
- `dashboard_zh.ts` - Chinese

### Step 3: Compile Translations

Compile `.ts` (source) to `.qm` (compiled binary):

```bash
# Option 1: Use the helper script
python src/dashboard/localization/compile_translations.py

# Option 2: Manual compilation
lrelease dashboard_de.ts -qm dashboard_de.qm
```

**Installation of lrelease**:
```bash
# Ubuntu/Debian
sudo apt install qt6-tools-dev

# macOS
brew install qt6

# Or use PySide6
pip install PySide6
```

### Step 4: Use Translations

```python
from dashboard.localization import TranslationManager, Language

translation_manager = TranslationManager(app)
translation_manager.load_language(Language.GERMAN)
```

## API Reference

### Language Enum

```python
from dashboard.localization import Language

Language.ENGLISH   # ("en", "English")
Language.GERMAN    # ("de", "Deutsch")
Language.FRENCH    # ("fr", "Français")
Language.SPANISH   # ("es", "Español")
Language.CHINESE   # ("zh", "中文")

# Get from code
lang = Language.from_code("de")  # Returns Language.GERMAN

# Detect system language
lang = Language.get_system_language()
```

### TranslationManager Class

```python
manager = TranslationManager(app, translations_dir=Path("./translations"))

# Load a language
manager.load_language(Language.GERMAN)

# Get current language
current = manager.current_language

# Get available languages (with .qm files)
languages = manager.get_available_languages()

# Create template file for new translations
template = manager.create_translation_template()
```

### Translation Function

```python
from dashboard.localization import tr

# Basic usage (default context: "DashboardWidget")
text = tr("Start")

# With custom context
text = tr("Ready", "StatusMessages")
text = tr("Error", "ValidationMessages")
```

## Directory Structure

```
src/dashboard/localization/
├── __init__.py                      # Language enum, TranslationManager, tr()
├── compile_translations.py          # Helper script to compile .ts → .qm
└── translations/
    ├── dashboard_de.ts              # German source
    ├── dashboard_de.qm              # German compiled (generated)
    ├── dashboard_fr.ts              # French source
    ├── dashboard_fr.qm              # French compiled (generated)
    └── dashboard_template.ts        # Template for new languages
```

## Complete Example

### Example 1: Simple Dashboard with Language Switcher

```python
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QVBoxLayout, QWidget
from dashboard.localization import TranslationManager, Language, tr
from dashboard.ui.DashboardWidget import DashboardWidget

app = QApplication([])

# Initialize translation manager
translation_manager = TranslationManager(app)

# Create window
window = QMainWindow()
widget = QWidget()
layout = QVBoxLayout(widget)

# Language selector
language_selector = QComboBox()
for lang in translation_manager.get_available_languages():
    language_selector.addItem(lang.native_name, lang)
language_selector.currentIndexChanged.connect(
    lambda: translation_manager.load_language(
        language_selector.currentData()
    )
)

layout.addWidget(language_selector)

# Dashboard
dashboard = DashboardWidget()
layout.addWidget(dashboard)

window.setCentralWidget(widget)
window.show()

app.exec()
```

### Example 2: Auto-detect System Language

```python
from dashboard.localization import TranslationManager, Language

app = QApplication([])
translation_manager = TranslationManager(app)

# Auto-load system language
system_lang = Language.get_system_language()
print(f"Detected system language: {system_lang.native_name}")
translation_manager.load_language(system_lang)

# Continue with app...
```

## Creating New Translations

### 1. Generate Template

```python
from dashboard.localization import TranslationManager

manager = TranslationManager(app)
template = manager.create_translation_template()
print(f"Template created: {template}")
```

### 2. Copy and Translate

```bash
cd src/dashboard/localization/translations/
cp dashboard_template.ts dashboard_ja.ts  # Japanese
# Edit dashboard_ja.ts, replace translations
```

### 3. Compile

```bash
python ../compile_translations.py
```

### 4. Add to Language Enum

Edit `src/dashboard/localization/__init__.py`:

```python
class Language(Enum):
    # ...existing languages...
    JAPANESE = ("ja", "日本語")
```

## Qt Linguist (Optional)

For advanced translation work, use **Qt Linguist** GUI tool:

```bash
# Ubuntu/Debian
sudo apt install qttools5-dev-tools

# Open translation file
linguist dashboard_de.ts
```

Qt Linguist provides:
- Context-aware translation
- Plural form handling
- Translation memory
- Validation warnings

## Best Practices

1. **Always use `tr()` for user-visible text**
   ```python
   ✓ button.setText(tr("Start"))
   ✗ button.setText("Start")
   ```

2. **Use meaningful contexts**
   ```python
   tr("Ready", "StatusMessages")  # Context helps translators
   ```

3. **Implement `retranslateUi()` in custom widgets**
   ```python
   def retranslateUi(self):
       self.button.setText(tr("Start"))
   ```

4. **Avoid string concatenation**
   ```python
   ✗ tr("You have") + f" {count} " + tr("items")
   ✓ tr("You have %n item(s)", "", count)
   ```

5. **Keep translation files in version control**
   - Commit `.ts` files (source)
   - Add `.qm` files to `.gitignore` (generated)

## Troubleshooting

### Translations not loading

```python
# Check available languages
print(translation_manager.get_available_languages())

# Verify .qm files exist
ls src/dashboard/localization/translations/*.qm
```

### Text not updating

1. Ensure widget implements `changeEvent()` and `retranslateUi()`
2. Check that `tr()` is called, not hardcoded strings
3. Verify .qm file is compiled and in translations directory

### lrelease not found

```bash
# Install Qt tools
sudo apt install qt6-tools-dev  # Ubuntu/Debian

# Or use PySide6
pip install PySide6
```

## Integration with Dashboard Config

Add language support to `DashboardConfig`:

```python
@dataclass
class DashboardConfig:
    # ...existing fields...
    default_language: Language = Language.ENGLISH
```

Then in your application:

```python
config = DashboardConfig(default_language=Language.GERMAN)
translation_manager.load_language(config.default_language)
```

## Summary

✅ **PyQt6 native** - Uses QTranslator, no external dependencies  
✅ **Standard workflow** - Qt's `.ts`/`.qm` format  
✅ **Easy to use** - Simple `tr()` function wrapper  
✅ **Runtime switching** - Change language without restart  
✅ **Auto-detection** - Can detect system language  
✅ **Extensible** - Easy to add new languages  
✅ **Tool support** - Qt Linguist for professional translation  

The localization system is production-ready and follows Qt best practices! 🌍

