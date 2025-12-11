# Actions Immédiates - Dette Technique eos-downloader
**Date**: 11 décembre 2025  
**Priorité**: CRITIQUE  
**Document parent**: [technical-debt-analysis-dec-2025.md](technical-debt-analysis-dec-2025.md)

---

## 🚀 Quick Start - Actions à Faire Maintenant

Ce document liste les **actions concrètes et immédiates** pour commencer la remédiation de la dette technique. Toutes ces tâches peuvent être réalisées **cette semaine**.

---

## ✅ Tâche 1: Support Python 3.12 (⏱️ 2 heures)

### Objectif
Ajouter le support officiel de Python 3.12 au projet.

### Actions
```bash
# 1. Éditer le fichier de configuration
nano .github/python-versions.json

# Modifier pour inclure Python 3.12:
{
  "versions": ["3.9", "3.10", "3.11", "3.12", "3.13"],
  "uv_version": "latest"
}

# 2. Synchroniser avec pyproject.toml
uv run python .github/scripts/sync-python-versions.py

# 3. Vérifier que tout est correct
git diff pyproject.toml

# 4. Commit et push
git add .github/python-versions.json pyproject.toml
git commit -m "feat: Add Python 3.12 support"
git push
```

### Validation
- [ ] CI GitHub Actions teste Python 3.12
- [ ] Tous les tests passent pour Python 3.12
- [ ] pyproject.toml inclut Python 3.12 dans classifiers

### Issue GitHub à créer
```markdown
**Title**: Add Python 3.12 support
**Labels**: enhancement, python
**Description**: 
The project currently supports Python 3.9, 3.10, 3.11, and 3.13 but is missing Python 3.12.

**Tasks**:
- [ ] Update `.github/python-versions.json`
- [ ] Run sync script
- [ ] Verify CI tests pass
- [ ] Update documentation if needed
```

---

## ✅ Tâche 2: Masquage des Tokens dans les Logs (⏱️ 3 heures)

### Objectif
Empêcher l'exposition accidentelle de tokens Arista dans les logs.

### Actions

#### Étape 1: Créer le module de sécurité
```bash
# Créer le fichier
touch eos_downloader/helpers/security.py
```

**Contenu de `eos_downloader/helpers/security.py`**:
```python
#!/usr/bin/env python
# coding: utf-8 -*-
"""Security utilities for handling sensitive data."""

from typing import Optional


def mask_token(token: Optional[str], show_chars: int = 4) -> str:
    """
    Mask a token for safe logging.
    
    Parameters
    ----------
    token : Optional[str]
        The token to mask
    show_chars : int, optional
        Number of characters to show at start and end, by default 4
        
    Returns
    -------
    str
        Masked token in format: "abcd...wxyz"
        
    Examples
    --------
    >>> mask_token("abcdefghijklmnopqrstuvwxyz")
    'abcd...wxyz'
    >>> mask_token("")
    '***'
    >>> mask_token(None)
    '***'
    """
    if not token or len(token) < show_chars * 2:
        return "***"
    
    return f"{token[:show_chars]}...{token[-show_chars:]}"


def validate_arista_token(token: Optional[str]) -> bool:
    """
    Validate Arista token format.
    
    Parameters
    ----------
    token : Optional[str]
        Token to validate
        
    Returns
    -------
    bool
        True if token is valid
        
    Raises
    ------
    ValueError
        If token is invalid
    """
    if not token:
        raise ValueError("Token cannot be empty")
    
    if len(token) < 20:
        raise ValueError(
            "Token too short. Arista tokens are typically longer than 20 characters."
        )
    
    return True
```

#### Étape 2: Créer les tests
```bash
touch tests/unit/helpers/test_security.py
```

**Contenu de `tests/unit/helpers/test_security.py`**:
```python
"""Tests for security utilities."""

import pytest
from eos_downloader.helpers.security import mask_token, validate_arista_token


class TestTokenMasking:
    """Test token masking functionality."""
    
    def test_mask_long_token(self):
        """Test masking a long token."""
        token = "abcdefghijklmnopqrstuvwxyz0123456789"
        masked = mask_token(token)
        
        assert "abcd" in masked
        assert "6789" in masked
        assert "..." in masked
        assert len(masked) < len(token)
    
    def test_mask_empty_token(self):
        """Test masking an empty token."""
        assert mask_token("") == "***"
        assert mask_token(None) == "***"
    
    def test_mask_short_token(self):
        """Test masking a very short token."""
        assert mask_token("abc") == "***"
    
    def test_custom_show_chars(self):
        """Test masking with custom number of visible chars."""
        token = "abcdefghijklmnop"
        masked = mask_token(token, show_chars=2)
        
        assert "ab" in masked
        assert "op" in masked


class TestTokenValidation:
    """Test token validation."""
    
    def test_valid_token(self):
        """Test validation of a valid token."""
        token = "a" * 25  # Token long enough
        assert validate_arista_token(token) is True
    
    def test_empty_token(self):
        """Test validation of empty token."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_arista_token("")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_arista_token(None)
    
    def test_short_token(self):
        """Test validation of too short token."""
        with pytest.raises(ValueError, match="too short"):
            validate_arista_token("short")
```

