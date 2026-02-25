import SwiftUI

// MARK: - Arista Brand Colors

/// Arista Networks brand colors as SwiftUI Color extensions.
extension Color {
    /// Arista primary blue (#004E9A)
    static let aristaBlue = Color(red: 0.0, green: 0.306, blue: 0.604)

    /// Arista dark blue for text (#003366)
    static let aristaDarkBlue = Color(red: 0.0, green: 0.2, blue: 0.4)

    /// Arista light accent (#0078D4)
    static let aristaAccent = Color(red: 0.0, green: 0.47, blue: 0.83)
}

// MARK: - Sidebar

/// Sidebar navigation sections.
enum SidebarSection: String, CaseIterable, Identifiable {
    case download = "Download"
    case info = "Info"
    case settings = "Settings"
    case debug = "Debug"

    var id: String { rawValue }

    var icon: String {
        switch self {
        case .download: return "arrow.down.circle.fill"
        case .info: return "info.circle.fill"
        case .settings: return "gearshape.fill"
        case .debug: return "ladybug.fill"
        }
    }

    var iconColor: Color {
        switch self {
        case .download: return .aristaBlue
        case .info: return .teal
        case .settings: return .gray
        case .debug: return .orange
        }
    }

    var subtitle: String {
        switch self {
        case .download: return "EOS, CVP, Path"
        case .info: return "Versions & releases"
        case .settings: return "Token & binary"
        case .debug: return "XML & diagnostics"
        }
    }
}

struct SidebarView: View {
    @Binding var selection: SidebarSection

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // App title
            Text("EOS Downloader")
                .font(.headline)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 16)
                .padding(.top, 12)
                .padding(.bottom, 8)

            // Navigation items
            VStack(spacing: 2) {
                ForEach(SidebarSection.allCases) { section in
                    SidebarRow(section: section, isSelected: selection == section)
                        .onTapGesture {
                            withAnimation(.easeInOut(duration: 0.15)) {
                                selection = section
                            }
                        }
                }
            }
            .padding(.horizontal, 8)

            Spacer()
        }
        .background(Color(nsColor: .windowBackgroundColor))
    }
}

private struct SidebarRow: View {
    let section: SidebarSection
    let isSelected: Bool

    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: section.icon)
                .font(.body)
                .foregroundStyle(isSelected ? .white : section.iconColor)
                .frame(width: 22)

            VStack(alignment: .leading, spacing: 1) {
                Text(section.rawValue)
                    .font(.body.weight(.medium))
                    .foregroundStyle(isSelected ? .white : .primary)
                Text(section.subtitle)
                    .font(.caption)
                    .foregroundStyle(isSelected ? .white.opacity(0.8) : .secondary)
            }

            Spacer()
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(isSelected ? Color.aristaBlue : Color.clear)
        )
        .contentShape(Rectangle())
    }
}
