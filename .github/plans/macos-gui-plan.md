# Interface graphique macOS native pour eos-downloader

> **Statut** : En cours — Phase 1 terminée, Phase 2 en cours
> **Date** : 2026-02-24 — Mis à jour : 2026-02-25
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

**Canal unique de distribution : Homebrew Cask.**

L'App Sandbox du Mac App Store interdit l'exécution de sous-processus arbitraires — incompatible avec l'architecture CLI-runner. Cette option est définitivement exclue.

Le pipeline retenu est :
```
tag git gui-v* → GitHub Actions → DMG signé + notarisé → GitHub Release → Homebrew Cask
```
L'utilisateur final installe via `brew install --cask eos-downloader` et met à jour via `brew upgrade`. Aucun téléchargement manuel.

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

### Phase 1 — MVP ✅ Terminée

**Objectif :** Téléchargement EOS fonctionnel de bout en bout

- [x] `CLIBinaryLocator.swift` — cherche dans `Contents/Resources/ardl_bundle/` puis `PATH`
- [x] `CLIError.swift` — enum exhaustif avec `title`, `summary`, `detailText`, parsing tracebacks Python
- [x] `CLIResult.swift` — exitCode, stdout, stderr
- [x] `CLIRunner.swift` — `actor` Process wrapper, `run(args:env:)`, `stream(args:env:onLine:)`, `cancel()`
- [x] Structs Codable `VersionEntry`, `LatestVersion`, `MappingEntry`
- [x] `KeychainTokenManager.swift` — lecture/écriture token Keychain
- [x] `SettingsView.swift` — `SecureField` token, validation, sélecteur de chemin `ardl`
- [x] `DownloadState.swift` — `ObservableObject`, formulaire EOS
- [x] `EosDownloadView.swift` — format, version, output, Docker, bouton Download, annulation
- [x] `LogOutputView.swift` — zone scrollable, auto-scroll, coloration par type de ligne
- [x] `ErrorAlertModifier.swift` + `ErrorSheetView` — sheet scrollable avec parsing traceback Python
- [x] `ContentView.swift` — sidebar custom `HStack` + `Divider` (220 px fixe), robuste vs SPM
- [x] `SidebarView.swift` — Arista blue, sections colorées, icônes SF Symbols
- [x] `ProgressBannerView.swift` + `DownloadProgress` — barre de progression avec phases, % et vitesse
- [x] Fix Python `download.py` — chemins complets dans `self.file` pour le checksum

### Phase 2 — Améliorations UX + Info ⬅️ En cours

**Objectif :** Panneau droit rétractable, section Info fonctionnelle, icône application

#### 2a — Panneau Output rétractable

Le panneau droit (log output) doit pouvoir être masqué/affiché avec un bouton dans son en-tête, symétrique au comportement souhaitable pour la sidebar gauche.

**Fichiers impactés :**
- `EosDownloadView.swift` — ajouter `@State var logPanelVisible: Bool = true`, conditionner le panneau droit + passer la logique d'affichage/masquage dans le `logHeader`
- Ajouter un bouton chevron `sidebar.right` / `sidebar.right.badge.checkmark` dans `logHeader` pour toggle
- Conserver `HSplitView` : quand le panneau est masqué, ne pas afficher le `Divider` et le panneau droit ; l'espace est récupéré par la colonne gauche
- Persister la préférence via `@AppStorage("logPanelVisible")` pour retrouver l'état au relancement

#### 2b — Section Info

La section Info expose trois onglets correspondant aux trois commandes `ardl info` :

**Nouveaux fichiers à créer :**

| Fichier | Rôle |
|---|---|
| `State/InfoState.swift` | `ObservableObject`, fetch async des trois commandes `info`, cache mémoire |
| `Views/Info/InfoView.swift` | Conteneur avec tab bar (Versions / Latest / Mapping) — remplace le placeholder |
| `Views/Info/VersionListView.swift` | Tableau `List` filtrable : package (EOS/CVP), branch, release type ; bouton "Use in Download" |
| `Views/Info/LatestVersionView.swift` | Version la plus récente avec bouton Copy ; sélecteur package + branch + release type |
| `Views/Info/MappingView.swift` | Tableau des formats d'image avec extension et préfixe |

