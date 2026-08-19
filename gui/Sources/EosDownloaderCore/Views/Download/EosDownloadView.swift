import SwiftUI

/// EOS download form view.
struct EosDownloadView: View {
    @EnvironmentObject private var state: DownloadState
    @AppStorage("logPanelVisible") private var logPanelVisible: Bool = true

    var body: some View {
        HStack(spacing: 0) {
            // Left: Form + progress bar
            VStack(spacing: 0) {
                Form {
                    formSection
                    dockerSection
                    flagsSection
                    actionSection
                }
                .formStyle(.grouped)

                if state.isRunning {
                    DownloadProgressView(
                        progress: state.progress,
                        onCancel: { state.cancelDownload() }
                    )
                    .transition(.move(edge: .bottom).combined(with: .opacity))
                    .animation(.easeInOut(duration: 0.25), value: state.isRunning)
                }
            }
            .frame(minWidth: 360, idealWidth: 420)

            // Right: Log panel (collapsible)
            if logPanelVisible {
                Divider()
                VStack(spacing: 0) {
                    logHeader
                    Divider()
                    LogOutputView(lines: state.logLines)
                }
                .frame(minWidth: 300)
                .transition(.move(edge: .trailing).combined(with: .opacity))
            }
        }
        .animation(.easeInOut(duration: 0.2), value: logPanelVisible)
        .cliErrorAlert(error: $state.currentError)
        .toolbar {
            ToolbarItem(placement: .automatic) {
                Button {
                    logPanelVisible.toggle()
                } label: {
                    Image(systemName: "sidebar.right")
                        .symbolVariant(logPanelVisible ? .fill : .none)
                }
                .help(logPanelVisible ? "Hide log panel" : "Show log panel")
            }
        }
    }

    // MARK: - Log Header

    private var logHeader: some View {
        HStack(spacing: 8) {
            Label("Output", systemImage: "terminal")
                .font(.callout.weight(.medium))
                .foregroundStyle(.secondary)
            Spacer()
            if !state.logLines.isEmpty {
                Button {
                    state.logLines.removeAll()
                } label: {
                    Image(systemName: "trash")
                        .font(.caption)
                }
                .buttonStyle(.plain)
                .foregroundStyle(.secondary)
                .help("Clear log")
            }
            // Toggle button to collapse/expand the panel
            Button {
                logPanelVisible.toggle()
            } label: {
                Image(systemName: logPanelVisible ? "sidebar.right" : "sidebar.right")
                    .font(.caption)
                    .symbolVariant(logPanelVisible ? .none : .fill)
            }
            .buttonStyle(.plain)
            .foregroundStyle(.secondary)
            .help(logPanelVisible ? "Hide log panel" : "Show log panel")
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(.bar)
    }

    // MARK: - Form Sections

    @ViewBuilder
    private var formSection: some View {
        Section {
            Picker("Format", selection: $state.selectedFormat) {
                ForEach(DownloadState.eosFormats, id: \.self) { fmt in
                    Text(fmt).tag(fmt)
                }
            }

            Toggle("Use Latest Version", isOn: $state.useLatest)
                .tint(Color.aristaBlue)

            if !state.useLatest {
                TextField("Version (e.g. 4.29.3M)", text: $state.version)
            }

            TextField("Branch (e.g. 4.29)", text: $state.branch)

            Picker("Release Type", selection: $state.releaseType) {
                ForEach(DownloadState.releaseTypes, id: \.self) { rt in
                    Text(rt == "M" ? "Maintenance (M)" : "Feature (F)").tag(rt)
                }
            }
        } header: {
            Label("Image", systemImage: "internaldrive.fill")
                .foregroundStyle(Color.aristaBlue)
        }

        Section {
            HStack {
                TextField("Output Directory", text: $state.outputPath)
                FileBrowserButton(selectedPath: $state.outputPath)
            }
        } header: {
            Label("Output", systemImage: "folder.fill")
                .foregroundStyle(Color.aristaBlue)
        }
    }

    @ViewBuilder
    private var dockerSection: some View {
        Section {
            Toggle("Import to Docker", isOn: $state.importDocker)
                .tint(Color.aristaBlue)

            if state.importDocker {
                TextField("Image Name", text: $state.dockerName)
                TextField("Image Tag", text: $state.dockerTag)
            }
        } header: {
            Label("Docker Import", systemImage: "shippingbox.fill")
                .foregroundStyle(.indigo)
        }
    }

    @ViewBuilder
    private var flagsSection: some View {
        Section {
            Toggle("Dry Run", isOn: $state.dryRun)
                .tint(.orange)
            Toggle("Force Download", isOn: $state.force)
                .tint(.red)
            Toggle("EVE-NG Provisioning", isOn: $state.eveNg)
                .tint(Color.aristaBlue)
                .help("Requires EVE-NG server access")
        } header: {
            Label("Options", systemImage: "slider.horizontal.3")
                .foregroundStyle(.secondary)
        }
    }

    @ViewBuilder
    private var actionSection: some View {
        Section {
            Button {
                state.startDownload()
            } label: {
                Label(
                    state.isRunning ? "Downloading..." : "Download",
                    systemImage: state.isRunning
                        ? "progress.indicator"
                        : "arrow.down.circle.fill"
                )
                .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(Color.aristaBlue)
            .controlSize(.large)
            .disabled(!isFormValid || state.isRunning)
        }
    }

    private var isFormValid: Bool {
        if state.useLatest { return true }
        return !state.version.isEmpty || !state.branch.isEmpty
    }
}
