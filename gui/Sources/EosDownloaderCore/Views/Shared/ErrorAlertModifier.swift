import SwiftUI

/// ViewModifier that presents CLIError as a native alert.
struct CLIErrorAlertModifier: ViewModifier {
    @Binding var error: CLIError?

    func body(content: Content) -> some View {
        content
            .alert(
                "Error",
                isPresented: Binding(
                    get: { error != nil },
                    set: { if !$0 { error = nil } }
                ),
                presenting: error
            ) { _ in
                Button("OK", role: .cancel) {
                    error = nil
                }
            } message: { cliError in
                VStack {
                    Text(cliError.localizedDescription)
                    if let suggestion = cliError.recoverySuggestion {
                        Text(suggestion)
                            .font(.caption)
                    }
                }
            }
    }
}

extension View {
    /// Attach a CLIError alert to any view.
    func cliErrorAlert(error: Binding<CLIError?>) -> some View {
        modifier(CLIErrorAlertModifier(error: error))
    }
}
