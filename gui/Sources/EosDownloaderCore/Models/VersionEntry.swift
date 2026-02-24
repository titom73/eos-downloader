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
}
