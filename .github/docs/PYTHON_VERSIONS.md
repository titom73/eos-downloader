# Python Version Management System# Python Version Management System# Python Version Management System



## 📋 Overview



This system allows you to **centralize and automatically synchronize** Python versions used across:## 📋 Overview## 📋 Overview

- ✅ GitHub Actions workflows (test matrices)

- ✅ `pyproject.toml` (classifiers and requires-python)

- ✅ Documentation

- ✅ Scripts and toolsThis system allows you to **centralize and automatically synchronize** Python versions used across:This system allows you to **centralize and automatically synchronize** Python versions used across:



## 🎯 Single Source of Truth- ✅ GitHub Actions workflows (test matrices)- ✅ GitHub Actions workflows (test matrices)



All Python versions are defined in a single file:- ✅ `pyproject.toml` (classifiers and requires-python)- ✅ `pyproject.toml` (classifiers and requires-python)



```- ✅ Documentation- ✅ Documentation

.github/python-versions.json

```- ✅ Scripts and tools- ✅ Scripts and tools



### File Format



```json## 🎯 Single Source of Truth## 🎯 Single Source of Truth

{

  "versions": ["3.9", "3.10", "3.11", "3.12"],

  "min_version": "3.9",

  "max_version": "3.12",All Python versions are defined in a single file:All Python versions are defined in a single file:

  "default_version": "3.11"

}

```

``````

**Fields**:

- `versions`: Complete list of versions to test.github/python-versions.json.github/python-versions.json

- `min_version`: Minimum required Python version

- `max_version`: Maximum supported Python version``````

- `default_version`: Default version for operations



## 🔄 Synchronization Workflow

### File Format### Format du fichier

### 1. Modify Versions



```bash

# Edit the JSON file```json```json

vim .github/python-versions.json

{{

# Example: add Python 3.13

{  "versions": ["3.9", "3.10", "3.11", "3.12"],  "versions": ["3.9", "3.10", "3.11", "3.12"],

  "versions": ["3.9", "3.10", "3.11", "3.12", "3.13"],

  "min_version": "3.9",  "min_version": "3.9",  "min_version": "3.9",

  "max_version": "3.13",

  "default_version": "3.11"  "max_version": "3.12",  "max_version": "3.12",

}

```  "default_version": "3.11"  "default_version": "3.11"



### 2. Synchronize Automatically}}



```bash``````

# Run the synchronization script

python .github/scripts/sync-python-versions.py

```

**Fields**:**Champs** :

**This script automatically updates**:

- ✅ Classifiers in `pyproject.toml`- `versions`: Complete list of versions to test- `versions` : Liste complète des versions à tester

- ✅ `requires-python` in `pyproject.toml`

- `min_version`: Minimum required Python version- `min_version` : Version Python minimale requise

### 3. Verify Synchronization

- `max_version`: Maximum supported Python version- `max_version` : Version Python maximale supportée

```bash

# Check that everything is synchronized- `default_version`: Default version for operations- `default_version` : Version par défaut pour les opérations

python .github/scripts/check-python-versions.py

```



### 4. Use in Workflows## 🔄 Synchronization Workflow## 🔄 Workflow de synchronisation



GitHub Actions workflows can automatically read versions from JSON:



```yaml### 1. Modify Versions### 1. Modifier les versions

jobs:

  setup:

    runs-on: ubuntu-latest

    outputs:```bash```bash

      python-versions: ${{ steps.set-versions.outputs.versions }}

    steps:# Edit the JSON file# Éditer le fichier JSON

      - uses: actions/checkout@v5

      vim .github/python-versions.jsonvim .github/python-versions.json

      - name: Load Python versions

        id: set-versions

        run: |

          VERSIONS=$(cat .github/python-versions.json | jq -c '.versions')# Example: add Python 3.12# Exemple : ajouter Python 3.12

          echo "versions=$VERSIONS" >> $GITHUB_OUTPUT

{{

  test:

    needs: setup  "versions": ["3.9", "3.10", "3.11", "3.12"],  "versions": ["3.9", "3.10", "3.11", "3.12"],

    strategy:

      matrix:  "min_version": "3.9",  "min_version": "3.9",

        python-version: ${{ fromJson(needs.setup.outputs.python-versions) }}

    # ... rest of the job  "max_version": "3.12",  "max_version": "3.12",

```

  "default_version": "3.11"  "default_version": "3.11"

