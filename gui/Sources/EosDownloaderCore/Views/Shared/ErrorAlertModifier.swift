import SwiftUI

/// ViewModifier that presents CLIError as a scrollable sheet dialog.
struct CLIErrorAlertModifier: ViewModifier {
    @Binding var error: CLIError?

    func body(content: Content) -> some View {
        content
            .sheet(isPresented: Binding(
                get: { error != nil },
                set: { if !$0 { error = nil } }
            )) {
                if let cliError = error {
                    ErrorSheetView(error: cliError) {
                        error = nil
                    }
                }
            }
    }
}

/// Sheet view for displaying CLI errors with full scrollable details.
private struct ErrorSheetView: View {
    let error: CLIError
    let onDismiss: () -> Void

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack(spacing: 10) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.title2)
                    .foregroundStyle(.red)
                Text(error.title)
                    .font(.headline)
                Spacer()
            }
            .padding()
            .background(Color.red.opacity(0.06))

            Divider()

            // Body
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    // Summary
                    Text(error.summary)
                        .font(.body)
                        .textSelection(.enabled)

                    // Recovery suggestion
                    if let suggestion = error.recoverySuggestion {
                        HStack(alignment: .top, spacing: 8) {
                            Image(systemName: "lightbulb.fill")
                                .foregroundStyle(.orange)
                                .font(.callout)
                            Text(suggestion)
                                .font(.callout)
                                .foregroundStyle(.secondary)
                        }
                        .padding(10)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.orange.opacity(0.06))
                        .clipShape(RoundedRectangle(cornerRadius: 6))
                    }

                    // Full stderr (collapsible)
                    if let detail = error.detailText, !detail.isEmpty {
                        DisclosureGroup("Full error output") {
                            Text(detail)
                                .font(.system(.caption, design: .monospaced))
                                .textSelection(.enabled)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(8)
                                .background(Color(nsColor: .textBackgroundColor))
                                .clipShape(RoundedRectangle(cornerRadius: 4))
                        }
                        .font(.callout)
                        .foregroundStyle(.secondary)
                    }
                }
                .padding()
            }

            Divider()

            // Footer
            HStack {
                Spacer()
                Button("OK") {
                    onDismiss()
                }
                .buttonStyle(.borderedProminent)
                .tint(Color.aristaBlue)
                .keyboardShortcut(.defaultAction)
            }
            .padding()
        }
        .frame(minWidth: 440, idealWidth: 500, minHeight: 220, idealHeight: 340)
    }
}

extension View {
    /// Attach a CLIError sheet to any view.
    func cliErrorAlert(error: Binding<CLIError?>) -> some View {
        modifier(CLIErrorAlertModifier(error: error))
    }
}
