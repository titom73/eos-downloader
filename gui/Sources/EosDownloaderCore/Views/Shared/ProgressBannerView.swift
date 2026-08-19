import SwiftUI

/// Tracks the current phase and percentage of a download operation.
struct DownloadProgress {
    enum Phase: String {
        case searching = "Searching for version..."
        case downloading = "Downloading..."
        case checksum = "Verifying checksum..."
        case dockerImport = "Importing Docker image..."
        case completed = "Completed"
        case failed = "Failed"
    }

    var phase: Phase = .searching
    var percentage: Double?
    var speed: String?
    var downloadedSize: String?
    var totalSize: String?
    var currentFile: String?
    var fileIndex: Int = 0

    var isComplete: Bool { phase == .completed || phase == .failed }
    var isIndeterminate: Bool { percentage == nil }

    /// Fraction 0...1 for ProgressView
    var fractionCompleted: Double {
        guard let pct = percentage else { return 0 }
        return min(max(pct / 100.0, 0), 1)
    }

    var statusText: String {
        var text = phase.rawValue
        if let file = currentFile {
            // Show short filename
            let shortName = (file as NSString).lastPathComponent
            if fileIndex > 0 {
                text = "Downloading file \(fileIndex)... \(shortName)"
            } else {
                text = "\(phase.rawValue) \(shortName)"
            }
        }
        return text
    }

    var detailText: String? {
        var parts: [String] = []
        if let pct = percentage { parts.append(String(format: "%.1f%%", pct)) }
        if let spd = speed { parts.append(spd) }
        if let dl = downloadedSize, let tot = totalSize {
            parts.append("\(dl) / \(tot)")
        } else if let dl = downloadedSize {
            parts.append(dl)
        }
        return parts.isEmpty ? nil : parts.joined(separator: " · ")
    }

    // MARK: - Parsing

    /// Update progress from a new log line.
    mutating func update(from line: String) {
        let lower = line.lowercased()

        // Phase detection from CLI console output
        if lower.contains("searching for") {
            phase = .searching
            return
        }

        // Detect a new file starting to download — reset progress
        if lower.contains("downloading") && !lower.contains("download completed") {
            let newFile = Self.extractFilename(from: line)
            if let newFile = newFile, newFile != currentFile {
                // New file → reset progress counters
                fileIndex += 1
                currentFile = newFile
                percentage = nil
                speed = nil
                downloadedSize = nil
                totalSize = nil
            }
            phase = .downloading

            // Also extract percentage/speed/size from the same line (Rich progress lines)
            Self.extractMetrics(from: line, percentage: &percentage, speed: &speed,
                                downloadedSize: &downloadedSize, totalSize: &totalSize)
            return
        }

        if lower.contains("starting download") {
            phase = .downloading
            return
        }

        if lower.contains("checking checksum") || (lower.contains("checksum") && lower.contains("verif")) {
            phase = .checksum
            percentage = nil
            speed = nil
            return
        }

        if lower.contains("importing docker") {
            phase = .dockerImport
            percentage = nil
            speed = nil
            return
        }

        if lower.contains("download completed") || lower.contains("downloaded in:") || lower.contains("found in cache") {
            phase = .completed
            percentage = 100
            speed = nil
            return
        }

        if lower.contains("error") || lower.contains("failed") {
            phase = .failed
            return
        }

        // For lines that are just progress updates (percentage, speed, size)
        Self.extractMetrics(from: line, percentage: &percentage, speed: &speed,
                            downloadedSize: &downloadedSize, totalSize: &totalSize)
        if percentage != nil && phase == .searching {
            phase = .downloading
        }
    }

