import SwiftUI

/// Settings view for managing the Arista API token and ardl binary path.
public struct SettingsView: View {
    @State private var tokenInput: String = ""
    @State private var hasSavedToken: Bool = false
    @State private var statusMessage: String?
    @State private var customBinaryPath: String = ""

    public init() {}

    public var body: some View {
        Form {
            Section("Arista API Token") {
                SecureField("Paste your API token", text: $tokenInput)
                    .textFieldStyle(.roundedBorder)

                HStack {
                    Button("Save to Keychain") {
                        saveToken()
                    }
                    .disabled(tokenInput.isEmpty)

                    Button("Delete from Keychain", role: .destructive) {
                        deleteToken()
                    }
                    .disabled(!hasSavedToken)

                    Spacer()

                    if hasSavedToken {
                        Label("Token stored", systemImage: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                    } else {
                        Label("No token stored", systemImage: "xmark.circle")
                            .foregroundStyle(.secondary)
                    }
                }

                if let statusMessage {
                    Text(statusMessage)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Text("Your token is stored securely in the macOS Keychain and passed to ardl via the ARISTA_TOKEN environment variable.")
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }

            Section("ardl Binary") {
                HStack {
                    TextField("Custom ardl path (optional)", text: $customBinaryPath)
                        .textFieldStyle(.roundedBorder)
                    FileBrowserButton(selectedPath: $customBinaryPath)
                }

                Button("Reset to Bundled Binary") {
                    customBinaryPath = ""
                    UserDefaults.standard.removeObject(forKey: "customArdlPath")
                }
                .disabled(customBinaryPath.isEmpty)

                Text("Leave empty to use the bundled ardl binary. Set a custom path if you have ardl installed separately.")
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }
        }
        .formStyle(.grouped)
        .navigationTitle("Settings")
        .onAppear {
            loadInitialState()
        }
        .onChange(of: customBinaryPath) { newValue in
            if newValue.isEmpty {
                UserDefaults.standard.removeObject(forKey: "customArdlPath")
            } else {
                UserDefaults.standard.set(newValue, forKey: "customArdlPath")
            }
        }
    }

    private func loadInitialState() {
        hasSavedToken = KeychainTokenManager.readToken() != nil
        customBinaryPath = UserDefaults.standard.string(forKey: "customArdlPath") ?? ""
    }

    private func saveToken() {
        do {
            try KeychainTokenManager.saveToken(tokenInput)
            hasSavedToken = true
            tokenInput = ""
            statusMessage = "Token saved successfully."
        } catch {
            statusMessage = "Failed to save token: \(error.localizedDescription)"
        }
    }

    private func deleteToken() {
        KeychainTokenManager.deleteToken()
        hasSavedToken = false
        statusMessage = "Token deleted."
    }
}
