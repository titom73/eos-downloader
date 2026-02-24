import SwiftUI

/// Banner showing an indeterminate spinner with a cancel button.
struct ProgressBannerView: View {
    let message: String
    let onCancel: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            ProgressView()
                .controlSize(.small)
            Text(message)
                .font(.callout)
            Spacer()
            Button("Cancel", role: .destructive) {
                onCancel()
            }
            .buttonStyle(.bordered)
            .controlSize(.small)
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(.ultraThinMaterial)
    }
}
