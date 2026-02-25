import Foundation

/// Represents a version entry from `ardl info versions --format json`.
/// JSON contract: {"version": "4.29.3M", "branch": "4.29"}
struct VersionEntry: Codable, Identifiable, Hashable {
    var id: String { version }
    let version: String
    let branch: String

    /// Extract release type suffix (M, F, INT) from version string.
    var releaseType: String {
        if version.hasSuffix("M") { return "M" }
        if version.hasSuffix("F") { return "F" }
        if version.contains("INT") { return "INT" }
        return "Unknown"
    }

    /// Numeric (major, minor, patch) tuple for semantic descending sort.
    /// Strips trailing non-digit characters (M, F, INT…) before parsing.
    var versionSortKey: (Int, Int, Int) {
        let stripped = version.trimmingCharacters(in: .init(charactersIn: "MFINT"))
        let parts = stripped.split(separator: ".").compactMap { Int($0) }
        return (
            parts.indices.contains(0) ? parts[0] : 0,
            parts.indices.contains(1) ? parts[1] : 0,
            parts.indices.contains(2) ? parts[2] : 0
        )
    }
}
