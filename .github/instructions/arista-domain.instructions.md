---
applyTo: 'eos_downloader/**/*.py'
description: 'Domain-specific instructions for Arista EOS and CloudVision integration, covering API interactions, version management, and network automation best practices.'
---

# Arista EOS & CloudVision Domain Instructions

## Your Mission

As GitHub Copilot working on the **eos-downloader** project, you must understand Arista Networks' ecosystem, EOS (Extensible Operating System), and CloudVision Portal (CVP). This tool automates the download and deployment of Arista software packages for network automation workflows.

## Domain Knowledge

### Arista EOS (Extensible Operating System)

**What is EOS?**
EOS is Arista's Linux-based network operating system that powers their switches and routers. It's designed for cloud networking with a focus on programmability, automation, and operational simplicity.

**Key Characteristics:**
- **Single Binary Image**: One image runs across all Arista platforms
- **State Separation**: Configuration and state are separated from the OS
- **Linux Foundation**: Built on standard Linux kernel with full Linux shell access
- **Programmability**: Supports APIs, automation tools, and custom scripting

**Version Format:**
```
MAJOR.MINOR.PATCH[RELEASE_TYPE]

Examples:
- 4.29.3M  → Major: 4, Minor: 29, Patch: 3, Type: M (Maintenance)
- 4.30.1F  → Major: 4, Minor: 30, Patch: 1, Type: F (Feature)
- 4.28.0M  → Major: 4, Minor: 28, Patch: 0, Type: M
```

**Release Types:**

1. **M (Maintenance Release)**
   - Stable releases with bug fixes and security updates
   - Recommended for production environments
   - Conservative feature additions
   - Example: `4.29.3M`

2. **F (Feature Release)**
   - New features and enhancements
   - May include significant changes
   - Test thoroughly before production deployment
   - Example: `4.30.1F`

3. **INT (Internal Release)**
   - Internal testing and development builds
   - Not for production use
   - Used for beta testing new features
   - Example: `4.31.0F-INT`

**Branch Structure:**
```python
# Branch is MAJOR.MINOR
version = "4.29.3M"
branch = "4.29"  # First two numbers

# Code example
from eos_downloader.models.version import EosVersion

version = EosVersion.from_str("4.29.3M")
print(version.branch)  # Output: "4.29"
print(version.major)   # Output: 4
print(version.minor)   # Output: 29
print(version.patch)   # Output: 3
print(version.rtype)   # Output: "M"
```

### EOS Image Formats

Arista provides EOS in multiple formats for different deployment scenarios:

#### 1. Physical Hardware Images

**64-bit (64)**
- Standard image for 64-bit Arista switches
- File extension: `.swi`
- Typical size: 500MB - 1GB
- Example: `EOS-4.29.3M.swi`
- Use case: Physical Arista switches in production

```python
# Download 64-bit image
from eos_downloader.models.data import software_mapping

format_info = software_mapping.EOS["64"]
# {'extension': '.swi', 'prepend': 'EOS64'}
```

**INT (Internal Build)**
- Internal development builds
- File extension: `-INT.swi`
- Example: `EOS-4.29.3M-INT.swi`
- Use case: Testing pre-release features

**2GB-INT**
- 2GB variant of internal builds
- File extension: `-INT.swi`
- Optimized for devices with limited storage

#### 2. Virtual Images (vEOS)

**vEOS (Virtual EOS)**
- Full-featured virtual machine image
- File extensions: `.vmdk`, `.ova`, `.qcow2`
- Typical size: 300MB - 600MB
- Example: `vEOS-4.29.3M.vmdk`
- Use case: VMware, KVM, VirtualBox environments

**vEOS-lab**
- Lightweight version for lab/testing
- Reduced functionality for simulation
- File extension: `.vmdk`, `.qcow2`
- Example: `vEOS-lab-4.29.3M.vmdk`
- Use case: Network simulation labs, GNS3, EVE-NG

```python
# EVE-NG integration
EVE_QEMU_FOLDER_PATH = "/opt/unetlab/addons/qemu/"

# Install vEOS-lab to EVE-NG
def install_to_eveng(image_path: Path, version: str) -> Path:
    """Install vEOS-lab image to EVE-NG."""
    dest_dir = Path(EVE_QEMU_FOLDER_PATH) / f"veos-lab-{version}"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy and rename
    dest_file = dest_dir / "virtioa.qcow2"
    shutil.copy2(image_path, dest_file)

    # Set permissions
    dest_file.chmod(0o755)

    return dest_file
```

#### 3. Container Images (cEOS)

**cEOS (Container EOS)**
- Docker container image
- File extension: `.tar`, `.tar.xz`
- Typical size: 400MB - 800MB
- Example: `cEOS-lab-4.29.3M.tar.xz`
- Use case: Container-based network testing, CI/CD pipelines

