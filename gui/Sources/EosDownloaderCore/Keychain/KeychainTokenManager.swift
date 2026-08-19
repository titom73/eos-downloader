import Foundation
import Security

/// Manages the Arista API token in the macOS Keychain.
/// Service: "com.arista.eos-downloader", Account: "arista-api-token"
enum KeychainTokenManager {

    private static let service = "com.arista.eos-downloader"
    private static let account = "arista-api-token"

    /// Read the token from Keychain. Returns nil if not found.
    static func readToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess,
              let data = result as? Data,
              let token = String(data: data, encoding: .utf8) else {
            return nil
        }
        return token
    }

    /// Save or update the token in Keychain.
    static func saveToken(_ token: String) throws {
        guard let data = token.data(using: .utf8) else { return }

        // Try to update existing item first
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]

        let attributes: [String: Any] = [
            kSecValueData as String: data
        ]

        let updateStatus = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)

        if updateStatus == errSecItemNotFound {
            // Item doesn't exist, add it
            var addQuery = query
            addQuery[kSecValueData as String] = data
            let addStatus = SecItemAdd(addQuery as CFDictionary, nil)
            guard addStatus == errSecSuccess else {
                throw CLIError.processTerminated(
                    exitCode: -1,
                    stderr: "Keychain save failed with status: \(addStatus)"
                )
            }
        } else if updateStatus != errSecSuccess {
            throw CLIError.processTerminated(
                exitCode: -1,
                stderr: "Keychain update failed with status: \(updateStatus)"
            )
        }
    }

    /// Delete the token from Keychain.
    static func deleteToken() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
        SecItemDelete(query as CFDictionary)
    }

    /// Read token or throw CLIError.tokenMissing.
    static func requireToken() throws -> String {
        guard let token = readToken(), !token.isEmpty else {
            throw CLIError.tokenMissing
        }
        return token
    }
}
