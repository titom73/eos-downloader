# Interface graphique macOS native pour eos-downloader

> **Statut** : Proposition — à amender avant implémentation
> **Date** : 2026-02-24
> **Contexte** : Ce document décrit le plan pour créer une application macOS native qui expose les fonctionnalités de la CLI `ardl` dans une interface graphique. Cette option vient **en complément** de la CLI existante — aucun code Python n'est modifié.
> **Cible macOS** : 13.0 minimum (requis pour `NavigationSplitView`). Architecture : Universal Binary (arm64 + x86_64).

---

## Choix technologique : SwiftUI wrappant le CLI `ardl`

**Décision : Application SwiftUI qui shell-out vers `ardl`** et consomme sa sortie `--format json`.

### Évaluation des options

| Option | Verdict | Raison |
|---|---|---|
| **SwiftUI + `ardl` CLI** | ✅ Recommandé | Natif macOS, Keychain, notarisation triviale |
| Python + PyObjC/Toga | ❌ | Très verbeux, bugs backend macOS, maintenance lourde |
| Python + PyInstaller + tkinter | ❌ | `_tkinter` absent sur macOS 13+, bundles cassés aux MàJ |
| PySide6/PyQt6 | ❌ | Runtime Qt +100 MB, non-natif |
| Electron/Tauri | ❌ | Lourd, pas natif |

### Justification du choix SwiftUI

- Interface 100 % native (NavigationSplitView, Keychain, file picker)
- Le CLI expose déjà `--format json` → contrats JSON stables à consommer
- **Zéro modification du code Python existant**
- Séparation des responsabilités : Python gère la logique métier, Swift gère l'UI
- Packaging via PyInstaller `--onedir` (démarrage ~3× plus rapide que `--onefile`, qui extrait dans `/tmp` à chaque lancement)
- Distribution native via `.dmg` signé + notarisé

---

## Architecture de l'application

```
EosDownloaderApp (@main)
├── DownloadState (@Observable)        ← Bindings formulaires download (granulaire)
├── InfoState (@Observable)            ← Cache versions / formats
├── ContentView                        ← NavigationSplitView racine (@MainActor)
│   ├── SidebarView                    ← Navigation 4 sections
│   ├── DownloadView (TabView)
│   │   ├── EosDownloadView            ← get eos
│   │   ├── CvpDownloadView            ← get cvp
│   │   └── PathDownloadView           ← get path
│   ├── InfoView (TabView)
│   │   ├── VersionListView            ← info versions
│   │   ├── LatestVersionView          ← info latest
│   │   └── MappingView                ← info mapping
│   ├── SettingsView                   ← Token + préférences
│   └── DebugView                      ← debug xml
└── CLIRunner (actor)                  ← Process isolé, thread-safe
    ├── run(args:env:) async throws → CLIResult
    ├── stream(args:env:onLine:) async throws → AsyncStream
    └── cancel()                        ← Annulation téléchargements en cours
```

> **Note architecture** : Utiliser `@Observable` (Swift 5.9+, macOS 14) plutôt que `ObservableObject` pour éviter les re-renders globaux. Si macOS 13 doit être supporté, utiliser `ObservableObject` avec `@Published` par propriété pour limiter la propagation.

### Gestion des erreurs

Définir un enum `CLIError` exhaustif avant toute autre chose — c'est le contrat entre CLIRunner et les vues :

```swift
enum CLIError: LocalizedError {
    case binaryNotFound(searchedPaths: [String])
    case tokenMissing
    case tokenExpired                    // exit code 1 + message spécifique
    case networkUnavailable
    case processTerminated(exitCode: Int32, stderr: String)
    case outputDecodingFailed(raw: String, underlying: Error)
    case cancelled

    var errorDescription: String? { /* message user-friendly */ }
    var recoverySuggestion: String? { /* action corrective */ }
}
```

### Flux de données