**cEOS64**
- 64-bit optimized container version
- Better performance on modern hardware
- Example: `cEOS64-lab-4.29.3M.tar.xz`

```python
# Import cEOS to Docker
def import_ceos_to_docker(
    image_path: Path,
    docker_name: str = "arista/ceos",
    docker_tag: str = "latest"
) -> None:
    """Import cEOS image into Docker.

    Parameters
    ----------
    image_path : Path
        Path to the cEOS tar file
    docker_name : str
        Docker image name
    docker_tag : str
        Docker image tag

    Examples
    --------
    >>> import_ceos_to_docker(
    ...     Path("cEOS-lab-4.29.3M.tar.xz"),
    ...     "arista/ceos",
    ...     "4.29.3M"
    ... )
    """
    import subprocess

    cmd = [
        "docker", "import",
        str(image_path),
        f"{docker_name}:{docker_tag}"
    ]

    subprocess.run(cmd, check=True)
```

#### 4. Documentation & Source

**RN (Release Notes)**
- Release notes and documentation
- File extension: `.pdf`, `.html`
- Example: `RN-4.29.3M.pdf`

**SOURCE**
- Source code files (when available)
- File extension: `.tar.gz`, `.zip`
- Example: `EOS-4.29.3M-source.tar.gz`

### CloudVision Portal (CVP)

**What is CVP?**
CloudVision Portal is Arista's network-wide workload orchestration and automation platform. It provides centralized management, telemetry, and automation for Arista devices.

**Key Features:**
- **Centralized Management**: Manage all Arista devices from one interface
- **Configuration Management**: Deploy and manage configurations at scale
- **Telemetry & Analytics**: Real-time network telemetry and analytics
- **Change Control**: Workflow-based change management
- **Automation**: API-driven automation and integration

**Version Format:**
```
MAJOR.MINOR.PATCH

Examples:
- 2024.3.0  → Year: 2024, Quarter: 3, Patch: 0
- 2024.2.1  → Year: 2024, Quarter: 2, Patch: 1
- 2023.3.1  → Year: 2023, Quarter: 3, Patch: 1
```

**CVP Image Formats:**

1. **OVA (Open Virtual Appliance)**
   - VMware deployment format
   - File extension: `.ova`
   - Example: `cvp-2024.3.0.ova`
   - Use case: VMware ESXi, vCenter environments

2. **RPM (Red Hat Package Manager)**
   - On-premise installation package
   - File extension: `.rpm`
   - Example: `cvp-rpm-installer-2024.3.0.rpm`
   - Use case: On-premise Linux servers

3. **KVM (Kernel-based Virtual Machine)**
   - KVM/QEMU deployment
   - File extension: `-kvm.tgz`
   - Example: `cvp-2024.3.0-kvm.tgz`
   - Use case: KVM/QEMU virtualization

4. **ATSWI (Arista Test Suite Workload Image)**
   - Specialized testing image
   - File extension: `.atswi`
   - Example: `cvp-2024.3.0.atswi`

5. **Upgrade Package**
   - In-place upgrade packages
   - File extension: `.tgz`
   - Example: `cvp-upgrade-2024.3.0.tgz`
   - Use case: Upgrading existing CVP installations

```python
# CVP version parsing
from eos_downloader.models.version import CvpVersion

cvp_version = CvpVersion.from_str("2024.3.0")
print(cvp_version.major)   # Output: 2024
print(cvp_version.minor)   # Output: 3
print(cvp_version.patch)   # Output: 0
print(cvp_version.branch)  # Output: "2024.3"
```

## Arista API Integration

### API Endpoints

Arista provides several API endpoints for software management:

```python
from eos_downloader.defaults import (
    DEFAULT_SOFTWARE_FOLDER_TREE,  # Get software catalog
    DEFAULT_DOWNLOAD_URL,           # Get download links
    DEFAULT_SERVER_SESSION,         # Get session codes
)

# API URLs
CATALOG_URL = "https://www.arista.com/custom_data/api/cvp/getFolderTree/"
DOWNLOAD_URL = "https://www.arista.com/custom_data/api/cvp/getDownloadLink/"
SESSION_URL = "https://www.arista.com/custom_data/api/cvp/getSessionCode/"
```

### Authentication Flow

```python
# 1. User obtains API token from arista.com
#    - Login to arista.com
#    - Go to Profile → Generate API Token
#    - Token is valid for limited time

# 2. Use token in API requests
import requests

token = os.environ.get("ARISTA_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get(CATALOG_URL, headers=headers)

# 3. Handle authentication errors
if response.status_code == 401:
    raise TokenExpiredError(
        "API token expired. Regenerate at arista.com"
    )
```

### XML Catalog Structure

Arista's software catalog is returned as XML:

