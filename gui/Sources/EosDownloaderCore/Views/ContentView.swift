import SwiftUI

/// Root view using NavigationSplitView (macOS 13+).
public struct ContentView: View {
    @State private var selectedSection: SidebarSection? = .download

    public init() {}

    public var body: some View {
        NavigationSplitView {
            SidebarView(selection: $selectedSection)
        } detail: {
            switch selectedSection {
            case .download:
                DownloadView()
            case .info:
                InfoView()
            case .settings:
                SettingsView()
            case .debug:
                DebugView()
            case nil:
                Text("Select a section")
                    .foregroundStyle(.secondary)
            }
        }
        .navigationTitle("EOS Downloader")
    }
}
