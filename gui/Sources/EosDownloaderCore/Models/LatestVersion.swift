import Foundation

/// Represents the latest version response from `ardl info latest --format json`.
/// JSON contract: {"version": "4.29.3M"}
struct LatestVersion: Codable {
    let version: String
}