```xml
<folder>
    <dir label="EOS">
        <dir label="Active Releases">
            <dir label="4.29">
                <dir label="4.29.3M">
                    <dir label="EOS-4.29.3M">
                        <file>EOS-4.29.3M.swi</file>
                        <file>EOS-4.29.3M-INT.swi</file>
                    </dir>
                    <dir label="vEOS-4.29.3M">
                        <file>vEOS-4.29.3M.vmdk</file>
                        <file>vEOS-lab-4.29.3M.vmdk</file>
                    </dir>
                    <dir label="cEOS-4.29.3M">
                        <file>cEOS-lab-4.29.3M.tar.xz</file>
                    </dir>
                </dir>
            </dir>
        </dir>
    </dir>
</folder>
```

### XPath Queries

```python
import xml.etree.ElementTree as ET

# Parse XML catalog
xml_root = ET.fromstring(xml_response)

# Find all EOS versions in Active Releases
xpath_eos = './/dir[@label="Active Releases"]//dir[@label]'
version_nodes = xml_root.findall(xpath_eos)

for node in version_nodes:
    label = node.get("label")
    if EosVersion.regex_version.match(label):
        version = EosVersion.from_str(label)
        print(f"Found version: {version}")

# Find files for specific version
xpath_files = f'.//dir[@label="4.29.3M"]//file'
file_nodes = xml_root.findall(xpath_files)

for file_node in file_nodes:
    filename = file_node.text
    print(f"Available file: {filename}")
```

## Code Patterns for Arista Domain

### Pattern 1: Version Discovery

```python
from typing import List, Optional
from eos_downloader.models.version import EosVersion
from eos_downloader.models.types import ReleaseType

def discover_versions(
    token: str,
    branch: Optional[str] = None,
    rtype: Optional[ReleaseType] = None
) -> List[EosVersion]:
    """Discover available EOS versions from Arista catalog.

    Parameters
    ----------
    token : str
        Arista API token
    branch : Optional[str], optional
        Filter by branch (e.g., "4.29"), by default None
    rtype : Optional[ReleaseType], optional
        Filter by release type ("M" or "F"), by default None

    Returns
    -------
    List[EosVersion]
        List of available versions matching criteria

    Examples
    --------
    >>> # Get all versions in 4.29 branch
    >>> versions = discover_versions(
    ...     token=token,
    ...     branch="4.29"
    ... )

    >>> # Get only maintenance releases
    >>> versions = discover_versions(
    ...     token=token,
    ...     rtype="M"
    ... )

    >>> # Get maintenance releases in 4.29
    >>> versions = discover_versions(
    ...     token=token,
    ...     branch="4.29",
    ...     rtype="M"
    ... )
    """
    from eos_downloader.logics.arista_xml_server import AristaXmlQuerier

    querier = AristaXmlQuerier(token=token)
    versions = querier.available_public_versions(
        package="eos",
        branch=branch,
        rtype=rtype
    )

    return sorted(versions, reverse=True)
```

### Pattern 2: Version Comparison

```python
def get_latest_version(
    versions: List[EosVersion],
    branch: Optional[str] = None
) -> Optional[EosVersion]:
    """Get the latest version from a list.

    Parameters
    ----------
    versions : List[EosVersion]
        List of versions to search
    branch : Optional[str], optional
        Filter by branch, by default None

    Returns
    -------
    Optional[EosVersion]
        Latest version, or None if list is empty

    Examples
    --------
    >>> versions = [
    ...     EosVersion.from_str("4.29.3M"),
    ...     EosVersion.from_str("4.29.2M"),
    ...     EosVersion.from_str("4.30.1F"),
    ... ]
    >>> latest = get_latest_version(versions)
    >>> print(latest)
    4.30.1F

    >>> # Get latest in specific branch
    >>> latest_429 = get_latest_version(versions, branch="4.29")
    >>> print(latest_429)
    4.29.3M
    """
    if not versions:
        return None

    # Filter by branch if specified
    if branch:
        versions = [v for v in versions if v.branch == branch]

    if not versions:
        return None

    # Sort and return latest
    return max(versions)
```

### Pattern 3: Filename Generation

```python
from eos_downloader.models.data import software_mapping

def generate_eos_filename(
    version: str,
    image_format: str
) -> str:
    """Generate standard EOS filename.

    Parameters
    ----------
    version : str
        EOS version (e.g., "4.29.3M")
    image_format : str
        Image format (e.g., "64", "vEOS", "cEOS")

    Returns
    -------
    str
        Generated filename

    Examples
    --------
    >>> generate_eos_filename("4.29.3M", "64")
    'EOS-4.29.3M.swi'

    >>> generate_eos_filename("4.29.3M", "vEOS")
    'vEOS-4.29.3M.vmdk'

    >>> generate_eos_filename("4.29.3M", "cEOS")
    'cEOS-lab-4.29.3M.tar.xz'
    """
    format_info = software_mapping.EOS.get(image_format)
    if not format_info:
        raise ValueError(f"Unknown image format: {image_format}")

    prepend = format_info["prepend"]
    extension = format_info["extension"]

    # Handle special cases
    if image_format == "cEOS":
        return f"cEOS-lab-{version}.tar.xz"
    elif image_format == "vEOS":
        return f"vEOS-{version}.vmdk"
    else:
        return f"{prepend}-{version}{extension}"
```