```
Interaction utilisateur
  → Vue SwiftUI → Task { await state.perform() }
    → CLIRunner.run(args: ["ardl", "info", "versions", "--format", "json"],
                    env: ["ARISTA_TOKEN": token])   ← TOKEN VIA ENV, pas --token
      → Process.launch() avec stdout pipe
        → stdout capturé / streamé ligne par ligne
          → JSON décodé en structs Swift Codable
            → @MainActor { state.versions = decoded } → re-render SwiftUI
              → en cas d'erreur → CLIError → AlertView
```

> **Sécurité critique** : Le token **ne doit jamais** être passé via `--token TOKEN` en argument CLI. Cette valeur est visible dans `ps aux`, les logs système et Activity Monitor. Le passer **exclusivement via la variable d'environnement `ARISTA_TOKEN`** que le CLI supporte déjà nativement (voir `defaults.py`). La commande devient `ardl info versions --format json` avec `env["ARISTA_TOKEN"] = token`.

---

## Contrats JSON existants (interfaces stables)

Ces commandes `ardl` émettent déjà du JSON — aucun changement nécessaire. Les structs Swift Codable correspondantes doivent être implémentées **dès la Phase 1** (nécessaires pour la validation du token) :

| Commande | Structure JSON | Struct Swift |
|---|---|---|
| `ardl info versions --format json` | `[{"version": "4.29.3M", "branch": "4.29", "rtype": "M"}, ...]` | `[VersionEntry]` |
| `ardl info latest --format json` | `{"version": "4.29.3M"}` | `LatestVersion` |
| `ardl info mapping --format json` | `{"64": {"extension": ".swi", "prepend": "EOS64"}, ...}` | `[String: MappingEntry]` |

```swift
// à placer dans Models/
struct VersionEntry: Codable, Identifiable {
    var id: String { version }
    let version: String
    let branch: String
    let rtype: String?      // optionnel : certaines réponses peuvent l'omettre
}

struct LatestVersion: Codable {
    let version: String
}

struct MappingEntry: Codable {
    let extension: String   // "extension" est un mot réservé Swift
    let prepend: String     // utiliser CodingKeys pour le mapping
}
```

> **Stratégie de stabilité des contrats** : Ajouter un test Python dans `tests/unit/cli/` qui vérifie que `ardl info versions --format json` produit du JSON parsable avec les champs attendus. Ce test échoue si un refactor Python casse le contrat JSON, protégeant l'app Swift sans écrire de Swift.

Les commandes `get` (download) streament stdout/stderr ligne par ligne. Règles de parsing côté Swift :
- Stripping ANSI : `line.replacingOccurrences(of: #"\x1B\[[0-9;]*[mGKHF]"#, with: "", options: .regularExpression)`
- Une ligne vide en fin de stream indique la fin normale
- Exit code non-zéro → lève `CLIError.processTerminated(exitCode:stderr:)`

---

## Mapping CLI → Interface graphique

### Section Download > EOS (`get eos`)

| Option CLI | Élément UI | Valeur par défaut |
|---|---|---|
| `ARISTA_TOKEN` (env) | Depuis Keychain (Settings), injecté via `env` — jamais via `--token` | — |
| `--format` | Dropdown | `vEOS-lab` |
| `--version` | Champ texte | — |
| `--latest` | Toggle | off |
| `--branch` | Champ texte | — |
| `--release-type` | Dropdown (M/F) | `F` |
| `--output` | Champ + browser | `~/Downloads` |
| `--import-docker` | Checkbox | off |
| `--docker-name` | Champ (visible si docker coché) | `arista/ceos` |
| `--docker-tag` | Champ (visible si docker coché) | `latest` |
| `--eve-ng` | Checkbox (grisé si non EVE-NG) | off |
| `--dry-run` | Checkbox | off |
| `--force` | Checkbox | off |

### Section Download > CVP (`get cvp`)

