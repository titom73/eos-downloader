# Technical Debt Remediation: Command Injection Vulnerability Fix

## Summary Table

| Item | Overview | Ease | Impact | Risk | Status |
|------|----------|------|--------|------|--------|
| os.system() Command Injection | Replace `os.system()` with `subprocess.run()` using list arguments to prevent shell injection | 3 | 🔴 5 | 🔴 5 | ✅ Fixed |

## Detailed Plan

### Overview

The codebase contained command injection vulnerabilities through the use of `os.system()` with string interpolation. This allowed potential shell metacharacter injection via user-controlled inputs like file paths, docker image names, and tags.

**Vulnerable Code Locations:**
- [download.py#L656](../../../eos_downloader/logics/download.py#L656): Docker import command
- [download.py#L749](../../../eos_downloader/logics/download.py#L749): qemu-img convert command  
- [download.py#L759](../../../eos_downloader/logics/download.py#L759): unl_wrapper command

### Explanation

**Problem:**
The `os.system()` function executes commands through the shell, which interprets special characters like `;`, `|`, `&&`, `$()`, etc. When user-controlled data is interpolated into command strings, attackers can inject arbitrary commands.

Example of vulnerable code:
```python
# VULNERABLE - shell injection possible
cmd = f"$(which docker) import {local_file_path} {docker_name}:{docker_tag}"
os.system(cmd)
```

If `docker_name` contained `; rm -rf /`, the shell would execute the malicious command.

**Solution:**
Replace `os.system()` with `subprocess.run()` using a list of arguments instead of a shell string. This bypasses the shell entirely, treating each argument as a literal value:

```python
# SECURE - no shell interpretation
docker_path = shutil.which("docker")
subprocess.run([docker_path, "import", str(local_file_path), f"{docker_name}:{docker_tag}"], check=True)
```

### Requirements

- Python 3.9+ (already met)
- `subprocess` module (standard library)
- `shutil` module (standard library)
- Update related tests to mock `subprocess.run` instead of `os.system`

### Implementation Steps

1. ✅ **Replace docker import os.system() call**
   - Use `shutil.which("docker")` to get docker binary path
   - Use `subprocess.run()` with list arguments
   - Add proper error handling with `subprocess.CalledProcessError`

2. ✅ **Replace qemu-img convert os.system() call**
   - Use `shutil.which("qemu-img")` to get binary path
   - Use `subprocess.run()` with list arguments
   - Add validation that binary exists before calling

3. ✅ **Replace unl_wrapper os.system() call**
   - Use `subprocess.run()` with list arguments
   - Add check for wrapper existence before calling

4. ✅ **Update tests**
   - Replace `@patch("os.system")` with `@patch("subprocess.run")`
   - Update test assertions to verify `subprocess.run` calls
   - Add `@patch("shutil.which")` where binary path is needed

### Testing

- ✅ All 322 unit tests passing
- ✅ All integration tests passing
- ✅ 91% code coverage maintained
- ✅ flake8, pylint (10.00/10), mypy all passing

**Test Changes Made:**
- Updated `test_import_docker` to mock `subprocess.run`
- Updated `test_provision_eve` to mock `subprocess.run` and `shutil.which`
- Updated `test_import_docker_force_reimport` to mock `subprocess.run`
- Updated `test_import_docker_force_download_flag` to mock `subprocess.run`
- Updated `test_provision_eve_with_noztp` to mock `subprocess.run`
- Updated `test_provision_eve_url_none_raises_error` to mock `subprocess.run`
- Updated `test_provision_eve_dry_run_mode` to mock `subprocess.run`

### Security Impact

| Before | After |
|--------|-------|
| Shell command injection possible | No shell interpretation |
| User input could execute arbitrary commands | User input treated as literal arguments |
| CWE-78: Improper Neutralization of Special Elements | OWASP compliant |

### Related

- **GitHub Security Alert**: Code scanning alert #35
- **CWE Reference**: [CWE-78: OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
- **OWASP Reference**: [Command Injection](https://owasp.org/www-community/attacks/Command_Injection)
