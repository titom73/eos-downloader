import SwiftUI

/// Container for download tabs: EOS, CVP, Path.
struct DownloadView: View {
    @State private var selectedTab: DownloadTab = .eos

    enum DownloadTab: String, CaseIterable {
        case eos = "EOS"
        case cvp = "CVP"
        case path = "Direct Path"
    }

    var body: some View {
        VStack(spacing: 0) {
            Picker("Download Type", selection: $selectedTab) {
                ForEach(DownloadTab.allCases, id: \.self) { tab in
                    Text(tab.rawValue).tag(tab)
                }
            }
            .pickerStyle(.segmented)
            .padding()

            Divider()

            switch selectedTab {
            case .eos:
                EosDownloadView()
            case .cvp:
                // Phase 3 placeholder
                Text("CVP download — coming in Phase 3")
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            case .path:
                // Phase 3 placeholder
                Text("Direct path download — coming in Phase 3")
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
    }
}