## 🛠️ Available Scripts

}}

### `.github/scripts/sync-python-versions.py`

``````

**Purpose**: Synchronizes versions from JSON to pyproject.toml



**Usage**:

```bash### 2. Synchronize Automatically### 2. Synchroniser automatiquement

python .github/scripts/sync-python-versions.py

```



**Actions performed**:```bash```bash

1. Reads `.github/python-versions.json`

2. Updates Python classifiers in `pyproject.toml`# Run the synchronization script# Exécuter le script de synchronisation

3. Updates `requires-python` in `pyproject.toml`

4. Displays a summary of changespython .github/scripts/sync-python-versions.pypython scripts/sync-python-versions.py



**Example output**:``````

```

📋 Loading Python versions from JSON...

✅ Found versions: ['3.9', '3.10', '3.11', '3.12']

   Min version: 3.9**This script automatically updates**:**Ce script met à jour automatiquement** :

   Max version: 3.12

- ✅ Classifiers in `pyproject.toml`- ✅ Classifiers dans `pyproject.toml`

📝 Updating pyproject.toml...

✅ Updated Python version classifiers- ✅ `requires-python` in `pyproject.toml`- ✅ `requires-python` dans `pyproject.toml`

✅ Updated requires-python



🎉 Synchronization complete!

### 3. Verify Synchronization### 3. Vérifier la synchronisation

💡 Next steps:

   1. Review changes: git diff pyproject.toml

   2. Run tests to ensure compatibility

   3. Commit changes: git add pyproject.toml && git commit -m 'chore: sync Python versions'```bash```bash

```

# Check that everything is synchronized# Vérifier que tout est synchronisé

### `.github/scripts/check-python-versions.py`

python .github/scripts/check-python-versions.pypython scripts/check-python-versions.py

**Purpose**: Verifies that versions are synchronized

``````

**Usage**:

```bash

python .github/scripts/check-python-versions.py

```### 4. Use in Workflows### 4. Utiliser dans les workflows



**Return codes**:

- `0`: Everything is synchronized ✅

- `1`: Desynchronization detected ❌GitHub Actions workflows automatically read versions from JSON:Les workflows GitHub Actions lisent automatiquement les versions depuis le JSON :



**Example output (synchronized)**:

```

✅ Python versions are synchronized```yaml```yaml

```

jobs:jobs:

**Example output (out of sync)**:

```  setup:  setup:

❌ Python versions are out of sync!

    runs-on: ubuntu-latest    runs-on: ubuntu-latest

📋 Versions in .github/python-versions.json: ['3.9', '3.10', '3.11', '3.12']

📄 Versions in pyproject.toml: ['3.9', '3.10', '3.11']    outputs:    outputs:



💡 To fix this, run:      python-versions: ${{ steps.set-versions.outputs.versions }}      python-versions: ${{ steps.set-versions.outputs.versions }}

   python .github/scripts/sync-python-versions.py

```    steps:    steps:



## 🔍 Automatic CI Verification      - uses: actions/checkout@v5      - uses: actions/checkout@v5



The workflow `.github/workflows/check-python-versions.yml` automatically checks synchronization on:

- ✅ Every Pull Request modifying `python-versions.json` or `pyproject.toml`

- ✅ Every push to `main`      - name: Load Python versions      - name: Load Python versions



**If desynchronized**:        id: set-versions        id: set-versions

- ❌ The workflow fails

- 💡 Error message with instructions to fix        run: |        run: |



## 📝 Add Pre-commit Hook (Optional)          VERSIONS=$(cat .github/python-versions.json | jq -c '.versions')          VERSIONS=$(cat .github/python-versions.json | jq -c '.versions')



To check locally before each commit:          echo "versions=$VERSIONS" >> $GITHUB_OUTPUT          echo "versions=$VERSIONS" >> $GITHUB_OUTPUT



