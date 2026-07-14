import SwiftUI

/// Root view with a fixed-width sidebar and detail panel.
/// DownloadState is lifted here so InfoView can pre-fill the form via "Use in Download".
public struct ContentView: View {
    @State private var selectedSection: SidebarSection = .download
    @StateObject private var sharedDownloadState = DownloadState()

    public init() {}

    public var body: some View {
        HStack(spacing: 0) {
            // Sidebar
            SidebarView(selection: $selectedSection)
                .frame(width: 220)

            Divider()

            // Detail
            detailView
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .environmentObject(sharedDownloadState)
    }

    @ViewBuilder
    private var detailView: some View {
        switch selectedSection {
        case .download:
            DownloadView()
        case .info:
            InfoView(onNavigateToDownload: {
                withAnimation { selectedSection = .download }
            })
        case .settings:
            SettingsView()
        case .debug:
            DebugView()
        }
    }
}
