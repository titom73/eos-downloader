import SwiftUI

/// Container for Info tabs: Versions, Latest, Mapping.
struct InfoView: View {
    @StateObject private var infoState = InfoState()
    @EnvironmentObject private var downloadState: DownloadState
    let onNavigateToDownload: () -> Void

    @State private var selectedTab: InfoTab = .versions

    enum InfoTab: String, CaseIterable {
        case versions = "Versions"
        case latest = "Latest"
        case mapping = "Mapping"

        var icon: String {
            switch self {
            case .versions: return "list.bullet"
            case .latest: return "star.circle"
            case .mapping: return "rectangle.grid.2x2"
            }
        }
    }

    var body: some View {
        VStack(spacing: 0) {
            // Tab bar — same style as DownloadView
            HStack(spacing: 2) {
                ForEach(InfoTab.allCases, id: \.self) { tab in
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
            case .versions:
                VersionListView(
                    infoState: infoState,
                    onNavigateToDownload: onNavigateToDownload
                )
                .environmentObject(downloadState)
            case .latest:
                LatestVersionView(
                    infoState: infoState,
                    onNavigateToDownload: onNavigateToDownload
                )
                .environmentObject(downloadState)
            case .mapping:
                MappingView(infoState: infoState)
            }
        }
        .navigationTitle("Info")
    }
}
