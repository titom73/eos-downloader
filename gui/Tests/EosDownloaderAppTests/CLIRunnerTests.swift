import XCTest
@testable import EosDownloaderCore

final class CLIRunnerTests: XCTestCase {

    // MARK: - CLIBinaryLocator

    func testLocatorFallsBackToWhich() throws {
        // When no bundled binary and no custom path, locator should try `which`
        UserDefaults.standard.removeObject(forKey: "customArdlPath")
        // We can't guarantee ardl is on PATH in CI, so just verify the method doesn't crash
        _ = try? CLIBinaryLocator.locate()
    }

    func testLocatorRespectsCustomPath() throws {
        let tempBinary = FileManager.default.temporaryDirectory
            .appendingPathComponent("fake_ardl_\(UUID().uuidString)")
        FileManager.default.createFile(atPath: tempBinary.path, contents: Data())
        try FileManager.default.setAttributes([.posixPermissions: 0o755], ofItemAtPath: tempBinary.path)
        defer { try? FileManager.default.removeItem(at: tempBinary) }

        UserDefaults.standard.set(tempBinary.path, forKey: "customArdlPath")
        defer { UserDefaults.standard.removeObject(forKey: "customArdlPath") }

        let result = try CLIBinaryLocator.locate()
        XCTAssertEqual(result.path, tempBinary.path)
    }

    // MARK: - CLIError classification

    func testErrorFromExitCode1() {
        let error = CLIError.from(exitCode: 1, stderr: "some unknown error")
        XCTAssertEqual(error, .processTerminated(exitCode: 1, stderr: "some unknown error"))
    }

    func testErrorFromExitCode2WithTokenExpired() {
        let error = CLIError.from(exitCode: 2, stderr: "token expired please renew")
        XCTAssertEqual(error, .tokenExpired)
    }

    func testErrorFromExitCode2WithAuthFailed() {
        let error = CLIError.from(exitCode: 2, stderr: "authentication failed")
        XCTAssertEqual(error, .tokenExpired)
    }

    func testErrorFromExitCode2WithoutTokenKeyword() {
        let error = CLIError.from(exitCode: 2, stderr: "some other error")
        XCTAssertEqual(error, .processTerminated(exitCode: 2, stderr: "some other error"))
    }

    // MARK: - CLIResult

    func testCLIResultDecodeValidJSON() throws {
        let json = #"[{"version":"4.29.3M","branch":"4.29"}]"#
        let result = CLIResult(exitCode: 0, stdout: json, stderr: "")
        let entries = try result.decode([VersionEntry].self)
        XCTAssertEqual(entries.count, 1)
        XCTAssertEqual(entries[0].version, "4.29.3M")
        XCTAssertEqual(entries[0].branch, "4.29")
    }

    func testCLIResultDecodeInvalidJSON() {
        let result = CLIResult(exitCode: 0, stdout: "not json", stderr: "")
        XCTAssertThrowsError(try result.decode([VersionEntry].self))
    }

    // MARK: - ANSI stripping

    func testStripANSIRemovesCodes() {
        let input = "\u{1B}[32mSuccess\u{1B}[0m: done"
        let stripped = CLIRunner.stripANSI(input)
        XCTAssertEqual(stripped, "Success: done")
    }

    func testStripANSIPassthroughClean() {
        let input = "No ANSI here"
        let stripped = CLIRunner.stripANSI(input)
        XCTAssertEqual(stripped, "No ANSI here")
    }
}
