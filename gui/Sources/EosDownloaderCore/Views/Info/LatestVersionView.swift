import SwiftUI

/// Displays the latest available version for a given package/branch/type.
/// Provides copy-to-clipboard and "Use in Download" shortcuts.
struct LatestVersionView: View {
    @ObservedObject var infoState: InfoState
    @EnvironmentObject private var downloadState: DownloadState
    let onNavigateToDownload: () -> Void

    @State private var copied = false

    var body: some View {
        VStack(spacing: 0) {
            filterBar
            Divider()
            content
        }
        .cliErrorAlert(error: $infoState.latestError)
    }

    // MARK: - Filter bar

    private var filterBar: some View {
        HStack(spacing: 12) {
            Picker("Package", selection: $infoState.package) {
                Text("EOS").tag("eos")
                Text("CVP").tag("cvp")
            }
            .pickerStyle(.segmented)
            .labelsHidden()
            .frame(width: 110)

            TextField("Branch (e.g. 4.29)", text: $infoState.branch)
                .textFieldStyle(.roundedBorder)
                .frame(width: 150)

            // Type picker is only meaningful for EOS (CVP has no M/F releases)
            if infoState.package == "eos" {
                Picker("Type", selection: $infoState.releaseType) {
                    Text("Feature (F)").tag("F")
                    Text("Maintenance (M)").tag("M")
                }
                .labelsHidden()
                .frame(width: 150)
            }

            Button {
                Task { await infoState.fetchLatest() }
            } label: {
                Label("Get Latest", systemImage: "arrow.clockwise")
            }
            .buttonStyle(.borderedProminent)
            .tint(Color.aristaBlue)
            .disabled(infoState.isLoadingLatest)

            if infoState.isLoadingLatest {
                ProgressView().controlSize(.small)
            }

            Spacer()
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(.bar)
    }

    // MARK: - Content

    @ViewBuilder
    private var content: some View {
        if infoState.isLoadingLatest {
            VStack(spacing: 12) {
                ProgressView()
                Text("Querying latest version...")
                    .foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)

        } else if let latest = infoState.latest {
            VStack(spacing: 28) {
                Spacer()

                // Version label
                VStack(spacing: 6) {
                    Text("Latest \(infoState.package.uppercased()) Version")
                        .font(.callout)
                        .foregroundStyle(.secondary)
                        .textCase(.uppercase)
                        .kerning(0.6)

                    Text(latest.version)
                        .font(.system(size: 52, weight: .bold, design: .monospaced))
                        .foregroundStyle(Color.aristaBlue)
                        .textSelection(.enabled)
                }

                // Action buttons
                HStack(spacing: 12) {
                    Button {
                        NSPasteboard.general.clearContents()
                        NSPasteboard.general.setString(latest.version, forType: .string)
                        withAnimation { copied = true }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                            withAnimation { copied = false }
                        }
                    } label: {
                        Label(
                            copied ? "Copied!" : "Copy",
                            systemImage: copied ? "checkmark.circle.fill" : "doc.on.doc"
                        )
                    }
                    .buttonStyle(.bordered)
                    .tint(copied ? .green : nil)

                    Button {
                        downloadState.version = latest.version
                        downloadState.useLatest = false
                        onNavigateToDownload()
                    } label: {
                        Label("Use in Download", systemImage: "arrow.down.circle.fill")
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(Color.aristaBlue)
                }

                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)

        } else {
            VStack(spacing: 12) {
                Image(systemName: "star.circle")
                    .font(.title)
                    .foregroundStyle(.quaternary)
                Text("Select filters and click Get Latest")
                    .foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }
}
