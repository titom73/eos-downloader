import SwiftUI
import EosDownloaderCore

@main
struct EosDownloaderApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 800, minHeight: 500)
        }
        .windowResizability(.contentMinSize)

        #if os(macOS)
        Settings {
            SettingsView()
        }
        #endif
    }
}
