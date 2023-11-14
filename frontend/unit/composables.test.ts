import { expect, test, vi } from "vitest";
import { useQuery } from "@/util/composables";
import { sleep } from "@/util/debug";

/** useQuery tests */

/** mocked func to count calls inside api calls */
const mock = vi.fn();

/** simulated api call */
const apiCall = async ({ wait = 10, data = "", error = "" } = {}) => {
  await sleep(wait);
  if (error) throw Error(error);
  mock();
  return data;
};

test("Query function calls", async () => {
  /** returns callable query func */
  const { query } = useQuery(apiCall, "");
  await query();
  await query();
  await query();
  expect(mock.mock.calls.length).toBe(3);
});

test("Statuses work", async () => {
  const { query, isLoading, isError, isSuccess } = useQuery(apiCall, "");

  /** check all false at start */
  expect(isLoading.value).toBe(false);
  expect(isError.value).toBe(false);
  expect(isSuccess.value).toBe(false);

  /** start query (but don't wait to finish with await) */
  query();

  /** check loading started */
  expect(isLoading.value).toBe(true);
  expect(isError.value).toBe(false);
  expect(isSuccess.value).toBe(false);

  /** wait a good amount until query definitely done */
  await sleep(20);

  /** check loading done and success true */
  expect(isLoading.value).toBe(false);
  expect(isError.value).toBe(false);
  expect(isSuccess.value).toBe(true);

  /** start another query that will throw error */
  query({ error: "fake error" });

  /** check loading started, and other statuses reset */
  expect(isLoading.value).toBe(true);
  expect(isError.value).toBe(false);
  expect(isSuccess.value).toBe(false);

  /** wait until query done */
  await sleep(20);

  /** check loading done and error true */
  expect(isLoading.value).toBe(false);
  expect(isError.value).toBe(true);
  expect(isSuccess.value).toBe(false);
});

test("Data and default value works", async () => {
  const { query, data } = useQuery(apiCall, "");

  /** check default value */
  expect(data.value).toBe("");

  /** start query that will return fake data */
  query({ data: "fake data" });

  /** data shouldn't be ready yet */
  expect(data.value).toBe("");

  /** wait until query doe */
  await sleep(20);

  /** check data has returned/been set */
  expect(data.value).toBe("fake data");

  /** start another query that will throw error */
  query({ data: "fake data", error: "fake error" });

  /** data should reset to default value */
  expect(data.value).toBe("");

  /** wait until query doe */
  await sleep(20);

  /** data should still be default value */
  expect(data.value).toBe("");
});

test("Handles race conditions and calls success func", async () => {
  const onSuccess = vi.fn();
  const { query, data } = useQuery(apiCall, "", onSuccess);

  /** start two competing queries, but first will complete after second */
  query({ wait: 50, data: "first query" });
  query({ wait: 10, data: "second query" });

  /** wait until second query definitely done and check returned data */
  await sleep(20);
  expect(data.value).toBe("second query");

  /** wait until first query definitely done, */
  await sleep(100);
  /**
   * check returned data still matches second query because it was called most
   * recently
   */
  expect(data.value).toBe("second query");

  /** only final of concurrent queries should call onSuccess function. */
  expect(onSuccess.mock.calls.length).toBe(1);
  expect(onSuccess.mock.calls[0][0]).toBe("second query");
});