### Pattern 4: Download with Retry

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import requests

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(requests.RequestException)
)
def download_eos_file(
    url: str,
    token: str,
    output_path: Path
) -> Path:
    """Download EOS file with automatic retry on network errors.

    Retries up to 3 times with exponential backoff (4s, 8s, 10s).

    Parameters
    ----------
    url : str
        Download URL from Arista API
    token : str
        Authentication token
    output_path : Path
        Destination file path

    Returns
    -------
    Path
        Path to downloaded file

    Raises
    ------
    TokenExpiredError
        If authentication fails (no retry)
    DownloadError
        If download fails after all retries
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "eos-downloader"
    }

    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)

        # Don't retry on authentication errors
        if response.status_code == 401:
            raise TokenExpiredError("Token expired")

        response.raise_for_status()

        # Download with progress
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open('wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return output_path

    except requests.HTTPError as e:
        if e.response.status_code == 401:
            raise TokenExpiredError("Token expired") from e
        raise DownloadError(f"HTTP error: {e}") from e
```

## Network Automation Context

### Why This Tool Exists

Network engineers and automation teams need to:
1. **Download EOS images** for device upgrades
2. **Provision lab environments** (EVE-NG, GNS3)
3. **Test network configurations** in containers (cEOS)
4. **Automate CI/CD pipelines** for network validation
5. **Maintain consistent versions** across infrastructure

### Common Workflows

**Workflow 1: Production Upgrade**
```bash
# Download latest maintenance release
ardl get eos --version 4.29.3M --format 64 --output /staging

# Verify checksum
sha256sum EOS-4.29.3M.swi

# Deploy to switches (manual or via automation)
```

**Workflow 2: Lab Setup**
```bash
# Download and install to EVE-NG
ardl get eos --version 4.29.3M --format vEOS-lab --eve-ng

# Lab is ready for testing
```

**Workflow 3: CI/CD Testing**
```bash
# Download and import cEOS
ardl get eos --version 4.29.3M --format cEOS --import-docker

# Run network tests in containers
docker run -it arista/ceos:4.29.3M
```

## Best Practices

### 1. Always Validate Versions

```python
# ✅ Good: Validate before processing
def process_version(version_str: str) -> EosVersion:
    """Process and validate version string."""
    try:
        version = EosVersion.from_str(version_str)
        logger.info(f"Valid version: {version}")
        return version
    except ValueError as e:
        logger.error(f"Invalid version format: {version_str}")
        raise

# ❌ Bad: Assume version is valid
def process_version_bad(version_str):
    parts = version_str.split('.')
    major = int(parts[0])  # May fail
    return major
```

### 2. Handle API Errors Gracefully

```python
# ✅ Good: Specific error handling
try:
    versions = querier.available_public_versions()
except TokenExpiredError:
    console.print("[red]Token expired. Regenerate at arista.com[/red]")
    sys.exit(1)
except requests.RequestException as e:
    console.print(f"[red]Network error: {e}[/red]")
    sys.exit(1)

# ❌ Bad: Generic exception
try:
    versions = querier.available_public_versions()
except Exception as e:
    print(f"Error: {e}")
```

### 3. Use Appropriate Image Formats

```python
# ✅ Good: Guide users to correct format
def recommend_format(use_case: str) -> str:
    """Recommend image format based on use case."""
    recommendations = {
        "production": "64",
        "vmware_lab": "vEOS-lab",
        "eve-ng": "vEOS-lab",
        "docker_test": "cEOS",
        "kvm": "vEOS"
    }

    format_choice = recommendations.get(use_case, "64")
    logger.info(f"Recommended format for {use_case}: {format_choice}")
    return format_choice
```

### 4. Provide Clear User Feedback

```python
from rich.console import Console
from rich.progress import Progress

console = Console()

# ✅ Good: Rich feedback with progress
with Progress() as progress:
    task = progress.add_task(
        "[cyan]Downloading EOS-4.29.3M.swi...",
        total=file_size
    )

    # Download logic with progress updates
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
        progress.update(task, advance=len(chunk))

console.print("[green]✓ Download complete![/green]")

# ❌ Bad: No feedback
download_file(url, output)
print("Done")
```

---

**Remember**: You're building a critical tool for network automation. Understanding Arista's ecosystem, version schemes, and deployment patterns is essential for creating reliable, user-friendly functionality.