#### Étape 3: Utiliser dans le code existant

**Modifier `eos_downloader/cli/cli.py`**:
```python
# Ajouter l'import
from eos_downloader.helpers.security import mask_token, validate_arista_token

# Dans la fonction ardl()
@click.option("--token", ...)
def ardl(ctx: click.Context, token: str, log_level: str, debug_enabled: bool) -> None:
    """Arista Network Download CLI"""
    
    # Valider et masquer le token
    if token:
        try:
            validate_arista_token(token)
            logger.info(f"Using token: {mask_token(token)}")
            
            # Warning si token passé en CLI au lieu de variable d'environnement
            if not os.environ.get('ARISTA_TOKEN'):
                logger.warning(
                    "⚠️  Token passed via CLI is less secure. "
                    "Consider using ARISTA_TOKEN environment variable."
                )
        except ValueError as e:
            logger.error(f"Invalid token: {e}")
            sys.exit(1)
```

### Validation
```bash
# Exécuter les tests
pytest tests/unit/helpers/test_security.py -v

# Vérifier que le token est masqué dans les logs
ardl --token "test_token_1234567890" info eos --debug 2>&1 | grep -i token
# Devrait afficher: "test...7890" et non le token complet
```

### Issue GitHub à créer
```markdown
**Title**: Implement token masking for secure logging
**Labels**: security, enhancement
**Description**: 
Prevent accidental exposure of Arista API tokens in logs and terminal output.

**Security Impact**: Medium - prevents credential leakage

**Tasks**:
- [ ] Create `helpers/security.py` with masking utilities
- [ ] Add comprehensive tests
- [ ] Update CLI to use token masking
- [ ] Add warning for CLI token usage
- [ ] Document best practices in security guide
```

---

## ✅ Tâche 3: Pre-commit Hook detect-secrets (⏱️ 1 heure)

### Objectif
Empêcher les commits de secrets accidentels.

### Actions

#### Étape 1: Installer detect-secrets
```bash
uv pip install detect-secrets
```

#### Étape 2: Créer baseline
```bash
# Scanner le projet et créer baseline
detect-secrets scan > .secrets.baseline

# Auditer les secrets détectés
detect-secrets audit .secrets.baseline
```

#### Étape 3: Configurer pre-commit
**Modifier `.pre-commit-config.yaml`**:
```yaml
# Ajouter à la fin du fichier
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
      exclude: package.lock.json
```

#### Étape 4: Installer le hook
```bash
pre-commit install
```

### Validation
```bash
# Tester le hook
echo "api_key = 'sk-test123456789'" > test_secret.py
git add test_secret.py
git commit -m "test"  # Devrait échouer

# Nettoyer
rm test_secret.py
```

### Issue GitHub à créer
```markdown
**Title**: Add detect-secrets pre-commit hook
**Labels**: security, devops
**Description**: 
Prevent accidental commits of secrets and credentials.

**Tasks**:
- [ ] Install detect-secrets
- [ ] Create secrets baseline
- [ ] Configure pre-commit hook
- [ ] Update contributing guide
- [ ] Add to CI pipeline
```

---

## ✅ Tâche 4: Nettoyer __pycache__ (⏱️ 30 minutes)

### Objectif
S'assurer qu'aucun fichier `__pycache__` n'est tracké dans git.

### Actions

#### Étape 1: Vérifier
```bash
# Vérifier si des __pycache__ sont trackés
git ls-files | grep __pycache__
```

#### Étape 2: Nettoyer (si nécessaire)
```bash
# Si des fichiers sont trouvés, les retirer
find . -type d -name __pycache__ -exec git rm -r --cached {} + 2>/dev/null

# Commit le changement
git commit -m "chore: Remove __pycache__ directories from git tracking"
```

#### Étape 3: Ajouter commande Makefile
**Modifier `Makefile`**:
```makefile
.PHONY: clean-pycache
clean-pycache: ## Clean all __pycache__ directories and .pyc files
	@echo "Cleaning Python cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✓ Python cache cleaned"

.PHONY: clean-all
clean-all: clean clean-pycache ## Clean everything (build artifacts + cache)
	@echo "✓ All cleaned"
```

#### Étape 4: Vérifier .gitignore
**Vérifier que `.gitignore` contient**:
```gitignore
# Python cache
__pycache__/
*.py[cod]
*$py.class
*.pyc
*.pyo
```

### Validation
```bash
# Aucun __pycache__ ne devrait être listé
git ls-files | grep __pycache__ || echo "✓ Clean"

# Tester la commande make
make clean-pycache
```