```yaml

# Add to .pre-commit-config.yaml

repos:  test:  test:

  - repo: local

    hooks:    needs: setup    needs: setup

      - id: check-python-versions

        name: Check Python versions sync    strategy:    strategy:

        entry: python .github/scripts/check-python-versions.py

        language: system      matrix:      matrix:

        pass_filenames: false

        files: ^(\.github/python-versions\.json|pyproject\.toml)$        python-version: ${{ fromJson(needs.setup.outputs.python-versions) }}        python-version: ${{ fromJson(needs.setup.outputs.python-versions) }}

```

    # ... rest of the job    # ... rest of the job

Then:

```bash``````

pre-commit install

```



## 🎯 Use Cases## 🛠️ Available Scripts## 🛠️ Scripts disponibles



### Add a New Python Version



1. **Update JSON**:### `.github/scripts/sync-python-versions.py`### `scripts/sync-python-versions.py`

```json

{

  "versions": ["3.9", "3.10", "3.11", "3.12", "3.13"],

  "max_version": "3.13"**Purpose**: Synchronizes versions from JSON to pyproject.toml**Objectif** : Synchronise les versions depuis JSON vers pyproject.toml

}

```



2. **Synchronize**:**Usage**:**Usage** :

```bash

python .github/scripts/sync-python-versions.py```bash```bash

```

python .github/scripts/sync-python-versions.pypython scripts/sync-python-versions.py

3. **Verify**:

```bash``````

git diff pyproject.toml

```



4. **Commit**:**Actions performed**:**Actions effectuées** :

```bash

git add .github/python-versions.json pyproject.toml1. Reads `.github/python-versions.json`1. Lit `.github/python-versions.json`

git commit -m "feat: add Python 3.13 support"

```2. Updates Python classifiers in `pyproject.toml`2. Met à jour les classifiers Python dans `pyproject.toml`



### Remove an Old Version3. Updates `requires-python` in `pyproject.toml`3. Met à jour `requires-python` dans `pyproject.toml`



1. **Update JSON**:4. Displays a summary of changes4. Affiche un résumé des changements

```json

{

  "versions": ["3.10", "3.11", "3.12"],

  "min_version": "3.10"**Example output**:**Exemple de sortie** :

}

`````````



2. **Synchronize**:📋 Loading Python versions from JSON...📋 Loading Python versions from JSON...

```bash

python .github/scripts/sync-python-versions.py✅ Found versions: ['3.9', '3.10', '3.11', '3.12']✅ Found versions: ['3.9', '3.10', '3.11', '3.12']

```

   Min version: 3.9   Min version: 3.9

3. **Test**:

```bash   Max version: 3.12   Max version: 3.12

tox

```



4. **Commit**:📝 Updating pyproject.toml...📝 Updating pyproject.toml...

```bash

git add .github/python-versions.json pyproject.toml✅ Updated Python version classifiers✅ Updated Python version classifiers

git commit -m "chore: drop Python 3.9 support"

```✅ Updated requires-python✅ Updated requires-python



## 🔄 Affected Workflows



The following workflows use this system:🎉 Synchronization complete!🎉 Synchronization complete!



| Workflow | Usage |

|----------|-------|

| `pr-management.yml` | Tests all versions in pre-commit, compiling, linting, typing, pytest jobs |💡 Next steps:💡 Next steps:

| `documentation.yml` | Uses `default_version` to build documentation |

| `release.yml` | Uses `default_version` for release |   1. Review changes: git diff pyproject.toml   1. Review changes: git diff pyproject.toml

| `check-python-versions.yml` | Verifies synchronization |

   2. Run tests to ensure compatibility   2. Run tests to ensure compatibility

## ✅ Benefits

   3. Commit changes: git add pyproject.toml && git commit -m 'chore: sync Python versions'   3. Commit changes: git add pyproject.toml && git commit -m 'chore: sync Python versions'

1. **Single source of truth**: One modification to update everything

2. **Automation**: Scripts to synchronize and verify``````

3. **CI/CD integration**: Automatic verification in workflows

4. **Fewer errors**: Avoids synchronization oversights

