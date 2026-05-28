import SwiftUI

/// Container for download tabs: EOS, CVP, Path.
struct DownloadView: View {
    @State private var selectedTab: DownloadTab = .eos

    enum DownloadTab: String, CaseIterable {
        case eos = "EOS"
        case cvp = "CVP"
        case path = "Direct Path"

        var icon: String {
            switch self {
            case .eos: return "internaldrive"
            case .cvp: return "cloud"
            case .path: return "link"
            }
        }
    }

    var body: some View {
        VStack(spacing: 0) {
            // Tab bar
            HStack(spacing: 2) {
                ForEach(DownloadTab.allCases, id: \.self) { tab in
                    Button {
                        withAnimation(.easeInOut(duration: 0.15)) {
                            selectedTab = tab
                        }
                    } label: {
                        Label(tab.rawValue, systemImage: tab.icon)
                            .font(.callout.weight(.medium))
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(
                                selectedTab == tab
                                    ? Color.aristaBlue.opacity(0.12)
                                    : Color.clear
                            )
                            .foregroundStyle(
                                selectedTab == tab ? Color.aristaBlue : Color.secondary
                            )
                            .clipShape(RoundedRectangle(cornerRadius: 6))
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal)
            .padding(.vertical, 8)
            .background(.bar)

            Divider()

            switch selectedTab {
            case .eos:
                EosDownloadView()
            case .cvp:
                placeholderView(title: "CVP Download", icon: "cloud.fill", phase: 3)
            case .path:
                placeholderView(title: "Direct Path", icon: "link.circle.fill", phase: 3)
            }
        }
        .navigationTitle("Download")
    }

    private func placeholderView(title: String, icon: String, phase: Int) -> some View {
        VStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(size: 44))
                .foregroundStyle(Color.aristaBlue.opacity(0.3))
            Text(title)
                .font(.title2.weight(.semibold))
            Text("Coming in Phase \(phase)")
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 16)
                .padding(.vertical, 6)
                .background(Color.aristaBlue.opacity(0.08))
                .clipShape(Capsule())
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
