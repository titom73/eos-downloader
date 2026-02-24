import SwiftUI

/// Button that opens a folder picker and writes the selected path.
struct FileBrowserButton: View {
    @Binding var selectedPath: String

    var body: some View {
        Button {
            selectFolder()
        } label: {
            Image(systemName: "folder")
        }
        .help("Browse for output directory")
    }

    private func selectFolder() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false
        panel.canCreateDirectories = true
        panel.prompt = "Select Output Directory"

        if panel.runModal() == .OK, let url = panel.url {
            selectedPath = url.path
        }
    }
}