5. **Simplified maintenance**: Only one file to edit

6. **Clear documentation**: Readable and commented JSON format### `.github/scripts/check-python-versions.py`### `scripts/check-python-versions.py`



## 🚨 Important Notes



1. **Test before committing**: Always run tests after modification**Purpose**: Verifies that versions are synchronized**Objectif** : Vérifie que les versions sont synchronisées

2. **Check CI**: Ensure all jobs pass

3. **Documentation**: Update docs if necessary

4. **Dependencies**: Verify dependency compatibility

**Usage**:**Usage** :

## 📚 References

```bash```bash

- **Sync script**: `.github/scripts/sync-python-versions.py`

- **Check script**: `.github/scripts/check-python-versions.py`python .github/scripts/check-python-versions.pypython scripts/check-python-versions.py

- **Verification workflow**: `.github/workflows/check-python-versions.yml`

- **Source of truth**: `.github/python-versions.json```````



---



**Maintained by**: @titom73  **Return codes**:**Codes de retour** :

**Last updated**: 2024-10-24

- `0`: Everything is synchronized ✅- `0` : Tout est synchronisé ✅

- `1`: Desynchronization detected ❌- `1` : Désynchronisation détectée ❌



**Example output (OK)**:**Exemple de sortie (OK)** :

``````

✅ Python versions are synchronized✅ Python versions are synchronized

``````



**Example output (KO)**:**Exemple de sortie (KO)** :

``````

❌ Python versions are out of sync!❌ Python versions are out of sync!



📋 Versions in .github/python-versions.json: ['3.9', '3.10', '3.11', '3.12']📋 Versions in .github/python-versions.json: ['3.9', '3.10', '3.11', '3.12']

📄 Versions in pyproject.toml: ['3.9', '3.10', '3.11']📄 Versions in pyproject.toml: ['3.9', '3.10', '3.11']



💡 To fix this, run:💡 To fix this, run:

   python .github/scripts/sync-python-versions.py   python scripts/sync-python-versions.py

``````



## 🔍 Automatic CI Verification## 🔍 Vérification automatique dans CI



The workflow `.github/workflows/check-python-versions.yml` automatically checks synchronization on:Le workflow `.github/workflows/check-python-versions.yml` vérifie automatiquement la synchronisation sur :

- ✅ Every Pull Request modifying `python-versions.json` or `pyproject.toml`- ✅ Chaque Pull Request modifiant `python-versions.json` ou `pyproject.toml`

- ✅ Every push to `main`- ✅ Chaque push sur `main`



**If desynchronized**:**Si désynchronisé** :

- ❌ The workflow fails- ❌ Le workflow échoue

- 💡 Error message with instructions to fix- 💡 Message d'erreur avec instructions pour corriger



## 📝 Add Pre-commit Hook (Optional)## 📝 Ajouter le pre-commit hook (optionnel)



To check locally before each commit:Pour vérifier localement avant chaque commit :



```yaml```yaml

# Add to .pre-commit-config.yaml# Ajouter dans .pre-commit-config.yaml

repos:repos:

  - repo: local  - repo: local

    hooks:    hooks:

      - id: check-python-versions      - id: check-python-versions

        name: Check Python versions sync        name: Check Python versions sync

        entry: python .github/scripts/check-python-versions.py        entry: python scripts/check-python-versions.py

        language: system        language: system

        pass_filenames: false        pass_filenames: false

        files: ^(\.github/python-versions\.json|pyproject\.toml)$        files: ^(\.github/python-versions\.json|pyproject\.toml)$

``````



Then:Ensuite :

```bash```bash

pre-commit installpre-commit install

``````



## 🎯 Use Cases## 🎯 Cas d'usage



### Add a New Python Version### Ajouter une nouvelle version Python



1. **Update JSON**:1. **Mettre à jour JSON** :

```json```json

{{

  "versions": ["3.9", "3.10", "3.11", "3.12"],  "versions": ["3.9", "3.10", "3.11", "3.12"],

  "max_version": "3.12"  "max_version": "3.12"

}}

``````



2. **Synchronize**:2. **Synchroniser** :

```bash```bash

