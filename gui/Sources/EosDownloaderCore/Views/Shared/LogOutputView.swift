import SwiftUI

/// Scrollable log output view with auto-scroll to bottom and colored lines.
struct LogOutputView: View {
    let lines: [String]

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 1) {
                    ForEach(Array(lines.enumerated()), id: \.offset) { index, line in
                        HStack(spacing: 6) {
                            Text("\(index + 1)")
                                .font(.system(.caption2, design: .monospaced))
                                .foregroundStyle(.tertiary)
                                .frame(width: 28, alignment: .trailing)

                            Text(line)
                                .font(.system(.caption, design: .monospaced))
                                .foregroundStyle(colorForLine(line))
                                .textSelection(.enabled)
                        }
                        .padding(.vertical, 1)
                        .id(index)
                    }
                }
                .padding(8)
            }
            .background(Color(nsColor: .textBackgroundColor))
            .clipShape(RoundedRectangle(cornerRadius: 4))
            .onChange(of: lines.count) { _ in
                if let lastIndex = lines.indices.last {
                    withAnimation(.easeOut(duration: 0.1)) {
                        proxy.scrollTo(lastIndex, anchor: .bottom)
                    }
                }
            }
        }
        .overlay {
            if lines.isEmpty {
                VStack(spacing: 8) {
                    Image(systemName: "terminal")
                        .font(.title2)
                        .foregroundStyle(.quaternary)
                    Text("Log output will appear here")
                        .font(.callout)
                        .foregroundStyle(.tertiary)
                }
            }
        }
    }

    private func colorForLine(_ line: String) -> Color {
        let lower = line.lowercased()
        if lower.contains("error") || lower.contains("failed") || lower.contains("fatal") {
            return .red
        }
        if lower.contains("warning") || lower.contains("warn") {
            return .orange
        }
        if lower.contains("success") || lower.contains("completed") || lower.contains("done") {
            return .green
        }
        if lower.hasPrefix("running:") {
            return Color.aristaBlue
        }
        return .primary
    }
}