**`InfoState.swift` — responsabilités :**
- Paramètres : `package` (eos/cvp), `branch` (optionnel), `rtype` (M/F)
- Actions : `fetchVersions()`, `fetchLatest()`, `fetchMapping()`
- États : `isLoading: Bool`, `versions: [VersionEntry]`, `latest: LatestVersion?`, `mapping: [String: MappingEntry]`, `error: CLIError?`
- Cache : invalider si les paramètres changent ; bouton "Refresh"

**Commandes CLI correspondantes :**
```
ardl info versions --package eos [--branch 4.29] [--release-type M] --format json
ardl info latest   --package eos [--branch 4.29] [--release-type M] --format json
ardl info mapping  --package eos --format json
```
Token injecté via `env["ARISTA_TOKEN"]` comme dans `DownloadState`.

**`VersionListView` — détail :**
- Barre de filtre en haut (package picker, branch TextField, rtype picker)
- Bouton "Query" pour déclencher le fetch (pas d'auto-fetch pour éviter les appels inutiles à l'API)
- `List` avec colonnes : version, branch, release type
- Bouton "Use in Download" sur chaque ligne → met à jour le formulaire EOS/CVP via binding partagé sur `DownloadState`

**`LatestVersionView` — détail :**
- Sélecteurs package / branch / release type
- Bouton "Get Latest" → `ardl info latest --format json`
- Affichage en grand de la version, bouton copy presse-papier

**`MappingView` — détail :**
- Sélecteur package
- Bouton "Load Mapping"
- Table : format key, extension, prepend

#### 2c — Icône application

macOS exige un fichier `.icns` dans le bundle. La source est `docs/imgs/logo.jpg`.

**Procédure :**
1. Créer `gui/Sources/EosDownloaderApp/Assets.xcassets/AppIcon.appiconset/` avec les 9 tailles requises (16, 32, 64, 128, 256, 512, 1024 px) générées depuis `logo.jpg` via `sips`
2. Créer `gui/Sources/EosDownloaderApp/Assets.xcassets/Contents.json` pour référencer l'iconset
3. Ajouter `CFBundleIconFile` dans `Info.plist`
4. Mettre à jour `run.sh` pour copier `Assets.xcassets` dans le bundle lors du build

**Script de génération des icônes (intégré dans `run.sh`) :**
```bash
# Génère AppIcon.icns depuis docs/imgs/logo.jpg
SOURCE_LOGO="docs/imgs/logo.jpg"
ICONSET_DIR="gui/Sources/EosDownloaderApp/Assets.xcassets/AppIcon.appiconset"
mkdir -p "$ICONSET_DIR"
for SIZE in 16 32 64 128 256 512 1024; do
    sips -z $SIZE $SIZE "$SOURCE_LOGO" --out "$ICONSET_DIR/icon_${SIZE}x${SIZE}.png" >/dev/null
done
iconutil -c icns "$ICONSET_DIR" -o "$ICONSET_DIR/AppIcon.icns" 2>/dev/null || true
```

**Critères d'acceptation Phase 2 :**
1. Le panneau Output peut être masqué/affiché via un bouton ; l'état est mémorisé entre lancements
2. La section Info affiche la liste des versions EOS après avoir cliqué "Query"
3. "Get Latest" affiche la version la plus récente avec un bouton Copy fonctionnel
4. "Use in Download" pré-remplit le champ version dans `EosDownloadView`
5. L'icône Arista est visible dans le Dock et le Finder

### Phase 3 — Parité CLI complète (1–2 semaines)

**Pré-requis :** Phase 2 validée.

- [ ] `CvpDownloadView.swift` — formats CVP (ova/rpm/kvm/upgrade)
- [ ] `PathDownloadView.swift` — champ source direct + options Docker
- [ ] Options Docker dans `EosDownloadView` déjà présentes — vérifier CVP et Path
- [ ] Toggle EVE-NG — tooltip explicatif ("Requires EVE-NG server access")
- [ ] `DebugView.swift` — download XML brut + log output
- [ ] Historique des téléchargements (in-memory, persistable via `@AppStorage`)

