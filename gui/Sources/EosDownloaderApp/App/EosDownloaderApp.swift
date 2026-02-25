import SwiftUI
import EosDownloaderCore

@main
struct EosDownloaderApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 860, minHeight: 540)
                .frame(idealWidth: 1000, idealHeight: 620)
        }

        #if os(macOS)
        Settings {
            SettingsView()
                .frame(minWidth: 500, minHeight: 300)
        }
        #endif
    }
}