---

## ✅ Tâche 5: Créer Module de Configuration Logging Centralisé (⏱️ 2 heures)

### Objectif
Centraliser la configuration du logging pour faciliter la migration vers loguru.

### Actions

#### Étape 1: Créer le module
```bash
touch eos_downloader/logging_config.py
```

**Contenu de `eos_downloader/logging_config.py`**:
```python
#!/usr/bin/env python
# coding: utf-8 -*-
"""
Centralized logging configuration for eos-downloader.

This module provides a unified logging interface using loguru.
All modules should import and use the logger from this module.
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger


def configure_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    rotation: str = "10 MB",
) -> None:
    """
    Configure global logging settings.
    
    Parameters
    ----------
    level : str, optional
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL), by default "INFO"
    log_file : Optional[Path], optional
        Path to log file, by default None (console only)
    rotation : str, optional
        Log file rotation size, by default "10 MB"
        
    Examples
    --------
    >>> configure_logging(level="DEBUG")
    >>> configure_logging(level="INFO", log_file=Path("app.log"))
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler with formatting
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )
    
    # Add file handler if specified
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
            rotation=rotation,
            retention="1 week",
            compression="zip",
        )
    
    logger.info(f"Logging configured at level: {level}")


# Export logger for use in other modules
__all__ = ["logger", "configure_logging"]
```

#### Étape 2: Créer les tests
```bash
touch tests/unit/test_logging_config.py
```

**Contenu de `tests/unit/test_logging_config.py`**:
```python
"""Tests for logging configuration."""

import pytest
from pathlib import Path
from eos_downloader.logging_config import logger, configure_logging


class TestLoggingConfiguration:
    """Test logging configuration."""
    
    def test_logger_available(self):
        """Test that logger is available."""
        assert logger is not None
    
    def test_configure_basic(self):
        """Test basic logging configuration."""
        configure_logging(level="INFO")
        # Should not raise
    
    def test_configure_with_file(self, tmp_path):
        """Test logging configuration with file output."""
        log_file = tmp_path / "test.log"
        configure_logging(level="DEBUG", log_file=log_file)
        
        logger.info("Test message")
        
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content
    
    def test_different_levels(self):
        """Test different logging levels."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            configure_logging(level=level)
            # Should not raise
```

#### Étape 3: Migration plan pour modules existants
**Créer `.github/plans/logging-migration-checklist.md`**:
```markdown
# Migration Logging vers Configuration Centralisée

## Modules à Migrer

- [ ] eos_downloader/models/version.py
- [ ] eos_downloader/logics/arista_server.py
- [ ] eos_downloader/logics/arista_xml_server.py
- [ ] eos_downloader/logics/download.py
- [ ] eos_downloader/cli/utils.py

## Pattern de Migration

### Avant
```python
import logging
logging.debug("message")
```

### Après
```python
from eos_downloader.logging_config import logger
logger.debug("message")
```

## Validation
- [ ] Tous les tests passent
- [ ] Logs sont cohérents
- [ ] Aucun import de `logging` standard restant
```

### Validation
```bash
# Exécuter les tests
pytest tests/unit/test_logging_config.py -v

# Tester l'import
python -c "from eos_downloader.logging_config import logger; logger.info('Test')"
```

---

## 📋 Checklist Complète

Marquer chaque tâche une fois terminée:

### Cette Semaine
- [ ] Tâche 1: Support Python 3.12 (2h)
- [ ] Tâche 2: Masquage tokens (3h)
- [ ] Tâche 3: detect-secrets (1h)
- [ ] Tâche 4: Nettoyer __pycache__ (30min)
- [ ] Tâche 5: Module logging centralisé (2h)

### Validation Globale
- [ ] Tous les tests passent: `pytest`
- [ ] Linting OK: `make lint`
- [ ] Type checking OK: `make type`
- [ ] CI GitHub Actions passe
- [ ] Documentation mise à jour

---

## 🎯 Après Ces Actions

Une fois ces 5 tâches terminées, vous aurez:

✅ **+5% de couverture** (nouvelles fonctionnalités testées)  
✅ **Sécurité renforcée** (tokens masqués, detect-secrets)  
✅ **Support étendu** (Python 3.12)  
✅ **Base propre** (pas de cache git)  
✅ **Architecture améliorée** (logging centralisé)  

**Temps total estimé**: ~9 heures (1-2 jours)  
**Impact**: 🔴 Élevé - Fondations solides pour la suite

---

## 📞 Support

**Questions?** Ouvrir une discussion GitHub  
**Bugs?** Créer une issue avec label `technical-debt`  
**Document parent**: [technical-debt-analysis-dec-2025.md](technical-debt-analysis-dec-2025.md)

---

**Créé**: 11 décembre 2025  
**Status**: 🔄 Actions en attente
