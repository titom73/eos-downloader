import Foundation

/// Represents a single format entry from `ardl info mapping --format json`.
/// JSON contract: {"extension": ".swi", "prepend": "EOS64"}
/// Note: "extension" is a Swift keyword, requiring CodingKeys.
struct MappingEntry: Codable, Identifiable {
    var id: String { prepend }
    let fileExtension: String
    let prepend: String

    enum CodingKeys: String, CodingKey {
        case fileExtension = "extension"
        case prepend
    }
}

/// Full mapping response keyed by format name (e.g. "64", "cEOS", "vEOS-lab").
typealias MappingResponse = [String: MappingEntry]