| Option CLI | Élément UI | Valeur par défaut |
|---|---|---|
| `--format` | Dropdown (ova/rpm/kvm/upgrade) | `ova` |
| `--version` | Champ texte | — |
| `--latest` | Toggle | off |
| `--branch` | Champ texte | — |
| `--output` | Champ + browser | `~/Downloads` |
| `--dry-run` | Checkbox | off |
| `--force` | Checkbox | off |

### Section Download > Path (`get path`)

| Option CLI | Élément UI | Valeur par défaut |
|---|---|---|
| `--source` | Champ texte (requis) | — |
| `--output` | Champ + browser | `~/Downloads` |
| `--import-docker` | Checkbox | off |
| `--docker-name` | Champ | `arista/ceos:raw` |
| `--docker-tag` | Champ | `dev` |
| `--force` | Checkbox | off |

### Section Info

| Onglet | Commande CLI | Fonctionnalités UI |
|---|---|---|
| Versions | `info versions` | Tableau filtrable (package/branch/type), bouton "Use in Download" |
| Latest | `info latest` | Affichage version la plus récente, bouton copy |
| Mapping | `info mapping` | Liste des formats disponibles avec détails |

### Section Settings

- Token Arista (stocké dans Keychain, jamais affiché en clair, jamais passé en arg CLI)
- Bouton "Valider le token" (appelle `ardl info latest --format json` via `env["ARISTA_TOKEN"]`)
- Dossier de sortie par défaut (persisté via `@AppStorage`, pas `UserDefaults` manuel)
- Niveau de log (`ARDL_LOG_LEVEL`)
- Chemin vers `ardl` (bundlé ou custom via champ texte + sélecteur de fichier)

### Section Debug (`debug xml`)

- Champ chemin de sortie (défaut : `arista.xml`)
- Bouton "Download XML"
- Log output

---

## Structure des fichiers (nouveau répertoire `gui/`)

```
gui/
├── EosDownloaderApp/
│   ├── EosDownloaderApp.xcodeproj/
│   └── EosDownloaderApp/
│       ├── App/
│       │   └── EosDownloaderApp.swift      ← @main, MINIMUM_MACOS_VERSION = 13.0
│       ├── Views/
│       │   ├── ContentView.swift           ← NavigationSplitView racine
│       │   ├── SidebarView.swift
│       │   ├── Download/
│       │   │   ├── DownloadView.swift
│       │   │   ├── EosDownloadView.swift
│       │   │   ├── CvpDownloadView.swift
│       │   │   └── PathDownloadView.swift
│       │   ├── Info/
│       │   │   ├── InfoView.swift
│       │   │   ├── VersionListView.swift
│       │   │   ├── LatestVersionView.swift
│       │   │   └── MappingView.swift
│       │   ├── Settings/
│       │   │   └── SettingsView.swift
│       │   ├── Debug/
│       │   │   └── DebugView.swift
│       │   └── Shared/
│       │       ├── LogOutputView.swift         ← Log ANSI stripped, scrollable
│       │       ├── ErrorAlertModifier.swift    ← ViewModifier centralisé pour CLIError
│       │       ├── FileBrowserButton.swift
│       │       └── ProgressBannerView.swift
│       ├── CLI/
│       │   ├── CLIRunner.swift              ← actor Process wrapper, async/await + cancel()
│       │   ├── CLIResult.swift              ← exitCode, stdout, stderr
│       │   ├── CLIError.swift               ← enum exhaustif, LocalizedError
│       │   └── CLIBinaryLocator.swift       ← cherche dans Contents/Resources/ puis PATH
│       ├── Keychain/
│       │   └── KeychainTokenManager.swift   ← Security framework, throws KeychainError
│       ├── Models/
│       │   ├── VersionEntry.swift
│       │   ├── LatestVersion.swift
│       │   └── MappingResponse.swift
│       ├── State/
│       │   ├── DownloadState.swift          ← @Observable, 1 instance par vue Download
│       │   └── InfoState.swift              ← @Observable, partagé entre vues Info
│       └── Resources/
│           └── ardl_bundle/                 ← répertoire onedir PyInstaller (NON commité en git)
└── scripts/
    └── build_ardl_binary.sh
```

