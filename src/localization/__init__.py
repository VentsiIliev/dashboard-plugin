"""
Reusable localization support using PyQt6's QTranslator.

Can be used by any dashboard or plugin — just point TranslationManager
at the directory containing your language subdirectories.

Usage:
    from localization import TranslationManager, Language

    manager = TranslationManager(app, translations_dir=Path("my_plugin/translations"))
    manager.load_language(Language("de", "Deutsch"))

    # Or let the manager discover what's available from the filesystem:
    for lang in manager.get_available_languages():
        print(lang.code, lang.native_name)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from PyQt6.QtCore import QTranslator, QCoreApplication, QLocale


# Native display names for well-known language codes.
# Add entries here to get a proper name for new languages;
# unknown codes fall back to the uppercased code (e.g. "JA").
_NATIVE_NAMES: dict[str, str] = {
    "en": "English",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
    "it": "Italiano",
    "pt": "Português",
    "nl": "Nederlands",
    "pl": "Polski",
    "ru": "Русский",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "ar": "العربية",
}

ENGLISH = None  # set below after class definition


@dataclass(frozen=True)
class Language:
    """A language identified by its ISO 639-1 code."""
    code: str
    native_name: str

    @classmethod
    def from_code(cls, code: str) -> "Language":
        return cls(code=code, native_name=_NATIVE_NAMES.get(code, code.upper()))

    @classmethod
    def get_system_language(cls) -> "Language":
        """Detect system language, fallback to English."""
        code = QLocale.system().name()[:2]
        return cls.from_code(code)


ENGLISH = Language("en", "English")


class TranslationManager:
    """
    Manages a QTranslator for one translations directory.

    Directory layout expected:
        translations/
            de/
                <prefix>_de.qm
            fr/
                <prefix>_fr.qm
            ...

    Available languages are discovered from the filesystem — no code
    change needed when a new language folder is added.

    Multiple instances can be active simultaneously (one per plugin).
    Qt searches all installed translators for each translate() call.

    Args:
        app:              QApplication instance.
        translations_dir: Root directory containing per-language subdirs.
        file_prefix:      Prefix for .qm filenames (e.g. "glue" → "glue_de.qm").
    """

    def __init__(
        self,
        app: QCoreApplication,
        translations_dir: Optional[Path] = None,
        file_prefix: str = "translations",
    ):
        self.app = app
        self.translations_dir = translations_dir or Path(__file__).parent / "translations"
        self.file_prefix = file_prefix
        self.current_language: Language = ENGLISH
        self._translator: Optional[QTranslator] = None

    # ------------------------------------------------------------------ #

    def _qm_path(self, language: Language) -> Path:
        return (
            self.translations_dir
            / language.code
            / f"{self.file_prefix}_{language.code}.qm"
        )

    def get_available_languages(self) -> List[Language]:
        """
        Discover available languages by scanning the translations directory.

        A language is available when its subdirectory contains a compiled
        .qm file.  English is always included as the source language.
        """
        available = [ENGLISH]

        if not self.translations_dir.is_dir():
            return available

        for subdir in sorted(self.translations_dir.iterdir()):
            if not subdir.is_dir() or subdir.name == "en":
                continue
            qm = subdir / f"{self.file_prefix}_{subdir.name}.qm"
            if qm.exists():
                available.append(Language.from_code(subdir.name))

        return available

    def load_language(self, language: Language) -> bool:
        """
        Load the .qm file for *language* and install it in the app.

        Returns True on success.  English always succeeds (source language,
        no .qm file required).
        """
        if self._translator:
            self.app.removeTranslator(self._translator)
            self._translator = None

        if language.code == "en":
            self.current_language = ENGLISH
            return True

        qm_file = self._qm_path(language)

        if not qm_file.exists():
            print(f"[TranslationManager] file not found: {qm_file}")
            return False

        translator = QTranslator(self.app)
        if not translator.load(str(qm_file)):
            print(f"[TranslationManager] failed to load: {qm_file}")
            return False

        self.app.installTranslator(translator)
        self._translator = translator
        self.current_language = language
        print(f"[TranslationManager] loaded: {language.code}/{qm_file.name}")
        return True