python .github/scripts/sync-python-versions.pypython scripts/sync-python-versions.py

``````



3. **Verify**:3. **Vérifier** :

```bash```bash

git diff pyproject.tomlgit diff pyproject.toml

``````



4. **Commit**:4. **Committer** :

```bash```bash

git add .github/python-versions.json pyproject.tomlgit add .github/python-versions.json pyproject.toml

git commit -m "feat: add Python 3.12 support"git commit -m "feat: add Python 3.12 support"

``````



### Remove an Old Version### Retirer une ancienne version



1. **Update JSON**:1. **Mettre à jour JSON** :

```json```json

{{

  "versions": ["3.10", "3.11", "3.12"],  "versions": ["3.10", "3.11", "3.12"],

  "min_version": "3.10"  "min_version": "3.10"

}}

``````



2. **Synchronize**:2. **Synchroniser** :

```bash```bash

python .github/scripts/sync-python-versions.pypython scripts/sync-python-versions.py

``````



3. **Test**:3. **Tester** :

```bash```bash

toxtox

``````



4. **Commit**:4. **Committer** :

```bash```bash

git add .github/python-versions.json pyproject.tomlgit add .github/python-versions.json pyproject.toml

git commit -m "chore: drop Python 3.9 support"git commit -m "chore: drop Python 3.9 support"

``````



## 🔄 Affected Workflows## 🔄 Workflows concernés



The following workflows use this system:Les workflows suivants utilisent ce système :



| Workflow | Usage || Workflow | Utilisation |

|----------|-------||----------|-------------|

| `pr-management.yml` | Tests all versions in pre-commit, compiling, linting, typing, pytest jobs || `pr-management.yml` | Teste toutes les versions dans les jobs pre-commit, compiling, linting, typing, pytest |

| `documentation.yml` | Uses `default_version` to build documentation || `documentation.yml` | Utilise `default_version` pour builder la doc |

| `release.yml` | Uses `default_version` for release || `release.yml` | Utilise `default_version` pour la release |

| `check-python-versions.yml` | Verifies synchronization || `check-python-versions.yml` | Vérifie la synchronisation |



## ✅ Benefits## ✅ Avantages



1. **Single source of truth**: One modification to update everything1. **Source unique de vérité** : Une seule modification pour tout mettre à jour

2. **Automation**: Scripts to synchronize and verify2. **Automatisation** : Scripts pour synchroniser et vérifier

3. **CI/CD integration**: Automatic verification in workflows3. **CI/CD intégré** : Vérification automatique dans les workflows

4. **Fewer errors**: Avoids synchronization oversights4. **Moins d'erreurs** : Évite les oublis de synchronisation

5. **Simplified maintenance**: Only one file to edit5. **Maintenance simplifiée** : Un seul fichier à éditer

6. **Clear documentation**: Readable and commented JSON format6. **Documentation claire** : Format JSON lisible et commenté



## 🚨 Important Notes## 🚨 Points d'attention



1. **Test before committing**: Always run tests after modification1. **Tester avant de commiter** : Toujours exécuter les tests après modification

2. **Check CI**: Ensure all jobs pass2. **Vérifier la CI** : S'assurer que tous les jobs passent

3. **Documentation**: Update docs if necessary3. **Documentation** : Mettre à jour la doc si nécessaire

4. **Dependencies**: Verify dependency compatibility4. **Dependencies** : Vérifier la compatibilité des dépendances



## 📚 References## 📚 Références



- **Sync script**: `.github/scripts/sync-python-versions.py`- **Script de sync** : `scripts/sync-python-versions.py`

- **Check script**: `.github/scripts/check-python-versions.py`- **Script de check** : `scripts/check-python-versions.py`

- **Verification workflow**: `.github/workflows/check-python-versions.yml`- **Workflow de vérification** : `.github/workflows/check-python-versions.yml`

- **Source of truth**: `.github/python-versions.json`- **Source de vérité** : `.github/python-versions.json`



------



**Maintained by**: @titom73  **Maintenu par** : @titom73

**Last updated**: 2024-10-24**Dernière mise à jour** : 2024-10-24