**Aucun fichier Python n'est modifié.**

> **`.gitignore`** : Ajouter `gui/EosDownloaderApp/EosDownloaderApp/Resources/ardl_bundle/` — ce répertoire est généré par le script de build et ne doit pas être commité. Documenter dans le README GUI que le build du binaire est étape préalable obligatoire.

---

## Packaging

### Build du binaire `ardl`

```bash
#!/usr/bin/env bash
# gui/scripts/build_ardl_binary.sh
set -euo pipefail

DEST="gui/EosDownloaderApp/EosDownloaderApp/Resources/ardl_bundle"

uv sync --all-extras

# Build universel : arm64 (Apple Silicon) + x86_64 (Intel)
# --onedir est 3× plus rapide au lancement que --onefile (pas d'extraction /tmp)
uv run pyinstaller \
  --onedir \
  --name ardl \
  --hidden-import eos_downloader \
  --target-architecture universal2 \
  --osx-bundle-identifier com.arista.eos-downloader.cli \
  eos_downloader/cli/__main__.py

# Remplacer le bundle précédent
rm -rf "$DEST"
cp -r dist/ardl "$DEST"

echo "✅ ardl bundle prêt dans $DEST"
echo "   -> Test : $DEST/ardl info versions --help"
```

Le répertoire `--onedir` (~30 MB) est auto-contenu : Python + toutes dépendances inclus. Dans `CLIBinaryLocator.swift`, le binaire à lancer est `Contents/Resources/ardl_bundle/ardl` (pas un fichier unique).

### Makefile (nouvelle cible)

```makefile
.PHONY: gui-binary
gui-binary: ## Build le binaire ardl bundlable dans l'app macOS
	@bash gui/scripts/build_ardl_binary.sh
```

### Distribution

| Option | Recommandation |
|---|---|
| GitHub Releases | ✅ v1 — `.dmg` signé + notarisé |
| Homebrew Cask | ✅ v2 — `brew tap titom73/tap && brew install --cask eos-downloader` |
| Mac App Store | ❌ À éviter — l'App Sandbox interdit l'exécution de sous-processus arbitraires ; incompatible avec l'architecture CLI-runner |

---

## Sécurité du token

- Stocké dans le **Keychain macOS** (service: `"com.arista.eos-downloader"`, account: `"arista-api-token"`)
- **Jamais** écrit sur disque, jamais loggé, jamais affiché dans les logs CLI
- Injecté **exclusivement via variable d'environnement** : `process.environment["ARISTA_TOKEN"] = token` — le flag `--token` **ne doit pas être utilisé** (visible dans `ps aux` et les logs système Activity Monitor)
- Affiché masqué dans l'UI (champ `SecureField`)
- Erreur Keychain → `CLIError.tokenMissing` → redirection vers `SettingsView` avec alerte explicite

---

## Plan d'implémentation par phases

> **Règle générale** : Chaque phase doit se terminer par des tests manuels des critères d'acceptation avant de passer à la suivante. Ne pas commencer la Phase N+1 si Phase N est incomplète.

### Phase 1 — MVP (2–3 semaines)

**Objectif :** Téléchargement EOS fonctionnel de bout en bout

