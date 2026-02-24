import SwiftUI

/// EOS download form view — Phase 1 MVP.
struct EosDownloadView: View {
    @StateObject private var state = DownloadState()
    @State private var showFileBrowser = false

    var body: some View {
        HSplitView {
            // Left: Form
            Form {
                formSection
                dockerSection
                flagsSection
                actionSection
            }
            .formStyle(.grouped)
            .frame(minWidth: 350)

            // Right: Log output
            LogOutputView(lines: state.logLines)
                .frame(minWidth: 300)
        }
        .cliErrorAlert(error: $state.currentError)
    }

    // MARK: - Form Sections

    @ViewBuilder
    private var formSection: some View {
        Section("Image") {
            Picker("Format", selection: $state.selectedFormat) {
                ForEach(DownloadState.eosFormats, id: \.self) { fmt in
                    Text(fmt).tag(fmt)
                }
            }

            Toggle("Use Latest Version", isOn: $state.useLatest)

            if !state.useLatest {
                TextField("Version (e.g. 4.29.3M)", text: $state.version)
            }

            TextField("Branch (e.g. 4.29)", text: $state.branch)

            Picker("Release Type", selection: $state.releaseType) {
                ForEach(DownloadState.releaseTypes, id: \.self) { rt in
                    Text(rt == "M" ? "Maintenance (M)" : "Feature (F)").tag(rt)
                }
            }
        }

        Section("Output") {
            HStack {
                TextField("Output Directory", text: $state.outputPath)
                FileBrowserButton(selectedPath: $state.outputPath)
            }
        }
    }

    @ViewBuilder
    private var dockerSection: some View {
        Section("Docker Import") {
            Toggle("Import to Docker", isOn: $state.importDocker)

            if state.importDocker {
                TextField("Image Name", text: $state.dockerName)
                TextField("Image Tag", text: $state.dockerTag)
            }
        }
    }

    @ViewBuilder
    private var flagsSection: some View {
        Section("Options") {
            Toggle("Dry Run", isOn: $state.dryRun)
            Toggle("Force Download", isOn: $state.force)
            Toggle("EVE-NG Provisioning", isOn: $state.eveNg)
                .help("Requires EVE-NG server access")
        }
    }

    @ViewBuilder
    private var actionSection: some View {
        Section {
            if state.isRunning {
                HStack {
                    ProgressView()
                        .controlSize(.small)
                    Text("Downloading...")
                    Spacer()
                    Button("Cancel", role: .destructive) {
                        state.cancelDownload()
                    }
                }
            } else {
                Button("Download") {
                    state.startDownload()
                }
                .buttonStyle(.borderedProminent)
                .disabled(!isFormValid)
            }
        }
    }

    private var isFormValid: Bool {
        if state.useLatest { return true }
        return !state.version.isEmpty || !state.branch.isEmpty
    }
}
