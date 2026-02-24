import SwiftUI

/// Placeholder view for debug tools.
/// Full implementation planned for Phase 2.
struct DebugView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "ladybug")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)
            Text("Debug Tools")
                .font(.title2)
            Text("Inspect XML data and validate token.\nComing in Phase 2.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .navigationTitle("Debug")
    }
}