- [ ] `build_ardl_binary.sh` — script PyInstaller `--onedir` universal2, vérifier `ardl info versions --format json`
- [ ] `CLIBinaryLocator.swift` — cherche dans `Contents/Resources/ardl_bundle/` puis `PATH`
- [ ] `CLIError.swift` — enum exhaustif, à implémenter **avant** CLIRunner
- [ ] `CLIResult.swift` — exitCode, stdout, stderr
- [ ] `CLIRunner.swift` — `actor` Process wrapper, `run(args:env:)`, `stream(args:env:onLine:)`, `cancel()`
- [ ] Structs Codable `VersionEntry`, `LatestVersion`, `MappingEntry` — **nécessaires pour la validation du token en Phase 1**
- [ ] `KeychainTokenManager.swift` — lecture/écriture token Keychain, throws `CLIError.tokenMissing`
- [ ] `SettingsView.swift` — `SecureField` token, validation via `ardl info latest --format json` (env var, pas `--token`)
- [ ] `DownloadState.swift` — @Observable, formulaire EOS
- [ ] `EosDownloadView.swift` — format, version, chemin output, bouton Download, annulation
- [ ] `LogOutputView.swift` — zone scrollable ANSI stripped, tail automatique
- [ ] `ErrorAlertModifier.swift` — ViewModifier pour présenter `CLIError` via `Alert`
- [ ] `ContentView.swift` — NavigationSplitView (Download / Info / Settings / Debug)

**Critères d'acceptation :**

1. Token validé dans Settings sans exposer le token dans `ps aux`
2. Téléchargement EOS `vEOS-lab 4.29.3M` vers `/tmp` réussi, fichier présent
3. Log en temps réel visible, codes ANSI absents
4. Bouton "Annuler" interrompt proprement le process `ardl`
5. Erreur réseau → alerte claire avec suggestion de correction (pas de crash)

### Phase 2 — Navigateur de versions (1–2 semaines)

**Pré-requis :** Phase 1 validée. Les structs Codable sont déjà disponibles depuis Phase 1.

- [ ] `InfoState.swift` — fetch async `ardl info versions --format json`, cache en mémoire
- [ ] `VersionListView.swift` — tableau filtrable (package, branch, release type)
- [ ] `LatestVersionView.swift` — version la plus récente + bouton Copy
- [ ] `MappingView.swift` — formats depuis `ardl info mapping --format json`
- [ ] Bouton "Use in Download" → pré-remplit le formulaire EOS/CVP via binding sur `DownloadState`
- [ ] Ajout test Python `tests/unit/cli/test_json_contracts.py` — vérifie les structures JSON des commandes `info`

**Critères d'acceptation :**

1. Liste EOS branch 4.29 se charge en < 5 s
2. Filtre par release type M/F fonctionne
3. "Use in Download" pré-remplit correctement la vue EOS Download

### Phase 3 — Parité CLI complète (1–2 semaines)

**Pré-requis :** Phase 2 validée.

- [ ] `CvpDownloadView.swift` — formats CVP (ova/rpm/kvm/upgrade)
- [ ] `PathDownloadView.swift` — champ source direct + options Docker
- [ ] Options Docker dans `EosDownloadView` — docker-name, docker-tag, n'apparaissent que si toggle activé
- [ ] Toggle EVE-NG — avec tooltip explicatif ("Requires EVE-NG server access")
- [ ] Dry-run et force checkboxes sur toutes les vues Download
- [ ] `ProgressBannerView.swift` — spinner indéterminé + bouton Annuler pendant exécution
- [ ] `DebugView.swift` — download XML brut
- [ ] Historique des téléchargements (in-memory uniquement, persistenté via `UserDefaults` optionnel)

**Critères d'acceptation :**

1. CVP `ova latest` se télécharge correctement
2. Docker import visible dans `docker images` après import cEOS
3. Dry-run ne crée aucun fichier, log indique dry-run mode

### Phase 4 — Distribution (1 semaine)

**Pré-requis :** Phase 3 validée, certificat Apple Developer actif.

- [ ] Icône application (1024×1024 PNG → `.icns` via `iconutil`)
- [ ] Workflow GitHub Actions : build → signature ad-hoc → notarisation Apple → `.dmg` → upload GitHub Release
- [ ] Ajouter `gui/EosDownloaderApp/EosDownloaderApp/Resources/ardl_bundle/` au `.gitignore`
- [ ] Formule Homebrew Cask (`brew tap titom73/tap`)
- [ ] Mise à jour `README.md` du projet Python (section GUI + lien release)