    /// Extract percentage, speed, and sizes from a log line.
    private static func extractMetrics(
        from line: String,
        percentage: inout Double?,
        speed: inout String?,
        downloadedSize: inout String?,
        totalSize: inout String?
    ) {
        // Extract percentage: "XX.X%"
        if let pctMatch = line.range(of: #"(\d{1,3}(?:\.\d+)?)%"#, options: .regularExpression) {
            let pctStr = line[pctMatch].dropLast()
            if let pct = Double(pctStr) {
                percentage = pct
            }
        }

        // Extract transfer speed: "XX.X MB/s" or "XX.X kB/s"
        if let speedMatch = line.range(of: #"\d+(?:\.\d+)?\s*(?:k|M|G)?B/s"#, options: .regularExpression) {
            speed = String(line[speedMatch])
        }

        // Extract download/total sizes: "500.0/1100.0 MB"
        if let sizeMatch = line.range(of: #"(\d+(?:\.\d+)?)\s*(?:k|M|G|T)?i?B?\s*/\s*(\d+(?:\.\d+)?)\s*(?:k|M|G|T)?i?B"#, options: .regularExpression) {
            let sizeStr = String(line[sizeMatch])
            let halves = sizeStr.split(separator: "/")
            if halves.count == 2 {
                downloadedSize = String(halves[0]).trimmingCharacters(in: .whitespaces)
                totalSize = String(halves[1]).trimmingCharacters(in: .whitespaces)
            }
        }
    }

    /// Extract filename from a log line like "Downloading cEOS64-lab-4.35.2F.tar.xz.sha512sum"
    private static func extractFilename(from line: String) -> String? {
        // Match "Downloading <filename>" — handles both Rich emoji prefix and plain text
        if let match = line.range(of: #"[Dd]ownloading\s+(\S+)"#, options: .regularExpression) {
            let sub = line[match]
            let parts = sub.split(separator: " ", maxSplits: 1)
            if parts.count > 1 {
                let candidate = String(parts[1])
                // Skip if it's just a keyword like "for" (from "Starting download for...")
                if candidate == "for" || candidate == "from" { return nil }
                return candidate
            }
        }
        return nil
    }
}

/// Download progress bar with phase indicator, percentage, and cancel button.
struct DownloadProgressView: View {
    let progress: DownloadProgress
    let onCancel: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Phase label + Cancel
            HStack {
                phaseIcon
                Text(progress.statusText)
                    .font(.callout.weight(.medium))
                    .foregroundStyle(phaseColor)
                    .lineLimit(1)
                Spacer()
                Button("Cancel", role: .destructive) {
                    onCancel()
                }
                .buttonStyle(.bordered)
                .controlSize(.small)
            }

            // Progress bar
            if progress.isIndeterminate {
                ProgressView()
                    .progressViewStyle(.linear)
                    .tint(Color.aristaBlue)
            } else {
                ProgressView(value: progress.fractionCompleted)
                    .progressViewStyle(.linear)
                    .tint(progressTint)
            }

            // Detail line: percentage · speed · size
            if let detail = progress.detailText {
                Text(detail)
                    .font(.system(.caption, design: .monospaced))
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(Color.aristaBlue.opacity(0.06))
        .overlay(alignment: .bottom) { Divider() }
    }

    private var phaseIcon: some View {
        Group {
            switch progress.phase {
            case .searching:
                Image(systemName: "magnifyingglass")
            case .downloading:
                Image(systemName: "arrow.down.circle.fill")
            case .checksum:
                Image(systemName: "checkmark.shield")
            case .dockerImport:
                Image(systemName: "shippingbox.fill")
            case .completed:
                Image(systemName: "checkmark.circle.fill")
            case .failed:
                Image(systemName: "xmark.circle.fill")
            }
        }
        .font(.callout)
        .foregroundStyle(phaseColor)
    }

    private var phaseColor: Color {
        switch progress.phase {
        case .searching: return .secondary
        case .downloading: return Color.aristaBlue
        case .checksum: return .orange
        case .dockerImport: return .indigo
        case .completed: return .green
        case .failed: return .red
        }
    }

    private var progressTint: Color {
        switch progress.phase {
        case .completed: return .green
        case .failed: return .red
        default: return Color.aristaBlue
        }
    }
}

/// Legacy shim – simple banner with indeterminate spinner.
struct ProgressBannerView: View {
    let message: String
    let onCancel: () -> Void

    var body: some View {
        DownloadProgressView(
            progress: {
                var p = DownloadProgress()
                p.phase = .downloading
                return p
            }(),
            onCancel: onCancel
        )
    }
}
