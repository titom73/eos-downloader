import SwiftUI

/// Placeholder view for version information queries.
/// Full implementation planned for Phase 2.
struct InfoView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "info.circle")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)
            Text("Version Information")
                .font(.title2)
            Text("Query available EOS and CVP versions.\nComing in Phase 2.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .navigationTitle("Info")
    }
}
