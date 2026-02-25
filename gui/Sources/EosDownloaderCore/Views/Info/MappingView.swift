import SwiftUI

/// Identifiable wrapper to display [String: MappingEntry] in a List.
private struct MappingRow: Identifiable {
    let id: String       // format key, e.g. "64", "vEOS-lab"
    let fileExtension: String
    let prepend: String
}

/// Displays the image format mapping table for EOS or CVP.
struct MappingView: View {
    @ObservedObject var infoState: InfoState

    private var rows: [MappingRow] {
        infoState.mapping
            .map { key, val in MappingRow(id: key, fileExtension: val.fileExtension, prepend: val.prepend) }
            .sorted { $0.id < $1.id }
    }

    var body: some View {
        VStack(spacing: 0) {
            filterBar
            Divider()
            content
        }
        .cliErrorAlert(error: $infoState.mappingError)
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

            Button {
                Task { await infoState.fetchMapping() }
            } label: {
                Label("Load Mapping", systemImage: "arrow.clockwise")
            }
            .buttonStyle(.borderedProminent)
            .tint(Color.aristaBlue)
            .disabled(infoState.isLoadingMapping)

            if infoState.isLoadingMapping {
                ProgressView().controlSize(.small)
            }

            Spacer()

            if !rows.isEmpty {
                Text("\(rows.count) format(s)")
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
        if infoState.isLoadingMapping {
            VStack(spacing: 12) {
                ProgressView()
                Text("Loading mapping...")
                    .foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)

        } else if rows.isEmpty {
            VStack(spacing: 12) {
                Image(systemName: "rectangle.grid.2x2")
                    .font(.title)
                    .foregroundStyle(.quaternary)
                Text("Select a package and click Load Mapping")
                    .foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)

        } else {
            // Header row
            VStack(spacing: 0) {
                HStack(spacing: 0) {
                    columnHeader("Format", width: 150)
                    columnHeader("Extension", width: 120)
                    columnHeader("Prepend", width: nil)
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 6)
                .background(Color(nsColor: .controlBackgroundColor))

                Divider()

                List(rows) { row in
                    HStack(spacing: 0) {
                        Text(row.id)
                            .font(.system(.body, design: .monospaced).weight(.medium))
                            .frame(width: 150, alignment: .leading)

                        Text(row.fileExtension)
                            .font(.system(.body, design: .monospaced))
                            .foregroundStyle(.secondary)
                            .frame(width: 120, alignment: .leading)

                        Text(row.prepend)
                            .font(.system(.body, design: .monospaced))
                            .foregroundStyle(.secondary)

                        Spacer()
                    }
                }
                .listStyle(.plain)
            }
        }
    }

    private func columnHeader(_ title: String, width: CGFloat?) -> some View {
        Text(title)
            .font(.caption.weight(.semibold))
            .foregroundStyle(.secondary)
            .textCase(.uppercase)
            .frame(width: width, alignment: .leading)
    }
}