**Critères d'acceptation :**

1. CVP `ova latest` se télécharge correctement
2. Docker import visible dans `docker images` après import cEOS
3. Dry-run ne crée aucun fichier, log indique dry-run mode

### Phase 4 — Distribution via Homebrew (2–3 semaines)

**Pré-requis :** Phase 3 validée.

Cette phase couvre l'intégralité du pipeline de distribution macOS : build release → signature → notarisation → DMG → GitHub Release → Homebrew Cask. Chaque étape est bloquante pour la suivante.

---

#### 4.0 — Prérequis : compte Apple Developer

> **Coût : 99 $/an** — obligatoire pour signer et notariser une app distribuée en dehors de tout store officiel (ce qui est notre cas : distribution via Homebrew uniquement).

Sans ce certificat, l'app est bloquée par Gatekeeper à l'ouverture (popup "Apple ne peut pas vérifier que cette app ne contient pas de logiciel malveillant"). Il existe une solution de contournement (ad-hoc signature) documentée plus bas, mais elle dégrade l'expérience utilisateur.

**Étapes :**
1. Créer/vérifier le compte sur [developer.apple.com](https://developer.apple.com)
2. Dans Xcode → Settings → Accounts → ajouter le compte
3. Générer un certificat **Developer ID Application** (pas "Development" ni "Distribution") :
   - Xcode → Settings → Accounts → Manage Certificates → `+` → Developer ID Application
   - Ou via [developer.apple.com/account/resources/certificates](https://developer.apple.com/account/resources/certificates)
4. Vérifier que le certificat est dans le Keychain : `security find-identity -v -p codesigning`
   - Doit afficher quelque chose comme `"Developer ID Application: Your Name (TEAMID)"`
5. Créer un **mot de passe d'application** (app-specific password) sur [appleid.apple.com](https://appleid.apple.com) → Security → App-Specific Passwords → pour la notarisation CI

**Identifiants à noter pour la suite :**
```
APPLE_ID        = votre@email.com
APPLE_TEAM_ID   = XXXXXXXXXX  (10 caractères, visible sur developer.apple.com)
APPLE_CERT_NAME = "Developer ID Application: Prénom Nom (TEAMID)"
```

---

#### 4.1 — Build Release (Universal Binary)

Le build debug actuel (`swift build`) n'est pas distribuable. Il faut :
1. Un build **release** (optimisé, sans symboles de debug)
2. Un **Universal Binary** combinant arm64 (Apple Silicon) et x86_64 (Intel)

**Script `gui/scripts/build_release.sh` à créer :**
```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

APP_NAME="EosDownloader"
BUNDLE_ID="com.arista.eos-downloader"
VERSION="${1:-1.0.0}"

echo "==> Building for arm64..."
swift build -c release --arch arm64

echo "==> Building for x86_64..."
swift build -c release --arch x86_64

echo "==> Creating universal binary with lipo..."
mkdir -p .build/universal-release
lipo -create \
  .build/arm64-apple-macosx/release/EosDownloaderApp \
  .build/x86_64-apple-macosx/release/EosDownloaderApp \
  -output ".build/universal-release/EosDownloaderApp"

echo "==> Verifying: $(file .build/universal-release/EosDownloaderApp)"
# Doit afficher: Mach-O universal binary with 2 architectures: [x86_64] [arm64]
```

---

#### 4.2 — Bundle `.app` release

Même structure que `run.sh` mais en mode release + icône + version correcte dans `Info.plist`.

**Additions à `Info.plist` :**
```xml
<key>CFBundleShortVersionString</key>
<string>1.0.0</string>
<key>CFBundleVersion</key>
<string>1</string>
<key>NSHumanReadableCopyright</key>
<string>Copyright © 2026 titom73. MIT License.</string>
```

Le script de release crée `EosDownloader.app` dans `.build/release/`.

---

#### 4.3 — Signature du code (codesign)

La signature permet à Gatekeeper de vérifier que l'app n'a pas été modifiée après distribution.

**Commandes de signature :**
```bash
# 1. Signer le binaire ardl bundlé (PyInstaller)
codesign --force --options runtime \
  --sign "Developer ID Application: Prénom Nom (TEAMID)" \
  --timestamp \
  "EosDownloader.app/Contents/Resources/ardl_bundle/ardl"

# 2. Signer le bundle entier (deep = récursif sur les frameworks/libs inclus)
codesign --force --deep --options runtime \
  --sign "Developer ID Application: Prénom Nom (TEAMID)" \
  --timestamp \
  --entitlements "gui/scripts/entitlements.plist" \
  "EosDownloader.app"

# 3. Vérifier la signature
codesign --verify --deep --strict "EosDownloader.app"
spctl --assess --type execute --verbose "EosDownloader.app"
# Doit afficher: EosDownloader.app: accepted
```

**`gui/scripts/entitlements.plist` à créer :**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Requis pour lancer des sous-processus (ardl) avec Hardened Runtime -->
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <false/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <!-- Permet au binaire PyInstaller d'accéder au réseau -->
    <key>com.apple.security.network.client</key>
    <true/>
</dict>
</plist>
```

> **Hardened Runtime** (`--options runtime`) est obligatoire pour la notarisation. Il durcit la sécurité de l'app et impose que tous les entitlements soient déclarés explicitement.

---

#### 4.4 — Création du DMG

Le `.dmg` est le format standard de distribution macOS. L'utilisateur ouvre le DMG, glisse l'app dans Applications, et éjecte.

**Via `hdiutil` (intégré macOS, aucune dépendance) :**
```bash
# Créer une image staging
mkdir -p /tmp/dmg-staging
cp -r "EosDownloader.app" /tmp/dmg-staging/

# Lien symbolique vers /Applications (facilite le glisser-déposer)
ln -s /Applications /tmp/dmg-staging/Applications

# Créer le DMG
hdiutil create \
  -volname "EOS Downloader" \
  -srcfolder /tmp/dmg-staging \
  -ov -format UDZO \
  "EosDownloader-${VERSION}.dmg"

rm -rf /tmp/dmg-staging
```

**Alternative avec `create-dmg` (meilleure apparence) :**
```bash
brew install create-dmg  # une seule fois en dev

create-dmg \
  --volname "EOS Downloader" \
  --volicon "docs/imgs/logo.jpg" \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "EosDownloader.app" 175 190 \
  --app-drop-link 425 190 \
  "EosDownloader-${VERSION}.dmg" \
  "EosDownloader.app"
```

---

#### 4.5 — Notarisation Apple

La notarisation soumet le DMG aux serveurs Apple qui scannent le binaire pour malware. Si approuvé, Apple émet un "ticket" qui est attaché (stapled) au DMG.

```bash
# 1. Soumettre à Apple pour validation (prend 1–5 minutes)
xcrun notarytool submit "EosDownloader-${VERSION}.dmg" \
  --apple-id "$APPLE_ID" \
  --password "$APPLE_APP_PASSWORD" \
  --team-id "$APPLE_TEAM_ID" \
  --wait  # attend la fin de la validation, affiche le statut

# 2. Attacher le ticket de notarisation au DMG
xcrun stapler staple "EosDownloader-${VERSION}.dmg"

# 3. Vérifier
xcrun stapler validate "EosDownloader-${VERSION}.dmg"
spctl --assess --type open --context context:primary-signature "EosDownloader-${VERSION}.dmg"
# Doit afficher: accepted
```

En cas d'échec, afficher les logs :
```bash
xcrun notarytool log <submission-id> \
  --apple-id "$APPLE_ID" --password "$APPLE_APP_PASSWORD" --team-id "$APPLE_TEAM_ID"
```

> **Option sans Apple Developer** : Remplacer `codesign --sign "Developer ID..."` par `codesign --sign -` (ad-hoc). La notarisation est impossible. Les utilisateurs devront faire clic-droit → Ouvrir → Ouvrir quand même à la première utilisation. Documenter clairement dans le README.

---

#### 4.6 — GitHub Release

```bash
# Calculer le SHA256 (requis pour la formule Homebrew)
SHA256=$(shasum -a 256 "EosDownloader-${VERSION}.dmg" | awk '{print $1}')
echo "SHA256: $SHA256"  # à copier dans la formule Cask

# Créer la release GitHub (via gh CLI)
gh release create "gui-v${VERSION}" \
  --title "EOS Downloader GUI v${VERSION}" \
  --notes "macOS GUI for eos-downloader v${VERSION}" \
  "EosDownloader-${VERSION}.dmg"
```

L'URL téléchargeable sera :
`https://github.com/titom73/eos-downloader/releases/download/gui-v${VERSION}/EosDownloader-${VERSION}.dmg`

---

#### 4.7 — Homebrew Tap (repository séparé)

Homebrew nécessite un repository GitHub nommé exactement `homebrew-<tapname>`.

**Créer le repository `titom73/homebrew-tap` :**
```bash
gh repo create titom73/homebrew-tap --public --description "Homebrew tap for titom73 tools"
```

**Structure du repository :**
```
homebrew-tap/
├── README.md
└── Casks/
    └── eos-downloader.rb
```

**Formule `Casks/eos-downloader.rb` :**
```ruby
cask "eos-downloader" do
  version "1.0.0"
  sha256 "REMPLACER_PAR_LE_SHA256_REEL"

  url "https://github.com/titom73/eos-downloader/releases/download/gui-v#{version}/EosDownloader-#{version}.dmg"
  name "EOS Downloader"
  desc "macOS GUI for downloading Arista EOS and CloudVision images"
  homepage "https://github.com/titom73/eos-downloader"

  # Requis pour l'installation silencieuse (Gatekeeper)
  depends_on macos: ">= :ventura"  # macOS 13+

  app "EosDownloader.app"

  # Nettoyage complet à la désinstallation
  zap trash: [
    "~/Library/Preferences/com.arista.eos-downloader.plist",
    "~/Library/Application Support/EOS Downloader",
    "~/Library/Logs/EOS Downloader",
  ]
end
```

**Installation utilisateur :**
```bash
brew tap titom73/tap
brew install --cask eos-downloader

# Mise à jour
brew upgrade --cask eos-downloader

# Désinstallation complète
brew uninstall --cask eos-downloader --zap
```

---

#### 4.8 — Workflow GitHub Actions (CI/CD)

Fichier `.github/workflows/gui-release.yml` à créer. Se déclenche sur un tag `gui-v*`.

**Secrets GitHub à configurer dans Settings → Secrets :**
```
APPLE_CERT_BASE64           # contenu du certificat .p12 encodé en base64
                            # export: Keychain → clic-droit → Export → .p12
                            # encode: base64 -i cert.p12 | pbcopy
APPLE_CERT_PASSWORD         # mot de passe du .p12
APPLE_ID                    # votre@email.com
APPLE_APP_PASSWORD          # mot de passe app-specific (appleid.apple.com)
APPLE_TEAM_ID               # identifiant équipe (10 caractères)
TAP_REPO_TOKEN              # GitHub PAT avec scope repo pour pousser sur homebrew-tap
```

**`.github/workflows/gui-release.yml` :**
```yaml
name: GUI Release

on:
  push:
    tags:
      - 'gui-v*'

jobs:
  build-and-release:
    runs-on: macos-14  # Apple Silicon, Swift 5.9 inclus
    env:
      APP_NAME: EosDownloader
      BUNDLE_ID: com.arista.eos-downloader

    steps:
      - uses: actions/checkout@v4

      - name: Set version from tag
        run: echo "VERSION=${GITHUB_REF_NAME#gui-v}" >> $GITHUB_ENV

      - name: Set up Python + uv
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install uv && uv sync --all-extras

      - name: Build ardl PyInstaller bundle
        run: bash gui/scripts/build_ardl_binary.sh

      - name: Import Apple certificate
        env:
          CERT_BASE64: ${{ secrets.APPLE_CERT_BASE64 }}
          CERT_PASSWORD: ${{ secrets.APPLE_CERT_PASSWORD }}
        run: |
          CERT_FILE=$(mktemp /tmp/cert.XXXXXX.p12)
          echo "$CERT_BASE64" | base64 --decode > "$CERT_FILE"
          security create-keychain -p "ci-keychain" build.keychain
          security default-keychain -s build.keychain
          security unlock-keychain -p "ci-keychain" build.keychain
          security import "$CERT_FILE" -k build.keychain \
            -P "$CERT_PASSWORD" -T /usr/bin/codesign
          security set-key-partition-list -S apple-tool:,apple: \
            -s -k "ci-keychain" build.keychain
          rm "$CERT_FILE"

      - name: Build release (Universal Binary)
        run: bash gui/scripts/build_release.sh "$VERSION"

      - name: Sign app bundle
        env:
          CERT_NAME: ${{ secrets.APPLE_CERT_NAME }}
        run: |
          codesign --force --deep --options runtime \
            --sign "$CERT_NAME" --timestamp \
            --entitlements gui/scripts/entitlements.plist \
            ".build/release/$APP_NAME.app"

      - name: Create DMG
        run: |
          brew install create-dmg
          create-dmg \
            --volname "$APP_NAME" \
            --volicon "docs/imgs/logo.jpg" \
            --window-size 600 400 \
            --icon "$APP_NAME.app" 175 190 \
            --app-drop-link 425 190 \
            "${APP_NAME}-${VERSION}.dmg" \
            ".build/release/$APP_NAME.app"

      - name: Notarize DMG
        env:
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_APP_PASSWORD: ${{ secrets.APPLE_APP_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
        run: |
          xcrun notarytool submit "${APP_NAME}-${VERSION}.dmg" \
            --apple-id "$APPLE_ID" \
            --password "$APPLE_APP_PASSWORD" \
            --team-id "$APPLE_TEAM_ID" \
            --wait
          xcrun stapler staple "${APP_NAME}-${VERSION}.dmg"

      - name: Compute SHA256
        run: |
          SHA256=$(shasum -a 256 "${APP_NAME}-${VERSION}.dmg" | awk '{print $1}')
          echo "SHA256=${SHA256}" >> $GITHUB_ENV

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: "${{ env.APP_NAME }}-${{ env.VERSION }}.dmg"
          generate_release_notes: true

      - name: Update Homebrew Cask
        env:
          TAP_TOKEN: ${{ secrets.TAP_REPO_TOKEN }}
          VERSION: ${{ env.VERSION }}
          SHA256: ${{ env.SHA256 }}
        run: |
          git clone "https://x-access-token:${TAP_TOKEN}@github.com/titom73/homebrew-tap.git" tap-repo
          cd tap-repo
          sed -i '' "s/version \".*\"/version \"${VERSION}\"/" Casks/eos-downloader.rb
          sed -i '' "s/sha256 \".*\"/sha256 \"${SHA256}\"/" Casks/eos-downloader.rb
          git config user.email "ci@github.com"
          git config user.name "GitHub Actions"
          git add Casks/eos-downloader.rb
          git diff --staged --quiet || git commit -m "chore: bump eos-downloader to ${VERSION}"
          git push
```

**Déclencher une release :**
```bash
git tag gui-v1.0.0
git push origin gui-v1.0.0
```

---

#### Checklist Phase 4

- [ ] Compte Apple Developer actif, certificat Developer ID Application dans Keychain
- [ ] Mot de passe app-specific créé sur appleid.apple.com
- [ ] `gui/scripts/build_release.sh` créé et testé localement
- [ ] Entitlements `gui/scripts/entitlements.plist` créé
- [ ] `Info.plist` mis à jour avec `CFBundleShortVersionString`
- [ ] DMG créé et testé localement (glisser-déposer dans Applications fonctionne)
- [ ] Signature vérifiée (`spctl --assess` → `accepted`)
- [ ] Notarisation réussie en local avant de passer à CI
- [ ] Repository `titom73/homebrew-tap` créé avec `Casks/eos-downloader.rb`
- [ ] Les 6 secrets GitHub configurés dans Settings → Secrets
- [ ] Workflow `gui-release.yml` créé et déclenché sur `gui-v0.1.0`
- [ ] `brew tap titom73/tap && brew install --cask eos-downloader` fonctionne sur machine test
- [ ] `.gitignore` mis à jour (`ardl_bundle/`)
- [ ] `README.md` mis à jour avec instructions d'installation Homebrew

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