---

## Stratégie de test

### Tests Python (protection des contrats JSON)

Fichier à créer en Phase 2 : `tests/unit/cli/test_json_contracts.py`

```python
"""Vérifie que les sorties JSON de la CLI respectent les contrats attendus par l'app Swift."""
from click.testing import CliRunner
from eos_downloader.cli.cli import ardl
import json

def test_info_latest_json_contract(mock_arista_server):
    """La clé 'version' doit être présente dans info latest --format json."""
    runner = CliRunner()
    result = runner.invoke(ardl, ["info", "latest", "--format", "json", "--package", "eos"])
    data = json.loads(result.output)
    assert "version" in data

def test_info_versions_json_contract(mock_arista_server):
    """Chaque entrée doit avoir 'version' et 'branch'."""
    runner = CliRunner()
    result = runner.invoke(ardl, ["info", "versions", "--format", "json", "--package", "eos"])
    entries = json.loads(result.output)
    assert isinstance(entries, list)
    for entry in entries:
        assert "version" in entry
        assert "branch" in entry
```

### Tests Swift (unité)

- `CLIRunnerTests.swift` — tester le parsing exit code / stdout / stderr avec un process mock (`echo`, `false`)
- `KeychainTokenManagerTests.swift` — tester read/write/delete sur un service Keychain de test (suffix `-test`)
- `CLIBinaryLocatorTests.swift` — tester la logique de recherche avec des paths temporaires
- `VersionEntryTests.swift` — tester le décodage JSON avec des cas limites (champ absent, type inattendu)

> Les tests Swift n'utilisent **jamais** un vrai processus `ardl`. Utiliser des fixtures JSON statiques pour les tests de décodage Codable.

---

## Vérification end-to-end

1. **Build** : `make gui-binary` → `ardl_bundle/ardl info versions --format json` retourne du JSON valide
2. **Sécurité** : `ps aux | grep ardl` pendant une opération — aucun token visible en argument
3. **Token** : Settings → saisir token Arista → "Valider" → message "Token valide"
4. **Token invalide** : Token erroné → alerte claire "Token expiré" avec lien vers arista.com
5. **Info** : Info → Versions → EOS, branch 4.29 → liste se peuple, latest affiché
6. **Download** : Download → EOS → format `vEOS-lab`, version `4.29.3M`, output `/tmp` → fichier présent dans `/tmp`
7. **Annulation** : Démarrer un téléchargement → cliquer Annuler → fichier partiel absent, aucun process `ardl` orphelin
8. **CVP** : Download → CVP → format `ova`, `Latest` coché → téléchargement réussi
9. **Dry-run** : cocher "Dry Run" → Download → pas de fichier créé, log indique dry-run mode
10. **Docker** : cocher "Import to Docker", image name `arista/ceos`, tag `4.29.3M` → import Docker visible dans `docker images`
11. **Architecture** : `file ardl_bundle/ardl` → doit afficher `Mach-O universal binary with 2 architectures: [x86_64] [arm64]`

---

## Fichiers Python de référence (lecture seule)

Ces fichiers définissent les contrats que l'app Swift doit respecter :

| Fichier | Utilité pour le GUI |
|---|---|
| `eos_downloader/cli/info/commands.py` | Contrats JSON exacts des commandes `info` |
| `eos_downloader/cli/get/commands.py` | Tous les flags CLI pour `get eos`, `get cvp`, `get path` |
| `eos_downloader/models/data.py` | Mapping complet des formats d'image |
| `eos_downloader/cli/get/utils.py` | Ordre de composition des arguments CLI |
| `pyproject.toml` | Entry point `ardl` et dépendances → spec PyInstaller |
| `tests/unit/cli/test_json_contracts.py` | Tests de régression sur les contrats JSON (créé en Phase 2) |
