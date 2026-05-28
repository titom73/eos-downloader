import SwiftUI

/// Displays a filterable list of available EOS/CVP versions.
/// Includes a "Use in Download" shortcut that pre-fills EosDownloadView.
struct VersionListView: View {
    @ObservedObject var infoState: InfoState
    @EnvironmentObject private var downloadState: DownloadState
    let onNavigateToDownload: () -> Void

    var body: some View {
        VStack(spacing: 0) {
            filterBar
            Divider()
            content
        }
        .cliErrorAlert(error: $infoState.versionsError)
    }

    // MARK: - Filter bar

    /// Versions sorted semantically (newest first).
    private var sortedVersions: [VersionEntry] {
        infoState.versions.sorted {
            let a = $0.versionSortKey
            let b = $1.versionSortKey
            if a.0 != b.0 { return a.0 > b.0 }
            if a.1 != b.1 { return a.1 > b.1 }
            return a.2 > b.2
        }
    }

    private var filterBar: some View {
        HStack(spacing: 12) {
            Picker("Package", selection: $infoState.package) {
                Text("EOS").tag("eos")
                Text("CVP").tag("cvp")
            }
            .pickerStyle(.segmented)
            .labelsHidden()  // label is redundant — EOS/CVP segments are self-explanatory
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
                Task { await infoState.fetchVersions() }
            } label: {
                Label("Query", systemImage: "magnifyingglass")
            }
            .buttonStyle(.borderedProminent)
            .tint(Color.aristaBlue)
            .disabled(infoState.isLoadingVersions)

            if infoState.isLoadingVersions {
                ProgressView().controlSize(.small)
            }

            Spacer()

            if !infoState.versions.isEmpty {
                Text("\(infoState.versions.count) version(s)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(.bar)
    }

    // MARK: - Content

    @ViewBuilder
    private var content: some View {
        if infoState.isLoadingVersions {
            loadingView("Fetching versions...")
        } else if infoState.versions.isEmpty {
            emptyView(
                icon: "list.bullet.rectangle",
                message: "Select filters and click Query"
            )
        } else {
            List(sortedVersions) { entry in
                versionRow(entry)
            }
            .listStyle(.plain)
        }
    }

    private func versionRow(_ entry: VersionEntry) -> some View {
        HStack(spacing: 12) {
            // Version
            Text(entry.version)
                .font(.system(.body, design: .monospaced).weight(.medium))
                .frame(width: 110, alignment: .leading)

            // Branch
            Text(entry.branch)
                .font(.system(.body, design: .monospaced))
                .foregroundStyle(.secondary)
                .frame(width: 80, alignment: .leading)

            // Release type badge
            releaseTypeBadge(entry.releaseType)

            Spacer()

            // Use in Download
            Button("Use in Download") {
                downloadState.version = entry.version
                downloadState.useLatest = false
                downloadState.branch = entry.branch
                downloadState.releaseType = entry.releaseType == "M" ? "M" : "F"
                onNavigateToDownload()
            }
            .buttonStyle(.bordered)
            .controlSize(.small)
            .tint(Color.aristaBlue)
        }
        .padding(.vertical, 2)
    }

    @ViewBuilder
    private func releaseTypeBadge(_ type: String) -> some View {
        Text(type)
            .font(.caption.weight(.semibold))
            .padding(.horizontal, 8)
            .padding(.vertical, 2)
            .background(type == "M" ? Color.green.opacity(0.1) : Color.aristaBlue.opacity(0.1))
            .foregroundStyle(type == "M" ? Color.green : Color.aristaBlue)
            .clipShape(Capsule())
    }

    private func loadingView(_ message: String) -> some View {
        VStack(spacing: 12) {
            ProgressView()
            Text(message)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private func emptyView(icon: String, message: String) -> some View {
        VStack(spacing: 12) {
            Image(systemName: icon)
                .font(.title)
                .foregroundStyle(.quaternary)
            Text(message)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
