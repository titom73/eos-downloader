import SwiftUI

/// Placeholder view for debug tools.
/// Full implementation planned for Phase 2.
struct DebugView: View {
    var body: some View {
        VStack(spacing: 20) {
            ZStack {
                Circle()
                    .fill(.orange.opacity(0.1))
                    .frame(width: 80, height: 80)
                Image(systemName: "ladybug.fill")
                    .font(.system(size: 40))
                    .foregroundStyle(.orange)
            }

            Text("Debug Tools")
                .font(.title2.weight(.semibold))

            Text("Inspect XML data and validate token.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)

            Text("Coming in Phase 2")
                .font(.subheadline)
                .foregroundStyle(.orange)
                .padding(.horizontal, 16)
                .padding(.vertical, 6)
                .background(.orange.opacity(0.08))
                .clipShape(Capsule())
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .navigationTitle("Debug")
    }
}
