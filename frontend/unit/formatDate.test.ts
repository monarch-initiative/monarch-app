import { afterEach, describe, expect, test, vi } from "vitest";
import { formatReleaseDate } from "@/util/formatDate";

/**
 * Pretend the viewer is somewhere other than UTC.
 *
 * Setting `process.env.TZ` does not work here: vitest resolves the zone once at
 * startup and it stays UTC, so a test written that way passes against the bug.
 * CI runs in UTC too, which is exactly why this shipped. So instead, intercept
 * the formatter and supply a default zone whenever the caller did not ask for
 * one -- which is what a browser does for a user in that zone, and what the
 * unfixed code relied on.
 */
function viewerIn(timeZone: string) {
  const Original = Intl.DateTimeFormat;
  vi.spyOn(Intl, "DateTimeFormat").mockImplementation(
    ((locale?: string, options: Intl.DateTimeFormatOptions = {}) =>
      new Original(locale, {
        ...options,
        timeZone: options.timeZone ?? timeZone,
      })) as unknown as typeof Intl.DateTimeFormat,
  );
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("formatReleaseDate", () => {
  // A KG release is "the 2026-09-04 release" everywhere. Date-only ISO strings parse
  // as UTC midnight, so formatting in the viewer's zone showed the day before to
  // everyone west of UTC.
  test.each([
    "America/Los_Angeles",
    "America/New_York",
    "America/Sao_Paulo",
    "UTC",
    "Europe/Berlin",
    "Pacific/Auckland",
  ])("renders the labelled day to a viewer in %s", (timeZone) => {
    viewerIn(timeZone);
    expect(formatReleaseDate("2026-09-04", "en-US")).toBe("September 4, 2026");
  });

  test("a release on the first of a month does not slip into the previous one", () => {
    viewerIn("America/Los_Angeles");
    expect(formatReleaseDate("2026-09-01", "en-US")).toBe("September 1, 2026");
  });

  test("a new year's release does not slip into the previous year", () => {
    viewerIn("America/Los_Angeles");
    expect(formatReleaseDate("2027-01-01", "en-US")).toBe("January 1, 2027");
  });

  // "unknown" is what /v3/api/version reports when it cannot determine a version, so
  // it reaches this function in normal operation, not only in error paths.
  test.each([null, undefined, "", "unknown", "not a date"])(
    "returns null for %s",
    (input) => {
      expect(formatReleaseDate(input, "en-US")).toBeNull();
    },
  );

  test("honours the requested locale", () => {
    viewerIn("America/New_York");
    expect(formatReleaseDate("2026-09-04", "de-DE")).toBe("4. September 2026");
  });
});
