# Frequently Asked Questions

## EVE-NG with OpenSSL issue.

On EVE-NG, you may have to install/upgrade __pyOpenSSL__ in version `23.0.0`:

```bash
# Error when running ardl: AttributeError: module 'lib' has no attribute 'X509_V_FLAG_CB_ISSUER_CHECK'

$ pip install pyopenssl --upgrade
```
