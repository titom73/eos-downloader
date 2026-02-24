import XCTest
@testable import EosDownloaderCore

final class ModelDecodingTests: XCTestCase {

    // MARK: - VersionEntry

    func testVersionEntryDecoding() throws {
        let json = Data(#"{"version":"4.29.3M","branch":"4.29"}"#.utf8)
        let entry = try JSONDecoder().decode(VersionEntry.self, from: json)
        XCTAssertEqual(entry.version, "4.29.3M")
        XCTAssertEqual(entry.branch, "4.29")
    }

    func testVersionEntryReleaseTypeM() throws {
        let json = Data(#"{"version":"4.29.3M","branch":"4.29"}"#.utf8)
        let entry = try JSONDecoder().decode(VersionEntry.self, from: json)
        XCTAssertEqual(entry.releaseType, "M")
    }

    func testVersionEntryReleaseTypeF() throws {
        let json = Data(#"{"version":"4.30.1F","branch":"4.30"}"#.utf8)
        let entry = try JSONDecoder().decode(VersionEntry.self, from: json)
        XCTAssertEqual(entry.releaseType, "F")
    }

    func testVersionEntryReleaseTypeUnknown() throws {
        let json = Data(#"{"version":"4.30.1","branch":"4.30"}"#.utf8)
        let entry = try JSONDecoder().decode(VersionEntry.self, from: json)
        XCTAssertNil(entry.releaseType)
    }

    func testVersionEntryArrayDecoding() throws {
        let json = Data(#"[{"version":"4.29.3M","branch":"4.29"},{"version":"4.30.1F","branch":"4.30"}]"#.utf8)
        let entries = try JSONDecoder().decode([VersionEntry].self, from: json)
        XCTAssertEqual(entries.count, 2)
    }

    // MARK: - LatestVersion

    func testLatestVersionDecoding() throws {
        let json = Data(#"{"version":"4.29.3M"}"#.utf8)
        let latest = try JSONDecoder().decode(LatestVersion.self, from: json)
        XCTAssertEqual(latest.version, "4.29.3M")
    }

    // MARK: - MappingEntry

    func testMappingEntryDecoding() throws {
        let json = Data(#"{"extension":".swi","prepend":"EOS"}"#.utf8)
        let entry = try JSONDecoder().decode(MappingEntry.self, from: json)
        XCTAssertEqual(entry.fileExtension, ".swi")
        XCTAssertEqual(entry.prepend, "EOS")
    }

    func testMappingResponseDecoding() throws {
        let json = Data(#"{"64":{"extension":".swi","prepend":"EOS"},"cEOS64":{"extension":".tar.xz","prepend":"cEOS64-lab"}}"#.utf8)
        let response = try JSONDecoder().decode(MappingResponse.self, from: json)
        XCTAssertEqual(response.count, 2)
        XCTAssertEqual(response["64"]?.fileExtension, ".swi")
        XCTAssertEqual(response["cEOS64"]?.prepend, "cEOS64-lab")
    }

    // MARK: - Edge cases

    func testEmptyVersionArray() throws {
        let json = Data("[]".utf8)
        let entries = try JSONDecoder().decode([VersionEntry].self, from: json)
        XCTAssertTrue(entries.isEmpty)
    }

    func testMissingFieldThrows() {
        let json = Data(#"{"version":"4.29.3M"}"#.utf8)
        XCTAssertThrowsError(try JSONDecoder().decode(VersionEntry.self, from: json)) { error in
            XCTAssertTrue(error is DecodingError)
        }
    }
}
