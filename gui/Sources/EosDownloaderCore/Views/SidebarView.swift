import SwiftUI

/// Sidebar navigation sections.
enum SidebarSection: String, CaseIterable, Identifiable {
    case download = "Download"
    case info = "Info"
    case settings = "Settings"
    case debug = "Debug"

    var id: String { rawValue }

    var icon: String {
        switch self {
        case .download: return "arrow.down.circle"
        case .info: return "info.circle"
        case .settings: return "gearshape"
        case .debug: return "ladybug"
        }
    }
}

struct SidebarView: View {
    @Binding var selection: SidebarSection?

    var body: some View {
        List(SidebarSection.allCases, selection: $selection) { section in
            Label(section.rawValue, systemImage: section.icon)
                .tag(section)
        }
        .listStyle(.sidebar)
        .navigationTitle("Sections")
    }
}
